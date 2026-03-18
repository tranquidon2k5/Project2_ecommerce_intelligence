# 🏗️ Kiến trúc Hệ thống - ShopSmart Analytics

---

## 1. High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐  │
│  │Dashboard │ │ Product  │ │  Price   │ │   AI Insights     │  │
│  │  Home    │ │ Search   │ │ Compare  │ │   & Alerts        │  │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────────┬──────────┘  │
│       └─────────────┴────────────┴────────────────┘             │
│                            │ REST API                           │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│  ┌─────────────┐ ┌────────┴───────┐ ┌────────────────────────┐ │
│  │  API Router  │ │  Business      │ │    ML Service          │ │
│  │  - products  │ │  Logic Layer   │ │  - price_predictor     │ │
│  │  - prices    │ │  - services    │ │  - anomaly_detector    │ │
│  │  - analytics │ │  - validators  │ │  - review_analyzer     │ │
│  │  - alerts    │ │  - formatters  │ │  - recommender         │ │
│  └──────┬──────┘ └───────┬────────┘ └───────────┬────────────┘ │
│         └────────────────┴──────────────────────┘               │
│                            │                                     │
│  ┌─────────────────────────┼─────────────────────────────────┐  │
│  │              DATA ACCESS LAYER (SQLAlchemy)                │  │
│  └─────────────────────────┼─────────────────────────────────┘  │
└────────────────────────────┼────────────────────────────────────┘
                             │
┌────────────────────────────┼────────────────────────────────────┐
│                      DATA LAYER                                  │
│  ┌──────────────┐ ┌───────┴──────┐ ┌──────────────────────┐    │
│  │ PostgreSQL   │ │    Redis     │ │   File Storage       │    │
│  │ - products   │ │ - cache      │ │ - ML models (.pkl)   │    │
│  │ - prices     │ │ - rate limit │ │ - crawl logs         │    │
│  │ - reviews    │ │ - sessions   │ │ - export files       │    │
│  │ - alerts     │ │              │ │                      │    │
│  └──────────────┘ └──────────────┘ └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              DATA PIPELINE (APScheduler / Background Tasks)      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Crawl   │───>│  Clean   │───>│Transform │───>│  Load    │  │
│  │  Task    │    │  Task    │    │  Task    │    │  Task    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │                                               │         │
│  ┌────┴─────────────────────────────────────────┐     │         │
│  │           Scrapy + Playwright                │     │         │
│  │  ┌────────┐ ┌────────┐ ┌────────┐           │     │         │
│  │  │Shopee  │ │ Tiki   │ │Lazada  │           │     │         │
│  │  │Spider  │ │Spider  │ │Spider  │           │     │         │
│  │  └────────┘ └────────┘ └────────┘           │     │         │
│  └──────────────────────────────────────────────┘     │         │
│                                                       │         │
│  ┌────────────────────────────────────────────────────┴──────┐  │
│  │              ML Training Pipeline                         │  │
│  │  Retrain models weekly with new data                      │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    MONITORING (Simple)                           │
│  - FastAPI /stats endpoint   - API response time                │
│  - Crawl success rate        - Error rates                      │
│  - Data freshness            - Health checks                    │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Chi Tiết

### Flow 1: Data Collection (Crawl Pipeline)
```
APScheduler Trigger (cron: every 6h)
    │
    ├─> Scrapy Spider khởi chạy
    │   ├─> Crawl product listing pages
    │   ├─> Extract: name, price, rating, reviews, seller info
    │   └─> Playwright xử lý pages cần JavaScript render
    │
    ├─> Data Cleaning
    │   ├─> Remove duplicates
    │   ├─> Validate data types
    │   ├─> Normalize price (VND)
    │   └─> Handle missing values
    │
    ├─> Transform & Enrich
    │   ├─> Calculate price changes
    │   ├─> Compute moving averages
    │   └─> Flag anomalies
    │
    └─> Load to PostgreSQL
        ├─> Upsert products table
        ├─> Insert price_history table
        └─> Invalidate Redis cache
```

### Flow 2: User Request (API Flow)
```
User Request
    │
    ├─> Check Redis Cache ──(hit)──> Return cached response
    │         │
    │       (miss)
    │         │
    ├─> FastAPI Router
    │   ├─> Validate request (Pydantic)
    │   ├─> Business Logic Layer
    │   │   ├─> Query PostgreSQL
    │   │   ├─> Call ML Service (if needed)
    │   │   └─> Format response
    │   └─> Set Redis Cache (TTL: 5min)
    │
    └─> Return JSON Response
```

### Flow 3: ML Pipeline
```
Weekly Trigger (APScheduler)
    │
    ├─> Extract training data from PostgreSQL
    │   ├─> Price history (last 90 days)
    │   ├─> Review texts
    │   └─> Product metadata
    │
    ├─> Train Models
    │   ├─> Prophet: Price forecasting per category
    │   ├─> IsolationForest: Anomaly detection
    │   └─> RandomForest: Fake review classifier (feature-based, NOT PhoBERT)
    │
    ├─> Evaluate
    │   ├─> Compare with previous model metrics
    │   └─> Log to MLflow (optional)
    │
    └─> Deploy
        ├─> Save model artifacts (.pkl)
        └─> Reload ML Service (hot swap)
```

