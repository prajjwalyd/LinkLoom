package main

import (
	"context"
	"encoding/json"
	"log"
	"net/http"
	"os"
	"sync"

	"github.com/go-redis/redis/v8"
)

var (
	urlMappings = make(map[string]string)
	mu          sync.RWMutex
	redisClient *redis.Client
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

	// Subscribe to Redis channel
	subscriber := redisClient.Subscribe(ctx, "url_channel")
	defer subscriber.Close()

	go func() {
		for msg := range subscriber.Channel() {
			var mapping URLMapping
			if err := json.Unmarshal([]byte(msg.Payload), &mapping); err != nil {
				log.Printf("Error unmarshalling message: %v\n", err)
				continue
			}

			// Store the URL mapping in memory
			mu.Lock()
			urlMappings[mapping.ShortURL] = mapping.LongURL
			mu.Unlock()
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

	mu.RLock()
	longURL, exists := urlMappings[shortURL]
	mu.RUnlock()

	if !exists {
		http.Error(w, "Short URL not found", http.StatusNotFound)
		return
	}

	// Redirect to long URL
	http.Redirect(w, r, longURL, http.StatusFound)
}
