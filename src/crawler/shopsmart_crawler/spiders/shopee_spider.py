import json
import scrapy
from scrapy_playwright.page import PageMethod


class ShopeeSpider(scrapy.Spider):
    name = "shopee"
    allowed_domains = ["shopee.vn"]

    # Shopee search API - more stable than HTML parsing
    SHOPEE_SEARCH_API = "https://shopee.vn/api/v4/search/search_items"

    custom_settings = {
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "args": ["--no-sandbox", "--disable-dev-shm-usage"],
        },
        "DOWNLOAD_HANDLERS": {
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "CONCURRENT_REQUESTS": 4,
        "AUTOTHROTTLE_ENABLED": True,
    }

    # Category keywords to search
    SEARCH_KEYWORDS = [
        "điện thoại samsung",
        "iphone",
        "laptop asus",
        "tai nghe bluetooth",
        "đồng hồ thông minh",
        "máy tính bảng",
        "loa bluetooth",
        "bàn phím cơ",
    ]

    def start_requests(self):
        for keyword in self.SEARCH_KEYWORDS:
            # Use Shopee API endpoint directly
            params = {
                "by": "relevancy",
                "keyword": keyword,
                "limit": 60,
                "newest": 0,
                "order": "desc",
                "page_type": "search",
            }
            url = f"{self.SHOPEE_SEARCH_API}?" + "&".join(f"{k}={v}" for k, v in params.items())
            yield scrapy.Request(
                url=url,
                callback=self.parse_search,
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "playwright_page_methods": [
                        PageMethod("wait_for_load_state", "networkidle"),
                    ],
                    "keyword": keyword,
                    "errback": self.errback,
                },
                headers={
                    "Accept": "application/json",
                    "X-API-SOURCE": "pc",
                    "Referer": "https://shopee.vn/",
                },
            )

    async def parse_search(self, response):
        page = response.meta.get("playwright_page")
        if page:
            await page.close()

        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.warning(f"Failed to parse JSON from Shopee API: {response.url}")
            return

        items = data.get("items", []) or []

        for item in items:
            item_info = item.get("item_basic", {})
            if not item_info:
                continue

            shopid = item_info.get("shopid")
            itemid = item_info.get("itemid")
            if not shopid or not itemid:
                continue

            # Extract pricing (Shopee returns price * 100000)
            price_raw = item_info.get("price", 0)
            price_min_raw = item_info.get("price_min", 0)
            current_price = int(price_raw / 100000) if price_raw else int(price_min_raw / 100000)

            price_before_raw = item_info.get("price_before_discount", 0)
            original_price = int(price_before_raw / 100000) if price_before_raw else None

            discount = item_info.get("discount", None)
            discount_percent = float(str(discount).replace("%", "")) if discount else None

            images = item_info.get("images", [])
            image_id = images[0] if images else None
            image_url = f"https://cf.shopee.vn/file/{image_id}" if image_id else None

            product_url = f"https://shopee.vn/-i.{shopid}.{itemid}"

            yield {
                "platform": "shopee",
                "external_id": f"{shopid}_{itemid}",
                "name": item_info.get("name", ""),
                "url": product_url,
                "image_url": image_url,
                "current_price": current_price,
                "original_price": original_price,
                "discount_percent": discount_percent,
                "rating_avg": item_info.get("item_rating", {}).get("rating_star", None),
                "rating_count": item_info.get("item_rating", {}).get("rating_count", [0])[0] if item_info.get("item_rating") else 0,
                "total_sold": item_info.get("sold", 0),
                "seller_name": item_info.get("shop_name", None),
                "is_official_store": item_info.get("is_official_shop", False),
                "category_name": response.meta.get("keyword", ""),
            }

    def errback(self, failure):
        self.logger.error(f"Shopee request failed: {failure}")
