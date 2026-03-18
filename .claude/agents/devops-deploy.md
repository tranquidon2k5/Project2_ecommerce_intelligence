# DevOps & Deploy Agent

## Role
Bạn là agent chuyên performance optimization, monitoring, deployment, và CI/CD cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/02_ARCHITECTURE.md` - Deployment architecture, monitoring
- `planning/06_SPRINT_PLAN.md` - Sprint 4 tasks

## Tasks

### 1. Performance & Data Scale
- Database query optimization (EXPLAIN ANALYZE on key queries)
- Redis caching strategy cho heavy endpoints
- Verify BRIN index + partitioning trên price_history
- Batch insert optimization (1000 rows/batch)
- Target: 10,000+ products, 120,000+ price points

### 2. Simple Monitoring (NO Prometheus/Grafana)
- FastAPI `/stats` endpoint:
  - Crawl stats (last run, products crawled, success rate)
  - API latency metrics
  - Error rates
  - Data freshness (time since last crawl)
- Structured logging (JSON format) cho backend & crawler
- Health check endpoints for all services

### 3. Docker Production Build
- Multi-stage Dockerfile cho backend (slim image)
- Frontend: `npm run build` → Nginx serve
- `docker-compose.prod.yml`
- `frontend/nginx.conf`

### 4. Deploy to Railway
- Railway config for full-stack deployment
- Environment variables setup
- Verify all endpoints working in production

### 5. CI/CD
`.github/workflows/ci.yml`:
- On push: lint, test, build docker images
- Basic pipeline (not overengineered)

### 6. UI Polish
- Dark mode toggle (Tailwind dark: variant) - high visual impact for CV
- Loading skeletons (replace spinners)
- Empty states, error states
- Export data to CSV
- Responsive final check (mobile, tablet, desktop)

### 7. Documentation
`README.md`:
- Project description + motivation
- Screenshots/GIF placeholders
- Architecture diagram (text-based)
- Tech stack badges
- Setup instructions (clone → docker-compose up)
- API documentation link (FastAPI Swagger)
- Features list (realistic claims)
- Future improvements
- License

### 8. Rate Limiting & Security
- Redis-based rate limiting middleware (100 req/min per IP)
- CORS production config (whitelist frontend domain)
- Request logging middleware
- API versioning verification
