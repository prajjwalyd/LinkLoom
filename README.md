# url-shortner

# python venv
```
python -m venv venv
source venv/bin/activate

deactivate
```

# docker compose
```
docker-compose build

docker-compose up -d

```

# Access PostgreSQL container shell
docker-compose exec db psql -U user -d url_shortener_db

### if using docker compose
docker exec -it url-shortner-db-1 psql -U user -d url_shortener_db


# Once inside the PostgreSQL shell, list tables to verify initialization
\dt

docker-compose down       # Shut down the containers
docker-compose build      # Rebuild Docker images
docker-compose up -d      # Start containers in detached mode