# ML/AI Agent

## Role
Bạn là agent chuyên implement Machine Learning và AI features cho ShopSmart Analytics.

## Context
Đọc các file planning:
- `planning/02_ARCHITECTURE.md` - ML architecture, model choices, memory constraints
- `planning/04_API_DESIGN.md` - AI endpoints (predict-price, anomalies, check-reviews)
- `planning/06_SPRINT_PLAN.md` - Sprint 3 scope (2 ML models + rule-based review)

## Constraints
- Docker Compose environment - memory conscious
- NO PhoBERT (400MB model, 2GB+ RAM) - use lightweight approach
- Models loaded on-demand, NOT always-running service
- Save models as .pkl files in `backend/app/ml/models/`

## Tasks

### 1. Price Prediction
`backend/app/ml/price_predictor.py`:
- Class PricePredictor:
  - `train(product_id)`: fetch price_history → train Facebook Prophet
  - `predict(product_id, days=7)`: return predictions + confidence intervals
  - **Data threshold**: only use Prophet for products with 30+ data points
  - **Fallback**: moving average + % change heuristics for <30 points
  - **New products**: return "Insufficient data" message
  - Save/load model with joblib

API: GET /api/v1/ai/predict-price/{product_id}?days=7
Response: predictions list + recommendation + model_info (MAE, MAPE)

### 2. Anomaly Detection
`backend/app/ml/anomaly_detector.py`:
- Class AnomalyDetector:
  - Features: price_change_percent, price_vs_avg_30d, price_vs_avg_category, discount_percent, time_since_last_change
  - Model: IsolationForest (scikit-learn) - lightweight, runs on-demand
  - `train()`: train on all price data
  - `detect(product_id)`: return anomaly_score (0-1), anomaly_type
  - Types: "sudden_price_drop", "fake_discount", "price_manipulation", "unusual_pattern"

API: GET /api/v1/ai/anomalies?limit=20

### 3. Review Analysis (Rule-based, NOT deep learning)
`backend/app/ml/review_analyzer.py`:
- Class ReviewAnalyzer:
  - **Sentiment**: `underthesea` library (Vietnamese lexicon-based)
    - Return sentiment_score (-1.0 to 1.0)
  - **Fake Detection** (rule-based features):
    - review_length (too short/generic)
    - has_generic_phrases ("sản phẩm tốt", "giao hàng nhanh" repeated)
    - rating_vs_sentiment_mismatch (5 stars but negative text)
    - timestamp_clustering (many reviews same day)
    - reviewer_review_count (new accounts)
  - RandomForest classifier on extracted features
  - `batch_analyze(product_id)`: analyze all reviews, update DB

API: POST /api/v1/ai/check-reviews (body: {product_id})

### 4. Buy Signal / Recommender
`backend/app/ml/recommender.py`:
- Class BuyRecommender:
  - **Rule-based** (NOT ML): combine price trend + anomaly score + prediction direction
  - Signals: "strong_buy", "buy", "hold", "wait"
  - Return signal + Vietnamese reason text
  - Example: "Giá hiện tại thấp hơn 2.7% so với trung bình 30 ngày, xu hướng giảm"

### 5. Training Pipeline
`backend/app/ml/trainer.py`:
- Script to train all models
- Train price predictor for top products (by popularity)
- Train anomaly detector on all price data
- Train review classifier
- Log metrics to ml_model_metrics table

### 6. APScheduler Integration
- Crawl every 6h → trigger analytics computation
- Daily: compute product_analytics records (min/max/avg price, anomaly scores, buy signals)
- Weekly: retrain ML models

## Requirements
Add to `backend/requirements.txt`:
- prophet
- scikit-learn
- joblib
- underthesea
- numpy
- pandas
