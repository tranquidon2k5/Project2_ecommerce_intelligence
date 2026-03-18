from fastapi import APIRouter, Depends
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as aioredis

from ..database import get_db
from ..config import settings
from ..models.crawl_log import CrawlLog

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "success": True,
        "data": {
            "status": "ok",
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
    """Get system statistics."""
    from sqlalchemy import func
    from ..models.product import Product, PriceHistory
    from ..models.review import Review

    product_count = await db.execute(select(func.count(Product.id)))
    price_count = await db.execute(select(func.count(PriceHistory.id)))
    review_count = await db.execute(select(func.count(Review.id)))

    return {
        "success": True,
        "data": {
            "products": product_count.scalar() or 0,
            "price_history_records": price_count.scalar() or 0,
            "reviews": review_count.scalar() or 0,
        },
        "message": None,
    }
