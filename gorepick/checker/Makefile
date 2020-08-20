APP_NAME=gorepick-checker

proto:
	@echo "Make protos..."
	protoc -I=../service/proto --go_out=pb --go-grpc_out=pb ../service/proto/api.proto

build:
	@echo "Building..."
	CGO_ENABLED=0 go build -mod=vendor -ldflags -s -installsuffix cgo -v -o $(APP_NAME) .

release:
	@echo "Building release..."
	CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -mod=vendor -ldflags -s -installsuffix cgo -v -o $(APP_NAME) .

clean:
	@echo "Cleaning..."
	go clean .
	rm -f $(APP_NAME)

.PHONY: proto clean