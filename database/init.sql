-- -- Create the database for URL shortener
-- CREATE DATABASE url_shortener_db;

-- Create table for storing URLs
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    long_url TEXT NOT NULL,
    short_url TEXT UNIQUE NOT NULL,
    custom_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Create table for storing analytics
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    short_url_id INT REFERENCES urls(id),
    click_count INT DEFAULT 0,
    last_clicked TIMESTAMP
);
