# 🔌 API Design - ShopSmart Analytics

---

## Base URL
```
Development: http://localhost:8000/api/v1
Production:  https://api.shopsmart.vn/api/v1
```

## Response Format
```json
{
    "success": true,
    "data": { ... },
    "meta": {
        "page": 1,
        "per_page": 20,
        "total": 150,
        "total_pages": 8
    },
    "message": null
}
```

## Error Format
```json
{
    "success": false,
    "data": null,
    "error": {
        "code": "PRODUCT_NOT_FOUND",
        "message": "Product with id 123 not found"
    }
}
```

---

## 1. Products API

### GET /products
Danh sách sản phẩm, hỗ trợ search, filter, sort, pagination.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| q | string | - | Tìm kiếm theo tên |
| category_id | int | - | Filter theo danh mục |
| platform | string | - | Filter: shopee, tiki, lazada |
| min_price | int | - | Giá tối thiểu (VND) |
| max_price | int | - | Giá tối đa (VND) |
| min_rating | float | - | Rating tối thiểu (1-5) |
| min_discount | float | - | Discount tối thiểu (%) |
| sort_by | string | relevance | relevance, price_asc, price_desc, rating, discount, popular |
| page | int | 1 | Trang |
| per_page | int | 20 | Số item/trang (max 100) |

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "id": 1,
            "name": "iPhone 15 Pro Max 256GB",
            "platform": "shopee",
            "category": "Điện thoại",
            "url": "https://shopee.vn/...",
            "image_url": "https://...",
            "current_price": 28990000,
            "original_price": 34990000,
            "discount_percent": 17.15,
            "rating_avg": 4.8,
            "rating_count": 1520,
            "total_sold": 5200,
            "seller_name": "Apple Official Store",
            "is_official_store": true,
            "ai_insights": {
                "buy_signal": "buy",
                "trend": "down",
                "predicted_price_7d": 28500000
            },
            "last_crawled_at": "2025-01-15T10:30:00Z"
        }
    ],
    "meta": { "page": 1, "per_page": 20, "total": 150 }
}
```

---

### GET /products/{id}
Chi tiết sản phẩm.

**Response:**
```json
{
    "success": true,
    "data": {
        "id": 1,
        "name": "iPhone 15 Pro Max 256GB",
        "platform": "shopee",
        "category": { "id": 5, "name": "Điện thoại", "slug": "dien-thoai" },
        "url": "https://shopee.vn/...",
        "image_url": "https://...",
        "current_price": 28990000,
        "original_price": 34990000,
        "discount_percent": 17.15,
        "rating_avg": 4.8,
        "rating_count": 1520,
        "total_sold": 5200,
        "seller_name": "Apple Official Store",
        "seller_rating": 4.9,
        "is_official_store": true,
        "first_seen_at": "2024-12-01T00:00:00Z",
        "last_crawled_at": "2025-01-15T10:30:00Z",
        "price_stats": {
            "min_30d": 27990000,
            "max_30d": 32990000,
            "avg_30d": 29800000,
            "current_vs_avg": -2.72
        },
        "ai_insights": {
            "buy_signal": "buy",
            "buy_signal_reason": "Giá hiện tại thấp hơn 2.7% so với trung bình 30 ngày, xu hướng giảm",
            "trend_direction": "down",
            "predicted_price_7d": 28500000,
            "anomaly_score": 0.12,
            "fake_review_percent": 5.2
        }
    }
}
```

---

### GET /products/{id}/price-history
Lịch sử giá sản phẩm.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| period | string | 30d | 7d, 30d, 90d, 180d, 1y, all |
| granularity | string | auto | hourly, daily, weekly |

**Response:**
```json
{
    "success": true,
    "data": {
        "product_id": 1,
        "product_name": "iPhone 15 Pro Max 256GB",
        "period": "30d",
        "price_points": [
            { "date": "2024-12-16", "min": 29990000, "max": 30500000, "avg": 30200000 },
            { "date": "2024-12-17", "min": 29500000, "max": 30200000, "avg": 29800000 }
        ],
        "statistics": {
            "min": 27990000,
            "max": 32990000,
            "avg": 29800000,
            "volatility": 0.034,
            "trend": "down",
            "total_data_points": 120
        }
    }
}
```

---

### GET /products/{id}/reviews
Reviews của sản phẩm.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| rating | int | - | Filter theo rating (1-5) |
| sort_by | string | recent | recent, helpful, rating_high, rating_low |
| show_fake | bool | false | Hiện cả reviews bị đánh dấu fake |
| page | int | 1 | |
| per_page | int | 20 | |

**Response:**
```json
{
    "success": true,
    "data": {
        "summary": {
            "total_reviews": 1520,
            "avg_rating": 4.8,
            "rating_distribution": { "5": 1200, "4": 200, "3": 80, "2": 25, "1": 15 },
            "fake_review_percent": 5.2,
            "sentiment": { "positive": 85.5, "neutral": 10.2, "negative": 4.3 }
        },
        "reviews": [
            {
                "id": 101,
                "author_name": "Nguyễn V.A",
                "rating": 5,
                "content": "Sản phẩm chính hãng, giao hàng nhanh...",
                "created_date": "2025-01-10",
                "likes_count": 15,
                "is_purchased": true,
                "sentiment_score": 0.92,
                "is_fake": false,
                "fake_confidence": 0.05
            }
        ]
    }
}
```

---

## 2. Analytics API

### GET /analytics/trending
Sản phẩm đang trending (giảm giá mạnh, bán chạy).

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| type | string | price_drop | price_drop, best_seller, best_deal, most_reviewed |
| category_id | int | - | Filter theo danh mục |
| platform | string | - | Filter theo sàn |
| limit | int | 20 | Max 50 |

---

### GET /analytics/price-comparison
So sánh giá sản phẩm giữa các sàn.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| q | string | required | Tên sản phẩm cần so sánh |
| category_id | int | - | Thu hẹp phạm vi tìm |

**Response:**
```json
{
    "success": true,
    "data": {
        "query": "iPhone 15 Pro Max",
        "comparisons": [
            {
                "product_name": "iPhone 15 Pro Max 256GB",
                "platforms": [
                    { "platform": "shopee", "price": 28990000, "rating": 4.8, "url": "..." },
                    { "platform": "tiki", "price": 29490000, "rating": 4.7, "url": "..." },
                    { "platform": "lazada", "price": 29190000, "rating": 4.6, "url": "..." }
                ],
                "best_price": { "platform": "shopee", "price": 28990000 },
                "price_diff_percent": 1.72
            }
        ]
    }
}
```

---

### GET /analytics/market-overview
Tổng quan thị trường.

**Response:**
```json
{
    "success": true,
    "data": {
        "total_products_tracked": 52340,
        "total_price_points": 1250000,
        "platforms": {
            "shopee": { "products": 25000, "avg_discount": 15.3 },
            "tiki": { "products": 18000, "avg_discount": 12.1 },
            "lazada": { "products": 9340, "avg_discount": 18.7 }
        },
        "top_categories_by_discount": [...],
        "price_trend_index": { "overall": "stable", "electronics": "down", "fashion": "up" },
        "last_updated": "2025-01-15T10:30:00Z"
    }
}
```

---

### GET /analytics/category-insights/{category_id}
Phân tích theo danh mục.

---

## 3. AI Insights API

### GET /ai/predict-price/{product_id}
Dự đoán giá sản phẩm.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| days | int | 7 | Dự đoán bao nhiêu ngày (7, 14, 30) |

**Response:**
```json
{
    "success": true,
    "data": {
        "product_id": 1,
        "current_price": 28990000,
        "predictions": [
            { "date": "2025-01-16", "predicted_price": 28800000, "confidence": 0.85 },
            { "date": "2025-01-17", "predicted_price": 28650000, "confidence": 0.82 },
            { "date": "2025-01-22", "predicted_price": 28500000, "confidence": 0.70 }
        ],
        "recommendation": {
            "signal": "hold",
            "reason": "Giá đang có xu hướng giảm, dự kiến chạm đáy trong 5-7 ngày",
            "best_buy_date": "2025-01-22",
            "potential_savings": 490000
        },
        "model_info": {
            "model": "prophet_v2",
            "mae": 245000,
            "mape": 0.82
        }
    }
}
```

---

### GET /ai/anomalies
Phát hiện giá bất thường.

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "product_id": 42,
            "product_name": "Samsung Galaxy S24",
            "platform": "shopee",
            "anomaly_type": "sudden_price_drop",
            "anomaly_score": 0.95,
            "current_price": 12990000,
            "expected_price": 18990000,
            "deviation_percent": -31.6,
            "possible_reason": "Flash sale hoặc giá ảo",
            "detected_at": "2025-01-15T08:00:00Z"
        }
    ]
}
```

