# Use an official Golang runtime as a parent image
FROM golang:1.22-alpine as builder

# Set the current working directory inside the container
WORKDIR /app

# Copy the code into the container
COPY . .

# Build the Go application
RUN go build -o redirection-service .

# Use a minimal base image for the final build
FROM alpine:latest

# Set the working directory in the container
WORKDIR /app

# Copy the binary from the builder stage
COPY --from=builder /app/redirection-service .

# Command to run the executable
CMD ["./redirection-service"]
