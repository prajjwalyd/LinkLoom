# LinkLoom


docker system prune --volumes

# Mongo
```
docker-compose exec mongo_db bash
mongo -u root -p example --authenticationDatabase admin
use url_service_db
db.entries.find().pretty()
```

# Postgres

```
docker-compose exec analytics_db bash
psql -U user -d analytics_db
\dt

# or

SELECT * FROM analytics;

# quit
\q 
```

docker-compose up --build
docker-compose down