# 🤖 Claude Code Prompts - ShopSmart Analytics

> **Hướng dẫn:** Copy từng prompt bên dưới, paste vào Claude Code theo đúng thứ tự.
> Mỗi prompt tương ứng 1 task. Chờ hoàn thành rồi mới chạy prompt tiếp theo.
> Nếu có lỗi, paste lỗi vào Claude Code để fix trước khi đi tiếp.

---

## 🔧 PHASE 1: Infrastructure Setup

### Prompt 1.1 — Project Initialization
```
Tạo project "shopsmart-analytics" với cấu trúc folder đầy đủ theo file 05_FOLDER_STRUCTURE.md.

Tạo các file cấu hình:
- .gitignore (Python, Node, Docker, .env)
- .env.example với tất cả biến môi trường cần thiết
- Makefile với commands: dev, build, down, logs, db-migrate, db-seed, crawl, test
- README.md placeholder

Init git repo.
```

### Prompt 1.2 — Docker Compose
```
Tạo docker-compose.yml và docker-compose.dev.yml cho project shopsmart-analytics.

Services cần có:
1. backend: FastAPI + Uvicorn, port 8000, hot reload khi dev
2. frontend: React + Vite, port 3000, hot reload
3. db: PostgreSQL 16, port 5432, persistent volume
4. redis: Redis 7, port 6379
5. crawler: Python container cho Scrapy + Playwright

Backend Dockerfile: Python 3.11, install requirements
Frontend Dockerfile: Node 20, install packages
Crawler Dockerfile: Python 3.11 + Playwright browsers

Tất cả services cùng network. Backend depends_on db và redis.
Dev compose override: mount source code volumes, enable debug.
```

### Prompt 1.3 — Backend Foundation
```
Setup FastAPI backend cho shopsmart-analytics/backend/app/:

1. main.py: FastAPI app với CORS, lifespan (startup/shutdown), include router
2. config.py: Pydantic Settings đọc từ env vars (DATABASE_URL, REDIS_URL, etc.)
3. database.py: SQLAlchemy async engine, sessionmaker, get_db dependency
4. requirements.txt: fastapi, uvicorn, sqlalchemy, asyncpg, alembic, pydantic, redis, httpx, python-dotenv

Setup Alembic:
- alembic.ini
- migrations/env.py đọc DATABASE_URL từ config

Verify: uvicorn app.main:app chạy được, /health trả {"status": "ok"}
```

---

## 🗄️ PHASE 2: Database & Models

### Prompt 2.1 — SQLAlchemy Models
```
Tạo tất cả SQLAlchemy models theo file 03_DATABASE_SCHEMA.md.

Các file cần tạo trong backend/app/models/:
- platform.py: Platform model
- category.py: Category model (self-referencing parent_id)
- product.py: Product model + PriceHistory model
- review.py: Review model
- analytics.py: ProductAnalytics model
- alert.py: PriceAlert model
- crawl_log.py: CrawlLog + MLModelMetrics models
- __init__.py: import tất cả models

Mỗi model có:
- Đúng data types, constraints, defaults theo schema
- Relationships (back_populates)
- Indexes đã define trong schema
- __repr__ method

Tạo Alembic migration: alembic revision --autogenerate -m "initial_schema"
```

### Prompt 2.2 — Pydantic Schemas
```
Tạo Pydantic schemas (request/response models) theo file 04_API_DESIGN.md.

Các file trong backend/app/schemas/:
- common.py: PaginationMeta, BaseResponse, ErrorResponse
- product.py: ProductSearchParams, ProductResponse, ProductDetailResponse, PriceHistoryResponse, PricePointResponse
- analytics.py: TrendingParams, PriceComparisonResponse, MarketOverviewResponse
- alert.py: CreateAlertRequest, AlertResponse
- __init__.py

Mỗi schema có validators, Field descriptions, examples.
Response models kế thừa BaseResponse pattern.
```

### Prompt 2.3 — Seed Data
```
Tạo scripts/seed_data.py:

Insert dữ liệu khởi tạo vào PostgreSQL:
1. Platforms: shopee, tiki, lazada (với base_url)
2. Categories: Điện thoại, Laptop, Thời trang, Gia dụng, Mỹ phẩm, Sách, Thể thao, Thực phẩm (khoảng 15-20 danh mục phổ biến, có parent-child)

Script đọc DATABASE_URL từ env, dùng SQLAlchemy để insert.
Chạy: python scripts/seed_data.py
```