---

### POST /ai/check-reviews
Phân tích reviews, phát hiện fake.

**Request Body:**
```json
{
    "product_id": 1
}
```

---

## 4. Alerts API

### POST /alerts
Tạo price alert.

**Request Body:**
```json
{
    "product_id": 1,
    "user_email": "user@example.com",
    "target_price": 27000000,
    "alert_type": "below"
}
```

### GET /alerts?email={email}
Danh sách alerts của user.

### DELETE /alerts/{id}
Xóa alert.

---

## 5. System API

### GET /health
Health check.

### GET /stats/crawl
Thống kê crawl gần nhất.

### GET /stats/system
System metrics (cho Grafana).

---

## 6. Pydantic Models (Reference)

```python
# === Request Models ===

class ProductSearchParams(BaseModel):
    q: Optional[str] = None
    category_id: Optional[int] = None
    platform: Optional[str] = None
    min_price: Optional[int] = Field(None, ge=0)
    max_price: Optional[int] = Field(None, ge=0)
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    min_discount: Optional[float] = Field(None, ge=0, le=100)
    sort_by: str = "relevance"
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)

class CreateAlertRequest(BaseModel):
    product_id: int
    user_email: EmailStr
    target_price: int = Field(gt=0)
    alert_type: Literal["below", "above", "any_change"] = "below"

# === Response Models ===

class ProductResponse(BaseModel):
    id: int
    name: str
    platform: str
    category: Optional[str]
    url: str
    image_url: Optional[str]
    current_price: int
    original_price: Optional[int]
    discount_percent: Optional[float]
    rating_avg: Optional[float]
    rating_count: int
    total_sold: int
    seller_name: Optional[str]
    is_official_store: bool
    ai_insights: Optional[AIInsightsResponse]

class PricePointResponse(BaseModel):
    date: str
    min: int
    max: int
    avg: int

class PredictionResponse(BaseModel):
    date: str
    predicted_price: int
    confidence: float
```
