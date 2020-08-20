APP_NAME=gorepick

build:
	@echo "Building..."
	CGO_ENABLED=0 go build -mod=vendor -ldflags -s -installsuffix cgo -v -o $(APP_NAME) .

proto:
	@echo "Make protos..."
	protoc -I=proto --go_out=pb --go-grpc_out=pb proto/api.proto

clean:
	@echo "Cleaning..."
	go clean .
	rm -f $(APP_NAME)

.PHONY: proto clean
