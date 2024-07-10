# LinkLoom


docker system prune --volumes

# Mongo
```
docker-compose exec mongo-db bash
mongo -u root -p example --authenticationDatabase admin
use url_db
db.entries.find().pretty()
```

# Postgres

```
docker-compose exec analytics-db bash
psql -U user -d analytics-db
\dt

# or

SELECT * FROM analytics;

# quit
\q 
```

docker-compose up --build
docker-compose down

```
minikube start
kubectl apply -f k8s
kubectl get pods


minikube stop
```