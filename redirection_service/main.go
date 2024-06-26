package main

import (
	"database/sql"
	"fmt"
	"log"
	"net/http"
	"os"

	_ "github.com/lib/pq"
)

// Database connection string
const (
	host     = "db"
	port     = 5432
	user     = "user"
	password = "password"
	dbname   = "url_shortener_db"
)

var db *sql.DB

func main() {
	// Setup database connection
	dbInfo := fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
		host, port, user, password, dbname)

	var err error
	db, err = sql.Open("postgres", dbInfo)
	if err != nil {
		log.Fatalf("Error opening database connection: %v\n", err)
	}
	defer db.Close()

	// Test database connection
	err = db.Ping()
	if err != nil {
		log.Fatalf("Error connecting to database: %v\n", err)
	}

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

	var longURL string
	err := db.QueryRow("SELECT long_url FROM urls WHERE short_url = $1", shortURL).Scan(&longURL)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Short URL not found", http.StatusNotFound)
		} else {
			http.Error(w, "Internal server error", http.StatusInternalServerError)
		}
		return
	}

	// Redirect to long URL
	http.Redirect(w, r, longURL, http.StatusFound)
}
