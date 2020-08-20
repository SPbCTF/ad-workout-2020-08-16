package api

import (
	"context"
	"github.com/sirupsen/logrus"
	"google.golang.org/grpc/metadata"
	"gorepick/storage"
	"strings"
)

type Server struct {
	st  *storage.Service
	log *logrus.Entry
}

func New(st *storage.Service, log *logrus.Entry) *Server {
	return &Server{
		st:  st,
		log: log,
	}
}

// Only works if user authenticated
func (s *Server) GetUsername(ctx context.Context) string {
	md, _ := metadata.FromIncomingContext(ctx)
	authHeader, _ := md["authorization"]

	auth := authHeader[0]
	authData := strings.Split(auth, ":")

	return authData[0]
}
