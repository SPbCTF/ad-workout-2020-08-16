package help

import (
	"fmt"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"reflect"
)

func HandleError(method string, err error) {
	if err != nil {
		e, ok := status.FromError(err)
		if !ok {
			Exit(MUMBLE, "not grpc error returned", err.Error())
		}

		switch e.Code() {
		case codes.Unavailable:
			Exit(DOWN, fmt.Sprintf("%s unavailable", method), e.Message())
		default:
			Exit(MUMBLE, fmt.Sprintf("%s returned code %v", method, e.Code()), e.Message())
		}
	}
}

func AssertEqual(method string, name string, expected interface{}, got interface{}) {
	if !reflect.DeepEqual(expected, got) {
		Exit(
			MUMBLE,
			fmt.Sprintf("%s Filed %s has unexpected value", method, name),
			fmt.Sprintf("%s Field %s has unexpected value. Expected: %v. Got: %v", method, name, expected, got),
		)
	}
}
