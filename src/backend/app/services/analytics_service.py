import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select, desc, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import Product, PriceHistory
from ..models.platform import Platform
from ..models.category import Category
from ..models.analytics import ProductAnalytics
from ..models.crawl_log import CrawlLog

logger = logging.getLogger(__name__)


async def get_trending(
    db: AsyncSession,
    trend_type: str = "price_drop",
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    """Get trending products by type."""

    query = (
        select(Product, Platform.name.label("platform_name"), Category.name.label("category_name"))
        .join(Platform, Product.platform_id == Platform.id)
        .outerjoin(Category, Product.category_id == Category.id)
        .where(Product.is_active == True)
    )

    if category_id:
        query = query.where(Product.category_id == category_id)

    if platform:
        query = query.where(Platform.name == platform)

    if trend_type == "price_drop":
        query = query.where(Product.discount_percent > 0).order_by(desc(Product.discount_percent))
    elif trend_type == "best_seller":
        query = query.order_by(desc(Product.total_sold))
    elif trend_type == "best_deal":
        # Best deal: high discount + high rating
        query = query.where(
            Product.discount_percent > 10,
            Product.rating_avg >= 4.0
        ).order_by(desc(Product.discount_percent))
    elif trend_type == "most_reviewed":
        query = query.order_by(desc(Product.rating_count))

    query = query.limit(limit)
    result = await db.execute(query)
    rows = result.all()

    return [
        {
            "id": row[0].id,
            "name": row[0].name,
            "platform": row[1],
            "category": row[2],
            "url": row[0].url,
            "image_url": row[0].image_url,
            "current_price": row[0].current_price,
            "original_price": row[0].original_price,
            "discount_percent": float(row[0].discount_percent) if row[0].discount_percent else None,
            "rating_avg": float(row[0].rating_avg) if row[0].rating_avg else None,
            "rating_count": row[0].rating_count,
            "total_sold": row[0].total_sold,
            "seller_name": row[0].seller_name,
            "is_official_store": row[0].is_official_store,
            "last_crawled_at": row[0].last_crawled_at,
        }
        for row in rows
    ]


async def get_price_comparison(
    db: AsyncSession,
    q: str,
    category_id: Optional[int] = None,
) -> Dict:
    """Compare prices for a product across platforms."""

    # Search for products matching query across platforms
    search_query = (
        select(Product, Platform.name.label("platform_name"))
        .join(Platform, Product.platform_id == Platform.id)
        .where(
            Product.is_active == True,
            text("products.name ILIKE :q_like").params(q_like=f"%{q}%")
        )
    )

    if category_id:
        search_query = search_query.where(Product.category_id == category_id)

    search_query = search_query.limit(50)
    result = await db.execute(search_query)
    rows = result.all()

    # Group by similar names
    comparisons = []
    seen_names = set()

    for row in rows:
        product, platform_name = row[0], row[1]
        # Simple grouping: take first word of name as key
        name_key = product.name[:30].lower()

        if name_key not in seen_names:
            seen_names.add(name_key)

            # Find all platforms for similar product
            similar_query = (
                select(Product, Platform.name.label("platform_name"))
                .join(Platform, Product.platform_id == Platform.id)
                .where(
                    Product.is_active == True,
                    text("products.name ILIKE :name_like").params(name_like=f"%{product.name[:20]}%")
                )
                .limit(10)
            )

            similar_result = await db.execute(similar_query)
            similar_rows = similar_result.all()

            platforms = []
            for sr in similar_rows:
                platforms.append({
                    "platform": sr[1],
                    "price": sr[0].current_price,
                    "rating": float(sr[0].rating_avg) if sr[0].rating_avg else None,
                    "url": sr[0].url,
                })

            if len(platforms) > 1:
                best = min(platforms, key=lambda x: x["price"])
                max_price = max(p["price"] for p in platforms)
                min_price = min(p["price"] for p in platforms)
                price_diff = ((max_price - min_price) / min_price * 100) if min_price else 0

                comparisons.append({
                    "product_name": product.name,
                    "platforms": platforms,
                    "best_price": best,
                    "price_diff_percent": round(price_diff, 2),
                })

    return {"query": q, "comparisons": comparisons[:10]}


async def get_market_overview(db: AsyncSession) -> Dict:
    """Get market overview statistics."""

    # Total products
    total_products = await db.execute(
        select(func.count(Product.id)).where(Product.is_active == True)
    )
    total_products_count = total_products.scalar() or 0

    # Total price points
    total_price_points = await db.execute(select(func.count(PriceHistory.id)))
    total_price_count = total_price_points.scalar() or 0

    # Per platform stats
    platform_stats_query = (
        select(
            Platform.name,
            func.count(Product.id).label("product_count"),
            func.avg(Product.discount_percent).label("avg_discount"),
        )
        .join(Product, Platform.id == Product.platform_id)
        .where(Product.is_active == True)
        .group_by(Platform.name)
    )

    platform_result = await db.execute(platform_stats_query)
    platform_rows = platform_result.all()

    platforms = {}
    for row in platform_rows:
        platforms[row[0]] = {
            "products": row[1],
            "avg_discount": round(float(row[2]), 2) if row[2] else 0.0,
        }

    # Top categories by discount
    cat_discount_query = (
        select(
            Category.name,
            func.avg(Product.discount_percent).label("avg_discount"),
            func.count(Product.id).label("product_count"),
        )
        .join(Product, Category.id == Product.category_id)
        .where(Product.is_active == True, Product.discount_percent > 0)
        .group_by(Category.name)
        .order_by(desc(func.avg(Product.discount_percent)))
        .limit(5)
    )

    cat_result = await db.execute(cat_discount_query)
    cat_rows = cat_result.all()

    top_categories = [
        {"name": row[0], "avg_discount": round(float(row[1]), 2), "product_count": row[2]}
        for row in cat_rows
    ]

    return {
        "total_products_tracked": total_products_count,
        "total_price_points": total_price_count,
        "platforms": platforms,
        "top_categories_by_discount": top_categories,
        "last_updated": datetime.utcnow().isoformat(),
    }


async def get_category_insights(db: AsyncSession, category_id: int) -> Optional[Dict]:
    """Get insights for a specific category."""

    cat_result = await db.execute(select(Category).where(Category.id == category_id))
    category = cat_result.scalar_one_or_none()
    if not category:
        return None

    # Product stats in category
    stats_query = (
        select(
            func.count(Product.id).label("total"),
            func.avg(Product.current_price).label("avg_price"),
            func.min(Product.current_price).label("min_price"),
            func.max(Product.current_price).label("max_price"),
            func.avg(Product.discount_percent).label("avg_discount"),
        )
        .where(Product.category_id == category_id, Product.is_active == True)
    )

    stats_result = await db.execute(stats_query)
    stats = stats_result.first()

    # By platform
    platform_query = (
        select(
            Platform.name,
            func.count(Product.id).label("count"),
            func.avg(Product.current_price).label("avg_price"),
        )
        .join(Product, Platform.id == Product.platform_id)
        .where(Product.category_id == category_id, Product.is_active == True)
        .group_by(Platform.name)
    )

    platform_result = await db.execute(platform_query)
    platform_rows = platform_result.all()

    return {
        "category_id": category_id,
        "category_name": category.name,
        "total_products": stats.total or 0,
        "avg_price": int(stats.avg_price) if stats.avg_price else None,
        "min_price": stats.min_price,
        "max_price": stats.max_price,
        "avg_discount": round(float(stats.avg_discount), 2) if stats.avg_discount else None,
        "top_platforms": [
            {"platform": row[0], "count": row[1], "avg_price": int(row[2]) if row[2] else None}
            for row in platform_rows
        ],
    }
