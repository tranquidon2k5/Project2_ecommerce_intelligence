"""Anomaly detection using IsolationForest on price time-series features."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def compute_price_features(prices: list[float]) -> np.ndarray:
    """
    Extract features from a price sequence for anomaly detection.
    Returns array of shape (n_samples, 5).
    Features: price, pct_change, rolling_mean_7, z_score, rolling_std_7
    """
    arr = np.array(prices, dtype=float)
    n = len(arr)

    pct_change = np.zeros(n)
    if n > 1:
        pct_change[1:] = (arr[1:] - arr[:-1]) / (arr[:-1] + 1e-9)

    window = min(7, n)
    rolling_mean = pd.Series(arr).rolling(window, min_periods=1).mean().values
    rolling_std = pd.Series(arr).rolling(window, min_periods=1).std().fillna(0).values

    global_std = np.std(arr) + 1e-9
    global_mean = np.mean(arr)
    z_score = (arr - global_mean) / global_std

    features = np.stack([arr, pct_change, rolling_mean, z_score, rolling_std], axis=1)
    return features


def compute_anomaly_score(prices: list[float]) -> float:
    """
    Compute an anomaly score in [0, 1] for the LATEST price point.
    Score > 0.7 → anomalous.

    Returns 0.0 for products with fewer than 10 price points.
    """
    if len(prices) < 10:
        return 0.0

    features = compute_price_features(prices)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
    )
    model.fit(scaled)

    # score_samples returns negative; convert to [0,1] where 1 = most anomalous
    raw_scores = model.score_samples(scaled)
    # Normalize: lower raw score = more anomalous
    min_s, max_s = raw_scores.min(), raw_scores.max()
    if max_s == min_s:
        return 0.0
    normalized = 1.0 - (raw_scores - min_s) / (max_s - min_s)
    latest_score = float(normalized[-1])
    return round(min(latest_score, 1.0), 4)


def batch_compute_anomaly_scores(product_prices: dict[int, list[float]]) -> dict[int, float]:
    """
    Compute anomaly scores for a batch of products using a single shared model.
    Returns {product_id: score}.
    """
    if not product_prices:
        return {}

    # Separate products with enough data from those without
    eligible = {pid: prices for pid, prices in product_prices.items() if len(prices) >= 10}
    result = {pid: 0.0 for pid in product_prices}  # default 0.0 for ineligible

    if not eligible:
        return result

    # Build combined feature matrix with product index tracking
    all_features = []
    product_last_idx = {}  # pid -> index in all_features of its latest point
    offset = 0
    for pid, prices in eligible.items():
        features = compute_price_features(prices)
        all_features.append(features)
        product_last_idx[pid] = offset + len(features) - 1
        offset += len(features)

    combined = np.vstack(all_features)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(combined)

    model = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    model.fit(scaled)

    raw_scores = model.score_samples(scaled)
    min_s, max_s = raw_scores.min(), raw_scores.max()
    if max_s == min_s:
        return result

    normalized = 1.0 - (raw_scores - min_s) / (max_s - min_s)
    for pid, idx in product_last_idx.items():
        result[pid] = round(float(min(normalized[idx], 1.0)), 4)

    return result
