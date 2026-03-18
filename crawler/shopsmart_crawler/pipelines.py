import logging
import os
from datetime import datetime
from typing import Optional

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

logger = logging.getLogger(__name__)


class CleaningPipeline:
    """Validate and clean scraped data."""

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Require name
        if not adapter.get("name") or not adapter.get("name").strip():
            raise DropItem(f"Missing name: {item}")

        # Require price
        price = adapter.get("price")
        if price is None or price <= 0:
            raise DropItem(f"Invalid price for {adapter.get('name')}: {price}")

        # Require external_id
        if not adapter.get("external_id"):
            raise DropItem(f"Missing external_id for {adapter.get('name')}")

        # Clean name
        adapter["name"] = adapter["name"].strip()[:500]

        # Ensure integer prices
        adapter["price"] = int(adapter["price"])
        if adapter.get("original_price"):
            adapter["original_price"] = int(adapter["original_price"])

        # Clamp discount
        if adapter.get("discount_percent"):
            adapter["discount_percent"] = max(0, min(100, float(adapter["discount_percent"])))

        # Clamp rating
        if adapter.get("rating"):
            adapter["rating"] = max(0, min(5, float(adapter["rating"])))

        return item


class PostgresPipeline:
    """Save products and price history to PostgreSQL."""

    def __init__(self):
        self.conn = None
        self.cursor = None
        self.items_buffer = []
        self.batch_size = 100
        self.platform_cache = {}
        self.category_cache = {}

    def open_spider(self, spider):
        import psycopg2
        from dotenv import load_dotenv

        load_dotenv()

        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://shopsmart:shopsmart123@localhost:5432/shopsmart_db"
        )

        # Convert asyncpg URL to psycopg2
        db_url = database_url.replace("postgresql+asyncpg://", "postgresql://")

        try:
            self.conn = psycopg2.connect(db_url)
            self.conn.autocommit = False
            self.cursor = self.conn.cursor()
            logger.info("Connected to PostgreSQL")
            self._load_platform_cache()
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def _load_platform_cache(self):
        """Load platform IDs into memory."""
        self.cursor.execute("SELECT id, name FROM platforms")
        for row in self.cursor.fetchall():
            self.platform_cache[row[1]] = row[0]
        logger.info(f"Loaded {len(self.platform_cache)} platforms: {list(self.platform_cache.keys())}")

    def _get_or_create_category(self, category_slug: str, category_name: Optional[str] = None) -> Optional[int]:
        """Get category ID, creating if not exists."""
        if category_slug in self.category_cache:
            return self.category_cache[category_slug]

        self.cursor.execute("SELECT id FROM categories WHERE slug = %s", (category_slug,))
        row = self.cursor.fetchone()

        if row:
            self.category_cache[category_slug] = row[0]
            return row[0]

        # Create new category
        name = category_name or category_slug.replace("-", " ").title()
        try:
            self.cursor.execute(
                "INSERT INTO categories (name, slug, created_at) VALUES (%s, %s, %s) RETURNING id",
                (name, category_slug, datetime.utcnow())
            )
            cat_id = self.cursor.fetchone()[0]
            self.conn.commit()
            self.category_cache[category_slug] = cat_id
            return cat_id
        except Exception as e:
            self.conn.rollback()
            logger.warning(f"Failed to create category {category_slug}: {e}")
            return None

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        if "price" not in adapter:
            return item

        self.items_buffer.append(dict(adapter))

        if len(self.items_buffer) >= self.batch_size:
            self._flush_buffer()

        return item

    def _flush_buffer(self):
        """Batch upsert buffered items."""
        if not self.items_buffer:
            return

        saved = 0
        for item in self.items_buffer:
            try:
                self._save_product(item)
                saved += 1
            except Exception as e:
                logger.error(f"Failed to save product {item.get('name', '?')}: {e}")
                self.conn.rollback()

        try:
            self.conn.commit()
        except Exception as e:
            logger.error(f"Commit failed: {e}")
            self.conn.rollback()

        logger.info(f"Flushed {saved}/{len(self.items_buffer)} items to DB")
        self.items_buffer = []

    def _save_product(self, item: dict):
        """Upsert a product and insert price_history."""

        platform_name = item.get("platform", "tiki")
        platform_id = self.platform_cache.get(platform_name)

        if not platform_id:
            logger.warning(f"Unknown platform: {platform_name}")
            return

        category_id = None
        if item.get("category"):
            category_id = self._get_or_create_category(item["category"])

        now = datetime.utcnow()

        # Upsert product
        self.cursor.execute("""
            INSERT INTO products (
                platform_id, category_id, external_id, name, url, image_url,
                seller_name, seller_rating, current_price, original_price,
                discount_percent, rating_avg, rating_count, total_sold,
                is_official_store, is_active, first_seen_at, last_crawled_at,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, TRUE, %s, %s, %s, %s
            )
            ON CONFLICT (platform_id, external_id) DO UPDATE SET
                name = EXCLUDED.name,
                current_price = EXCLUDED.current_price,
                original_price = EXCLUDED.original_price,
                discount_percent = EXCLUDED.discount_percent,
                rating_avg = EXCLUDED.rating_avg,
                rating_count = EXCLUDED.rating_count,
                total_sold = EXCLUDED.total_sold,
                last_crawled_at = EXCLUDED.last_crawled_at,
                updated_at = EXCLUDED.updated_at
            RETURNING id
        """, (
            platform_id,
            category_id,
            item["external_id"],
            item["name"][:500],
            item.get("url", ""),
            item.get("image_url"),
            item.get("seller_name"),
            item.get("seller_rating"),
            item["price"],
            item.get("original_price"),
            item.get("discount_percent"),
            item.get("rating"),
            item.get("review_count", 0),
            item.get("sold_count", 0),
            item.get("is_official_store", False),
            now,
            now,
            now,
            now,
        ))

        product_id = self.cursor.fetchone()[0]

        # Insert price history
        self.cursor.execute("""
            INSERT INTO price_history (
                product_id, price, original_price, discount_percent,
                in_stock, crawled_at, created_at
            ) VALUES (%s, %s, %s, %s, TRUE, %s, %s)
        """, (
            product_id,
            item["price"],
            item.get("original_price"),
            item.get("discount_percent"),
            now,
            now,
        ))

    def close_spider(self, spider):
        """Flush remaining items and close connection."""
        if self.items_buffer:
            self._flush_buffer()

        if self.conn:
            try:
                self.conn.commit()
                self.conn.close()
            except Exception:
                pass

        logger.info(f"Spider closed. Total items processed: {spider.items_scraped}")
