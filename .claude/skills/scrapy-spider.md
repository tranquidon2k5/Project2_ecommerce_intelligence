---
name: Scrapy Spider
description: How to create a new Scrapy spider for a new e-commerce platform
---

# Scrapy Spider Skill

## When to Use
When you need to crawl products from a new e-commerce platform.

## Steps

### 1. Create Spider

File: `crawler/shopsmart_crawler/spiders/<platform>_spider.py`

```python
import scrapy
from shopsmart_crawler.items import ProductItem, ReviewItem
from shopsmart_crawler.spiders.base_spider import BaseSpider


class NewPlatformSpider(BaseSpider):
    name = "newplatform"
    allowed_domains = ["newplatform.vn"]

    # API endpoint (preferred over HTML scraping)
    API_BASE = "https://newplatform.vn/api/v2/products"

    def __init__(self, category=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category

    def start_requests(self):
        url = f"{self.API_BASE}?category={self.category}&limit=40&page=1"
        yield scrapy.Request(url, callback=self.parse_listing, meta={"page": 1})

    def parse_listing(self, response):
        data = response.json()
        products = data.get("data", [])

        for product in products:
            item = ProductItem()
            item["external_id"] = str(product["id"])
            item["platform"] = "newplatform"
            item["name"] = product["name"]
            item["url"] = f"https://newplatform.vn/product/{product['id']}"
            item["image_url"] = product.get("thumbnail_url")
            item["current_price"] = int(product["price"])  # VND as integer
            item["original_price"] = int(product.get("original_price", product["price"]))
            item["discount_percent"] = product.get("discount_rate", 0)
            item["rating_avg"] = product.get("rating_average", 0)
            item["rating_count"] = product.get("review_count", 0)
            item["total_sold"] = product.get("quantity_sold", {}).get("value", 0)
            item["seller_name"] = product.get("seller", {}).get("name")
            item["category"] = self.category
            yield item

        # Pagination
        page = response.meta["page"]
        if products:  # more pages available
            next_page = page + 1
            url = f"{self.API_BASE}?category={self.category}&limit=40&page={next_page}"
            yield scrapy.Request(url, callback=self.parse_listing, meta={"page": next_page})
```

### 2. If JS Rendering Needed (SPA)

Use Playwright helper for platforms that block API access:

```python
from shopsmart_crawler.utils.playwright_helper import PlaywrightHelper

class SPAPlatformSpider(BaseSpider):
    name = "spa_platform"

    async def parse(self, response):
        helper = PlaywrightHelper()
        page_content = await helper.get_page_content(response.url)
        # Parse HTML with scrapy Selector
        sel = scrapy.Selector(text=page_content)
        for product_el in sel.css(".product-card"):
            item = ProductItem()
            item["name"] = product_el.css(".product-name::text").get()
            # ... extract other fields
            yield item
```

### 3. Add Review Crawling (Optional)

```python
def parse_reviews(self, response):
    data = response.json()
    for review in data.get("data", []):
        item = ReviewItem()
        item["product_external_id"] = response.meta["product_id"]
        item["platform"] = "newplatform"
        item["author"] = review.get("name", "Anonymous")
        item["rating"] = review.get("rating")
        item["content"] = review.get("content", "")
        item["date"] = review.get("created_at")
        yield item
```

### 4. Update Settings (if needed)

File: `crawler/shopsmart_crawler/settings.py`

```python
SPIDER_MODULES = ["shopsmart_crawler.spiders"]
# Add custom settings per spider if needed in the spider class:
# custom_settings = {"DOWNLOAD_DELAY": 3}
```

## Anti-Bot Checklist

- [ ] Set `DOWNLOAD_DELAY = 2` minimum (or `custom_settings`)
- [ ] Use `RandomUserAgentMiddleware` (already in middlewares.py)
- [ ] Prefer API endpoints over HTML scraping
- [ ] Add proper headers (`Accept`, `Referer`, `Accept-Language`)
- [ ] Implement exponential backoff on errors
- [ ] Circuit breaker: pause spider on >20% error rate
- [ ] Store raw JSON/HTML for re-parsing if selectors change

## Data Pipeline Flow

```
Spider yields ProductItem
  → CleaningPipeline (validate, normalize price VND, clean text)
  → PostgresPipeline (upsert products, insert price_history, batch 1000 rows)
  → CrawlLog recorded in crawl_logs table
```

## Run & Test

```bash
# Crawl a specific category
scrapy crawl newplatform -a category=dien-thoai

# Dry run (no DB save, just log items)
scrapy crawl newplatform -a category=dien-thoai -s LOG_LEVEL=INFO -o output.json

# Limit items for testing
scrapy crawl newplatform -a category=dien-thoai -s CLOSESPIDER_ITEMCOUNT=50
```

## Verify

1. Check PostgreSQL: `SELECT COUNT(*) FROM products WHERE platform_id = (SELECT id FROM platforms WHERE name = 'newplatform');`
2. Check price_history records were created
3. Check crawl_logs for the new spider run
