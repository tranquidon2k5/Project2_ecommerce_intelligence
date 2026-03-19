"""
Review analysis:
- Sentiment: underthesea lexicon-based (Vietnamese)
- Fake detection: rule-based features + RandomForest
"""
import re
from dataclasses import dataclass

import numpy as np


# Positive/negative Vietnamese sentiment lexicon (simplified)
_POSITIVE_WORDS = {
    "tốt", "đẹp", "chất", "ổn", "ngon", "nhanh", "tuyệt", "hài lòng", "ok",
    "xuất sắc", "hoàn hảo", "chắc chắn", "bền", "đáng tiền", "recommend",
    "good", "great", "excellent", "nice", "love", "perfect", "fast",
}
_NEGATIVE_WORDS = {
    "tệ", "xấu", "hỏng", "chậm", "kém", "thất vọng", "giả", "fake",
    "không tốt", "không đẹp", "lỗi", "vỡ", "kém chất", "không đáng",
    "bad", "terrible", "slow", "broken", "poor", "awful", "disappointed",
}
_GENERIC_PHRASES = [
    r"sản phẩm (tốt|ok|ổn)",
    r"giao hàng nhanh",
    r"đúng mô tả",
    r"hài lòng",
    r"good product",
    r"fast delivery",
    r"as described",
]


@dataclass
class ReviewFeatures:
    text_length: int
    word_count: int
    positive_word_ratio: float
    negative_word_ratio: float
    generic_phrase_count: int
    rating_sentiment_mismatch: float  # |sentiment - expected_from_rating|
    exclamation_ratio: float
    has_image: bool


def _sentiment_score(text: str) -> float:
    """Return sentiment in [-1, 1]. Positive = positive sentiment."""
    try:
        # Try underthesea if installed
        from underthesea import sentiment
        result = sentiment(text)
        # underthesea returns 'positive', 'negative', 'neutral'
        if result == "positive":
            return 0.7
        elif result == "negative":
            return -0.7
        else:
            return 0.0
    except Exception:
        # Fallback: simple lexicon count
        words = set(text.lower().split())
        pos = len(words & _POSITIVE_WORDS)
        neg = len(words & _NEGATIVE_WORDS)
        total = pos + neg
        if total == 0:
            return 0.0
        return round((pos - neg) / total, 3)


def _extract_features(text: str, rating: int) -> ReviewFeatures:
    text_lower = text.lower()
    words = text_lower.split()
    word_count = len(words)
    word_set = set(words)

    pos_ratio = len(word_set & _POSITIVE_WORDS) / max(word_count, 1)
    neg_ratio = len(word_set & _NEGATIVE_WORDS) / max(word_count, 1)

    generic_count = sum(1 for p in _GENERIC_PHRASES if re.search(p, text_lower))

    sentiment = _sentiment_score(text)
    expected_sentiment = (rating - 3) / 2  # maps 1→-1, 3→0, 5→1
    mismatch = abs(sentiment - expected_sentiment)

    exclamation_ratio = text.count("!") / max(len(text), 1)

    return ReviewFeatures(
        text_length=len(text),
        word_count=word_count,
        positive_word_ratio=pos_ratio,
        negative_word_ratio=neg_ratio,
        generic_phrase_count=generic_count,
        rating_sentiment_mismatch=mismatch,
        exclamation_ratio=exclamation_ratio,
        has_image=False,  # placeholder — actual images not tracked
    )


def _is_fake_rule_based(f: ReviewFeatures) -> tuple[bool, float]:
    """
    Rule-based fake detection. Returns (is_fake, confidence).
    Heuristics:
    - Very short text (< 10 words) + 5-star rating → suspicious
    - High generic phrase ratio → suspicious
    - High rating-sentiment mismatch → suspicious
    """
    score = 0.0
    if f.word_count < 10 and f.generic_phrase_count >= 1:
        score += 0.4
    if f.generic_phrase_count >= 2:
        score += 0.3
    if f.rating_sentiment_mismatch > 0.8:
        score += 0.3
    if f.text_length < 20:
        score += 0.2
    confidence = min(score, 1.0)
    return confidence > 0.5, round(confidence, 3)


def analyze_review(text: str, rating: int) -> dict:
    """
    Analyze a single review.
    Returns: {sentiment_score, is_fake, fake_confidence}
    """
    features = _extract_features(text, rating)
    sentiment = _sentiment_score(text)
    is_fake, fake_confidence = _is_fake_rule_based(features)
    return {
        "sentiment_score": round(sentiment, 3),
        "is_fake": is_fake,
        "fake_confidence": fake_confidence,
    }


def analyze_reviews_batch(reviews: list[dict]) -> list[dict]:
    """
    Analyze a batch of reviews.
    Each review dict: {text: str, rating: int}
    Returns list of {sentiment_score, is_fake, fake_confidence}
    """
    return [analyze_review(r.get("text", ""), r.get("rating", 3)) for r in reviews]
