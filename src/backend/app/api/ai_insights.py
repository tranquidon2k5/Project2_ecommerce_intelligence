from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from ..database import get_db
from ..models.product import Product
from ..models.analytics import ProductAnalytics

router = APIRouter(prefix="/ai", tags=["AI Insights"])


def success_response(data):
    return {"success": True, "data": data, "message": None}


@router.get("/predict-price/{product_id}")
async def predict_price(
    product_id: int,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Get price prediction for a product (stub — ML models in Sprint 2)."""
    product_result = await db.execute(
        select(Product).where(Product.id == product_id)
    )
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail={"code": "PRODUCT_NOT_FOUND", "message": f"Product {product_id} not found"})

    # Return analytics if available
    analytics_result = await db.execute(
        select(ProductAnalytics)
        .where(ProductAnalytics.product_id == product_id)
        .order_by(desc(ProductAnalytics.date))
        .limit(1)
    )
    analytics = analytics_result.scalar_one_or_none()

    return success_response({
        "product_id": product_id,
        "current_price": product.current_price,
        "predictions": [],
        "recommendation": {
            "signal": analytics.buy_signal if analytics else "hold",
            "reason": "ML models will be trained in Sprint 2",
        },
        "model_info": {"model": "stub", "note": "Prophet model training in Sprint 2"},
    })


@router.get("/anomalies")
async def get_anomalies(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get products with anomalous pricing."""
    from sqlalchemy import func
    result = await db.execute(
        select(ProductAnalytics, Product.name, Product.current_price)
        .join(Product, ProductAnalytics.product_id == Product.id)
        .where(ProductAnalytics.anomaly_score > 0.7)
        .order_by(desc(ProductAnalytics.anomaly_score))
        .limit(limit)
    )
    rows = result.all()

    return success_response([
        {
            "product_id": row[0].product_id,
            "product_name": row[1],
            "anomaly_score": float(row[0].anomaly_score),
            "buy_signal": row[0].buy_signal,
            "current_price": row[2],
        }
        for row in rows
    ])
