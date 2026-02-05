# 🚀 GeminiCRM Pro - Enterprise Deployment Guide

## Overview

This guide covers deploying GeminiCRM Pro to production environments with enterprise-grade infrastructure, security, and scalability.

---

## Table of Contents

1. [Infrastructure Setup](#infrastructure-setup)
2. [Docker Containerization](#docker-containerization)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Security Hardening](#security-hardening)
5. [Performance Tuning](#performance-tuning)
6. [Monitoring & Logging](#monitoring--logging)
7. [CI/CD Pipeline](#cicd-pipeline)
8. [Scaling Strategy](#scaling-strategy)

---

## Infrastructure Setup

### Cloud Providers

#### AWS
- **Compute**: EC2 instances or ECS
- **Database**: RDS PostgreSQL
- **Cache**: ElastiCache Redis
- **CDN**: CloudFront
- **Load Balancer**: ALB/NLB
- **Monitoring**: CloudWatch

#### Azure
- **Compute**: App Service or Container Instances
- **Database**: Azure Database for PostgreSQL
- **Cache**: Azure Cache for Redis
- **CDN**: Azure CDN
- **Load Balancer**: Application Gateway
- **Monitoring**: Application Insights

#### GCP
- **Compute**: Cloud Run or GKE
- **Database**: Cloud SQL PostgreSQL
- **Cache**: Memorystore Redis
- **CDN**: Cloud CDN
- **Load Balancer**: Cloud Load Balancing
- **Monitoring**: Cloud Monitoring

### Recommended Specs (Production)

```
API Server:
- CPU: 4+ vCPU
- RAM: 8+ GB
- Storage: 50+ GB SSD
- Network: 1 Gbps

Database Server:
- CPU: 8+ vCPU
- RAM: 32+ GB
- Storage: 500+ GB SSD
- Backup: Daily snapshots

Redis Cache:
- CPU: 2+ vCPU
- RAM: 8+ GB
- Network: Low latency (<1ms)

Load Balancer:
- Redundancy: Multi-AZ/Region
- SSL/TLS: Full encryption
- Health checks: Active monitoring
```

---

## Docker Containerization

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/health')"

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
```

### Docker Compose for Development

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: gemini-crm-app
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/gemini_crm
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    container_name: gemini-crm-db
    environment:
      - POSTGRES_USER=gemini_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=gemini_crm
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    container_name: gemini-crm-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: gemini-crm-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Build and Run

```bash
# Build image
docker build -t gemini-crm:latest .

# Push to registry
docker tag gemini-crm:latest your-registry/gemini-crm:latest
docker push your-registry/gemini-crm:latest

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

---

## Kubernetes Deployment

### Prerequisites

- kubectl configured
- Kubernetes cluster (EKS, AKS, GKE)
- Container registry access

### Namespace Setup

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gemini-crm
```

### ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: gemini-crm-config
  namespace: gemini-crm
data:
  FLASK_ENV: production
  GEMINI_MODEL: gemini-2.0-flash
  LOG_LEVEL: INFO
```

### Secrets

```yaml
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: gemini-crm-secrets
  namespace: gemini-crm
type: Opaque
stringData:
  GEMINI_API_KEY: your-api-key
  DATABASE_PASSWORD: secure_password
  REDIS_PASSWORD: redis_password
  SECRET_KEY: flask-secret-key
```

### Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gemini-crm-app
  namespace: gemini-crm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: gemini-crm
  template:
    metadata:
      labels:
        app: gemini-crm
    spec:
      containers:
      - name: app
        image: your-registry/gemini-crm:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          valueFrom:
            configMapKeyRef:
              name: gemini-crm-config
              key: FLASK_ENV
        - name: GEMINI_API_KEY
          valueFrom:
            secretKeyRef:
              name: gemini-crm-secrets
              key: GEMINI_API_KEY
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: gemini-crm-secrets
              key: DATABASE_URL
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: gemini-crm-service
  namespace: gemini-crm
spec:
  type: LoadBalancer
  selector:
    app: gemini-crm
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
```

### Ingress

```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: gemini-crm-ingress
  namespace: gemini-crm
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - gemini-crm.example.com
    secretName: gemini-crm-tls
  rules:
  - host: gemini-crm.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gemini-crm-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl apply -f secrets.yaml

# Create config
kubectl apply -f configmap.yaml

# Deploy app
kubectl apply -f deployment.yaml

# Create service
kubectl apply -f service.yaml

# Create ingress
kubectl apply -f ingress.yaml

# Check status
kubectl get pods -n gemini-crm
kubectl logs -f deployment/gemini-crm-app -n gemini-crm

# Scale replicas
kubectl scale deployment gemini-crm-app --replicas=5 -n gemini-crm
```

---

## Security Hardening

### SSL/TLS Configuration

```nginx
# nginx.conf
upstream gemini_app {
    server app:5000;
}

server {
    listen 80;
    server_name gemini-crm.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name gemini-crm.example.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://gemini_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Environment-Based Security

```python
# config.py
import os

class ProductionConfig:
    """Production security settings"""
    
    # Security headers
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # CORS restrictions
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'gemini-crm.example.com').split(',')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # API Key
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
```

### WAF Configuration

```
AWS WAF Rules:
- Rate limiting: 2000 requests/5 minutes
- SQL injection: Enable SQLi rule group
- XSS: Enable XSS rule group
- Common exploits: Enable common rule group
- IP reputation: Enable IP reputation list
```

---

## Performance Tuning

### Application Settings

```python
# app.py
import os
from gunicorn.app.wsgiapp import run

# Gunicorn configuration
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120

# Threading
threads = 2
threaded = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
```

### Database Optimization

```python
# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 40,
}

# Caching
from flask_caching import Cache

cache = Cache(app, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL'),
    'CACHE_DEFAULT_TIMEOUT': 300,
    'CACHE_KEY_PREFIX': 'gemini_crm'
})

# Use cache
@app.route('/api/stats')
@cache.cached(timeout=60)
def get_stats():
    return generate_stats()
```

### Query Optimization

```python
# Use eager loading
leads = Lead.query.options(
    db.joinedload(Lead.owner),
    db.joinedload(Lead.activity)
).all()

# Use pagination
from flask_sqlalchemy import Pagination
page = request.args.get('page', 1, type=int)
leads = Lead.query.paginate(page=page, per_page=20)

# Index frequently queried fields
class Lead(db.Model):
    __table_args__ = (
        Index('idx_owner_id', 'owner_id'),
        Index('idx_score', 'score'),
        Index('idx_created_at', 'created_at'),
    )
```

---

## Monitoring & Logging

### Application Monitoring

```python
# monitoring.py
from prometheus_client import Counter, Histogram, generate_latest
import time

# Metrics
request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('app_request_duration_seconds', 'Request duration')
errors = Counter('app_errors_total', 'Total errors', ['error_type'])

# Middleware
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    endpoint = request.endpoint or 'unknown'
    request_count.labels(method=request.method, endpoint=endpoint).inc()
    request_duration.observe(duration)
    return response

# Metrics endpoint
@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Logging Setup

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(app):
    """Configure application logging"""
    
    if not app.debug:
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('GeminiCRM Pro startup')

setup_logging(app)
```

### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    """Health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0',
        'database': 'connected',
        'cache': 'connected'
    }
    
    try:
        # Check database
        db.session.execute('SELECT 1')
    except:
        health_status['database'] = 'disconnected'
        health_status['status'] = 'degraded'
    
    try:
        # Check cache
        redis_client.ping()
    except:
        health_status['cache'] = 'disconnected'
        health_status['status'] = 'degraded'
    
    return jsonify(health_status), 200 if health_status['status'] == 'healthy' else 503
```

---

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: password
          POSTGRES_DB: gemini_crm_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: pytest tests/ --cov=app
    
    - name: Build Docker image
      run: docker build -t gemini-crm:${{ github.sha }} .
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USER }} --password-stdin
        docker tag gemini-crm:${{ github.sha }} your-registry/gemini-crm:latest
        docker push your-registry/gemini-crm:latest
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/gemini-crm-app \
          app=your-registry/gemini-crm:latest \
          -n gemini-crm
        kubectl rollout status deployment/gemini-crm-app -n gemini-crm
```

---

## Scaling Strategy

### Horizontal Scaling

```yaml
# hpa.yaml - Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: gemini-crm-hpa
  namespace: gemini-crm
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: gemini-crm-app
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Load Distribution

```
Request Flow:
1. DNS (Route 53/Cloud DNS)
2. CDN (CloudFront/Azure CDN)
3. Load Balancer (ALB/AGW)
4. Kubernetes Service
5. Pod (with auto-scaling)
6. Database (with read replicas)
```

---

## Backup & Disaster Recovery

### Database Backup

```bash
#!/bin/bash
# backup_db.sh

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Full backup
pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > $BACKUP_DIR/full_backup.sql.gz

# Upload to S3
aws s3 cp $BACKUP_DIR/full_backup.sql.gz s3://gemini-crm-backups/

# Keep only last 30 days
find /backups -type d -mtime +30 -exec rm -rf {} \;
```

### Recovery Procedure

```bash
# Restore from backup
gunzip < /backups/2024-02-04/full_backup.sql.gz | psql -U $DB_USER -h $DB_HOST $DB_NAME
```

---

## Monitoring Dashboard

Recommended tools:
- **Datadog**: Full-stack monitoring
- **New Relic**: Application performance monitoring
- **Prometheus + Grafana**: Open-source monitoring
- **CloudWatch**: AWS native monitoring
- **Azure Monitor**: Azure native monitoring

---

## Checklist

- [ ] Infrastructure provisioned
- [ ] Database configured and backed up
- [ ] Redis cache running
- [ ] Docker image built and pushed
- [ ] Kubernetes cluster configured
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring dashboards set up
- [ ] Backup strategy implemented
- [ ] CI/CD pipeline configured
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated
- [ ] Team trained

---

**Last Updated**: February 4, 2026
**Version**: 1.0
**Status**: Production Ready
