# 📋 CHANGELOG — ShopSmart Analytics

> Ghi lại toàn bộ thay đổi theo từng sprint. Cập nhật mỗi khi hoàn thành 1 sprint.

---

## [Sprint 1] — 2026-03-18 ✅ HOÀN THÀNH

### Tóm tắt
Docker 5 services chạy, API trả data thực, crawler crawl được Tiki, DB schema đầy đủ.

### Verified
- `curl localhost:8000/health` → `{"status":"ok","version":"1.0.0"}`
- `curl localhost:8000/api/v1/products?limit=3` → 106 sản phẩm thực từ tiki.vn
- `alembic upgrade head` → 9 tables tạo thành công
- `scrapy crawl tiki` → 106 products lưu vào PostgreSQL

---

### Wave 1 — Project Initialization

**Files tạo mới:**
- `.gitignore` — Python, Node, Docker, .env exclusions
- `.env.example` — tất cả env vars (DATABASE_URL, REDIS_URL, SECRET_KEY, ...)
- `Makefile` — 12 targets: dev, build, down, logs, db-migrate, db-seed, crawl, test, ...
- `README.md` — project overview, quick start, tech stack
- `backend/app/ml/models/.gitkeep`
- `docs/screenshots/.gitkeep`

**Directories tạo:**
```
backend/app/{models,schemas,api,services,ml/models,utils}/
backend/{migrations/versions,tests}/
crawler/shopsmart_crawler/{spiders,utils}/
frontend/src/components/{layout,common,charts}/
frontend/src/{pages,hooks,services,store,utils}/
scripts/, docs/screenshots/
```

**Git:** Initialized (`git init`)

---

### Wave 2A — Docker Infrastructure

**Files tạo mới:**
- `docker-compose.yml` — 5 services: db (PostgreSQL 16), redis (Redis 7), backend (port 8000), frontend (port 3000), crawler; healthchecks, named volumes, bridge network
- `docker-compose.dev.yml` — hot reload overrides cho backend (uvicorn --reload) và frontend (vite dev)
- `backend/Dockerfile` — Python 3.11-slim, gcc, libpq-dev, uvicorn
- `frontend/Dockerfile` — multi-stage: Node 20 build → nginx:alpine serve
- `frontend/Dockerfile.dev` — Node 20 dev server
- `frontend/nginx.conf` — SPA fallback + `/api` reverse proxy → backend:8000
- `crawler/Dockerfile` — Python 3.11-slim (Playwright bỏ qua vì Tiki dùng JSON API)
- `crawler/requirements.txt` — scrapy, psycopg2-binary, fake-useragent, python-dotenv

**Lưu ý:**
- Xóa `playwright install-deps` khỏi crawler/Dockerfile vì Tiki spider dùng HTTP JSON API, không cần browser

---

### Wave 2B — Backend Foundation

**Files tạo mới:**
- `backend/requirements.txt` — fastapi, uvicorn, sqlalchemy[asyncio], asyncpg, alembic, pydantic-settings, redis, httpx, faker, numpy
- `backend/app/__init__.py`
- `backend/app/config.py` — Pydantic Settings (DATABASE_URL, REDIS_URL, cache TTLs, ...)
- `backend/app/database.py` — async SQLAlchemy engine, `AsyncSessionLocal`, `get_db` dependency
- `backend/app/main.py` — FastAPI app, CORS, lifespan, `/health` endpoint, graceful router import
- `backend/app/utils/exceptions.py` — ProductNotFoundException, AlertNotFoundException, DatabaseException
- `backend/app/utils/pagination.py` — PaginationMeta, paginate()
- `backend/app/utils/helpers.py` — make_cache_key(), format_vnd()
- `backend/alembic.ini` — Alembic config
- `backend/migrations/env.py` — sync engine (psycopg2) cho migrations
- `backend/migrations/script.py.mako` — Alembic template
- `backend/pyproject.toml` — pytest config

**Fix đã áp dụng:**
- `migrations/env.py` ban đầu dùng `async_engine_from_config` với sync URL → fix sang `engine_from_config` (sync psycopg2)

---

### Wave 3A — SQLAlchemy Models

**Files tạo mới trong `backend/app/models/`:**
- `__init__.py` — export Platform, Category, Product, PriceHistory, Review, ProductAnalytics, PriceAlert, CrawlLog, MLModelMetrics
- `platform.py` — Platform model (id, name, base_url, is_active)
- `category.py` — Category model với self-referencing parent_id
- `product.py` — Product + PriceHistory; UniqueConstraint(platform_id, external_id); 5 indexes; tất cả giá là BIGINT
- `review.py` — Review model với sentiment_score, is_fake, fake_confidence
- `analytics.py` — ProductAnalytics: daily aggregates, trend_direction, buy_signal, anomaly_score
- `alert.py` — PriceAlert với CheckConstraint alert_type IN ('below','above','any_change')
- `crawl_log.py` — CrawlLog + MLModelMetrics

**`backend/migrations/versions/001_initial_schema.py`:**
- `CREATE EXTENSION pg_trgm`
- GIN index: `CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops)`
- BRIN index: `CREATE INDEX idx_price_history_crawled_brin ON price_history USING brin(crawled_at)`
- Partial indexes: fake reviews, active alerts
- 9 tables theo đúng thứ tự dependency

---

### Wave 3B — Pydantic Schemas

