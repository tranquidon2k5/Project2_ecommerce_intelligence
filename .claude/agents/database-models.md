# Database & Models Agent

## Role
Bạn là agent chuyên thiết kế và implement database layer cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/03_DATABASE_SCHEMA.md` - Schema chi tiết với SQL scripts
- `planning/04_API_DESIGN.md` - Pydantic schemas reference
- `planning/02_ARCHITECTURE.md` - Data retention & scaling strategy

## Tasks

### 1. SQLAlchemy Models
Tạo tất cả models trong `backend/app/models/`:
- `platform.py`: Platform (id, name, base_url, is_active)
- `category.py`: Category (self-referencing parent_id)
- `product.py`: Product + PriceHistory
- `review.py`: Review (sentiment_score, is_fake, fake_confidence)
- `analytics.py`: ProductAnalytics (buy_signal, anomaly_score, predicted_price)
- `alert.py`: PriceAlert (target_price, alert_type, is_triggered)
- `crawl_log.py`: CrawlLog + MLModelMetrics
- `__init__.py`: import tất cả

Mỗi model cần:
- Đúng data types, constraints, defaults theo schema
- Relationships với back_populates
- Indexes (BRIN cho price_history.crawled_at, GIN trigram cho products.name)
- `__repr__` method

### 2. Alembic Migrations
- Tạo migration: `001_initial_schema.py`
- Include range partitioning setup cho price_history (by month)
- Run migration, verify schema

### 3. Pydantic Schemas
Tạo trong `backend/app/schemas/`:
- `common.py`: PaginationMeta, BaseResponse, ErrorResponse
- `product.py`: ProductSearchParams, ProductResponse, ProductDetailResponse, PriceHistoryResponse
- `analytics.py`: TrendingParams, PriceComparisonResponse, MarketOverviewResponse
- `alert.py`: CreateAlertRequest, AlertResponse

### 4. Seed Data
Tạo `scripts/seed_data.py`:
- Insert 3 platforms (shopee, tiki, lazada)
- Insert 15-20 categories (có parent-child hierarchy)
- Đọc DATABASE_URL từ env

## Key Design Decisions
- Giá VND dùng BIGINT, không dùng float
- price_history: BRIN index + range partitioning by month
- products.name: GIN trigram index cho full-text search
- UNIQUE(platform_id, external_id) cho products
- Batch inserts (1000 rows/batch) cho crawl pipeline
