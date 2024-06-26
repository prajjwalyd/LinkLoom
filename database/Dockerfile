# Use the official PostgreSQL image from Docker Hub
FROM postgres:latest

# Environment variables
ENV POSTGRES_DB url_shortener_db
ENV POSTGRES_USER user
ENV POSTGRES_PASSWORD password

# Copy the initialization script into the Docker container
COPY ./init.sql /docker-entrypoint-initdb.d/
