package main

import (
	"context"
	"fmt"
	"github.com/bxcodec/faker/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"gorepick-checker/help"
	pb "gorepick-checker/pb"
	"io"
	"os"
	"strings"
	"time"
)

const (
	port = 2020
)

func Info(_ []string) {
	help.Exit(help.OK, "vulns: 1", "")
}

func checkEvents(done chan struct{}, eventsClient pb.Api_EventsClient, expectedEvents []*pb.Event) {
	count := 0
	method := "/Events"

	for {
		ev, err := eventsClient.Recv()
		if err == io.EOF {
			break
		}
		help.HandleError(method, err)

		if ev.Type != expectedEvents[count].Type ||
			ev.Username != expectedEvents[count].Username ||
			ev.Team != expectedEvents[count].Team {
			continue
		}

		now := time.Now()
		ts := ev.Timestamp.AsTime()
		delta := now.Sub(ts)
		if delta > 10*time.Second || delta < -10*time.Second {
			help.Exit(
				help.MUMBLE,
				"Invalid timestamp (more than 10 seconds delta) in /Events",
				fmt.Sprintf("Expected: %v. Got: %v", now, ts),
			)
		}

		count += 1
		if count == len(expectedEvents) {
			break
		}
	}

	if count == len(expectedEvents) {
		close(done)
	}
}

func Check(args []string) {
	ip := args[0]
	conn, err := grpc.Dial(fmt.Sprintf("%s:%v", ip, port), grpc.WithInsecure())
	if err != nil {
		help.Exit(help.DOWN, "can't grpc Dial", err.Error())
	}
	defer conn.Close()

	client := pb.NewApiClient(conn)
	ctx := context.Background()

	// generate fake data
	// first user
	user := faker.Username()
	password := faker.Password()
	// team
	team := "[" + faker.IPv6() + "]" + faker.Word() + " " + faker.Word()
	info := faker.Sentence()
	// second user
	user2 := faker.Username()
	password2 := faker.Password()
	// end generate fake data

	// Subscribe on events
	events, err := client.Events(ctx, &pb.EventsRequest{})
	method := "/Events"
	help.HandleError(method, err)

	done := make(chan struct{})
	go checkEvents(done, events, []*pb.Event{
		{
			Type:     pb.Event_register,
			Username: user,
		},
		{
			Type:     pb.Event_create,
			Username: user,
			Team:     team,
		},
		{
			Type:     pb.Event_register,
			Username: user2,
		},
		{
			Type:     pb.Event_join,
			Username: user2,
			Team:     team,
		},
		{
			Type:     pb.Event_leave,
			Username: user,
		},
	})
	// time for begin listen events
	time.Sleep(200 * time.Millisecond)

	// Try register
	regResp, err := client.Register(ctx, &pb.RegisterRequest{
		Username: user,
		Password: password,
	})
	method = "/Register"
	help.HandleError(method, err)

	authToken := regResp.Token
	ctx = metadata.AppendToOutgoingContext(
		ctx,
		"authorization",
		fmt.Sprintf("%s:%s", user, authToken),
	)

	// Try get Info
	infoResp, err := client.Info(ctx, &pb.InfoRequest{})
	method = "/Info"
	help.HandleError(method, err)

	help.AssertEqual(method, "Username", user, infoResp.Username)
	help.AssertEqual(method, "Team", "", infoResp.Team)
	help.AssertEqual(method, "TeamInfo", "", infoResp.TeamInfo)
	help.AssertEqual(method, "TeamToken", "", infoResp.TeamToken)

	// Try Create team
	createResp, err := client.CreateTeam(ctx, &pb.CreateTeamRequest{
		Name: team,
		Info: info,
	})
	method = "/CreateTeam"
	help.HandleError(method, err)

	teamToken := createResp.Token

	// Try get Info and check token and info
	infoResp, err = client.Info(ctx, &pb.InfoRequest{})
	method = "/Info"
	help.HandleError(method, err)

	help.AssertEqual(method, "Username", user, infoResp.Username)
	help.AssertEqual(method, "Team", team, infoResp.Team)
	help.AssertEqual(method, "TeamInfo", info, infoResp.TeamInfo)
	help.AssertEqual(method, "TeamToken", teamToken, infoResp.TeamToken)

	// Register another user for check join ability
	regResp, err = client.Register(ctx, &pb.RegisterRequest{
		Username: user2,
		Password: password2,
	})
	method = "/Register"
	help.HandleError(method, err)

	authToken2 := regResp.Token
	ctx2 := metadata.AppendToOutgoingContext(
		context.Background(),
		"authorization",
		fmt.Sprintf("%s:%s", user2, authToken2),
	)

	// Try join team
	_, err = client.JoinTeam(ctx2, &pb.JoinTeamRequest{
		Name:  team,
		Token: teamToken,
	})
	method = "/JoinTeam"
	help.HandleError(method, err)

	// Get info on user2 to check team
	infoResp, err = client.Info(ctx2, &pb.InfoRequest{})
	help.HandleError("/Info", err)

	help.AssertEqual(method, "Username", user2, infoResp.Username)
	help.AssertEqual(method, "Team", team, infoResp.Team)
	help.AssertEqual(method, "TeamInfo", info, infoResp.TeamInfo)
	help.AssertEqual(method, "TeamToken", teamToken, infoResp.TeamToken)

	// Leave team on first user
	_, err = client.LeaveTeam(ctx, &pb.LeaveTeamRequest{})
	method = "/LeaveTeam"
	help.HandleError(method, err)

	// Get info on user for checking leave team
	infoResp, err = client.Info(ctx, &pb.InfoRequest{})
	method = "/Info"
	help.HandleError(method, err)

	help.AssertEqual(method, "Username", user, infoResp.Username)
	help.AssertEqual(method, "Team", "", infoResp.Team)
	help.AssertEqual(method, "TeamInfo", "", infoResp.TeamInfo)
	help.AssertEqual(method, "TeamToken", "", infoResp.TeamToken)

	// Get info on user2 for checking joined team
	infoResp, err = client.Info(ctx2, &pb.InfoRequest{})
	method = "/Info"
	help.HandleError("/Info", err)

	help.AssertEqual(method, "Username", user2, infoResp.Username)
	help.AssertEqual(method, "Team", team, infoResp.Team)
	help.AssertEqual(method, "TeamInfo", info, infoResp.TeamInfo)
	help.AssertEqual(method, "TeamToken", teamToken, infoResp.TeamToken)

	deadline := time.After(10 * time.Second)
	for {
		select {
		case <-deadline:
			help.Exit(help.MUMBLE, "Wait for event too long", "")
		case <-done:
			help.Exit(help.OK, "", "")
		}
	}
}

