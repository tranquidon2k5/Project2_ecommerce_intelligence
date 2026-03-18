# 📅 Sprint Plan - ShopSmart Analytics (4 Sprints x ~4-5 ngày)

---

## Sprint 1: Foundation (Ngày 1-5)
**Mục tiêu: Setup infrastructure + Backend core + Crawler cơ bản**

### Day 1: Project Setup & Infrastructure
- [x] Tạo toàn bộ folder structure
- [x] Setup Docker Compose (PostgreSQL, Redis, Backend, Frontend, Crawler) — 5 services total
- [x] Tạo .env.example, Makefile
- [x] Verify tất cả containers chạy được
- [x] Setup Alembic cho database migration

### Day 2: Database & Backend Models
- [x] Tạo tất cả SQLAlchemy models (products, price_history, reviews, etc.)
- [x] Viết Alembic migration scripts
- [x] **Setup range partitioning by month for price_history table** (PostgreSQL native)
- [x] **Add BRIN index on price_history.crawled_at** (space-efficient for time-series)
- [x] Run migration, verify schema
- [x] Tạo seed data script (platforms, categories)
- [x] Setup Pydantic schemas (request/response models)

### Day 3: Core API Endpoints
- [x] GET /products (search, filter, pagination)
- [x] GET /products/{id} (chi tiết sản phẩm)
- [x] GET /products/{id}/price-history
- [x] GET /health
- [x] Setup Redis cache service
- [x] Test với Swagger docs (FastAPI auto-generated)

### Day 4-5: Crawler (1 sàn đầu tiên)
- [x] Setup Scrapy project
- [x] Implement Tiki spider (dễ crawl nhất, API rõ ràng)
- [x] Implement data cleaning pipeline
- [x] Implement DB saving pipeline
- [x] Crawl thử 1000+ sản phẩm
- [x] Verify data trong PostgreSQL

**✅ Sprint 1 Done khi:** Docker lên được (5 services), API trả data, crawl được 1000+ sản phẩm từ Tiki, price_history partitioned

---

## Sprint 2: Frontend + More Data (Ngày 6-10)
**Mục tiêu: Dashboard UI + Thêm data sources + API mở rộng**

### Day 6: Frontend Setup & Layout
- [ ] Init React + Vite + TailwindCSS
- [ ] Setup React Router
- [ ] Tạo Layout component (Header, Sidebar, Footer)
- [ ] Setup Axios API service
- [ ] Setup React Query

### Day 7: Core Pages
- [ ] Dashboard page (market overview, stats cards)
- [ ] Product Search page (search bar, filters, product cards)
- [ ] Pagination component
- [ ] Connect frontend → backend API

### Day 8: Product Detail Page
- [ ] Product detail layout
- [ ] Price History chart (Recharts line chart)
- [ ] Rating & review summary
- [ ] Related products section
- [ ] Responsive design

### Day 9: Thêm Crawler + Analytics API
- [ ] Implement Shopee spider (cần Playwright vì SPA)
- [ ] GET /analytics/trending
- [ ] GET /analytics/price-comparison
- [ ] GET /analytics/market-overview
- [ ] Trending page trên frontend

### Day 10: Price Compare, Alerts CRUD & Polish
- [ ] Price comparison page (cross-platform table/chart)
- [ ] Platform compare chart
- [ ] **Alerts CRUD API** (POST/GET/DELETE /alerts — this is CRUD, not AI work, moved from Sprint 3)
- [ ] **Alerts management page on frontend** (form + list + delete)
- [ ] Loading states, error handling
- [ ] Responsive mobile design

**✅ Sprint 2 Done khi:** Frontend chạy mượt, hiển thị data thật, có 2+ sàn TMĐT, alerts CRUD working

---

## Sprint 3: AI Features (Ngày 11-15)
**Mục tiêu: 2 ML models + Rule-based review analysis + AI Insights UI**

> **Scope reduction (risk mitigation):** Reduced from 3 ML models + alerts to 2 ML models + rule-based review analysis. Alerts CRUD moved to Sprint 2. PhoBERT replaced with lightweight lexicon approach.

### Day 11: Price Prediction Model
- [ ] Prepare training data (price_history → time-series)
- [ ] Train Prophet model cho price forecasting (only for products with 30+ data points)
- [ ] Fallback: moving average + % change heuristics for products with <30 data points
- [ ] Evaluate: MAE, MAPE
- [ ] Save model artifacts
- [ ] API: GET /ai/predict-price/{product_id}

### Day 12: Anomaly Detection
- [ ] Prepare features (price changes, statistical features)
- [ ] Train IsolationForest model
- [ ] Detect: sudden price drops, fake discounts, price manipulation
- [ ] API: GET /ai/anomalies
- [ ] Compute daily product_analytics records

### Day 13: Review Analysis (Rule-based) + Buy Signal
- [ ] Sentiment analysis: `underthesea` library (Vietnamese lexicon-based, NOT PhoBERT)
- [ ] Fake review detection: rule-based features (review length, generic phrases, rating-sentiment mismatch, timestamp clustering)
- [ ] RandomForest classifier on extracted features
- [ ] Update reviews table với sentiment_score, is_fake
- [ ] API: POST /ai/check-reviews
- [ ] **Buy signal logic**: simple formula (price trend + anomaly score + prediction direction)
- [ ] BuySignalBadge component trên frontend

