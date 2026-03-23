import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, select, text, and_, or_, desc, asc, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.product import Product, PriceHistory
from ..models.platform import Platform
from ..models.category import Category
from ..models.review import Review
from ..models.analytics import ProductAnalytics
from ..config import settings

logger = logging.getLogger(__name__)


def _make_search_key(params: dict) -> str:
    key_str = json.dumps(params, sort_keys=True, default=str)
    return f"products:search:{hashlib.md5(key_str.encode()).hexdigest()}"


async def get_products(
    db: AsyncSession,
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    platform: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    min_rating: Optional[float] = None,
    min_discount: Optional[float] = None,
    sort_by: str = "relevance",
    page: int = 1,
    per_page: int = 20,
) -> Tuple[List[Dict], int]:
    """Get paginated products with search/filter/sort."""

    # Build base query
    query = (
        select(Product, Platform.name.label("platform_name"), Category.name.label("category_name"))
        .join(Platform, Product.platform_id == Platform.id)
        .outerjoin(Category, Product.category_id == Category.id)
        .where(Product.is_active == True)
    )

    # Apply filters
    if q:
        # Use pg_trgm similarity search
        query = query.where(
            text("products.name % :q OR products.name ILIKE :q_like")
        ).params(q=q, q_like=f"%{q}%")

    if category_id:
        query = query.where(Product.category_id == category_id)

    if platform:
        query = query.where(Platform.name == platform)

    if min_price is not None:
        query = query.where(Product.current_price >= min_price)

    if max_price is not None:
        query = query.where(Product.current_price <= max_price)

    if min_rating is not None:
        query = query.where(Product.rating_avg >= min_rating)

    if min_discount is not None:
        query = query.where(Product.discount_percent >= min_discount)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    if sort_by == "price_asc":
        query = query.order_by(asc(Product.current_price))
    elif sort_by == "price_desc":
        query = query.order_by(desc(Product.current_price))
    elif sort_by == "rating":
        query = query.order_by(desc(Product.rating_avg))
    elif sort_by == "discount":
        query = query.order_by(desc(Product.discount_percent))
    elif sort_by == "popular":
        query = query.order_by(desc(Product.total_sold))
    else:  # relevance
        if q:
            query = query.order_by(
                desc(text("similarity(products.name, :q)").bindparams(q=q))
            )
        else:
            query = query.order_by(desc(Product.last_crawled_at))

    # Pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)
    rows = result.all()

    products = []
    for row in rows:
        product = row[0]
        platform_name = row[1]
        category_name = row[2]

        products.append({
            "id": product.id,
            "name": product.name,
            "platform": platform_name,
            "category": category_name,
            "url": product.url,
            "image_url": product.image_url,
            "current_price": product.current_price,
            "original_price": product.original_price,
            "discount_percent": float(product.discount_percent) if product.discount_percent else None,
            "rating_avg": float(product.rating_avg) if product.rating_avg else None,
            "rating_count": product.rating_count,
            "total_sold": product.total_sold,
            "seller_name": product.seller_name,
            "is_official_store": product.is_official_store,
            "ai_insights": None,  # Will be populated by AI service
            "last_crawled_at": product.last_crawled_at,
        })

    return products, total


