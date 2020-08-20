package api

import (
	"context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/metadata"
	"google.golang.org/grpc/status"
	"strings"
)

func (s *Server) authorize(ctx context.Context) error {
	md, ok := metadata.FromIncomingContext(ctx)
	if !ok {
		return status.Errorf(codes.InvalidArgument, "Retrieving metadata is failed")
	}

	authHeader, ok := md["authorization"]
	if !ok {
		return status.Errorf(codes.Unauthenticated, "Authorization token is not supplied")
	}

	auth := authHeader[0]
	idx := strings.LastIndex(auth, ":")

	if idx < 0 {
		return status.Errorf(codes.Unauthenticated, "Invalid authorization header")
	}

	token := auth[idx+1:]
	login := auth[:idx]

	err := s.st.Check(login, token)
	if err != nil {
		return err
	}

	return nil
}

func (s *Server) AuthInterceptor(ctx context.Context,
	req interface{},
	info *grpc.UnaryServerInfo,
	handler grpc.UnaryHandler) (interface{}, error) {

	if info.FullMethod != "/gorepick.api.Api/Register" && info.FullMethod != "/gorepick.api.Api/Events" {
		if err := s.authorize(ctx); err != nil {
			return nil, err
		}
	}

	h, err := handler(ctx, req)

	return h, err
}

func (s *Server) WithAuth() grpc.ServerOption {
	return grpc.UnaryInterceptor(s.AuthInterceptor)
}
