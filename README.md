# LinkLoom🔗

LinkLoom is a microservive application designed to provide URL shortening, QR code generation, analytics logging, and an integrated API service. The app is deployed on a local Kubernetes cluster using Minikube, with Helm managing the deployments of MongoDB, PostgreSQL, Prometheus, and Grafana for monitoring.

[![Tech Stack](https://skillicons.dev/icons?i=flask,python,go,postgres,mongodb,docker,githubactions,prometheus,grafana,k8s)](https://skillicons.dev)

---
## Architecture Overview:
```mermaid
graph LR
        A1[User]
    
    subgraph "LinkLoom Application"
        A[API Service]
        B[URL Shortener Service]
        C[QR Code Generator Service]
        D[Analytics Service]
    end
    
    subgraph Databases
        E[(PostgreSQL Analytics)]
        F[(MongoDB URLs & QR Codes)]
    end
    
    subgraph Monitoring
        G[Prometheus]
    end

    A1 --> |HTTP Requests| A

    A --> |POST /create| B
    A --> |GET /qr/:short_url| C
    A --> |Log access on each redirection| D
    A --> |GET /:short_url/analytics| D
    B --> |Returns short_url| A
    C --> |Returns QR Code| A
    D <--> |Stores Logs for each short_url| E

    D --> |Returns analytics| A
    

    A --> |Stores Long URL, Short URL, QR Code| F
    A --> |Fetches Long URL for Redirection| F

    B --> |/metrics| G
    C --> |/metrics| G
    D --> |/metrics| G
    A --> |/metrics| G

    G --> Grafana

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style B fill:#f9f,stroke:#333,stroke-width:2px
    style C fill:#f9f,stroke:#333,stroke-width:2px
    style D fill:#f9f,stroke:#333,stroke-width:2px
    style E fill:#bbf,stroke:#333,stroke-width:2px
    style F fill:#bbf,stroke:#333,stroke-width:2px
    style G fill:#bbf,stroke:#333,stroke-width:2px
    style A1 fill:#afa,stroke:#333,stroke-width:2px

```

## Components:

1. **URL Shortener Service**
   - **Description:** Provides functionality to shorten URLs, supporting custom short URLs.
   - **Endpoint:** `/shorten`
   - **Docker Image:** `docker.io/prajjwalyd/url-shortener`

2. **QR Code Generator Service**
   - **Description:** Generates QR codes for given URLs.
   - **Endpoint:** `/generate_qr`
   - **Docker Image:** `docker.io/prajjwalyd/qr-code-generator`

3. **Analytics Service**
   - **Description:** Logs analytics data (access time, IP, user agent, referrer) into a PostgreSQL database.
   - **Endpoints:** 
     - `/log` (for logging access)
     - `/<short_url>/analytics` (to retrieve analytics for a given short URL)
   - **Docker Image:** `docker.io/prajjwalyd/analytics`

4. **API Service**
   - **Description:** Integrates all services, manages URL mappings and QR codes, stores data in MongoDB, and provides unified endpoints.
   - **Endpoints:** 
     - `/create` (to create a shortened URL and optionally generate QR code)
     - `/<short_url>` (to redirect to the original long URL)
        - It logs data whenever a short url is accessed by sending a POST request to the Analytics service. 
     - `/qr/<short_url>` (to retrieve QR code)
     - `/<short_url>/analytics` (to fetch analytics data)
   - **Docker Image:** `docker.io/prajjwalyd/api`

    **Prometheus Metrics Endpoint:** Each service exposes `/metrics`.

5. **Databases**
   - **MongoDB:** Stores URL mappings and QR codes.
     - Helm Deployment: `my-mongo`
   - **PostgreSQL:** Stores analytics data.
     - Helm Deployment: `my-postgresql`

6. **Monitoring**
   - **Prometheus:** Collects metrics from each service.
     - Helm Deployment: `prometheus`
   - **Grafana:** Visualizes metrics and provides dashboards.
     - Helm Deployment: `grafana`

---

## Setup and Deployment:

#### Local Kubernetes Cluster Setup (Minikube):
[Minikube installation guide](https://minikube.sigs.k8s.io/docs/start/)
   ```
   minikube start
   ```

#### Helm:
[Helm installation guide](https://helm.sh/docs/intro/install/)
```
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

#### Deploy Databases:
```
helm install my-mongo bitnami/mongodb --set auth.rootPassword=example,auth.username=root,auth.password=example,auth.database=url_db
helm install my-postgresql bitnami/postgresql -f values.yaml
```

#### Deploy Prometheus and Grafana:
```
helm install prometheus prometheus-community/prometheus -f prometheus.yml
helm install grafana grafana/grafana
```

#### Deploy LinkLoom Application:
Apply Kubernetes manifests (`k8s/` directory)
```
kubectl apply -f k8s
```

#### Verify Deployment:
```
kubectl get pods
kubectl get svc
```

#### Access Prometheus and Grafana:
- Forward ports:
    ```
    kubectl port-forward deploy/prometheus-server 9090
    kubectl port-forward deploy/grafana 3000
    ```
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000`
    Login with username `admin` and retrieve your password using:
    ```
    kubectl get secret --namespace default grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo
    ```

#### Set Up Grafana Data Source:
Add Prometheus data source in Grafana with URL `http://prometheus-server.default.svc.cluster.local:80`

#### Import Dashboard:
Import the provided [JSON dashboard](https://github.com/prajjwalyd/LinkLoom/blob/main/LinkLoom-grafana.json) file for metrics visualization.


#### Testing Endpoints:
- Find your Minikube IP:
```
minikube ip
```
- Expose the API service:
```
kubectl port-forward service/api 30000:5000
```
- Curl commands:
```
# Replace `http://192.168.49.2` with your minikube IP

# Creating a short url:
curl http://192.168.49.2:30000/create -X POST -H "Content-Type: application/json" -d '{"long_url": "http://example.com"}'

# Crating a custom short url:
curl -X POST http://192.168.49.2:30000/create -H "Content-Type: application/json" -d '{"long_url": "https://example.com", "custom_url": "mycustomurl"}'

# Creating a short url with QR Code:
curl -X POST http://192.168.49.2:30000/create -H "Content-Type: application/json" -d '{"long_url": "https://example.com", "custom_url": "custom123", "generate_qr": true}'

# Retreive the QR Code and save it as PNG:
curl -X GET http://192.168.49.2:30000/qr/custom123 --output qr_code.png

# Test the redirection
curl -L http://192.168.49.2:30000/custom123

# Access the analytics
curl -X GET http://192.168.49.2:30000/custom123/analytics
```