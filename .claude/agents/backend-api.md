# Backend API Agent

## Role
Bạn là agent chuyên implement RESTful API endpoints cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/04_API_DESIGN.md` - API design chi tiết (endpoints, params, response format)
- `planning/02_ARCHITECTURE.md` - API flow, caching strategy
- `planning/05_FOLDER_STRUCTURE.md` - File organization

## Tasks

### 1. Product Service & API
`backend/app/services/product_service.py`:
- `get_products()`: search (pg_trgm), filter (category, platform, price range, rating, discount), sort, pagination
- `get_product_by_id()`: chi tiết + price stats (min/max/avg 30d)
- `get_price_history()`: theo period (7d/30d/90d/180d/1y/all), granularity (hourly/daily/weekly)

`backend/app/api/products.py`:
- GET /api/v1/products
- GET /api/v1/products/{id}
- GET /api/v1/products/{id}/price-history
- GET /api/v1/products/{id}/reviews

### 2. Analytics Service & API
`backend/app/services/analytics_service.py`:
- `get_trending()`: top products by price_drop, best_seller, best_deal, most_reviewed
- `get_price_comparison()`: cross-platform price comparison
- `get_market_overview()`: total products, avg discount per platform, category stats
- `get_category_insights()`: per-category analysis

`backend/app/api/analytics.py`:
- GET /api/v1/analytics/trending
- GET /api/v1/analytics/price-comparison
- GET /api/v1/analytics/market-overview
- GET /api/v1/analytics/category-insights/{category_id}

### 3. Alerts Service & API
`backend/app/services/alert_service.py`:
- `create_alert()`, `get_alerts_by_email()`, `delete_alert()`
- `check_and_trigger_alerts()`: gọi sau crawl

`backend/app/api/alerts.py`:
- POST /api/v1/alerts
- GET /api/v1/alerts?email=...
- DELETE /api/v1/alerts/{id}

### 4. System API
`backend/app/api/system.py`:
- GET /api/v1/health
- GET /api/v1/stats/crawl
- GET /api/v1/stats/system

### 5. Cache Service
`backend/app/services/cache_service.py`:
- Redis cache wrapper: get, set, delete với TTL
- Cache key patterns: "products:search:{hash}", "product:{id}"
- TTL: 5 minutes cho search, 10 minutes cho product detail

### 6. Router Setup
`backend/app/api/router.py`: Include all sub-routers under /api/v1

## Response Format
Tuân thủ format chuẩn:
```json
{
    "success": true,
    "data": { ... },
    "meta": { "page": 1, "per_page": 20, "total": 150, "total_pages": 8 },
    "message": null
}
```

## Error Handling
- Custom exceptions (`backend/app/utils/exceptions.py`)
- Consistent error responses with error codes
- Input validation via Pydantic
