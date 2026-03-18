---
name: Pydantic Schema
description: How to create Pydantic request/response schemas following project conventions
---

# Pydantic Schema Skill

## When to Use
When you need to create request validation or response models for API endpoints.

## Steps

### 1. Create Schema File

File: `backend/app/schemas/<domain>.py`

```python
from typing import Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# === Request Models ===

class ItemSearchParams(BaseModel):
    """Query parameters for search/filter."""
    q: Optional[str] = Field(None, description="Search by name")
    category_id: Optional[int] = Field(None, description="Filter by category")
    platform: Optional[str] = Field(None, description="Filter: shopee, tiki, lazada")
    min_price: Optional[int] = Field(None, ge=0, description="Min price VND")
    max_price: Optional[int] = Field(None, ge=0, description="Max price VND")
    sort_by: str = Field("relevance", description="Sort: relevance, price_asc, price_desc, rating")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class CreateItemRequest(BaseModel):
    """Body for POST requests."""
    name: str = Field(..., min_length=1, max_length=500)
    price: int = Field(..., gt=0, description="Price in VND")
    email: EmailStr = Field(..., description="Notification email")
    item_type: Literal["type_a", "type_b"] = Field("type_a")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15 Pro Max",
                "price": 28990000,
                "email": "user@example.com",
                "item_type": "type_a",
            }
        }


# === Response Models ===

class ItemResponse(BaseModel):
    """Single item in list responses."""
    id: int
    name: str
    platform: str
    current_price: int
    original_price: Optional[int] = None
    discount_percent: Optional[float] = None
    rating_avg: Optional[float] = None
    rating_count: int = 0
    image_url: Optional[str] = None

    class Config:
        from_attributes = True  # auto-convert SQLAlchemy models


class ItemDetailResponse(ItemResponse):
    """Extended detail response."""
    url: str
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    is_official_store: bool = False
    total_sold: int = 0
    first_seen_at: Optional[datetime] = None
    last_crawled_at: Optional[datetime] = None
    ai_insights: Optional[dict] = None
    price_stats: Optional[dict] = None
```

### 2. Register in `__init__.py`

File: `backend/app/schemas/__init__.py`

```python
from app.schemas.<domain> import (
    ItemSearchParams,
    CreateItemRequest,
    ItemResponse,
    ItemDetailResponse,
)
```

### 3. Use in Route Handlers

```python
from app.schemas.<domain> import ItemSearchParams, CreateItemRequest

@router.get("/", response_model=None)  # We use custom response format
async def list_items(params: ItemSearchParams = Depends()):
    # params.q, params.page, etc. auto-validated
    ...

@router.post("/")
async def create_item(body: CreateItemRequest):
    # body.name, body.price auto-validated
    ...
```

## Common Schema Patterns

### Base Response (in `common.py`)

```python
class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    total_pages: int

class BaseResponse(BaseModel):
    success: bool = True
    data: Optional[Any] = None
    meta: Optional[PaginationMeta] = None
    message: Optional[str] = None

class ErrorResponse(BaseModel):
    success: bool = False
    data: None = None
    error: dict  # {"code": "...", "message": "..."}
```

### Price Point (for charts)

```python
class PricePointResponse(BaseModel):
    date: str
    min: int
    max: int
    avg: int
```

### Prediction

```python
class PredictionResponse(BaseModel):
    date: str
    predicted_price: int
    confidence: float = Field(ge=0, le=1)
```

## Conventions

| Convention | Rule |
|------------|------|
| **Prices** | Always `int` (VND BIGINT), never float |
| **Config** | Use `from_attributes = True` for ORM conversion |
| **Optional** | Use `Optional[type] = None` with default |
| **Validation** | Use `Field()` with `ge`, `le`, `gt`, `lt`, `min_length`, `max_length` |
| **Literal** | Use `Literal["a", "b"]` for fixed choices |
| **Examples** | Add `json_schema_extra` for Swagger docs |

## Verify

1. Start backend and open `http://localhost:8000/docs`
2. Check that Swagger shows correct schemas with examples
3. Test validation by sending invalid data (wrong types, out-of-range values)
4. Verify error messages are descriptive
