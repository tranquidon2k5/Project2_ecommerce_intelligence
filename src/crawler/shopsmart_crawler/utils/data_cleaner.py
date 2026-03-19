import re


def clean_price(price_str) -> int:
    """Convert price string to integer VND."""
    if isinstance(price_str, (int, float)):
        return int(price_str)
    if not price_str:
        return 0
    # Remove non-numeric chars except decimal
    cleaned = re.sub(r'[^\d]', '', str(price_str))
    return int(cleaned) if cleaned else 0


def clean_text(text: str, max_length: int = 500) -> str:
    """Clean and truncate text."""
    if not text:
        return ""
    return text.strip()[:max_length]


def compute_discount(price: int, original_price: int) -> float:
    """Compute discount percentage."""
    if not original_price or original_price <= price:
        return 0.0
    return round((original_price - price) / original_price * 100, 2)