## 3. Component Details

### 3.1 Crawler Service
- **Scrapy**: Crawl nhanh, hỗ trợ concurrent requests, auto retry
- **Playwright**: Render JavaScript cho Shopee (SPA) — limit max 3-5 concurrent pages (~300MB RAM each)
- **Rate Limiting**: 1 request/2s per domain, rotate User-Agent
- **Proxy**: Residential proxy rotation (not just UA rotation) — required for Shopee/Lazada
- **Anti-bot Mitigation**:
  - Prioritize Tiki (public API, least aggressive anti-bot)
  - Shopee: use internal API endpoints (GraphQL) with proper headers, not HTML scraping
  - Lazada: use JSON endpoints where available, Playwright as fallback
  - Request fingerprint randomization (TLS, header order, viewport)
  - Exponential backoff + circuit breaker pattern (pause spider on >20% error rate)
  - Selector validation layer: alert on extraction failure rate spikes
  - Store raw HTML/JSON responses for re-parsing capability
- **Realistic Scale**: Target **10,000+ products** (not 50k). At 1 req/2s, 50k requires ~28h — impossible in 6h window on single instance
- **Fallback**: Generate synthetic data for Shopee/Lazada demo if crawling is blocked

### 3.2 Backend API
- **FastAPI**: Async, auto OpenAPI docs, type validation
- **SQLAlchemy**: ORM, migration với Alembic
- **Pydantic**: Request/Response validation
- **Background Tasks**: FastAPI background tasks cho lightweight jobs

### 3.3 ML Service
- **Price Prediction**: Facebook Prophet (time-series)
  - Minimum data threshold: 30+ price points before Prophet activates
  - Fallback: moving average + % change heuristics for products with <30 data points
  - New products: display "Insufficient data" rather than unreliable predictions
  - Add confidence intervals; clearly label low-confidence predictions
- **Anomaly Detection**: IsolationForest (scikit-learn) — lightweight, runs on-demand
- **Fake Review Detection**: Rule-based approach (NOT PhoBERT)
  - PhoBERT (~400MB model, ~2GB+ RAM inference) causes memory explosion alongside other Docker services
  - Use `underthesea` library for Vietnamese sentiment (lexicon-based, lightweight)
  - Fake detection via: review length, generic phrases, rating-sentiment mismatch, timestamp clustering, reviewer review count
  - RandomForest classifier on extracted features — no heavy NLP model needed
- **Buy Signal / Recommendation**: Simple formula combining price trend + anomaly score + prediction direction (rule-based, not ML)
- **Model Loading**: On-demand loading, NOT always-running service — conserve memory

### 3.4 Frontend
- **React 18**: SPA, React Router
- **TailwindCSS**: Utility-first styling
- **Recharts**: Biểu đồ giá, trends
- **React Query**: Data fetching, caching
- **Zustand**: State management (lightweight)

## 4. Communication Patterns

| From | To | Protocol | Format |
|------|----|----------|--------|
| Frontend | Backend | HTTP/REST | JSON |
| Backend | PostgreSQL | TCP | SQL (via SQLAlchemy) |
| Backend | Redis | TCP | Redis Protocol |
| APScheduler | Crawlers | Process spawn | Python callable |
| APScheduler | PostgreSQL | TCP | SQL |
| ML Service | File Storage | Filesystem | pickle/joblib |

## 5. Deployment Architecture (Docker Compose)

```yaml
services:
  frontend:      # React dev server / Nginx (prod)
    ports: 3000

  backend:       # FastAPI + Uvicorn + APScheduler (pipeline scheduling built-in)
    ports: 8000
    depends_on: [db, redis]

  db:            # PostgreSQL 16
    ports: 5432
    volumes: [pgdata]

  redis:         # Redis 7
    ports: 6379

  crawler:       # Scrapy + Playwright
    depends_on: [db, redis]

# Total: 5 services (reduced from 8 — removed Airflow, Prometheus, Grafana)
# APScheduler runs inside backend process — no separate orchestrator needed
# Monitoring via FastAPI /stats endpoint + structured logging
```

## 6. Data Retention & price_history Scaling

- **Problem**: 10k products × 4 crawls/day = 40k rows/day = ~1.2M rows/month. Without partitioning, queries degrade after 2-4 weeks.
- **Range Partitioning**: Implement PostgreSQL native range partitioning by month on `price_history` from Sprint 1
- **BRIN Index**: Use `BRIN` index on `crawled_at` instead of B-tree — much more space-efficient for time-series append-only data
- **Data Aggregation**: After 90 days, aggregate raw data into daily summaries (min/max/avg) and archive raw records
- **Batch Inserts**: Crawl pipeline uses batch inserts (1000 rows at a time) rather than single-row inserts to minimize lock contention

## 7. Security Considerations

- **Rate Limiting**: Redis-based, 100 req/min per IP
- **CORS**: Whitelist frontend domain only
- **Input Validation**: Pydantic models cho mọi endpoint
- **SQL Injection**: SQLAlchemy parameterized queries
- **Crawl Ethics**: Respect robots.txt, reasonable crawl rate