**Files tạo mới trong `backend/app/schemas/`:**
- `__init__.py`
- `common.py` — PaginationMeta, BaseResponse[T] (generic), ErrorDetail, ErrorResponse
- `product.py` — ProductSearchParams, ProductResponse, ProductDetailResponse, PriceHistoryResponse, PricePointResponse, ReviewResponse, ReviewSummaryResponse, AIInsightsResponse, PriceStatsResponse
- `analytics.py` — TrendingParams, PriceComparisonResponse, MarketOverviewResponse, CategoryInsightsResponse
- `alert.py` — CreateAlertRequest (EmailStr validation), AlertResponse

---

### Wave 3C — Seed Data

**Files tạo mới:**
- `scripts/seed_data.py` — insert 3 platforms + 21 categories (8 parent + 13 child) vào PostgreSQL; idempotent (check before insert)

**Kết quả khi chạy:**
```
✓ shopee / tiki / lazada
✓ 8 parent categories: Điện thoại & Phụ kiện, Máy tính & Laptop, Thời trang, ...
✓ 13 sub-categories: Điện thoại, Laptop, Thời trang nam/nữ, Giày dép, ...
```

---

### Wave 4A — Product API

**Files tạo mới:**
- `backend/app/services/__init__.py`
- `backend/app/services/cache_service.py` — Redis async wrapper (get/set/delete/delete_pattern), singleton `cache_service`
- `backend/app/services/product_service.py` — get_products (pg_trgm search, filter, sort, pagination), get_product_by_id (+ 30d price stats), get_price_history (daily aggregation), get_product_reviews
- `backend/app/api/__init__.py`
- `backend/app/api/products.py` — GET /api/v1/products, /{id}, /{id}/price-history, /{id}/reviews
- `backend/app/api/router.py` — main router, graceful include (try/except ImportError)

---

### Wave 4B — Analytics + System API

**Files tạo mới:**
- `backend/app/services/analytics_service.py` — get_trending (price_drop/best_seller/best_deal/most_reviewed), get_price_comparison, get_market_overview, get_category_insights
- `backend/app/api/analytics.py` — GET /api/v1/analytics/trending, /price-comparison, /market-overview, /category-insights/{id}
- `backend/app/api/system.py` — GET /health, GET /stats/crawl, GET /stats/system

---

### Wave 4C — Alerts API + AI Stub

**Files tạo mới:**
- `backend/app/services/alert_service.py` — create_alert, get_alerts_by_email, delete_alert, check_and_trigger_alerts
- `backend/app/api/alerts.py` — POST /api/v1/alerts, GET /alerts?email=, DELETE /alerts/{id}
- `backend/app/api/ai_insights.py` — GET /ai/predict-price/{id} (stub), GET /ai/anomalies (từ product_analytics)

---

### Wave 5A — Scrapy Tiki Crawler

**Files tạo mới trong `crawler/`:**
- `scrapy.cfg`
- `shopsmart_crawler/settings.py` — CONCURRENT_REQUESTS=8, DOWNLOAD_DELAY=2, AUTOTHROTTLE, retry config
- `shopsmart_crawler/items.py` — ProductItem, ReviewItem
- `shopsmart_crawler/middlewares.py` — RandomUserAgentMiddleware (fake_useragent + fallback)
- `shopsmart_crawler/pipelines.py` — CleaningPipeline (validate/sanitize) + PostgresPipeline (upsert product + insert price_history, batch 100)
- `shopsmart_crawler/spiders/base_spider.py` — BaseSpider với progress logging
- `shopsmart_crawler/spiders/tiki_spider.py` — crawl `tiki.vn/api/personalish/v1/blocks/listings`, 9 categories, pagination
- `shopsmart_crawler/utils/data_cleaner.py` — clean_price, clean_text, compute_discount

**Kết quả crawl thực tế:**
- 106 sản phẩm điện thoại từ tiki.vn (3 pages)
- 4 HTTP requests, 7 giây, 0 errors

---

### Wave 5B — Mock Data Generator

**Files tạo mới:**
- `scripts/generate_fake_data.py` — tạo 10,000 products × 3 platforms, 120,000+ price_history (30d × 4/day), 200,000+ reviews; 5 price patterns (stable/decreasing/increasing/flash_sale/volatile); batch insert (5000/2000/1000 rows)

---

### Các vấn đề đã gặp và fix

| Vấn đề | Nguyên nhân | Fix |
|--------|-------------|-----|
| `alembic upgrade head` lỗi async driver | `migrations/env.py` dùng `async_engine_from_config` với sync URL | Đổi sang `engine_from_config` (sync psycopg2) |
| `docker cp` path bị Git Bash convert | Git Bash tự convert `/app/` → `C:/Program Files/Git/app/` | Dùng `MSYS_NO_PATHCONV=1 docker exec` |
| `crawler/Dockerfile` build fail | `playwright install-deps` lỗi trên python:3.11-slim | Xóa Playwright khỏi Dockerfile (Tiki spider không cần browser) |
| `make db-seed` path lỗi | Makefile dùng `/app/scripts/...` bị Git Bash convert | Dùng `docker exec` trực tiếp với `MSYS_NO_PATHCONV=1` |

---

## [Sprint 2] — Chưa bắt đầu

Kế hoạch:
- Frontend React (Dashboard, ProductSearch, ProductDetail, PriceCompare, Trending, Alerts)
- ML features (Prophet, IsolationForest, fake review detection)
- APScheduler (crawl 6h, analytics daily, retrain weekly)

---

## [Sprint 3] — Chưa bắt đầu

Kế hoạch:
- AI Insights page
- Shopee spider (Playwright)
- Full integration testing

---

## [Sprint 4] — Chưa bắt đầu

Kế hoạch:
- Production Docker builds
- Deploy (Railway hoặc VPS)
- CI/CD (GitHub Actions)
- README hoàn chỉnh với screenshots
