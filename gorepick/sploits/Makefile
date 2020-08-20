proto:
	@echo "Make protos..."
	protoc -I=../service/proto --go_out=pb --go-grpc_out=pb ../service/proto/api.proto

teamInvite:
	@echo "Make team invite sploit..."
	CGO_ENABLED=0 go build -mod=vendor -ldflags -s -installsuffix cgo -v -o teamInvite teamInvite.go

registerUser:
	@echo "Make register user sploit..."
	CGO_ENABLED=0 go build -mod=vendor -ldflags -s -installsuffix cgo -v -o registerUser registerUser.go

clean:
	@echo "Cleaning..."
	go clean .
	rm -f teamInvite
	rm -f registerUser

.PHONY: proto clean