---

## 🔌 PHASE 3: API Endpoints

### Prompt 3.1 — Product API
```
Implement Product API endpoints theo 04_API_DESIGN.md.

Files:
1. backend/app/services/product_service.py:
   - get_products(): search, filter (category, platform, price range, rating), sort, pagination
   - get_product_by_id(): chi tiết + price stats (min/max/avg 30d)
   - get_price_history(): theo period (7d/30d/90d), granularity
   - Full-text search dùng PostgreSQL pg_trgm

2. backend/app/services/cache_service.py:
   - Redis cache wrapper: get, set, delete, với TTL
   - Cache key pattern: "products:search:{hash}", "product:{id}"

3. backend/app/api/products.py:
   - GET /api/v1/products
   - GET /api/v1/products/{id}
   - GET /api/v1/products/{id}/price-history
   - GET /api/v1/products/{id}/reviews
   - Sử dụng Depends(get_db), response_model

4. backend/app/api/router.py: Include products router

Test bằng Swagger UI tại http://localhost:8000/docs
```

### Prompt 3.2 — Analytics API
```
Implement Analytics API endpoints:

1. backend/app/services/analytics_service.py:
   - get_trending(): top sản phẩm giảm giá, bán chạy, deals tốt
   - get_price_comparison(): tìm sản phẩm tương tự cross-platform, so sánh giá
   - get_market_overview(): tổng sản phẩm, avg discount per platform, category stats

2. backend/app/api/analytics.py:
   - GET /api/v1/analytics/trending
   - GET /api/v1/analytics/price-comparison?q=...
   - GET /api/v1/analytics/market-overview
   - GET /api/v1/analytics/category-insights/{category_id}

3. backend/app/api/system.py:
   - GET /api/v1/health
   - GET /api/v1/stats/crawl (latest crawl log)
```

### Prompt 3.3 — Alerts API
```
Implement Alerts API:

1. backend/app/services/alert_service.py:
   - create_alert(): validate product exists, tạo alert
   - get_alerts_by_email(): list user's alerts
   - delete_alert()
   - check_and_trigger_alerts(): gọi sau mỗi lần crawl, check giá vs target

2. backend/app/api/alerts.py:
   - POST /api/v1/alerts
   - GET /api/v1/alerts?email=...
   - DELETE /api/v1/alerts/{id}
```

---

## 🕷️ PHASE 4: Crawler

### Prompt 4.1 — Scrapy Setup & Tiki Spider
```
Setup Scrapy project trong crawler/ folder.

1. scrapy.cfg, settings.py:
   - CONCURRENT_REQUESTS = 8
   - DOWNLOAD_DELAY = 2
   - AUTOTHROTTLE_ENABLED = True
   - USER_AGENT rotation
   - ITEM_PIPELINES

2. items.py:
   - ProductItem: name, price, original_price, url, image_url, rating, review_count, sold_count, seller_name, platform, external_id, category
   - ReviewItem: product_external_id, author, rating, content, date, platform

3. spiders/tiki_spider.py:
   - Crawl Tiki qua API (tiki.vn/api/v2/products)
   - Crawl theo category
   - Parse JSON response → ProductItem
   - Crawl reviews cho mỗi product

4. pipelines.py:
   - CleaningPipeline: validate, clean data, normalize price
   - PostgresPipeline: upsert product, insert price_history
   - Đọc DATABASE_URL từ env

5. middlewares.py:
   - RandomUserAgentMiddleware

Chạy thử: scrapy crawl tiki -a category=dien-thoai --nolog | head -20
Target: crawl 1000+ sản phẩm thành công
```

### Prompt 4.2 — Shopee Spider (Playwright)
```
Implement Shopee spider dùng Playwright (vì Shopee là SPA, cần render JS).

1. crawler/shopsmart_crawler/utils/playwright_helper.py:
   - PlaywrightHelper class: init browser, get page content, close
   - Handle anti-bot: random delay, scroll, wait for content

2. crawler/shopsmart_crawler/spiders/shopee_spider.py:
   - Dùng Shopee internal API nếu có (shopee.vn/api/v4/search/search_items)
   - Fallback: Playwright render page → parse HTML
   - Extract: product name, price, rating, sold count, shop info
   - Pagination qua API params

3. Update pipelines.py nếu cần handle Shopee-specific data format

Lưu ý: Respect rate limits, 1 request mỗi 2-3 giây
```

