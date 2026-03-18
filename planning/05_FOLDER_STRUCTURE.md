# 📁 Folder Structure - ShopSmart Analytics

---

```
shopsmart-analytics/
│
├── README.md                          # Project overview, setup guide, screenshots
├── LICENSE
├── .gitignore
├── .env.example                       # Environment variables template
├── docker-compose.yml                 # Orchestrate all services
├── docker-compose.dev.yml             # Dev overrides (hot reload, debug)
├── Makefile                           # Shortcuts: make dev, make crawl, make test
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini                    # Database migration config
│   ├── pyproject.toml
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config.py                  # Settings (from env vars)
│   │   ├── database.py                # SQLAlchemy engine, session
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── product.py             # Product, PriceHistory
│   │   │   ├── review.py              # Review
│   │   │   ├── analytics.py           # ProductAnalytics
│   │   │   ├── alert.py               # PriceAlert
│   │   │   ├── platform.py            # Platform
│   │   │   ├── category.py            # Category
│   │   │   └── crawl_log.py           # CrawlLog, MLModelMetrics
│   │   │
│   │   ├── schemas/                   # Pydantic request/response models
│   │   │   ├── __init__.py
│   │   │   ├── product.py
│   │   │   ├── analytics.py
│   │   │   ├── alert.py
│   │   │   └── common.py              # Pagination, base response
│   │   │
│   │   ├── api/                       # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── router.py              # Main router, include all sub-routers
│   │   │   ├── products.py            # /products endpoints
│   │   │   ├── analytics.py           # /analytics endpoints
│   │   │   ├── ai_insights.py         # /ai endpoints
│   │   │   ├── alerts.py              # /alerts endpoints
│   │   │   └── system.py              # /health, /stats endpoints
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── product_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── alert_service.py
│   │   │   └── cache_service.py       # Redis cache logic
│   │   │
│   │   ├── ml/                        # Machine Learning module
│   │   │   ├── __init__.py
│   │   │   ├── price_predictor.py     # Prophet time-series forecasting
│   │   │   ├── anomaly_detector.py    # IsolationForest anomaly detection
│   │   │   ├── review_analyzer.py     # Sentiment + fake review detection
│   │   │   ├── recommender.py         # Buy signal recommendation logic
│   │   │   ├── trainer.py             # Training pipeline script
│   │   │   └── models/                # Saved model artifacts
│   │   │       ├── .gitkeep
│   │   │       ├── price_prophet.pkl
│   │   │       ├── anomaly_iforest.pkl
│   │   │       └── review_classifier.pkl
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── pagination.py
│   │       ├── exceptions.py          # Custom exception classes
│   │       └── helpers.py
│   │
│   ├── migrations/                    # Alembic migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py                # Pytest fixtures
│       ├── test_products.py
│       ├── test_analytics.py
│       ├── test_ml.py
│       └── test_crawlers.py
│
├── crawler/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── scrapy.cfg
│   │
│   ├── shopsmart_crawler/
│   │   ├── __init__.py
│   │   ├── settings.py                # Scrapy settings
│   │   ├── items.py                   # Scrapy items (ProductItem, ReviewItem)
│   │   ├── pipelines.py              # Data cleaning, DB saving pipeline
│   │   ├── middlewares.py             # User-Agent rotation, proxy, retry
│   │   │
│   │   ├── spiders/
│   │   │   ├── __init__.py
│   │   │   ├── base_spider.py         # Abstract base spider
│   │   │   ├── shopee_spider.py       # Shopee crawler
│   │   │   ├── tiki_spider.py         # Tiki crawler
│   │   │   └── lazada_spider.py       # Lazada crawler
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── playwright_helper.py   # Playwright browser automation
│   │       ├── data_cleaner.py        # Price normalization, text cleaning
│   │       └── proxy_manager.py       # Proxy rotation logic
│   │
│   └── tests/
│       ├── test_spiders.py
│       └── test_pipelines.py
│
├── airflow/
│   ├── Dockerfile
│   ├── requirements.txt
│   │
│   └── dags/
│       ├── crawl_pipeline.py          # Main crawl DAG (every 6h)
│       ├── ml_training_pipeline.py    # ML retrain DAG (weekly)
│       ├── analytics_pipeline.py      # Daily analytics computation
│       └── cleanup_pipeline.py        # Data retention cleanup
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf                     # Nginx config for production
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── logo.svg
│   │
│   └── src/
│       ├── main.jsx                   # React entry point
│       ├── App.jsx                    # Router setup
│       ├── index.css                  # Tailwind imports
│       │
│       ├── components/                # Reusable UI components
│       │   ├── layout/
│       │   │   ├── Header.jsx
│       │   │   ├── Sidebar.jsx
│       │   │   ├── Footer.jsx
│       │   │   └── Layout.jsx
│       │   │
│       │   ├── common/
│       │   │   ├── SearchBar.jsx
│       │   │   ├── ProductCard.jsx
│       │   │   ├── PriceTag.jsx
│       │   │   ├── RatingStars.jsx
│       │   │   ├── LoadingSpinner.jsx
│       │   │   ├── Pagination.jsx
│       │   │   └── BuySignalBadge.jsx
│       │   │
│       │   └── charts/
│       │       ├── PriceHistoryChart.jsx
│       │       ├── PricePredictionChart.jsx
│       │       ├── CategoryPieChart.jsx
│       │       ├── PlatformCompareChart.jsx
│       │       └── SentimentChart.jsx
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx          # Home / Market Overview
│       │   ├── ProductSearch.jsx      # Search & filter products
│       │   ├── ProductDetail.jsx      # Product detail + price chart
│       │   ├── PriceCompare.jsx       # Cross-platform comparison
│       │   ├── Trending.jsx           # Trending deals & drops
│       │   ├── AIInsights.jsx         # AI analysis dashboard
│       │   └── Alerts.jsx             # Manage price alerts
│       │
│       ├── hooks/                     # Custom React hooks
│       │   ├── useProducts.js
│       │   ├── usePriceHistory.js
│       │   ├── useAnalytics.js
│       │   └── useDebounce.js
│       │
│       ├── services/                  # API client
│       │   ├── api.js                 # Axios instance, interceptors
│       │   ├── productService.js
│       │   ├── analyticsService.js
│       │   └── alertService.js
│       │
│       ├── store/                     # Zustand state management
│       │   ├── useProductStore.js
│       │   └── useFilterStore.js
│       │
│       └── utils/
│           ├── formatPrice.js         # Format VND currency
│           ├── formatDate.js
│           └── constants.js
│
├── monitoring/
│   ├── prometheus/
│   │   └── prometheus.yml             # Prometheus scrape config
│   │
│   └── grafana/
│       └── dashboards/
│           ├── system.json            # System metrics dashboard
│           └── crawl.json             # Crawl pipeline dashboard
│
├── scripts/
│   ├── seed_data.py                   # Seed initial categories, platforms
│   ├── generate_fake_data.py          # Generate mock data for development
│   └── backup_db.sh                   # Database backup script
│
└── docs/
    ├── setup.md                       # Setup instructions
    ├── api.md                         # API documentation
    ├── architecture.md                # Architecture decisions
    └── screenshots/                   # Demo screenshots for README
        ├── dashboard.png
        ├── product-detail.png
        └── price-chart.png
```

## Notes cho Claude Code

Khi implement, tuân thủ thứ tự:
1. Tạo folder structure trước (mkdir -p)
2. Setup Docker Compose + DB trước
3. Backend models → migrations → API
4. Crawler cơ bản → test với 1 sàn
5. Frontend pages từng trang
6. ML module cuối cùng
7. Monitoring & polish
