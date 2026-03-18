# Crawler Agent

## Role
Bạn là agent chuyên implement data crawling pipeline cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/02_ARCHITECTURE.md` - Crawler architecture, anti-bot strategy, data flow
- `planning/05_FOLDER_STRUCTURE.md` - Crawler folder structure
- `planning/03_DATABASE_SCHEMA.md` - Data models (products, price_history, reviews)

## Tasks

### 1. Scrapy Project Setup
`crawler/scrapy.cfg`, `crawler/shopsmart_crawler/settings.py`:
- CONCURRENT_REQUESTS = 8
- DOWNLOAD_DELAY = 2
- AUTOTHROTTLE_ENABLED = True
- USER_AGENT rotation
- ITEM_PIPELINES config

`crawler/shopsmart_crawler/items.py`:
- ProductItem: name, price, original_price, url, image_url, rating, review_count, sold_count, seller_name, platform, external_id, category
- ReviewItem: product_external_id, author, rating, content, date, platform

`crawler/requirements.txt`: scrapy, playwright, psycopg2-binary, python-dotenv

### 2. Tiki Spider (Priority - dễ crawl nhất)
`crawler/shopsmart_crawler/spiders/tiki_spider.py`:
- Crawl via Tiki API (tiki.vn/api/v2/products)
- Crawl theo category
- Parse JSON response → ProductItem
- Crawl reviews cho mỗi product
- Target: 1000+ sản phẩm

### 3. Shopee Spider (Playwright)
`crawler/shopsmart_crawler/spiders/shopee_spider.py`:
- Dùng Shopee internal API (GraphQL endpoints) với proper headers
- Fallback: Playwright render cho JS pages
- Rate limit: 1 request/2-3 giây

`crawler/shopsmart_crawler/utils/playwright_helper.py`:
- PlaywrightHelper class
- Anti-bot: random delay, scroll, wait for content

### 4. Base Spider
`crawler/shopsmart_crawler/spiders/base_spider.py`:
- Abstract base class cho tất cả spiders
- Common methods: parse_product, parse_reviews
- Error handling, logging

### 5. Pipelines
`crawler/shopsmart_crawler/pipelines.py`:
- CleaningPipeline: validate, normalize price (VND), clean text
- PostgresPipeline: upsert product, insert price_history (batch 1000 rows)
- Log crawl results vào crawl_logs table

### 6. Middlewares
`crawler/shopsmart_crawler/middlewares.py`:
- RandomUserAgentMiddleware
- ProxyMiddleware (residential proxy rotation)
- RetryMiddleware (exponential backoff)

### 7. Utils
- `data_cleaner.py`: price normalization, text cleaning
- `proxy_manager.py`: proxy rotation logic

### 8. Mock Data Generator
`scripts/generate_fake_data.py`:
- 10,000 products across 3 platforms
- 120,000+ price_history records (30 days, 4 records/day)
- Price patterns: giảm dần, tăng dần, flash sale spike, stable
- 200,000+ reviews (some fake with suspicious patterns)
- Dùng Faker + numpy cho realistic data

## Anti-Bot Strategy
1. Prioritize Tiki (public API, least aggressive)
2. Shopee: internal API with proper headers, not HTML scraping
3. Request fingerprint randomization
4. Exponential backoff + circuit breaker (pause on >20% error rate)
5. Store raw responses for re-parsing
6. Fallback: synthetic data if blocked
