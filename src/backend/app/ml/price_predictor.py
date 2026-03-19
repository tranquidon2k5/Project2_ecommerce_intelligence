"""Price prediction using Prophet (30+ data points) or moving-average fallback."""
import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


def _moving_average_predict(prices: list[float], days: int) -> list[dict]:
    """Fallback: predict using 7-day moving average + linear trend."""
    arr = np.array(prices)
    if len(arr) < 3:
        last = float(arr[-1]) if len(arr) > 0 else 0
        return [{"date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"), "price": last, "lower": last * 0.95, "upper": last * 1.05} for i in range(days)]

    window = min(7, len(arr))
    ma = float(np.mean(arr[-window:]))
    trend = float(np.polyfit(range(len(arr[-window:])), arr[-window:], 1)[0])

    result = []
    for i in range(days):
        predicted = ma + trend * (i + 1)
        predicted = max(predicted, 0)
        result.append({
            "date": (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d"),
            "price": round(predicted),
            "lower": round(predicted * 0.92),
            "upper": round(predicted * 1.08),
        })
    return result


def predict_price(product_id: int, prices_df: pd.DataFrame, days: int = 7) -> dict[str, Any]:
    """
    Predict future prices for a product.

    Args:
        product_id: Product ID (used for model caching).
        prices_df: DataFrame with columns ['ds' (datetime), 'y' (price as float)].
        days: Number of days to forecast.

    Returns:
        dict with keys: predictions (list of {date, price, lower, upper}),
                        model_used ('prophet' or 'moving_average'),
                        mae (float, 0.0 if not available).
    """
    prices = prices_df["y"].tolist() if len(prices_df) > 0 else []

    if len(prices_df) < 30:
        return {
            "predictions": _moving_average_predict(prices, days),
            "model_used": "moving_average",
            "mae": 0.0,
            "note": f"Insufficient data ({len(prices_df)} points < 30). Using moving average.",
        }

    try:
        from prophet import Prophet  # lazy import — heavy

        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            changepoint_prior_scale=0.05,
            interval_width=0.80,
        )
        model.fit(prices_df[["ds", "y"]])

        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        forecast_rows = forecast.tail(days)

        predictions = [
            {
                "date": row["ds"].strftime("%Y-%m-%d"),
                "price": round(max(row["yhat"], 0)),
                "lower": round(max(row["yhat_lower"], 0)),
                "upper": round(max(row["yhat_upper"], 0)),
            }
            for _, row in forecast_rows.iterrows()
        ]

        # Compute in-sample MAE on last 7 actual points
        actual = prices_df["y"].tail(7).tolist()
        in_sample = forecast.head(len(prices_df)).tail(7)["yhat"].tolist()
        mae = float(np.mean(np.abs(np.array(actual) - np.array(in_sample)))) if actual else 0.0

        return {"predictions": predictions, "model_used": "prophet", "mae": round(mae, 2)}

    except Exception as e:
        # Prophet failed → fallback
        return {
            "predictions": _moving_average_predict(prices, days),
            "model_used": "moving_average",
            "mae": 0.0,
            "note": f"Prophet error: {e}. Using moving average.",
        }
