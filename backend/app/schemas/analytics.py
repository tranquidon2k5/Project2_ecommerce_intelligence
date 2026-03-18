from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class TrendingParams(BaseModel):
    type: str = Field("price_drop", description="price_drop, best_seller, best_deal, most_reviewed")
    category_id: Optional[int] = None
    platform: Optional[str] = None
    limit: int = Field(20, ge=1, le=50)


class PlatformPriceInfo(BaseModel):
    platform: str
    price: int
    rating: Optional[float] = None
    url: str


class ProductComparison(BaseModel):
    product_name: str
    platforms: List[PlatformPriceInfo]
    best_price: PlatformPriceInfo
    price_diff_percent: float


class PriceComparisonResponse(BaseModel):
    query: str
    comparisons: List[ProductComparison]


class PlatformStats(BaseModel):
    products: int
    avg_discount: float


class MarketOverviewResponse(BaseModel):
    total_products_tracked: int
    total_price_points: int
    platforms: Dict[str, PlatformStats]
    top_categories_by_discount: List[Dict[str, Any]]
    last_updated: Optional[str] = None


class CategoryInsightsResponse(BaseModel):
    category_id: int
    category_name: str
    total_products: int
    avg_price: Optional[int] = None
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    avg_discount: Optional[float] = None
    top_platforms: List[Dict[str, Any]]
