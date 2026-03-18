---
name: Redis Caching
description: How to implement Redis caching for API endpoints
---

# Redis Caching Skill

## When to Use
When you need to cache API responses to reduce database load and improve latency.

## Steps

### 1. Use CacheService

File: `backend/app/services/cache_service.py` (already exists)

```python
import json
import hashlib
from typing import Optional, Any
import redis.asyncio as redis
from app.config import settings


class CacheService:
    def __init__(self):
        self._redis: Optional[redis.Redis] = None

    async def _get_redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._redis

    async def get(self, key: str) -> Optional[dict]:
        r = await self._get_redis()
        data = await r.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 300):
        r = await self._get_redis()
        await r.set(key, json.dumps(value, default=str), ex=ttl)

    async def delete(self, key: str):
        r = await self._get_redis()
        await r.delete(key)

    async def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern. Use for cache invalidation."""
        r = await self._get_redis()
        keys = []
        async for key in r.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await r.delete(*keys)

    @staticmethod
    def make_key(prefix: str, **params) -> str:
        """Generate deterministic cache key from params."""
        param_str = json.dumps(params, sort_keys=True)
        hash_val = hashlib.md5(param_str.encode()).hexdigest()[:12]
        return f"{prefix}:{hash_val}"
```

### 2. Add Cache to Service Layer

File: `backend/app/services/<domain>_service.py`

```python
from app.services.cache_service import CacheService

cache = CacheService()

async def get_product_by_id(db: AsyncSession, product_id: int) -> dict:
    # Check cache first
    cache_key = f"product:{product_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Fetch from DB
    product = await db.get(Product, product_id)
    if not product:
        return None

    result = product.to_dict()

    # Store in cache
    await cache.set(cache_key, result, ttl=600)  # 10 minutes
    return result


async def search_products(db: AsyncSession, params: dict) -> tuple:
    # Cache search results with hashed params
    cache_key = CacheService.make_key("products:search", **params)
    cached = await cache.get(cache_key)
    if cached:
        return cached["items"], cached["total"]

    # ... DB query ...

    # Cache result
    await cache.set(cache_key, {"items": items, "total": total}, ttl=300)  # 5 min
    return items, total
```

### 3. Invalidate Cache on Data Changes

```python
async def on_crawl_complete():
    """Invalidate product caches after new crawl data."""
    cache = CacheService()
    # Invalidate all product detail caches
    await cache.delete_pattern("product:*")
    # Invalidate all search result caches
    await cache.delete_pattern("products:search:*")
    # Invalidate analytics caches
    await cache.delete_pattern("analytics:*")
```

### 4. Cache in Route Handler (Alternative)

```python
@router.get("/analytics/market-overview")
async def market_overview(db: AsyncSession = Depends(get_db)):
    cache = CacheService()
    cache_key = "analytics:market_overview"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    # Heavy computation
    data = await analytics_service.get_market_overview(db)
    response = {"success": True, "data": data, "meta": None, "message": None}

    await cache.set(cache_key, response, ttl=600)  # 10 min for heavy endpoints
    return response
```

## Cache Key Patterns

| Pattern | TTL | Description |
|---------|-----|-------------|
| `product:{id}` | 10 min | Single product detail |
| `products:search:{hash}` | 5 min | Search results |
| `analytics:market_overview` | 10 min | Market overview stats |
| `analytics:trending:{type}` | 5 min | Trending products |
| `ai:prediction:{product_id}` | 30 min | Price predictions |

## Cache Invalidation Triggers

| Event | Keys to Invalidate |
|-------|-------------------|
| Crawl completes | `product:*`, `products:search:*`, `analytics:*` |
| ML retrain | `ai:prediction:*` |
| Alert created/deleted | `alerts:{email}` |
| Product updated | `product:{id}`, `products:search:*` |

## Verify

```bash
# Check Redis is running
docker-compose exec redis redis-cli ping
# → PONG

# Monitor cache activity
docker-compose exec redis redis-cli monitor

# Check cache keys
docker-compose exec redis redis-cli keys "*"

# Check TTL of a key
docker-compose exec redis redis-cli ttl "product:1"
```
