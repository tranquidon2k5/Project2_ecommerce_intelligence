import scrapy
from datetime import datetime


class BaseSpider(scrapy.Spider):
    """Base spider with common functionality."""

    custom_settings = {
        "DOWNLOAD_DELAY": 2,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.items_scraped = 0
        self.started_at = datetime.utcnow()

    def log_progress(self):
        elapsed = (datetime.utcnow() - self.started_at).seconds
        self.logger.info(
            f"Progress: {self.items_scraped} items in {elapsed}s "
            f"({self.items_scraped / max(1, elapsed):.1f} items/s)"
        )
