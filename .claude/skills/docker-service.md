---
name: Docker Service
description: How to add or modify a Docker Compose service
---

# Docker Service Skill

## When to Use
When you need to add a new service or modify an existing one in Docker Compose.

## Steps

### 1. Create Dockerfile

File: `<service>/Dockerfile`

```dockerfile
# Multi-stage build for smaller image
FROM python:3.11-slim AS base

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Production stage
FROM base AS production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Dev stage (with hot reload)
FROM base AS development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 2. Add Service to docker-compose.yml

File: `docker-compose.yml`

```yaml
services:
  # ... existing services (backend, frontend, db, redis, crawler) ...

  new_service:
    build:
      context: ./new_service
      dockerfile: Dockerfile
    container_name: shopsmart-new-service
    ports:
      - "9000:9000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/shopsmart
      - REDIS_URL=redis://redis:6379
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    networks:
      - shopsmart-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### 3. Add Dev Override

File: `docker-compose.dev.yml`

```yaml
services:
  new_service:
    build:
      target: development
    volumes:
      - ./new_service:/app  # Hot reload source code
    environment:
      - DEBUG=true
```

### 4. Add Makefile Shortcut

File: `Makefile`

```makefile
# Add to existing Makefile
new-service:
	docker-compose exec new_service <command>

new-service-logs:
	docker-compose logs -f new_service
```

### 5. Network & Volumes

Service must connect to the shared network:

```yaml
networks:
  shopsmart-network:
    driver: bridge

volumes:
  pgdata:  # PostgreSQL persistent storage
```

## Existing Services Reference

| Service | Port | Image | Notes |
|---------|------|-------|-------|
| `backend` | 8000 | Python 3.11 + FastAPI | APScheduler runs inside |
| `frontend` | 3000 | Node 20 + Vite (dev) / Nginx (prod) | |
| `db` | 5432 | PostgreSQL 16 | Volume: `pgdata` |
| `redis` | 6379 | Redis 7 | |
| `crawler` | — | Python 3.11 + Scrapy + Playwright | No exposed port |

## Common Commands

```bash
# Start all services
make dev
# or: docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Rebuild a specific service
docker-compose build new_service

# View logs
docker-compose logs -f new_service

# Shell into container
docker-compose exec new_service bash

# Stop all
make down
```

## Verify

1. `docker-compose up -d` brings up the new service
2. `docker-compose ps` shows the service as "running" / "healthy"
3. Service can connect to `db` and `redis` via internal DNS names
4. Health check passes
