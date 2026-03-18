---
name: ML Model
description: How to train, save, load, and serve a Machine Learning model
---

# ML Model Skill

## When to Use
When you need to add a new ML model or modify the training/serving pipeline.

## Steps

### 1. Create Model Class

File: `backend/app/ml/<model_name>.py`

```python
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import PriceHistory, Product

MODEL_DIR = Path(__file__).parent / "models"
MODEL_DIR.mkdir(exist_ok=True)


class NewModel:
    """Description of what this model does."""

    MODEL_PATH = MODEL_DIR / "new_model.pkl"
    MIN_DATA_POINTS = 30  # minimum data required

    def __init__(self):
        self._model = None

    def _load_model(self):
        """Load model on-demand (NOT always-running)."""
        if self._model is None and self.MODEL_PATH.exists():
            self._model = joblib.load(self.MODEL_PATH)
        return self._model

    async def _fetch_training_data(self, db: AsyncSession) -> pd.DataFrame:
        """Extract training data from PostgreSQL."""
        query = select(
            PriceHistory.product_id,
            PriceHistory.price,
            PriceHistory.crawled_at
        ).order_by(PriceHistory.crawled_at)

        result = await db.execute(query)
        rows = result.all()

        return pd.DataFrame(rows, columns=["product_id", "price", "crawled_at"])

    async def train(self, db: AsyncSession) -> dict:
        """Train model and save to disk. Return metrics."""
        df = await self._fetch_training_data(db)

        if len(df) < self.MIN_DATA_POINTS:
            return {"error": "Insufficient data", "count": len(df), "required": self.MIN_DATA_POINTS}

        # === Feature engineering ===
        # Example: price change features
        df["price_change"] = df.groupby("product_id")["price"].pct_change()
        df = df.dropna()

        X = df[["price_change"]].values
        # y = ...  # define your target

        # === Train model ===
        from sklearn.ensemble import IsolationForest  # or Prophet, RandomForest, etc.
        model = IsolationForest(contamination=0.1, random_state=42)
        model.fit(X)

        # === Save model ===
        self._model = model
        joblib.dump(model, self.MODEL_PATH)

        # === Compute metrics ===
        metrics = {
            "model_name": "new_model",
            "training_samples": len(X),
            "status": "success",
        }
        return metrics

    async def predict(self, db: AsyncSession, product_id: int) -> dict:
        """Generate predictions for a product."""
        model = self._load_model()
        if model is None:
            return {"error": "Model not trained yet"}

        # Fetch product data
        # ... feature extraction ...

        # For products with insufficient data, use fallback
        # if data_count < self.MIN_DATA_POINTS:
        #     return self._fallback_predict(data)

        prediction = model.predict(features)
        return {
            "product_id": product_id,
            "prediction": prediction.tolist(),
        }

    def _fallback_predict(self, data: pd.Series) -> dict:
        """Moving average fallback for products with <30 data points."""
        ma_7 = data.rolling(window=7).mean().iloc[-1]
        pct_change = data.pct_change().mean()
        return {
            "method": "moving_average",
            "predicted_price": int(ma_7 * (1 + pct_change)),
            "confidence": 0.3,  # low confidence for fallback
        }
```

### 2. Log Metrics to Database

```python
from app.models.crawl_log import MLModelMetrics

async def log_metrics(db: AsyncSession, metrics: dict):
    record = MLModelMetrics(
        model_name=metrics["model_name"],
        model_version="v1",
        metric_name="training_samples",
        metric_value=metrics["training_samples"],
    )
    db.add(record)
    await db.commit()
```

### 3. Add to Trainer

File: `backend/app/ml/trainer.py`

```python
from app.ml.new_model import NewModel

async def train_all_models(db: AsyncSession):
    # ... existing models ...

    # Train new model
    new_model = NewModel()
    metrics = await new_model.train(db)
    await log_metrics(db, metrics)
    print(f"NewModel trained: {metrics}")
```

### 4. Create API Endpoint

File: `backend/app/api/ai_insights.py`

```python
from app.ml.new_model import NewModel

@router.get("/new-prediction/{product_id}")
async def get_new_prediction(product_id: int, db: AsyncSession = Depends(get_db)):
    model = NewModel()
    result = await model.predict(db, product_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"success": True, "data": result, "meta": None, "message": None}
```

### 5. APScheduler Integration

In `backend/app/main.py` lifespan or scheduler setup:

```python
# Weekly retrain
scheduler.add_job(train_all_models, "cron", day_of_week="sun", hour=3)
```

## Project Constraints

| Constraint | Rule |
|------------|------|
| **No PhoBERT** | Too heavy (~400MB + 2GB RAM). Use `underthesea` for Vietnamese NLP |
| **On-demand loading** | Models loaded when needed, NOT always in memory |
| **Save format** | `.pkl` files in `backend/app/ml/models/` |
| **Data threshold** | Prophet needs 30+ data points; fallback to moving average |
| **Memory** | Docker Compose env — keep total ML memory < 500MB |

## Verify

```bash
# Train model manually
python -c "
import asyncio
from app.database import async_session
from app.ml.new_model import NewModel
async def main():
    async with async_session() as db:
        model = NewModel()
        metrics = await model.train(db)
        print(metrics)
asyncio.run(main())
"

# Test prediction via API
curl http://localhost:8000/api/v1/ai/new-prediction/1
```
