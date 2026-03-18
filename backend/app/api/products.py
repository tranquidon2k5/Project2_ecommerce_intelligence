from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.product_service import (
    get_products, get_product_by_id, get_price_history, get_product_reviews
)
from ..utils.exceptions import ProductNotFoundException

router = APIRouter(prefix="/products", tags=["Products"])


def success_response(data, meta=None):
    resp = {"success": True, "data": data, "meta": meta, "message": None}
    return resp


@router.get("")
async def list_products(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None, ge=0),
    max_price: Optional[int] = Query(None, ge=0),
    min_rating: Optional[float] = Query(None, ge=1.0, le=5.0),
    min_discount: Optional[float] = Query(None, ge=0.0, le=100.0),
    sort_by: str = Query("relevance"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """List products with search, filter, and sort."""
    products, total = await get_products(
        db, q=q, category_id=category_id, platform=platform,
        min_price=min_price, max_price=max_price, min_rating=min_rating,
        min_discount=min_discount, sort_by=sort_by, page=page, per_page=per_page
    )

    total_pages = (total + per_page - 1) // per_page
    meta = {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages}
    return success_response(products, meta)


@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get product detail with price stats and AI insights."""
    product = await get_product_by_id(db, product_id)
    if not product:
        raise ProductNotFoundException(product_id)
    return success_response(product)


@router.get("/{product_id}/price-history")
async def get_product_price_history(
    product_id: int,
    period: str = Query("30d", description="7d, 30d, 90d, 180d, 1y, all"),
    granularity: str = Query("auto"),
    db: AsyncSession = Depends(get_db),
):
    """Get price history for a product."""
    history = await get_price_history(db, product_id, period=period, granularity=granularity)
    if not history:
        raise ProductNotFoundException(product_id)
    return success_response(history)


@router.get("/{product_id}/reviews")
async def get_product_reviews_endpoint(
    product_id: int,
    rating: Optional[int] = Query(None, ge=1, le=5),
    sort_by: str = Query("recent"),
    show_fake: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get reviews for a product."""
    summary, total = await get_product_reviews(
        db, product_id, rating=rating, sort_by=sort_by,
        show_fake=show_fake, page=page, per_page=per_page
    )

    total_pages = (total + per_page - 1) // per_page
    meta = {"page": page, "per_page": per_page, "total": total, "total_pages": total_pages}
    return success_response(summary, meta)
