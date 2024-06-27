package main

import (
	"context"
	"encoding/json"
	_ "fmt"
	"log"
	"net/http"
	"os"

	"github.com/go-redis/redis/v8"
)

var (
	redisClient  *redis.Client
	streamName   = "url_stream"
	groupName    = "url_group"
	consumerName = "url_consumer"
)

type URLMapping struct {
	ShortURL string `json:"short_url"`
	LongURL  string `json:"long_url"`
}

func main() {
	// Setup Redis client
	redisClient = redis.NewClient(&redis.Options{
		Addr: "redis:6379",
	})
	ctx := context.Background()

	// Create Consumer Group if not exists
	err := redisClient.XGroupCreateMkStream(ctx, streamName, groupName, "$").Err()
	if err != nil && err.Error() != "BUSYGROUP Consumer Group name already exists" {
		log.Fatalf("Error creating consumer group: %v\n", err)
	}

	go func() {
		for {
			// Read from Redis Stream
			streams, err := redisClient.XReadGroup(ctx, &redis.XReadGroupArgs{
				Group:    groupName,
				Consumer: consumerName,
				Streams:  []string{streamName, ">"},
				Count:    1,
				Block:    0,
			}).Result()
			if err != nil {
				log.Printf("Error reading from Redis Stream: %v\n", err)
				continue
			}

			for _, stream := range streams {
				for _, message := range stream.Messages {
					// Extract and parse the data field from the message
					data, ok := message.Values["data"].(string)
					if !ok {
						log.Printf("Data field missing or of wrong type in message: %v\n", message.Values)
						continue
					}
					
					var mapping URLMapping
					if err := json.Unmarshal([]byte(data), &mapping); err != nil {
						log.Printf("Error unmarshalling message: %v\n", err)
						continue
					}

					// Log the received URL mapping
					log.Printf("Storing URL mapping in Redis: %s -> %s\n", mapping.ShortURL, mapping.LongURL)

					// Store the URL mapping in Redis
					err := redisClient.Set(ctx, mapping.ShortURL, mapping.LongURL, 0).Err()
					if err != nil {
						log.Printf("Error storing URL mapping in Redis: %v\n", err)
					} else {
						log.Printf("Successfully stored URL mapping in Redis: %s -> %s\n", mapping.ShortURL, mapping.LongURL)
					}

					// Acknowledge message
					redisClient.XAck(ctx, streamName, groupName, message.ID)
				}
			}
		}
	}()

	// Setup HTTP server
	http.HandleFunc("/", redirectHandler)
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}
	log.Printf("Server listening on :%s...\n", port)
	log.Fatal(http.ListenAndServe(":"+port, nil))
}

func redirectHandler(w http.ResponseWriter, r *http.Request) {
	shortURL := r.URL.Path[1:] // Extract short URL from request path
	if shortURL == "" {
		http.Error(w, "Short URL not provided", http.StatusBadRequest)
		return
	}

	// Retrieve the long URL from Redis
	ctx := context.Background()
	longURL, err := redisClient.Get(ctx, shortURL).Result()
	if err == redis.Nil {
		http.Error(w, "Short URL not found", http.StatusNotFound)
		return
	} else if err != nil {
		http.Error(w, "Internal server error", http.StatusInternalServerError)
		return
	}

	// Log the redirection
	log.Printf("Redirecting: %s -> %s\n", shortURL, longURL)

	// Redirect to long URL
	http.Redirect(w, r, longURL, http.StatusFound)
}
