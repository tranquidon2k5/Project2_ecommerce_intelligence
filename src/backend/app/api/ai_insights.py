"""AI Insights API — price prediction, anomaly detection, review analysis."""
from datetime import datetime, timedelta

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..config import settings
from ..models.analytics import ProductAnalytics
from ..models.product import PriceHistory, Product
from ..ml.price_predictor import predict_price
from ..ml.review_analyzer import analyze_reviews_batch
from ..services.cache_service import cache_service

router = APIRouter(prefix="/ai", tags=["AI Insights"])


def success_response(data):
    return {"success": True, "data": data, "message": None}


@router.get("/predict-price/{product_id}")
async def predict_price_endpoint(
    product_id: int,
    days: int = Query(7, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
):
    """Predict future prices using Prophet (or moving-average fallback)."""
    cache_key = f"ai:predict:{product_id}:{days}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    product_result = await db.execute(select(Product).where(Product.id == product_id))
    product = product_result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail={"code": "PRODUCT_NOT_FOUND", "message": f"Product {product_id} not found"})

    cutoff = datetime.utcnow() - timedelta(days=90)
    ph_result = await db.execute(
        select(PriceHistory.crawled_at, PriceHistory.price)
        .where(PriceHistory.product_id == product_id)
        .where(PriceHistory.crawled_at >= cutoff)
        .order_by(PriceHistory.crawled_at)
    )
    ph_rows = ph_result.all()

    prices_df = pd.DataFrame(
        [(r.crawled_at, float(r.price)) for r in ph_rows],
        columns=["ds", "y"],
    ) if ph_rows else pd.DataFrame(columns=["ds", "y"])

    pred = predict_price(product_id, prices_df, days)

    # Get latest analytics for buy signal
    analytics_result = await db.execute(
        select(ProductAnalytics)
        .where(ProductAnalytics.product_id == product_id)
        .order_by(desc(ProductAnalytics.date))
        .limit(1)
    )
    analytics = analytics_result.scalar_one_or_none()

    response = success_response({
        "product_id": product_id,
        "current_price": product.current_price,
        "predictions": pred["predictions"],
        "model_used": pred["model_used"],
        "mae": pred.get("mae", 0.0),
        "note": pred.get("note"),
        "recommendation": {
            "signal": analytics.buy_signal if analytics else "hold",
            "trend": analytics.trend_direction if analytics else "stable",
        },
        "model_info": {"model": pred["model_used"], "data_points": len(ph_rows)},
    })
    await cache_service.set(cache_key, response, ttl=settings.cache_ttl_analytics)
    return response


@router.get("/anomalies")
async def get_anomalies(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get products with anomalous pricing (anomaly_score > 0.7)."""
    cache_key = f"ai:anomalies:{limit}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached

    result = await db.execute(
        select(ProductAnalytics, Product.name, Product.current_price)
        .join(Product, ProductAnalytics.product_id == Product.id)
        .where(ProductAnalytics.anomaly_score > 0.7)
        .order_by(desc(ProductAnalytics.anomaly_score))
        .limit(limit)
    )
    rows = result.all()

    response = success_response([
        {
            "product_id": row[0].product_id,
            "product_name": row[1],
            "anomaly_score": float(row[0].anomaly_score),
            "buy_signal": row[0].buy_signal,
            "current_price": row[2],
            "trend_direction": row[0].trend_direction,
        }
        for row in rows
    ])
    await cache_service.set(cache_key, response, ttl=settings.cache_ttl_analytics)
    return response


@router.post("/check-reviews")
async def check_reviews(body: dict):
    """
    Analyze a list of reviews for sentiment and fake detection.
    Body: {"reviews": [{"text": "...", "rating": 5}, ...]}
    """
    reviews = body.get("reviews", [])
    if not reviews:
        raise HTTPException(status_code=422, detail="reviews list is required")
    if len(reviews) > 100:
        raise HTTPException(status_code=422, detail="Max 100 reviews per request")

    results = analyze_reviews_batch(reviews)
    return success_response({"results": results, "total": len(results)})