### Prompt 4.3 — Mock Data Generator
```
Tạo scripts/generate_fake_data.py:

Generate dữ liệu mock realistic cho development & demo:
- 10,000 products across 3 platforms, nhiều categories
- 120,000+ price_history records (30 ngày, mỗi product 4 records/ngày)
- Price patterns: giảm dần, tăng dần, flash sale spike, stable, seasonal
- 200,000+ reviews với sentiment đa dạng
- Một số fake reviews (repetitive, generic, suspicious patterns)

Dùng Faker library, numpy cho price patterns.
Insert batch vào PostgreSQL (bulk_insert_mappings cho performance).

Mục đích: có đủ data để demo AI features và dashboard đẹp mắt.
```

---

## ⚛️ PHASE 5: Frontend

### Prompt 5.1 — React Setup & Layout
```
Setup React frontend trong frontend/ folder:

1. Init Vite + React project
2. Install: tailwindcss, react-router-dom, @tanstack/react-query, axios, recharts, zustand, lucide-react, clsx
3. Setup TailwindCSS config (custom colors: primary blue, accent green/red cho price)
4. Tạo Layout component:
   - Header: logo, search bar, navigation
   - Sidebar: category navigation, platform filter
   - Footer: credits, links
   - Responsive: sidebar collapse trên mobile
5. Setup React Router:
   - / → Dashboard
   - /search → ProductSearch
   - /products/:id → ProductDetail
   - /compare → PriceCompare
   - /trending → Trending
   - /insights → AIInsights
   - /alerts → Alerts
6. Setup Axios instance (base URL, interceptors)
7. Setup React Query provider

Verify: app chạy trên localhost:3000, navigate giữa các routes
```

### Prompt 5.2 — Dashboard & Search Pages
```
Implement Dashboard và Product Search pages:

1. src/pages/Dashboard.jsx:
   - Stats cards: tổng sản phẩm, tổng sàn, avg discount (từ /analytics/market-overview)
   - Trending products carousel/grid (từ /analytics/trending)
   - Platform comparison bar chart (Recharts)
   - "Deals hôm nay" section
   - Giao diện clean, professional, dùng Tailwind

2. src/pages/ProductSearch.jsx:
   - Search bar (debounce 300ms)
   - Filter sidebar: category, platform, price range (slider), rating
   - Product grid (responsive: 4 cols desktop, 2 tablet, 1 mobile)
   - Sort dropdown: relevance, price asc/desc, rating, discount
   - Pagination
   - Loading skeleton

3. src/components/common/ProductCard.jsx:
   - Image, name (truncate), platform badge, price (current + original strikethrough)
   - Rating stars, sold count
   - BuySignalBadge: "Nên mua" (green), "Chờ thêm" (yellow), "Cảnh báo" (red)

4. src/hooks/useProducts.js: React Query hook gọi product API
5. src/services/productService.js: API calls
```

### Prompt 5.3 — Product Detail Page
```
Implement Product Detail page:

1. src/pages/ProductDetail.jsx:
   - Product hero section: image, name, platform, seller
   - Current price (lớn, nổi bật) + original price + discount badge
   - AI Buy Signal badge lớn + recommendation text
   - Price History chart (Recharts AreaChart):
     - Line chart hiển thị giá 30/60/90 ngày
     - Toggle period buttons
     - Hover tooltip hiện giá + ngày
   - Price Prediction overlay (nét đứt, màu khác) nếu có AI data
   - Price Statistics cards: min 30d, max 30d, avg, current vs avg
   - Reviews summary: rating distribution bar, sentiment pie chart
   - Fake review warning banner nếu fake_review_percent > 10%
   - "Tạo Alert" button → modal form
   - Link "Mua ngay" → redirect to product URL trên sàn

2. src/components/charts/PriceHistoryChart.jsx:
   - Recharts AreaChart, responsive
   - Gradient fill, smooth curve
   - Custom tooltip

3. src/hooks/usePriceHistory.js
```

