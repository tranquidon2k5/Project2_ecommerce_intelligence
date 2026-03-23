"""CSV export endpoints for products and price history."""
import csv
import io
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.product import Product, PriceHistory
from ..models.platform import Platform

router = APIRouter(prefix="/export", tags=["Export"])


@router.get("/products")
async def export_products_csv(
    q: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    platform: Optional[str] = Query(None),
    min_price: Optional[int] = Query(None),
    max_price: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export filtered products to CSV. Max 1000 rows."""
    query = (
        select(
            Product.id,
            Product.name,
            Platform.name.label("platform"),
            Product.current_price,
            Product.original_price,
            Product.discount_percent,
            Product.rating_avg,
            Product.rating_count,
            Product.total_sold,
            Product.seller_name,
            Product.url,
        )
        .join(Platform, Product.platform_id == Platform.id)
        .where(Product.is_active == True)
    )

    if q:
        query = query.where(Product.name.ilike(f"%{q}%"))
    if category_id:
        query = query.where(Product.category_id == category_id)
    if platform:
        query = query.where(Platform.name == platform)
    if min_price is not None:
        query = query.where(Product.current_price >= min_price)
    if max_price is not None:
        query = query.where(Product.current_price <= max_price)

    query = query.order_by(Product.id).limit(1000)
    result = await db.execute(query)
    rows = result.all()

    output = io.StringIO()
    fieldnames = [
        "id", "name", "platform", "current_price", "original_price",
        "discount_percent", "rating_avg", "rating_count", "total_sold",
        "seller_name", "url",
    ]
    writer = csv.writer(output)
    writer.writerow(fieldnames)
    for row in rows:
        writer.writerow([
            row.id, row.name, row.platform,
            row.current_price, row.original_price,
            float(row.discount_percent) if row.discount_percent else "",
            float(row.rating_avg) if row.rating_avg else "",
            row.rating_count or "", row.total_sold or "",
            row.seller_name or "", row.url or "",
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=products.csv"},
    )


@router.get("/price-history/{product_id}")
async def export_price_history_csv(
    product_id: int,
    period: str = Query("30d"),
    db: AsyncSession = Depends(get_db),
):
    """Export price history for a product to CSV."""
    from datetime import datetime, timedelta

    period_map = {"7d": 7, "30d": 30, "90d": 90, "180d": 180, "1y": 365, "all": None}
    days = period_map.get(period, 30)

    query = select(
        func.date(PriceHistory.crawled_at).label("date"),
        func.min(PriceHistory.price).label("min_price"),
        func.max(PriceHistory.price).label("max_price"),
        func.avg(PriceHistory.price).label("avg_price"),
    ).where(PriceHistory.product_id == product_id)

    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.where(PriceHistory.crawled_at >= cutoff)

    query = query.group_by(func.date(PriceHistory.crawled_at)).order_by(func.date(PriceHistory.crawled_at))
    result = await db.execute(query)
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "min_price", "max_price", "avg_price"])
    for row in rows:
        writer.writerow([str(row.date), row.min_price, row.max_price, int(row.avg_price)])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=price_history_{product_id}.csv"},
    )
