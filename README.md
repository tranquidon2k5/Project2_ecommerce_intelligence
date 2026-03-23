<p align="center">
  <h1 align="center">ShopSmart Analytics</h1>
  <p align="center">E-commerce intelligence platform — track prices, detect anomalies, get AI-powered buy recommendations across Vietnamese e-commerce platforms.</p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?logo=tailwindcss&logoColor=white" alt="TailwindCSS">
</p>

---

## Features

- **Price Tracking** — Crawl real-time prices from Shopee, Tiki, Lazada (10,000+ products)
- **Price History Charts** — Interactive charts with trend analysis and min/max/avg statistics
- **AI Price Prediction** — Prophet time-series forecasting with moving-average fallback
- **Anomaly Detection** — IsolationForest identifies fake discounts and price manipulation
- **Fake Review Detection** — NLP sentiment analysis + rule-based classifier (Vietnamese)
- **Buy Signal Recommendations** — Rule-based signals combining price trend + anomaly + prediction
- **Price Drop Alerts** — Set alerts and get notified when prices drop below target
- **Cross-Platform Comparison** — Compare product prices across all 3 platforms
- **CSV Data Export** — Export product lists and price history for offline analysis
- **System Monitoring** — Real-time health checks, API metrics, crawl logs dashboard
- **Dark Mode** — Full dark theme with Tailwind CSS
- **Responsive Design** — Mobile, tablet, and desktop layouts

## Architecture

```
Browser (React 18 + Vite + TailwindCSS)
    |
    | REST API /api/v1/*
    v
FastAPI + SQLAlchemy (async)
    |--- Services layer (business logic)
    |--- ML module (Prophet, IsolationForest, NLP)
    |--- APScheduler (crawl 6h, analytics daily, ML retrain weekly)
    |
    v
PostgreSQL 16  +  Redis 7
    ^
    |
Scrapy + Playwright (Crawler)
```

**5 Docker Compose services:** `backend`, `frontend`, `db`, `redis`, `crawler`

## Screenshots

<!-- Add screenshots here -->
<!-- ![Dashboard](docs/screenshots/dashboard.png) -->
<!-- ![AI Insights](docs/screenshots/ai-insights.png) -->
<!-- ![Product Detail](docs/screenshots/product-detail.png) -->

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/your-username/shopsmart-analytics.git
cd shopsmart-analytics

# 2. Configure environment
cp .env.example .env

# 3. Start all services
docker-compose up --build

# 4. Generate sample data (10,000 products)
make generate-data
```

Open [http://localhost:3000](http://localhost:3000) for the dashboard, [http://localhost:8000/docs](http://localhost:8000/docs) for the Swagger API docs.

## Development Setup

### Backend

```bash
cd src/backend
pip install -r requirements.txt
alembic upgrade head              # Apply migrations
uvicorn app.main:app --reload     # Dev server on :8000
python -m pytest tests/           # Run tests
```

### Frontend

```bash
cd src/frontend
npm install
npm run dev                       # Vite dev server on :3000
npm run build                     # Production build
```

### Crawler

```bash
cd src/crawler
scrapy crawl tiki -a category=dien-thoai
```

### Docker (development with hot reload)

```bash
make dev          # Start all containers with hot reload
make logs         # View logs
make down         # Stop all containers
```

## API Endpoints

Interactive documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/products` | GET | Search products (filter, sort, paginate) |
| `/api/v1/products/{id}` | GET | Product detail with price stats |
| `/api/v1/products/{id}/price-history` | GET | Price history with period selection |
| `/api/v1/products/{id}/reviews` | GET | Reviews with fake detection |
| `/api/v1/analytics/trending` | GET | Trending products (price_drop, best_seller, etc.) |
| `/api/v1/analytics/market-overview` | GET | Market overview statistics |
| `/api/v1/analytics/price-comparison` | GET | Cross-platform price comparison |
| `/api/v1/ai/predict-price/{id}` | GET | AI price prediction (Prophet/MA) |
| `/api/v1/ai/anomalies` | GET | Anomalous products (score > 0.7) |
| `/api/v1/ai/check-reviews` | POST | Batch review sentiment/fake analysis |
| `/api/v1/alerts` | GET/POST/DELETE | Price alert CRUD |
| `/api/v1/export/products` | GET | Export products to CSV |
| `/api/v1/export/price-history/{id}` | GET | Export price history to CSV |
| `/api/v1/health` | GET | Health check (DB + Redis) |
| `/api/v1/stats/system` | GET | System metrics and data freshness |
| `/api/v1/stats/crawl` | GET | Crawl job history |