### Prompt 5.4 — Compare & Trending Pages
```
Implement remaining frontend pages:

1. src/pages/PriceCompare.jsx:
   - Search input: nhập tên sản phẩm
   - Comparison table: platform | price | rating | seller | link
   - Highlight best price (green)
   - Bar chart so sánh giá giữa các sàn

2. src/pages/Trending.jsx:
   - Tabs: "Giảm giá sốc", "Bán chạy", "Deals tốt nhất"
   - Product grid cho mỗi tab
   - Auto-refresh mỗi 5 phút

3. src/pages/Alerts.jsx:
   - Form tạo alert: chọn product, nhập target price, chọn type
   - List alerts hiện tại (table)
   - Toggle active/inactive
   - Delete alert

4. Responsive check toàn bộ pages trên mobile
```

---

## 🧠 PHASE 6: AI/ML Features

### Prompt 6.1 — Price Prediction
```
Implement price prediction model:

1. backend/app/ml/price_predictor.py:
   - Class PricePredictor:
     - train(product_id): lấy price_history, train Facebook Prophet model
     - predict(product_id, days=7): return list predictions + confidence
     - Fallback: nếu không đủ data (< 30 points), dùng simple moving average
   - Save/load model với joblib

2. backend/app/ml/trainer.py:
   - Script train tất cả models
   - Train price predictor cho top 100 products (theo views/popularity)
   - Log metrics vào ml_model_metrics table

3. backend/app/api/ai_insights.py:
   - GET /api/v1/ai/predict-price/{product_id}?days=7
   - Response: predictions list + recommendation + model info

4. requirements.txt: thêm prophet, scikit-learn, joblib

Test: train model cho 1 product, predict 7 ngày, verify output format
```

### Prompt 6.2 — Anomaly Detection
```
Implement anomaly detection:

1. backend/app/ml/anomaly_detector.py:
   - Class AnomalyDetector:
     - Features: price_change_percent, price_vs_avg_30d, price_vs_avg_category, discount_percent, time_since_last_change
     - Model: IsolationForest (scikit-learn)
     - train(): train trên toàn bộ price data
     - detect(product_id): return anomaly_score (0-1), anomaly_type
     - Anomaly types: "sudden_price_drop", "fake_discount", "price_manipulation", "unusual_pattern"

2. backend/app/ml/recommender.py:
   - Class BuyRecommender:
     - Inputs: price trend, prediction, anomaly score, discount vs historical
     - Output: buy_signal ("strong_buy", "buy", "hold", "wait") + reason text
     - Logic rule-based kết hợp ML signals

3. API: GET /api/v1/ai/anomalies?limit=20
4. Compute daily product_analytics records (cron job hoặc API trigger)
```

### Prompt 6.3 — Review Analysis (NLP)
```
Implement review analysis:

1. backend/app/ml/review_analyzer.py:
   - Class ReviewAnalyzer:
     - analyze_sentiment(text): Vietnamese sentiment analysis
       - Option A (simple): Dùng dictionary-based approach với Vietnamese sentiment lexicon
       - Option B (better): Dùng pre-trained model (underthesea hoặc PhoBERT nếu resources cho phép)
       - Return: sentiment_score (-1 to 1)
     - detect_fake_review(review): 
       - Features: review_length, has_generic_phrases, rating_vs_sentiment_mismatch, reviewer_review_count, time_pattern
       - Model: RandomForest classifier
       - Return: is_fake (bool), confidence (0-1)
     - batch_analyze(product_id): analyze all reviews for a product

2. API: POST /api/v1/ai/check-reviews (body: {product_id})
3. Update reviews table: sentiment_score, is_fake, fake_confidence

requirements.txt: thêm underthesea (Vietnamese NLP), hoặc dùng simple lexicon approach
```

---

## 🔄 PHASE 7: Data Pipeline & Polish

