import hashlib
import json
from typing import Any


def make_cache_key(*args: Any, prefix: str = "") -> str:
    """Generate a deterministic cache key from args."""
    key_data = json.dumps(args, sort_keys=True, default=str)
    key_hash = hashlib.md5(key_data.encode()).hexdigest()
    return f"{prefix}:{key_hash}" if prefix else key_hash


def format_vnd(price: int) -> str:
    """Format price as Vietnamese Dong string."""
    return f"{price:,}đ".replace(",", ".")