All responses follow a consistent format:
```json
{"success": true, "data": {...}, "meta": {"page": 1, "per_page": 20, "total": 100}, "message": null}
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI 0.109, SQLAlchemy 2.0 (async), Pydantic 2.5 |
| Frontend | React 18, Vite 5, TailwindCSS 3.4, Recharts, Zustand, React Query 5 |
| Database | PostgreSQL 16 (BRIN index, GIN trigram, range partitioning) |
| Cache | Redis 7 (async, TTL-based) |
| Crawler | Scrapy, Playwright (headless Chromium for Shopee) |
| ML/AI | Prophet (price prediction), scikit-learn IsolationForest (anomaly), underthesea (Vietnamese NLP) |
| Scheduler | APScheduler (crawl 6h, analytics daily, ML retrain weekly) |
| Deploy | Docker Compose, multi-stage Dockerfiles, GitHub Actions CI/CD |

## Project Structure

```
shopsmart-analytics/
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/            # Route handlers (products, analytics, ai, alerts, export, system)
│   │   │   ├── models/         # SQLAlchemy ORM (9 tables)
│   │   │   ├── schemas/        # Pydantic request/response validation
│   │   │   ├── services/       # Business logic (product, analytics, alert, cache)
│   │   │   ├── ml/             # ML models (price_predictor, anomaly_detector, review_analyzer)
│   │   │   ├── main.py         # FastAPI app + middleware
│   │   │   ├── config.py       # Settings (Pydantic)
│   │   │   ├── database.py     # Async SQLAlchemy engine
│   │   │   └── scheduler.py    # APScheduler jobs
│   │   ├── migrations/         # Alembic migrations
│   │   ├── Dockerfile          # Multi-stage production build
│   │   └── requirements.txt
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── pages/          # 8 pages (Dashboard, Search, Detail, Compare, Trending, Alerts, AIInsights, System)
│   │   │   ├── components/     # Layout + common components
│   │   │   ├── hooks/          # React Query hooks
│   │   │   ├── services/       # API services
│   │   │   ├── store/          # Zustand stores
│   │   │   └── utils/          # Helpers, constants, CSV export
│   │   ├── Dockerfile          # Multi-stage (Node build → Nginx serve)
│   │   └── nginx.conf
│   ├── crawler/
│   │   └── shopsmart_crawler/
│   │       ├── spiders/        # tiki_spider, shopee_spider
│   │       └── pipelines.py    # Cleaning + PostgreSQL batch upsert
│   └── scripts/
│       ├── seed_data.py        # Seed platforms & categories
│       └── generate_fake_data.py  # Generate 10k sample products
├── docker-compose.yml          # Production (5 services)
├── docker-compose.dev.yml      # Development overrides (hot reload)
├── Makefile                    # Build/dev convenience commands
├── railway.json                # Railway deployment config
├── .github/workflows/ci.yml   # CI/CD (lint + build + docker)
└── .env.example
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | `postgresql+asyncpg://shopsmart:shopsmart123@localhost:5432/shopsmart_db` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `APP_ENV` | Environment (`development` / `production`) | `development` |
| `SECRET_KEY` | Application secret key | `your-secret-key-change-in-production` |
| `CRAWLER_DELAY` | Delay between crawl requests (seconds) | `2` |
| `CRAWLER_CONCURRENT` | Concurrent crawl requests | `8` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |
| `POSTGRES_USER` | PostgreSQL username | `shopsmart` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `shopsmart123` |
| `POSTGRES_DB` | PostgreSQL database name | `shopsmart_db` |

## Key Design Decisions

- **Prices as BIGINT** — VND has no decimals, avoid floating-point issues
- **BRIN index on price_history.crawled_at** — Space-efficient for time-series queries (40k rows/day)
- **GIN trigram index on products.name** — Fast Vietnamese full-text search via `pg_trgm`
- **No PhoBERT** — Uses `underthesea` lexicon-based NLP to stay within Docker memory limits
- **Prophet requires 30+ data points** — Falls back to moving-average for new products
- **APScheduler over Airflow** — Simpler orchestration for single-instance deployment
- **In-memory metrics** — Simple request tracking without Prometheus overhead

## License

MIT
