---
name: FastAPI Endpoint
description: How to create a new FastAPI endpoint following ShopSmart Analytics patterns
---

# FastAPI Endpoint Skill

## When to Use
When you need to add a new REST API endpoint to the backend.

## Steps

### 1. Create Service Function

File: `backend/app/services/<domain>_service.py`

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import Product  # import relevant models

async def get_items(
    db: AsyncSession,
    page: int = 1,
    per_page: int = 20,
    q: str | None = None,
) -> tuple[list, int]:
    """Return (items, total_count)."""
    query = select(Product).where(Product.is_active == True)

    # Search with pg_trgm (full-text)
    if q:
        query = query.where(Product.name.ilike(f"%{q}%"))

    # Count total
    total = await db.scalar(select(func.count()).select_from(query.subquery()))

    # Pagination
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    items = result.scalars().all()

    return items, total
```

### 2. Create Route Handler

File: `backend/app/api/<domain>.py`

```python
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.<domain>_service import get_items
from app.schemas.common import BaseResponse, PaginationMeta

router = APIRouter(prefix="/api/v1/<domain>", tags=["<Domain>"])

@router.get("/")
async def list_items(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    q: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    items, total = await get_items(db, page=page, per_page=per_page, q=q)
    return {
        "success": True,
        "data": [item.to_dict() for item in items],
        "meta": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": (total + per_page - 1) // per_page,
        },
        "message": None,
    }

@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return {"success": True, "data": item.to_dict(), "meta": None, "message": None}
```

### 3. Register Router

File: `backend/app/api/router.py`

```python
from app.api.<domain> import router as <domain>_router
api_router.include_router(<domain>_router)
```

### 4. Add Redis Cache (Optional)

```python
from app.services.cache_service import CacheService

@router.get("/{item_id}")
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    cache = CacheService()
    cache_key = f"<domain>:{item_id}"

    cached = await cache.get(cache_key)
    if cached:
        return cached

    # ... fetch from DB ...

    response = {"success": True, "data": data, "meta": None, "message": None}
    await cache.set(cache_key, response, ttl=600)  # 10 min
    return response
```

## Response Format (MUST follow)

```json
{
    "success": true,
    "data": { "..." },
    "meta": { "page": 1, "per_page": 20, "total": 150, "total_pages": 8 },
    "message": null
}
```

Error:
```json
{
    "success": false,
    "data": null,
    "error": { "code": "ITEM_NOT_FOUND", "message": "Item with id 123 not found" }
}
```

## Verify

1. Start backend: `uvicorn app.main:app --reload --port 8000`
2. Open Swagger: `http://localhost:8000/docs`
3. Test the new endpoint in Swagger UI
4. Check response matches the standard format above
