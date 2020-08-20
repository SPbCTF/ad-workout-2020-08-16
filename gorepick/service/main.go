package main

import (
	"github.com/sirupsen/logrus"
	"github.com/spf13/viper"
	"google.golang.org/grpc"
	"google.golang.org/grpc/reflection"
	"gorepick/api"
	pb "gorepick/pb"
	"gorepick/storage"
	"gorepick/storage/notifier"
	"net"
	"os"
	"time"
)

func InitLog() {
	formatter := logrus.TextFormatter{
		ForceColors:     true,
		TimestampFormat: time.Stamp,
		FullTimestamp:   true,
	}
	logrus.SetFormatter(&formatter)
	logrus.SetOutput(os.Stdout)
}

func main() {
	// Automatic getting ENV
	viper.AutomaticEnv()
	InitLog()

	log := logrus.NewEntry(logrus.StandardLogger())

	notifier := notifier.New(log.WithField("scope", "notify"))

	st := storage.New(
		viper.GetString("REDIS_ADDR"),
		notifier,
		log.WithField("scope", "storage"),
	)

	// Init api
	s := api.New(
		st,
		log.WithField("scope", "api"),
	)

	// Register GRPC server
	grpcServer := grpc.NewServer(
		s.WithAuth(),
	)
	pb.RegisterApiServer(grpcServer, s)
	reflection.Register(grpcServer)

	// Try to listen port
	listener, err := net.Listen("tcp", viper.GetString("LISTEN"))
	if err != nil {
		logrus.WithError(err).Fatalf("Can't listen port")
	}

	// Serve GRPC API
	logrus.Infof("Start serving...")
	logrus.Fatal(grpcServer.Serve(listener))
}
