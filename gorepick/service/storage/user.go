package storage

import (
	"context"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	pb "gorepick/pb"
	"strings"
)

func (s *Service) Register(username string, password string) (string, error) {
	ctx := context.Background()

	cmd := s.rdb.EvalSha(ctx, s.scripts["/register"], []string{username, password})

	result, err := cmd.Result()
	if err != nil {
		return "", status.Errorf(codes.AlreadyExists, err.Error())
	}

	s.notify.Notify(&pb.Event{
		Type:     pb.Event_register,
		Username: username,
	})
	response, ok := result.(string)
	if ok {
		return response, nil
	} else {
		return "", status.Errorf(codes.DataLoss, "")
	}
}

func (s *Service) Check(username string, token string) error {
	ctx := context.Background()

	err := s.rdb.EvalSha(ctx, s.scripts["/login"], []string{username, token}).Err()
	switch {
	case err == nil:
		return nil
	case strings.HasPrefix(err.Error(), "User not found"):
		return status.Errorf(codes.NotFound, err.Error())
	case strings.HasPrefix(err.Error(), "Access denied"):
		return status.Errorf(codes.PermissionDenied, err.Error())
	default:
		return status.Errorf(codes.Unknown, "")
	}
}

func (s *Service) Info(username string) (*pb.InfoResponse, error) {
	ctx := context.Background()

	cmd := s.rdb.EvalSha(ctx, s.scripts["/info"], []string{username})
	result, _ := cmd.Result()
	data, ok := result.([]interface{})
	if !ok {
		return nil, status.Errorf(codes.DataLoss, "")
	}

	name, ok := data[0].(string)
	if !ok {
		return nil, status.Errorf(codes.DataLoss, "")
	}
	resp := &pb.InfoResponse{
		Username: name,
	}

	if len(data) > 1 {
		resp.Team, ok = data[1].(string)
		if !ok {
			return nil, status.Errorf(codes.DataLoss, "")
		}
		resp.TeamInfo, ok = data[2].(string)
		if !ok {
			return nil, status.Errorf(codes.DataLoss, "")
		}
		resp.TeamToken, ok = data[3].(string)
		if !ok {
			return nil, status.Errorf(codes.DataLoss, "")
		}
	}

	return resp, nil
}