async def get_product_by_id(db: AsyncSession, product_id: int) -> Optional[Dict]:
    """Get product detail with price stats."""

    query = (
        select(Product, Platform.name.label("platform_name"))
        .join(Platform, Product.platform_id == Platform.id)
        .where(Product.id == product_id, Product.is_active == True)
    )

    result = await db.execute(query)
    row = result.first()

    if not row:
        return None

    product, platform_name = row[0], row[1]

    # Get category
    category_data = None
    if product.category_id:
        cat_result = await db.execute(
            select(Category).where(Category.id == product.category_id)
        )
        category = cat_result.scalar_one_or_none()
        if category:
            category_data = {"id": category.id, "name": category.name, "slug": category.slug}

    # Get price stats for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    stats_query = select(
        func.min(PriceHistory.price).label("min_price"),
        func.max(PriceHistory.price).label("max_price"),
        func.avg(PriceHistory.price).label("avg_price"),
    ).where(
        PriceHistory.product_id == product_id,
        PriceHistory.crawled_at >= thirty_days_ago,
    )

    stats_result = await db.execute(stats_query)
    stats = stats_result.first()

    price_stats = None
    if stats and stats.min_price:
        avg_30d = int(stats.avg_price)
        current_vs_avg = ((product.current_price - avg_30d) / avg_30d * 100) if avg_30d else None
        price_stats = {
            "min_30d": stats.min_price,
            "max_30d": stats.max_price,
            "avg_30d": avg_30d,
            "current_vs_avg": round(current_vs_avg, 2) if current_vs_avg is not None else None,
        }

    # Get latest analytics
    analytics_result = await db.execute(
        select(ProductAnalytics)
        .where(ProductAnalytics.product_id == product_id)
        .order_by(desc(ProductAnalytics.date))
        .limit(1)
    )
    analytics = analytics_result.scalar_one_or_none()

    ai_insights = None
    if analytics:
        ai_insights = {
            "buy_signal": analytics.buy_signal,
            "trend_direction": analytics.trend_direction,
            "predicted_price_7d": analytics.predicted_price_7d,
            "anomaly_score": float(analytics.anomaly_score) if analytics.anomaly_score else None,
        }

    return {
        "id": product.id,
        "name": product.name,
        "platform": platform_name,
        "category": category_data,
        "url": product.url,
        "image_url": product.image_url,
        "current_price": product.current_price,
        "original_price": product.original_price,
        "discount_percent": float(product.discount_percent) if product.discount_percent else None,
        "rating_avg": float(product.rating_avg) if product.rating_avg else None,
        "rating_count": product.rating_count,
        "total_sold": product.total_sold,
        "seller_name": product.seller_name,
        "seller_rating": float(product.seller_rating) if product.seller_rating else None,
        "is_official_store": product.is_official_store,
        "first_seen_at": product.first_seen_at,
        "last_crawled_at": product.last_crawled_at,
        "price_stats": price_stats,
        "ai_insights": ai_insights,
    }


async def get_price_history(
    db: AsyncSession,
    product_id: int,
    period: str = "30d",
    granularity: str = "auto",
) -> Optional[Dict]:
    """Get price history for a product."""

    # Determine time range
    period_map = {
        "7d": 7, "30d": 30, "90d": 90, "180d": 180, "1y": 365, "all": None
    }
    days = period_map.get(period, 30)

    # Get product name
    product_result = await db.execute(
        select(Product.name).where(Product.id == product_id)
    )
    product_name = product_result.scalar_one_or_none()
    if not product_name:
        return None

    # Build history query
    where_clause = [PriceHistory.product_id == product_id]
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        where_clause.append(PriceHistory.crawled_at >= cutoff)

    # Group by date and aggregate
    history_query = (
        select(
            func.date(PriceHistory.crawled_at).label("date"),
            func.min(PriceHistory.price).label("min_price"),
            func.max(PriceHistory.price).label("max_price"),
            func.avg(PriceHistory.price).label("avg_price"),
        )
        .where(*where_clause)
        .group_by(func.date(PriceHistory.crawled_at))
        .order_by(func.date(PriceHistory.crawled_at))
    )

    result = await db.execute(history_query)
    rows = result.all()

    price_points = [
        {
            "date": str(row.date),
            "min": row.min_price,
            "max": row.max_price,
            "avg": int(row.avg_price),
        }
        for row in rows
    ]

    # Calculate statistics
    all_prices = [p["avg"] for p in price_points]
    statistics = {
        "min": min(all_prices) if all_prices else 0,
        "max": max(all_prices) if all_prices else 0,
        "avg": int(sum(all_prices) / len(all_prices)) if all_prices else 0,
        "volatility": None,
        "trend": None,
        "total_data_points": len(price_points),
    }

    if len(all_prices) >= 2:
        import statistics as stats
        try:
            std = stats.stdev(all_prices)
            mean = stats.mean(all_prices)
            statistics["volatility"] = round(std / mean, 4) if mean else None
        except Exception:
            pass

        # Simple trend detection
        if all_prices[-1] < all_prices[0] * 0.97:
            statistics["trend"] = "down"
        elif all_prices[-1] > all_prices[0] * 1.03:
            statistics["trend"] = "up"
        else:
            statistics["trend"] = "stable"

    return {
        "product_id": product_id,
        "product_name": product_name,
        "period": period,
        "price_points": price_points,
        "statistics": statistics,
    }


