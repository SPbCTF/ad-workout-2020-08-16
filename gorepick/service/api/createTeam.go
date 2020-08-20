package api

import (
	"context"
	pb "gorepick/pb"
)

func (s *Server) CreateTeam(ctx context.Context, request *pb.CreateTeamRequest) (*pb.CreateTeamResponse, error) {
	user := s.GetUsername(ctx)

	token, err := s.st.CreateTeam(user, request.Name, request.Info)
	if err != nil {
		return nil, err
	}

	return &pb.CreateTeamResponse{
		Token: token,
	}, nil
}
