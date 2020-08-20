package api

import (
	"context"
	pb "gorepick/pb"
)

func (s *Server) Info(ctx context.Context, _ *pb.InfoRequest) (*pb.InfoResponse, error) {
	user := s.GetUsername(ctx)

	resp, err := s.st.Info(user)
	if err != nil {
		return nil, err
	}

	return resp, nil
}