func Get(args []string) {
	ip := args[0]
	flagId := args[1]
	flag := args[2]

	flagIdData := strings.SplitN(flagId, ":", 2)
	if len(flagIdData) < 2 {
		help.Exit(help.CORRUPT, "Previous put failed", flagId)
	}
	team := flagIdData[0]
	teamToken := flagIdData[1]

	conn, err := grpc.Dial(fmt.Sprintf("%s:%v", ip, port), grpc.WithInsecure())
	if err != nil {
		help.Exit(help.DOWN, "can't grpc Dial", err.Error())
	}
	defer conn.Close()

	client := pb.NewApiClient(conn)
	ctx := context.Background()

	// generate fake data
	// first user
	user := faker.Username()
	password := faker.Password()
	// end generate fake data

	// Try register
	regResp, err := client.Register(ctx, &pb.RegisterRequest{
		Username: user,
		Password: password,
	})
	method := "/Register"
	help.HandleError(method, err)

	authToken := regResp.Token
	ctx = metadata.AppendToOutgoingContext(
		ctx,
		"authorization",
		fmt.Sprintf("%s:%s", user, authToken),
	)

	// Try join team
	_, err = client.JoinTeam(ctx, &pb.JoinTeamRequest{
		Name:  team,
		Token: teamToken,
	})
	method = "/JoinTeam"
	help.HandleError(method, err)

	// Get info
	infoResp, err := client.Info(ctx, &pb.InfoRequest{})
	help.HandleError("/Info", err)

	help.AssertEqual(method, "Username", user, infoResp.Username)
	help.AssertEqual(method, "Team", team, infoResp.Team)
	help.AssertEqual(method, "TeamToken", teamToken, infoResp.TeamToken)

	if !strings.Contains(infoResp.TeamInfo, flag) {
		help.Exit(
			help.CORRUPT,
			fmt.Sprintf("Flag not found"),
			infoResp.TeamInfo,
		)
	}

	help.Exit(help.OK, "", "")
}

func Put(args []string) {
	ip := args[0]
	flagId := args[1]
	flag := args[2]

	conn, err := grpc.Dial(fmt.Sprintf("%s:%v", ip, port), grpc.WithInsecure())
	if err != nil {
		help.Exit(help.DOWN, "can't grpc Dial", err.Error())
	}
	defer conn.Close()

	client := pb.NewApiClient(conn)
	ctx := context.Background()

	// generate fake data
	// first user
	user := faker.Username()
	password := faker.Password()
	// team
	team := flagId
	info := faker.Sentence() + " " + flag
	// end generate fake data

	// Try register
	regResp, err := client.Register(ctx, &pb.RegisterRequest{
		Username: user,
		Password: password,
	})
	method := "/Register"
	help.HandleError(method, err)

	authToken := regResp.Token
	ctx = metadata.AppendToOutgoingContext(
		ctx,
		"authorization",
		fmt.Sprintf("%s:%s", user, authToken),
	)

	// Try Create team
	createResp, err := client.CreateTeam(ctx, &pb.CreateTeamRequest{
		Name: team,
		Info: info,
	})
	method = "/CreateTeam"
	help.HandleError(method, err)

	teamToken := createResp.Token

	help.Exit(
		help.OK,
		fmt.Sprintf("%s:%s", flagId, teamToken),
		"",
	)
}

func main() {
	if len(os.Args) < 2 {
		help.Exit(help.CHECKER_ERROR, "", "wrong arguments")
	}

	switch os.Args[1] {
	case "info":
		Info(os.Args[2:])
	case "check":
		Check(os.Args[2:])
	case "get":
		Get(os.Args[2:])
	case "put":
		Put(os.Args[2:])
	}
}
