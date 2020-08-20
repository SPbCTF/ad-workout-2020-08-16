package storage

import (
	"context"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	pb "gorepick/pb"
	"strings"
)

func (s *Service) CreateTeam(username string, team string, info string) (string, error) {
	ctx := context.Background()

	cmd := s.rdb.EvalSha(ctx, s.scripts["/create_team"], []string{username, team, info})

	result, err := cmd.Result()
	if err != nil {
		return "", status.Errorf(codes.AlreadyExists, err.Error())
	}

	s.notify.Notify(&pb.Event{
		Type:     pb.Event_create,
		Username: username,
		Team:     team,
	})
	response, ok := result.(string)
	if ok {
		return response, nil
	} else {
		return "", status.Errorf(codes.DataLoss, "")
	}
}

func (s *Service) JoinTeam(username string, team string, token string) error {
	ctx := context.Background()

	err := s.rdb.EvalSha(ctx, s.scripts["/join_team"], []string{username, team, token}).Err()

	switch {
	case err == nil:
		s.notify.Notify(&pb.Event{
			Type:     pb.Event_join,
			Username: username,
			Team:     team,
		})
		return nil
	case strings.HasPrefix(err.Error(), "Access denied"):
		return status.Errorf(codes.PermissionDenied, err.Error())
	case strings.HasPrefix(err.Error(), "Already"):
		return status.Errorf(codes.AlreadyExists, err.Error())
	default:
		return status.Errorf(codes.Unknown, "")
	}
}

func (s *Service) LeaveTeam(username string) error {
	ctx := context.Background()

	err := s.rdb.EvalSha(ctx, s.scripts["/leave_team"], []string{username}).Err()
	switch {
	case err == nil:
		s.notify.Notify(&pb.Event{
			Type:     pb.Event_leave,
			Username: username,
		})
		return nil
	case strings.HasPrefix(err.Error(), "Already"):
		return status.Errorf(codes.Canceled, err.Error())
	default:
		return status.Errorf(codes.Unknown, "")
	}
}
