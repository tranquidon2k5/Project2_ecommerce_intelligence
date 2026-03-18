# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ShopSmart Analytics** — E-commerce intelligence platform tracking product prices across Vietnamese e-commerce platforms (Shopee, Tiki, Lazada). Crawls product data, analyzes price trends, detects anomalies/fake reviews, and provides buy recommendations via a dashboard.

## Architecture

```
Frontend (React 18 + Vite + TailwindCSS, port 3000)
    ↓ REST API (/api/v1/*)
Backend (FastAPI + SQLAlchemy async, port 8000)
    ├── Services layer (business logic)
    ├── ML module (Prophet, IsolationForest, rule-based NLP)
    └── APScheduler (crawl every 6h, analytics daily, ML retrain weekly)
    ↓
PostgreSQL 16 (port 5432) + Redis 7 (port 6379)
    ↑
Crawler (Scrapy + Playwright, separate container)
```

Five Docker Compose services: `backend`, `frontend`, `db`, `redis`, `crawler`.

## Build & Run Commands

```bash
make dev              # Start all containers (dev mode with hot reload)
make build            # Build production images
make down             # Stop all containers
make logs             # View container logs
make db-migrate       # Run Alembic migrations
make db-seed          # Seed platforms & categories
make crawl            # Run crawler manually
make test             # Run pytest
docker-compose up     # Alternative: start all services
```

**Backend only:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
alembic upgrade head                          # Apply migrations
alembic revision --autogenerate -m "msg"      # Create migration
python -m pytest tests/                       # Run all tests
python -m pytest tests/test_products.py -k "test_name"  # Single test
```

**Frontend only:**
```bash
cd frontend
npm install
npm run dev           # Vite dev server on :3000
npm run build         # Production build
```

**Crawler only:**
```bash
cd crawler
scrapy crawl tiki -a category=dien-thoai
python ../scripts/generate_fake_data.py       # Generate 10k mock products
```

## Key Design Decisions

- **Prices stored as BIGINT** (VND, no floats) throughout the stack
- **price_history** uses PostgreSQL range partitioning by month + BRIN index on `crawled_at` — critical for query performance at scale (40k rows/day)
- **products.name** uses GIN trigram index (`pg_trgm`) for full-text search
- **No PhoBERT** — uses `underthesea` lexicon-based sentiment + RandomForest on extracted features for fake review detection (memory constraint under Docker)
- **Prophet requires 30+ data points** — products with fewer use moving-average fallback; new products show "Insufficient data"
- **ML models loaded on-demand**, not always-running — saves container memory
- **APScheduler inside backend process** instead of Airflow — simpler orchestration
- **Buy signals are rule-based**, combining price trend + anomaly score + prediction direction
- **Target scale: 10,000 products** (realistic for single Docker instance at 1 req/2s crawl rate)

## API Response Format

All endpoints return:
```json
{"success": true, "data": {...}, "meta": {"page": 1, "per_page": 20, "total": N}, "message": null}
```
Errors return: `{"success": false, "data": null, "error": {"code": "...", "message": "..."}}`

## Backend Structure

- `backend/app/models/` — SQLAlchemy ORM (9 tables: platforms, categories, products, price_history, reviews, product_analytics, price_alerts, crawl_logs, ml_model_metrics)
- `backend/app/schemas/` — Pydantic request/response validation
- `backend/app/api/` — Route handlers grouped by domain (products, analytics, ai_insights, alerts, system)
- `backend/app/services/` — Business logic layer (product_service, analytics_service, alert_service, cache_service)
- `backend/app/ml/` — ML module (price_predictor, anomaly_detector, review_analyzer, recommender, trainer); saved models in `ml/models/*.pkl`

## Frontend Structure

- Pages: Dashboard (`/`), ProductSearch (`/search`), ProductDetail (`/products/:id`), PriceCompare (`/compare`), Trending (`/trending`), AIInsights (`/insights`), Alerts (`/alerts`)
- State: Zustand stores (`useProductStore`, `useFilterStore`)
- Data fetching: React Query hooks in `hooks/`
- Charts: Recharts (PriceHistoryChart, PricePredictionChart, SentimentChart)
- API client: Axios instance in `services/api.js`

## Crawler Structure

- `crawler/shopsmart_crawler/spiders/` — Per-platform spiders (tiki_spider priority, shopee_spider uses Playwright)
- `crawler/shopsmart_crawler/pipelines.py` — CleaningPipeline → PostgresPipeline (batch upserts of 1000 rows)
- Anti-bot: UA rotation, 2s delay, exponential backoff, circuit breaker at >20% error rate
- Fallback: `scripts/generate_fake_data.py` generates synthetic data if crawling is blocked

## Planning Docs

Detailed specs live in `planning/`:
- `03_DATABASE_SCHEMA.md` — Full SQL DDL and reference queries
- `04_API_DESIGN.md` — All endpoints with params, response examples, Pydantic models
- `06_SPRINT_PLAN.md` — 4-sprint implementation plan with risk matrix

## Subagents

Specialized agent instructions in `.claude/agents/` for: infrastructure-setup, database-models, backend-api, crawler, frontend, ml-ai, devops-deploy, testing.
