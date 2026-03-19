"""
Analytics training and daily compute:
- compute_daily_analytics(): updates product_analytics table for all products
- Runs as APScheduler daily job
"""
import logging
from datetime import date, datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product import Product, PriceHistory
from ..models.analytics import ProductAnalytics
from .price_predictor import predict_price
from .anomaly_detector import compute_anomaly_score
from .recommender import compute_buy_signal

logger = logging.getLogger(__name__)


async def compute_daily_analytics(db: AsyncSession) -> dict:
    """
    Compute analytics for all products and upsert into product_analytics.
    Called daily by APScheduler.
    Returns summary dict.
    """
    today = date.today()
    processed = 0
    errors = 0

    # Load all products
    result = await db.execute(select(Product.id, Product.current_price))
    products = result.all()

    for product_id, current_price in products:
        try:
            # Load price history (last 90 days)
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
            )
            prices = [float(r.price) for r in ph_rows]

            # Price prediction
            pred_result = predict_price(product_id, prices_df, days=7)
            predicted_7d = pred_result["predictions"][6]["price"] if len(pred_result["predictions"]) >= 7 else current_price

            # Anomaly score
            anomaly_score = compute_anomaly_score(prices)

            # Trend direction
            if len(prices) >= 7:
                recent_avg = sum(prices[-7:]) / 7
                older_avg = sum(prices[-14:-7]) / 7 if len(prices) >= 14 else recent_avg
                if recent_avg < older_avg * 0.97:
                    trend = "down"
                elif recent_avg > older_avg * 1.03:
                    trend = "up"
                else:
                    trend = "stable"
            else:
                trend = "stable"

            # Price stats 30d
            prices_30d = [float(r.price) for r in ph_rows[-30:]] if len(ph_rows) >= 1 else [float(current_price)]
            price_30d_avg = sum(prices_30d) / len(prices_30d)

            # Volatility: std/mean
            if len(prices_30d) > 1:
                volatility = float(np.std(prices_30d) / (np.mean(prices_30d) + 1e-9))
            else:
                volatility = 0.0

            # Buy signal
            buy_signal, _ = compute_buy_signal(
                trend_direction=trend,
                anomaly_score=anomaly_score,
                predicted_price=float(predicted_7d),
                current_price=float(current_price),
                price_30d_avg=price_30d_avg,
            )

            # Upsert into product_analytics
            existing = await db.execute(
                select(ProductAnalytics).where(
                    ProductAnalytics.product_id == product_id,
                    ProductAnalytics.date == today,
                )
            )
            analytics = existing.scalar_one_or_none()
            if analytics is None:
                analytics = ProductAnalytics(product_id=product_id, date=today)
                db.add(analytics)

            analytics.anomaly_score = anomaly_score
            analytics.buy_signal = buy_signal
            analytics.trend_direction = trend
            analytics.predicted_price_7d = int(predicted_7d)
            analytics.price_volatility = round(volatility, 4)

            processed += 1

        except Exception as e:
            logger.error(f"Error computing analytics for product {product_id}: {e}")
            errors += 1

    try:
        await db.commit()
    except Exception as e:
        logger.error(f"Failed to commit analytics: {e}")
        await db.rollback()
        raise
    logger.info(f"Daily analytics done: {processed} processed, {errors} errors")
    return {"processed": processed, "errors": errors, "date": str(today)}
