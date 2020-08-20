package api

import (
	"context"
	pb "gorepick/pb"
)

func (s *Server) LeaveTeam(ctx context.Context, request *pb.LeaveTeamRequest) (*pb.LeaveTeamResponse, error) {
	user := s.GetUsername(ctx)

	err := s.st.LeaveTeam(user)
	if err != nil {
		return nil, err
	}

	return &pb.LeaveTeamResponse{}, nil
}
