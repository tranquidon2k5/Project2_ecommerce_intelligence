from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models.crawl_log import CrawlLog

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint with DB and Redis verification."""
    checks = {"api": "ok"}
    try:
        await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"
    try:
        from ..services.cache_service import cache_service
        redis_client = await cache_service.get_client()
        await redis_client.ping()
        checks["redis"] = "ok"
    except Exception:
        checks["redis"] = "error"
    overall = "ok" if all(v == "ok" for v in checks.values()) else "degraded"
    return {
        "success": True,
        "data": {
            "status": overall,
            "checks": checks,
            "version": "1.0.0",
        },
        "message": None,
    }


@router.get("/stats/crawl")
async def crawl_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get latest crawl statistics."""
    result = await db.execute(
        select(CrawlLog).order_by(CrawlLog.started_at.desc()).limit(10)
    )
    logs = result.scalars().all()

    data = [
        {
            "id": log.id,
            "spider_name": log.spider_name,
            "status": log.status,
            "products_crawled": log.products_crawled,
            "products_new": log.products_new,
            "products_updated": log.products_updated,
            "errors_count": log.errors_count,
            "duration_seconds": float(log.duration_seconds) if log.duration_seconds else None,
            "started_at": log.started_at,
            "finished_at": log.finished_at,
        }
        for log in logs
    ]

    return {"success": True, "data": data, "message": None}


@router.get("/stats/system")
async def system_stats(
    db: AsyncSession = Depends(get_db),
):
    """Get system statistics with data freshness and API metrics."""
    from sqlalchemy import func
    from ..models.product import Product, PriceHistory
    from ..models.review import Review
    from ..metrics import metrics_collector

    product_count = await db.execute(select(func.count(Product.id)))
    price_count = await db.execute(select(func.count(PriceHistory.id)))
    review_count = await db.execute(select(func.count(Review.id)))

    # Data freshness
    last_crawl = await db.execute(select(func.max(CrawlLog.finished_at)))
    last_price = await db.execute(select(func.max(PriceHistory.crawled_at)))

    from datetime import datetime
    now = datetime.utcnow()
    last_crawl_at = last_crawl.scalar()
    last_price_at = last_price.scalar()

    return {
        "success": True,
        "data": {
            "counts": {
                "products": product_count.scalar() or 0,
                "price_history_records": price_count.scalar() or 0,
                "reviews": review_count.scalar() or 0,
            },
            "data_freshness": {
                "last_crawl_at": last_crawl_at.isoformat() if last_crawl_at else None,
                "last_price_point_at": last_price_at.isoformat() if last_price_at else None,
                "minutes_since_last_crawl": round((now - last_crawl_at).total_seconds() / 60, 1) if last_crawl_at else None,
            },
            "api_metrics": metrics_collector.get_summary(),
        },
        "message": None,
    }