### Prompt 7.1 — Airflow DAGs
```
Setup Apache Airflow và tạo DAGs:

1. airflow/Dockerfile: Python 3.11 + Apache Airflow
2. Update docker-compose.yml: thêm airflow-webserver, airflow-scheduler services

3. airflow/dags/crawl_pipeline.py:
   - DAG: crawl_all_platforms, schedule="0 */6 * * *" (mỗi 6h)
   - Tasks: crawl_tiki >> crawl_shopee >> update_analytics >> check_alerts
   - Mỗi task gọi Scrapy spider qua subprocess
   - Log crawl results vào crawl_logs table

4. airflow/dags/analytics_pipeline.py:
   - DAG: compute_daily_analytics, schedule="0 1 * * *" (1h sáng daily)
   - Tasks: compute price stats >> compute anomaly scores >> update buy signals

5. airflow/dags/ml_training_pipeline.py:
   - DAG: retrain_models, schedule="0 3 * * 0" (3h sáng Chủ nhật)
   - Tasks: train_price_predictor >> train_anomaly_detector >> train_review_classifier >> log_metrics

Verify: Airflow UI chạy tại localhost:8080, DAGs visible
```

### Prompt 7.2 — Monitoring
```
Setup monitoring stack:

1. monitoring/prometheus/prometheus.yml:
   - Scrape targets: backend (metrics endpoint), node_exporter

2. Backend: thêm prometheus_fastapi_instrumentator
   - Auto metrics: request count, latency, status codes
   - Custom metrics: crawl_products_total, ml_prediction_latency

3. monitoring/grafana/dashboards/system.json:
   - API request rate & latency
   - Error rate
   - Database connections
   - Redis hit rate

4. monitoring/grafana/dashboards/crawl.json:
   - Products crawled per run
   - Crawl success rate
   - Data freshness (time since last crawl)
   - Products per platform over time

5. Update docker-compose: thêm prometheus, grafana services
   - Grafana port 3001, auto-provision dashboards

Verify: Grafana accessible, dashboards hiển thị data
```

### Prompt 7.3 — AI Insights Frontend Page
```
Implement AI Insights dashboard page:

1. src/pages/AIInsights.jsx:
   - Section "Dự đoán giá": search product → hiện prediction chart
   - Section "Cảnh báo bất thường": table anomalies mới nhất
     - Columns: product, anomaly type, score, giá hiện tại vs expected, ngày
     - Color code theo severity
   - Section "Phân tích Review": 
     - Search product → pie chart sentiment distribution
     - Fake review percentage indicator
     - Sample fake reviews highlighted
   - Section "Tín hiệu mua": grid products với buy signals
     - Tabs: "Nên mua ngay", "Chờ thêm", "Cảnh báo"

2. src/components/charts/PricePredictionChart.jsx:
   - Recharts: historical price (solid line) + predicted (dashed line)
   - Confidence interval band (shaded area)
   - Tooltip hiện predicted price + confidence

3. src/components/charts/SentimentChart.jsx:
   - Donut chart: positive/neutral/negative
```

### Prompt 7.4 — Final Polish & Deploy
```
Final polish và deploy preparation:

1. Frontend:
   - Dark mode toggle (Tailwind dark: variant)
   - Loading skeletons cho tất cả pages
   - Error boundary component
   - Empty state illustrations
   - SEO meta tags
   - Favicon + logo

2. Backend:
   - Rate limiting middleware (Redis-based, 100 req/min)
   - Request logging middleware
   - CORS production config
   - API versioning verify

3. Docker production:
   - Multi-stage Dockerfile cho backend (slim image)
   - Frontend: build → Nginx serve
   - docker-compose.prod.yml

4. README.md hoàn chỉnh:
   - Project description + motivation
   - Screenshots/GIFs (placeholder paths)
   - Architecture diagram (text-based)
   - Tech stack badges
   - Setup instructions (clone, docker-compose up)
   - API documentation link
   - Features list
   - Future improvements
   - License

5. .github/workflows/ci.yml:
   - On push: lint, test, build docker images

Verify: docker-compose -f docker-compose.prod.yml up chạy clean
```

---

## 💡 Tips Sử Dụng Prompts

1. **Mỗi lần 1 prompt**: Đừng paste nhiều prompts cùng lúc
2. **Verify trước khi tiếp**: Chạy thử, test endpoint, check UI trước khi sang prompt mới
3. **Fix lỗi ngay**: Nếu có lỗi, paste error log vào Claude Code kèm context
4. **Có thể skip**: Nếu hết thời gian, skip Phase 7.1 (Airflow) và 7.2 (Monitoring), focus vào deploy
5. **Commit thường xuyên**: Sau mỗi prompt thành công, git commit
6. **Tham chiếu docs**: Khi paste prompt, kèm thêm "Tham khảo file [tên file].md trong thư mục planning/" nếu cần Claude Code đọc design docs
