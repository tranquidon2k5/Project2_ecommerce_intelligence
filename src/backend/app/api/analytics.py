from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..services.analytics_service import (
    get_trending, get_price_comparison, get_market_overview, get_category_insights
)
from ..services.cache_service import cache_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def success_response(data, meta=None):
    return {"success": True, "data": data, "meta": meta, "message": None}


@router.get("/trending")
async def trending_products(
    type: str = Query("price_drop", description="price_drop, best_seller, best_deal, most_reviewed"),
    category_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Get trending products."""
    cache_key = f"trending:{type}:{category_id}:{platform}:{limit}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    products = await get_trending(db, trend_type=type, category_id=category_id, platform=platform, limit=limit)
    response = success_response(products)
    await cache_service.set(cache_key, response, ttl=settings.cache_ttl_trending)
    return response


@router.get("/price-comparison")
async def price_comparison(
    q: str = Query(..., description="Product name to compare"),
    category_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Compare product prices across platforms."""
    result = await get_price_comparison(db, q=q, category_id=category_id)
    return success_response(result)


@router.get("/market-overview")
async def market_overview(
    db: AsyncSession = Depends(get_db),
):
    """Get market overview statistics."""
    cache_key = "market:overview"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    result = await get_market_overview(db)
    response = success_response(result)
    await cache_service.set(cache_key, response, ttl=settings.cache_ttl_analytics)
    return response


@router.get("/category-insights/{category_id}")
async def category_insights(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get insights for a category."""
    cache_key = f"category:insights:{category_id}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    result = await get_category_insights(db, category_id)
    if not result:
        raise HTTPException(status_code=404, detail={"code": "CATEGORY_NOT_FOUND", "message": f"Category {category_id} not found"})
    response = success_response(result)
    await cache_service.set(cache_key, response, ttl=settings.cache_ttl_analytics)
    return response
