"""
Rule-based buy signal generator.
Combines: price trend direction + anomaly score + Prophet prediction direction.
"""
from typing import Literal

BuySignal = Literal["strong_buy", "buy", "hold", "wait"]


def compute_buy_signal(
    trend_direction: str,       # "up" | "down" | "stable"
    anomaly_score: float,       # 0–1, higher = more anomalous
    predicted_price: float,     # predicted price N days ahead
    current_price: float,       # current price
    price_30d_avg: float,       # 30-day average price
) -> tuple[BuySignal, str]:
    """
    Compute buy signal and human-readable reason.

    Logic:
    - strong_buy: price trending down + predicted further drop + below 30d avg + low anomaly
    - buy: price at or below 30d avg + stable/down trend
    - wait: price trending up + above 30d avg
    - hold: all other cases

    Returns (signal, reason_string).
    """
    if current_price <= 0:
        return "hold", "Không đủ dữ liệu giá"

    pct_vs_avg = (current_price - price_30d_avg) / max(price_30d_avg, 1)
    pred_direction = "down" if predicted_price < current_price else ("up" if predicted_price > current_price else "stable")
    anomaly_flag = anomaly_score > 0.7

    if anomaly_flag:
        return "wait", f"Phát hiện bất thường giá (điểm bất thường: {anomaly_score:.2f})"

    if trend_direction == "down" and pred_direction == "down" and pct_vs_avg < -0.05:
        return "strong_buy", "Giá đang giảm mạnh, dự báo tiếp tục giảm, thấp hơn trung bình 30 ngày"

    if pct_vs_avg <= 0.02 and trend_direction in ("down", "stable"):
        return "buy", "Giá đang ở mức tốt so với 30 ngày qua"

    if trend_direction == "up" and pct_vs_avg > 0.05:
        return "wait", "Giá đang tăng, nên chờ đợi thêm"

    return "hold", "Giá ổn định, không có tín hiệu rõ ràng"
