# 📊 PROGRESS — ShopSmart Analytics

> **Cách dùng:** Đánh dấu `[x]` khi task hoàn thành. Chi tiết thay đổi xem `CHANGELOG.md`.
> **Rule:** Làm theo thứ tự từ trên xuống. Sprint trước phải xong mới sang Sprint sau.

---

## Sprint 1: Foundation ✅ HOÀN THÀNH — 2026-03-18

### Day 1: Project Setup & Infrastructure
- [x] Tạo folder structure
- [x] Docker Compose (5 services: backend, frontend, db, redis, crawler)
- [x] Config files (.env.example, Makefile, .gitignore)
- [x] Verify containers chạy được (db + redis + backend ✅)
- [x] Backend foundation (main.py, config.py, database.py)
- [x] Alembic setup

### Day 2: Database & Models
- [x] SQLAlchemy models (9 tables)
- [x] Alembic migration (001_initial_schema)
- [x] BRIN index on price_history.crawled_at
- [x] GIN trigram index on products.name (pg_trgm)
- [x] Pydantic schemas (request/response)
- [x] Seed data (3 platforms, 21 categories)

### Day 3: Core API
- [x] GET /api/v1/products (search, filter, pagination)
- [x] GET /api/v1/products/{id} (detail + price stats)
- [x] GET /api/v1/products/{id}/price-history
- [x] GET /api/v1/products/{id}/reviews
- [x] GET /health
- [x] Redis cache service
- [x] Analytics API (trending, market-overview, price-comparison)
- [x] Alerts API (POST/GET/DELETE)
- [x] Swagger UI tại localhost:8000/docs ✅

### Day 4-5: Crawler
- [x] Scrapy project setup
- [x] Tiki spider (JSON API crawl)
- [x] CleaningPipeline + PostgresPipeline
- [x] Crawl thực tế: 106 sản phẩm điện thoại từ tiki.vn ✅
- [x] Verify data in PostgreSQL

### Mock Data Generator
- [x] generate_fake_data.py (10k products, 120k prices, 200k reviews)

**✅ Sprint 1 Checkpoint:**
- Docker 5 services ✓
- `localhost:8000/health` → `{"status":"ok"}` ✓
- `localhost:8000/docs` → Swagger UI ✓
- `localhost:8000/api/v1/products` → 106 sản phẩm thực ✓
- Crawler Tiki hoạt động ✓
- DB schema: 9 tables + pg_trgm + GIN + BRIN ✓

---

## Sprint 2: Frontend + More Data ✅ HOÀN THÀNH — 2026-03-19

### Day 6: Frontend Setup
- [x] Init React + Vite + TailwindCSS
- [x] React Router (6 routes)
- [x] Layout (Header, Sidebar, Layout wrapper)
- [x] Axios instance + React Query setup

### Day 7: Core Pages
- [x] Dashboard page (stats, platform distribution, best deals grid)
- [x] ProductSearch page (search, filters, grid, pagination)
- [x] ProductCard component
- [x] Connect frontend → backend API

### Day 8: Product Detail
- [x] Product detail layout (hero, price stats, history chart)
- [x] PriceHistoryChart (Recharts AreaChart với gradient)
- [x] Alert modal (inline trong ProductDetail)
- [x] Dark mode toggle (localStorage persist)

### Day 9: More Crawler + Analytics
- [x] Shopee spider (Playwright + JSON API)
- [x] Trending page (4 tabs: price_drop, best_seller, best_deal, most_reviewed)
- [x] PriceCompare page (multi-platform price diff highlight)

### Day 10: Alerts & Polish
- [x] Alerts management page (CRUD: create/list/delete)
- [x] Loading skeletons (CardSkeleton, StatSkeleton, TableRowSkeleton)
- [x] Error states (isError banner)
- [x] Responsive grid layout (2→3→4→5 cols)

### Charts
- [x] PriceHistoryChart (AreaChart + ReferenceLine cho min price)
- [x] PlatformCompareChart (BarChart + Cell colors per platform)
- [x] SentimentChart (PieChart donut)

**✅ Sprint 2 Checkpoint:**
- `npm run build` → thành công, 0 errors ✓
- Frontend dev server chạy port 3000 ✓
- 6 pages hoàn chỉnh ✓
- Dark mode toggle hoạt động ✓
- Alerts CRUD (create/list/delete) ✓
- Shopee spider sẵn sàng (Playwright + JSON API) ✓
- 2 sàn có spider: Tiki ✓, Shopee ✓

---

## Sprint 3: AI Features — Chưa bắt đầu

### Day 11: Price Prediction
- [ ] Prophet model (≥30 data points)
- [ ] Moving average fallback (<30 points)
- [ ] GET /ai/predict-price/{product_id}

### Day 12: Anomaly Detection
- [ ] IsolationForest model
- [ ] GET /ai/anomalies
- [ ] Daily product_analytics computation

### Day 13: Review Analysis + Buy Signal
- [ ] Sentiment analysis (underthesea)
- [ ] Fake review detection (RandomForest)
- [ ] POST /ai/check-reviews
- [ ] Buy signal logic (rule-based)
- [ ] BuySignalBadge component

### Day 14-15: AI Frontend + Scheduler
- [ ] AI Insights dashboard page
- [ ] PricePredictionChart (solid + dashed lines)
- [ ] APScheduler: crawl mỗi 6h, analytics daily, retrain weekly

**Sprint 3 Checkpoint:** AI predict ✓, Anomaly ✓, Review analysis ✓, Pipelines scheduled ✓

---

## Sprint 4: Polish + Deploy — Chưa bắt đầu

### Day 16-17: Performance & Monitoring
- [ ] Query optimization
- [ ] Redis caching optimization
- [ ] Generate 10,000+ products data
- [ ] Structured logging (JSON)
- [ ] Health checks all services

### Day 18: UI Polish
- [ ] Dark mode toggle
- [ ] Loading skeletons
- [ ] Empty/error states
- [ ] Export CSV

### Day 19: Deploy
- [ ] Docker production builds
- [ ] Deploy to Railway / VPS
- [ ] CI/CD (GitHub Actions)

### Day 20: Documentation
- [ ] README.md (screenshots, architecture, setup)
- [ ] API documentation
- [ ] Demo GIF

### Testing (anytime)
- [ ] Backend API tests (pytest)
- [ ] Service layer tests
- [ ] ML model tests
- [ ] Crawler tests

**Sprint 4 Checkpoint:** Live deploy ✓, README ✓, Tests ✓

---

## Ghi chú kỹ thuật quan trọng

| Vấn đề | Fix |
|--------|-----|
| Alembic async driver lỗi | Dùng sync `engine_from_config` trong `migrations/env.py` |
| Git Bash convert paths trong Docker | Dùng `MSYS_NO_PATHCONV=1` trước `docker exec` |
| Playwright build fail | Bỏ khỏi crawler/Dockerfile — Tiki dùng JSON API |
| `make db-seed` path lỗi trên Windows | Dùng `docker exec` trực tiếp thay vì Makefile |
