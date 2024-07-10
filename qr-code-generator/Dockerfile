FROM golang:1.22-alpine as builder

WORKDIR /app

COPY . .

RUN go build -o qr-code-generator .

FROM alpine:latest

WORKDIR /app

COPY --from=builder /app/qr-code-generator .

CMD ["./qr-code-generator"]