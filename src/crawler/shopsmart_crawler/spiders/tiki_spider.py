import json
import scrapy
from ..items import ProductItem, ReviewItem
from .base_spider import BaseSpider


# Tiki category IDs for common categories
TIKI_CATEGORIES = {
    "dien-thoai": 1795,
    "laptop": 1846,
    "thoi-trang-nu": 931,
    "thoi-trang-nam": 915,
    "gia-dung": 1882,
    "my-pham": 44792,
    "sach": 8322,
    "the-thao": 1975,
    "thuc-pham": 4384,
}


class TikiSpider(BaseSpider):
    name = "tiki"
    allowed_domains = ["tiki.vn"]

    # Tiki product listing API
    BASE_API = "https://tiki.vn/api/personalish/v1/blocks/listings"
    PRODUCT_API = "https://tiki.vn/api/v2/products/{product_id}"
    REVIEW_API = "https://tiki.vn/api/v2/reviews"

    custom_settings = {
        **BaseSpider.custom_settings,
        "DOWNLOAD_DELAY": 2,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "application/json",
            "Accept-Language": "vi-VN,vi;q=0.9",
            "Referer": "https://tiki.vn/",
        }
    }

    def __init__(self, category="dien-thoai", max_pages=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.category = category
        self.category_id = TIKI_CATEGORIES.get(category, 1795)
        self.max_pages = int(max_pages)
        self.current_page = 1

    def start_requests(self):
        self.logger.info(f"Starting Tiki crawl: category={self.category}, max_pages={self.max_pages}")
        url = self._build_listing_url(page=1)
        yield scrapy.Request(
            url,
            callback=self.parse_listing,
            errback=self.handle_error,
            meta={"page": 1},
        )

    def _build_listing_url(self, page: int) -> str:
        return (
            f"{self.BASE_API}"
            f"?limit=40"
            f"&include=advertisement"
            f"&aggregations=2"
            f"&version=home-persionalized"
            f"&trackity_id=tiki-spider"
            f"&category={self.category_id}"
            f"&page={page}"
            f"&urlKey={self.category}"
        )

    def parse_listing(self, response):
        try:
            data = response.json()
        except Exception as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            return

        products = data.get("data", [])
        if not products:
            self.logger.info("No more products found, stopping")
            return

        self.logger.info(f"Page {response.meta['page']}: found {len(products)} products")

        for product_data in products:
            yield self._parse_product(product_data)
            self.items_scraped += 1

        if self.items_scraped % 100 == 0:
            self.log_progress()

        # Next page
        current_page = response.meta["page"]
        if current_page < self.max_pages and len(products) > 0:
            next_page = current_page + 1
            yield scrapy.Request(
                self._build_listing_url(next_page),
                callback=self.parse_listing,
                errback=self.handle_error,
                meta={"page": next_page},
            )

    def _parse_product(self, product_data: dict) -> ProductItem:
        """Parse product data from Tiki API response."""

        price = product_data.get("price", 0)
        original_price = product_data.get("list_price", price)

        discount_percent = None
        if original_price and original_price > price and price > 0:
            discount_percent = round((original_price - price) / original_price * 100, 2)

        return ProductItem(
            name=product_data.get("name", ""),
            price=int(price) if price else 0,
            original_price=int(original_price) if original_price else None,
            url=f"https://tiki.vn/{product_data.get('url_key', '')}-p{product_data.get('id', '')}.html",
            image_url=product_data.get("thumbnail_url", ""),
            rating=product_data.get("rating_average", None),
            review_count=product_data.get("review_count", 0),
            sold_count=product_data.get("all_time_quantity_sold", 0),
            seller_name=product_data.get("seller", {}).get("name", "") if isinstance(product_data.get("seller"), dict) else "",
            seller_rating=None,
            is_official_store=product_data.get("is_authentic", False),
            platform="tiki",
            external_id=str(product_data.get("id", "")),
            category=self.category,
            category_id=self.category_id,
            discount_percent=discount_percent,
        )

    def handle_error(self, failure):
        self.logger.error(f"Request failed: {failure.value}")
