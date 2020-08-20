package api

import (
	"context"
	pb "gorepick/pb"
)

func (s *Server) Register(ctx context.Context, request *pb.RegisterRequest) (*pb.RegisterResponse, error) {
	token, err := s.st.Register(request.Username, request.Password)
	if err != nil {
		return nil, err
	}

	return &pb.RegisterResponse{
		Token: token,
	}, nil
}
