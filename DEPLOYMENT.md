# CodeSensei Deployment Guide

Complete guide for deploying CodeSensei locally and to production.

---

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Production Deployment](#production-deployment)
4. [Monitoring & Observability](#monitoring--observability)
5. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.9+
- pip
- Git
- Groq API key

### Setup Steps

```bash
# Clone repository
git clone https://github.com/yourusername/codesensei.git
cd codesensei

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Run tests
pytest src/tests/ -v

# Start API server
uvicorn src.api.main:app --reload --port 8000
```

### Access Points

- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

---

## Docker Compose Deployment

### Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Quick Start

```bash
# Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f codesensei-api

# Check health
curl http://localhost:8000/health

# Stop services
docker-compose down
```

### Architecture

The Docker Compose setup includes:

1. **codesensei-api** (port 8000) - Main application
2. **redis** (port 6379) - Caching layer
3. **postgres** (port 5432) - Database
4. **nginx** (port 80) - Reverse proxy
5. **prometheus** (port 9090) - Metrics collection
6. **grafana** (port 3000) - Visualization

### Service URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| API | http://localhost:8000 | - |
| Nginx | http://localhost | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
| Redis | localhost:6379 | - |
| Postgres | localhost:5432 | codesensei/password |

### Configuration

Edit `docker-compose.yml` to customize:

- **Environment variables**: Add to `environment` section
- **Resource limits**: Add `deploy.resources` section
- **Port mappings**: Change `ports` section
- **Volumes**: Modify `volumes` section

Example resource limits:

```yaml
services:
  codesensei-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

---

## Production Deployment

### Option 1: Cloud Run (Google Cloud)

**Prerequisites:**
- Google Cloud account
- gcloud CLI installed

**Steps:**

```bash
# Authenticate
gcloud auth login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/codesensei

# Deploy
gcloud run deploy codesensei \
  --image gcr.io/YOUR_PROJECT_ID/codesensei \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GROQ_API_KEY=your_key \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --timeout 60s
```

**Cost Estimate:**
- Free tier: 2 million requests/month
- After free tier: ~$0.00002 per request
- 1000 users/month: ~$5-20/month

### Option 2: Railway

**Prerequisites:**
- Railway account
- GitHub repository

**Steps:**

1. Push code to GitHub
2. Go to railway.app
3. Click "New Project"
4. Select "Deploy from GitHub"
5. Choose your repository
6. Add environment variables:
   - `GROQ_API_KEY`
   - `ENVIRONMENT=production`
7. Railway will auto-deploy

**railway.json** (already included):

```json
{
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Cost:**
- Free tier: 500 hours/month
- Paid: $5/month (500 hours) + usage

### Option 3: Self-Hosted (VPS)

**Prerequisites:**
- Ubuntu 22.04 server
- 2GB RAM minimum
- Root access

**Installation Script:**

```bash
#!/bin/bash

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/yourusername/codesensei.git
cd codesensei

# Create .env
echo "GROQ_API_KEY=your_key" > .env

# Start services
docker-compose up -d

# Enable auto-start
sudo systemctl enable docker
```

**Nginx Configuration (for domain):**

```nginx
server {
    listen 80;
    server_name codesensei.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## Monitoring & Observability

### Accessing Grafana

1. Open http://localhost:3000
2. Login: admin/admin
3. Add Prometheus data source:
   - URL: http://prometheus:9090
   - Access: Server
4. Import dashboard (ID: 12345) or create custom

### Key Metrics to Monitor

**Request Metrics:**
- `codesensei_requests_total` - Total requests
- `codesensei_request_duration_seconds` - Response time
- `codesensei_active_requests` - Current load

**Analysis Metrics:**
- `codesensei_analysis_total` - Analyses performed
- `codesensei_issues_found` - Issues detected
- `codesensei_code_size_bytes` - Code size

**LLM Metrics:**
- `codesensei_llm_calls_total` - API calls
- `codesensei_llm_tokens_total` - Token usage (for cost tracking)

**Error Metrics:**
- `codesensei_errors_total` - Error count by type

### Alerting Rules (alerts.yml)

```yaml
groups:
  - name: codesensei_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(codesensei_errors_total[5m]) > 0.1
        annotations:
          summary: "High error rate detected"
      
      - alert: SlowRequests
        expr: histogram_quantile(0.95, rate(codesensei_request_duration_seconds_bucket[5m])) > 5
        annotations:
          summary: "95th percentile response time > 5s"
      
      - alert: ServiceDown
        expr: up{job="codesensei-api"} == 0
        for: 1m
        annotations:
          summary: "CodeSensei API is down"
```

### Viewing Logs

```bash
# Docker Compose logs
docker-compose logs -f codesensei-api

# JSON logs
tail -f logs/api.log | jq .

# Filter errors
tail -f logs/api.log | jq 'select(.level=="ERROR")'

# Search specific request
tail -f logs/api.log | jq 'select(.request_id=="req-123")'
```

---

## Troubleshooting

### Common Issues

#### 1. API won't start

**Symptom:** Container exits immediately

**Solution:**
```bash
# Check logs
docker-compose logs codesensei-api

# Common fixes:
- Verify GROQ_API_KEY is set
- Check if port 8000 is available
- Ensure requirements.txt is complete
```

#### 2. LLM services unavailable

**Symptom:** `/explain` and `/debug` return 503

**Solution:**
```bash
# Verify API key
echo $GROQ_API_KEY

# Test API key
curl https://api.groq.com/openai/v1/models \
  -H "Authorization: Bearer $GROQ_API_KEY"

# Check logs
docker-compose logs codesensei-api | grep "LLM"
```

#### 3. High memory usage

**Symptom:** Container getting OOM killed

**Solution:**
```bash
# Increase memory limit in docker-compose.yml
services:
  codesensei-api:
    mem_limit: 1g

# Or reduce workers in Dockerfile
CMD ["uvicorn", "src.api.main:app", "--workers", "1"]
```

#### 4. Slow analysis times

**Symptom:** Requests timing out

**Solution:**
```bash
# Disable LLM analysis
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"code":"...","use_llm":false}'

# Increase timeout
# In docker-compose.yml:
environment:
  - REQUEST_TIMEOUT=120

# In nginx.conf:
proxy_read_timeout 120s;
```

#### 5. Database connection errors

**Symptom:** "could not connect to server"

**Solution:**
```bash
# Check postgres is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U codesensei -d codesensei

# Recreate database
docker-compose down -v
docker-compose up -d postgres
docker-compose up -d codesensei-api
```

### Health Check Commands

```bash
# API health
curl http://localhost:8000/health | jq .

# Database health
docker-compose exec postgres pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# Check all services
docker-compose ps
```

### Performance Tuning

**For high load (1000+ concurrent users):**

```yaml
services:
  codesensei-api:
    deploy:
      replicas: 3  # Run 3 instances
      resources:
        limits:
          cpus: '2.0'
          memory: 1G
    command: >
      uvicorn src.api.main:app 
      --host 0.0.0.0 
      --port 8000 
      --workers 4  # 4 workers per instance
      --limit-concurrency 100
```

---

## Scaling Strategy

### Current State (MVP)
- Single container
- Handles ~100 concurrent users
- Cost: ~$10/month

### Phase 1: Basic Scaling (1000 users)
- Add Redis cache
- Horizontal scaling: 3 replicas
- Connection pooling
- Cost: ~$50/month

### Phase 2: Advanced Scaling (10,000 users)
- Kubernetes deployment
- Auto-scaling
- Separate worker processes
- CDN for static assets
- Cost: ~$200/month

### Phase 3: Enterprise (100,000+ users)
- Multi-region deployment
- Load balancer
- Dedicated database
- Monitoring & alerting
- Cost: ~$1000+/month

---

## Security Checklist

- [ ] Environment variables stored securely (not in code)
- [ ] API keys rotated regularly
- [ ] HTTPS enabled (use Cloudflare/Let's Encrypt)
- [ ] Rate limiting configured
- [ ] Input validation on all endpoints
- [ ] Security headers set (X-Frame-Options, etc.)
- [ ] Database credentials secured
- [ ] Regular dependency updates
- [ ] Monitoring & alerting configured
- [ ] Backup strategy in place

---

## Backup & Recovery

### Database Backup

```bash
# Manual backup
docker-compose exec postgres pg_dump -U codesensei codesensei > backup.sql

# Automated backup (cron)
0 2 * * * docker-compose exec postgres pg_dump -U codesensei codesensei > /backups/backup-$(date +\%Y\%m\%d).sql
```

### Restore

```bash
# Restore from backup
docker-compose exec -T postgres psql -U codesensei codesensei < backup.sql
```

---

## Contact & Support

- **Author**: Shobin Sebastian
- **Email**: shobinsebastian800@gmail.com
- **GitHub**: https://github.com/ShobinSebastian/codesensei
- **Issues**: https://github.com/ShobinSebastian/codesensei/issues

---

**Last Updated**: December 2025