### Day 14-15: AI Insights Frontend + Integration
- [ ] AI Insights dashboard page (prediction charts, anomaly table, sentiment overview, buy signals)
- [ ] Price prediction chart overlay trên product detail (historical solid + predicted dashed)
- [ ] Background job: check alerts khi crawl xong (trigger from APScheduler)
- [ ] **APScheduler setup**: crawl every 6h, analytics daily, ML retrain weekly
- [ ] Integration testing across all AI endpoints

**✅ Sprint 3 Done khi:** AI predict giá (with data thresholds), phát hiện anomaly, review analysis working, buy signals displayed, scheduled pipelines running

---

## Sprint 4: Performance + Deploy + Polish (Ngày 16-20)
**Mục tiêu: Data scale, monitoring, deploy, README**

> **Scope reduction (risk mitigation):** Airflow replaced with APScheduler (moved to Sprint 3 Day 14-15). Prometheus/Grafana replaced with simple /stats endpoint. Focus on deploy + README (highest CV visual impact).

### Day 16: Performance & Data Scale
- [ ] Database query optimization (EXPLAIN ANALYZE on key queries)
- [ ] Redis caching strategy cho heavy endpoints
- [ ] Generate thêm data (target: **10,000+ products, 120,000+ price points** — realistic for single instance)
- [ ] Database indexing review (verify BRIN, partitioning working)
- [ ] Batch insert optimization for crawl pipeline

### Day 17: Simple Monitoring & Logging
- [ ] FastAPI /stats endpoint (crawl stats, API latency, error rates) — no Prometheus needed
- [ ] Structured logging cho backend & crawler (JSON format)
- [ ] Crawl logs page on frontend (optional)
- [ ] Health check endpoints for all services
- [ ] Data freshness tracking (time since last crawl)

### Day 18: UI Polish & UX
- [ ] Dark mode toggle (Tailwind dark: variant) — high visual impact for CV
- [ ] Loading skeletons thay vì spinners
- [ ] Empty states, error states
- [ ] Export data to CSV
- [ ] Final responsive check (mobile, tablet, desktop)

### Day 19: Deploy
- [ ] Docker production build (multi-stage Dockerfile for backend + frontend)
- [ ] Frontend: build → Nginx serve
- [ ] Deploy: **Railway** (simplest for full-stack, single target)
- [ ] Setup CI/CD (GitHub Actions - basic lint + build)
- [ ] Verify all endpoints working in production

### Day 20: Documentation & Demo
- [ ] README.md chuyên nghiệp (screenshots, architecture diagram, tech stack badges)
- [ ] Setup instructions (clone → docker-compose up → working app)
- [ ] API documentation link (FastAPI auto-generated Swagger)
- [ ] Features list with realistic claims
- [ ] Record demo video / GIF
- [ ] Chuẩn bị nội dung cho CV

**✅ Sprint 4 Done khi:** Project live trên internet, README đẹp, sẵn sàng show trong CV

---

## Daily Workflow Gợi Ý

```
08:00 - 09:00  Review plan, đọc docs nếu cần
09:00 - 12:00  Code session 1 (focus, không distraction)
12:00 - 13:00  Break
13:00 - 17:00  Code session 2
17:00 - 17:30  Git commit, push, viết notes
17:30 - 18:00  Plan cho ngày mai
```

## Risk Matrix

| # | Risk | Severity | Likelihood | Impact | Priority |
|---|------|----------|------------|--------|----------|
| 1.1 | Anti-bot blocking (Shopee/Lazada) | CRITICAL | Very High | Crawl pipeline fails entirely | P0 |
| 1.3 | 50k products infeasible on 1 instance | HIGH | Certain | Can't deliver claimed scale | P0 — **MITIGATED: target reduced to 10k** |
| 2.3 | PhoBERT memory explosion | CRITICAL | High | Docker Compose crashes | P0 — **MITIGATED: replaced with lexicon-based** |
| 4.1 | Sprint 3 overloaded (5 days, 7+ days work) | CRITICAL | Certain | Sprint fails, project incomplete | P0 — **MITIGATED: reduced to 2 ML models, alerts moved to Sprint 2** |
| 4.2 | Sprint 4 overloaded | HIGH | Very High | No deploy, no README | P1 — **MITIGATED: Airflow → APScheduler, no Prometheus/Grafana** |
| 2.1 | Prophet with insufficient data (<30 points) | HIGH | Certain | Garbage predictions | P1 — **MITIGATED: data threshold + fallback heuristics** |
| 3.1 | price_history unbounded growth | HIGH | High | Query degradation after 1 month | P1 — **MITIGATED: partitioning + BRIN index from Sprint 1** |
| 1.2 | Selector/API changes break crawler | HIGH | Medium | Partial data loss | P2 |
| 2.2 | Concept drift / seasonal events | MEDIUM | Medium | Inaccurate predictions | P2 |
| 3.2 | DB race conditions during crawl | LOW | Low | Minor query latency | P3 |

### Remaining unmitigated risks:
- **1.1 (Anti-bot)**: Residential proxies help but Shopee/Lazada may still block. Fallback: synthetic data for demo.
- **1.2 (Selector changes)**: Monitor extraction failure rates. Store raw responses for re-parsing.
- **2.2 (Concept drift)**: Document as known limitation. Add event flags as future improvement.

## Priority nếu thiếu thời gian

Nếu chỉ có 2 tuần:
1. ✅ Sprint 1 (Foundation) - BẮT BUỘC
2. ✅ Sprint 2 (Frontend + Data + Alerts CRUD) - BẮT BUỘC
3. ⚠️ Sprint 3 (AI) - Already simplified: 2 ML models + rule-based review analysis
4. ❌ Sprint 4 — Skip monitoring. Focus deploy (Railway) + README + dark mode (highest CV visual impact)
