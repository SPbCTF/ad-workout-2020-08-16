FROM golang:1.14.0 as builder

WORKDIR /src-dir
COPY . .
RUN go build -o /go/bin/gorepick main.go

FROM ubuntu:xenial

COPY --from=builder /go/bin/gorepick /go/bin/gorepick
CMD ["/go/bin/gorepick"]