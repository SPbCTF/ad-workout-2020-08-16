package api

import (
	"context"
	pb "gorepick/pb"
)

func (s *Server) JoinTeam(ctx context.Context, request *pb.JoinTeamRequest) (*pb.JoinTeamResponse, error) {
	user := s.GetUsername(ctx)

	err := s.st.JoinTeam(user, request.Name, request.Token)
	if err != nil {
		return nil, err
	}

	return &pb.JoinTeamResponse{}, nil
}