async def get_product_reviews(
    db: AsyncSession,
    product_id: int,
    rating: Optional[int] = None,
    sort_by: str = "recent",
    show_fake: bool = False,
    page: int = 1,
    per_page: int = 20,
) -> Tuple[Dict, int]:
    """Get paginated reviews for a product."""

    # Review query
    query = select(Review).where(Review.product_id == product_id)

    if rating:
        query = query.where(Review.rating == rating)

    if not show_fake:
        query = query.where(or_(Review.is_fake == False, Review.is_fake == None))

    # Sort
    if sort_by == "helpful":
        query = query.order_by(desc(Review.likes_count))
    elif sort_by == "rating_high":
        query = query.order_by(desc(Review.rating))
    elif sort_by == "rating_low":
        query = query.order_by(asc(Review.rating))
    else:  # recent
        query = query.order_by(desc(Review.created_date))

    # Count
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    result = await db.execute(query)
    reviews = result.scalars().all()

    # Build summary using SQL aggregates
    agg_query = select(
        func.count(Review.id).label("total_reviews"),
        func.avg(Review.rating).label("avg_rating"),
        func.sum(case((Review.is_fake == True, 1), else_=0)).label("fake_count"),
        func.avg(Review.sentiment_score).label("avg_sentiment"),
    ).where(Review.product_id == product_id)
    agg_result = await db.execute(agg_query)
    agg = agg_result.one()

    total_reviews = agg.total_reviews or 0
    avg_rating = float(agg.avg_rating) if agg.avg_rating else 0.0
    fake_count = int(agg.fake_count) if agg.fake_count else 0
    fake_percent = (fake_count / total_reviews * 100) if total_reviews > 0 else 0

    # Rating distribution via GROUP BY
    rating_dist = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    dist_query = (
        select(Review.rating, func.count(Review.id))
        .where(Review.product_id == product_id)
        .where(Review.rating.isnot(None))
        .group_by(Review.rating)
    )
    dist_result = await db.execute(dist_query)
    for rating_val, cnt in dist_result.all():
        if rating_val and str(int(rating_val)) in rating_dist:
            rating_dist[str(int(rating_val))] = cnt

    # Sentiment buckets
    sentiment_total_query = select(func.count(Review.id)).where(
        Review.product_id == product_id, Review.sentiment_score.isnot(None)
    )
    sentiment_total_result = await db.execute(sentiment_total_query)
    sentiment_total = sentiment_total_result.scalar() or 0

    if sentiment_total > 0:
        pos_query = select(func.count(Review.id)).where(
            Review.product_id == product_id, Review.sentiment_score > 0.1
        )
        neg_query = select(func.count(Review.id)).where(
            Review.product_id == product_id, Review.sentiment_score < -0.1
        )
        pos_result = await db.execute(pos_query)
        neg_result = await db.execute(neg_query)
        pos = (pos_result.scalar() or 0) / sentiment_total * 100
        neg = (neg_result.scalar() or 0) / sentiment_total * 100
    else:
        pos = 0.0
        neg = 0.0
    neu = 100 - pos - neg

    summary = {
        "total_reviews": total_reviews,
        "avg_rating": round(avg_rating, 2),
        "rating_distribution": rating_dist,
        "fake_review_percent": round(fake_percent, 2),
        "sentiment": {"positive": round(pos, 1), "neutral": round(neu, 1), "negative": round(neg, 1)},
        "reviews": [
            {
                "id": r.id,
                "author_name": r.author_name,
                "rating": r.rating,
                "content": r.content,
                "created_date": r.created_date,
                "likes_count": r.likes_count,
                "is_purchased": r.is_purchased,
                "sentiment_score": float(r.sentiment_score) if r.sentiment_score else None,
                "is_fake": r.is_fake,
                "fake_confidence": float(r.fake_confidence) if r.fake_confidence else None,
            }
            for r in reviews
        ],
    }

    return summary, total
