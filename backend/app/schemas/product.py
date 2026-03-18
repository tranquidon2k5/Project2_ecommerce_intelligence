from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class CategoryBriefResponse(BaseModel):
    id: int
    name: str
    slug: str

    model_config = {"from_attributes": True}


class AIInsightsResponse(BaseModel):
    buy_signal: Optional[str] = None          # 'strong_buy', 'buy', 'hold', 'wait'
    buy_signal_reason: Optional[str] = None
    trend_direction: Optional[str] = None     # 'up', 'down', 'stable'
    predicted_price_7d: Optional[int] = None
    anomaly_score: Optional[float] = None
    fake_review_percent: Optional[float] = None


class PriceStatsResponse(BaseModel):
    min_30d: Optional[int] = None
    max_30d: Optional[int] = None
    avg_30d: Optional[int] = None
    current_vs_avg: Optional[float] = None    # percentage difference


class ProductSearchParams(BaseModel):
    q: Optional[str] = Field(None, description="Search query")
    category_id: Optional[int] = Field(None, description="Filter by category")
    platform: Optional[str] = Field(None, description="Filter by platform: shopee, tiki, lazada")
    min_price: Optional[int] = Field(None, ge=0, description="Minimum price in VND")
    max_price: Optional[int] = Field(None, ge=0, description="Maximum price in VND")
    min_rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Minimum rating")
    min_discount: Optional[float] = Field(None, ge=0.0, le=100.0, description="Minimum discount %")
    sort_by: str = Field("relevance", description="Sort: relevance, price_asc, price_desc, rating, discount, popular")
    page: int = Field(1, ge=1, description="Page number")
    per_page: int = Field(20, ge=1, le=100, description="Items per page")


class ProductResponse(BaseModel):
    id: int
    name: str
    platform: str
    category: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    current_price: int
    original_price: Optional[int] = None
    discount_percent: Optional[float] = None
    rating_avg: Optional[float] = None
    rating_count: int
    total_sold: int
    seller_name: Optional[str] = None
    is_official_store: bool
    ai_insights: Optional[AIInsightsResponse] = None
    last_crawled_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProductDetailResponse(BaseModel):
    id: int
    name: str
    platform: str
    category: Optional[CategoryBriefResponse] = None
    url: str
    image_url: Optional[str] = None
    current_price: int
    original_price: Optional[int] = None
    discount_percent: Optional[float] = None
    rating_avg: Optional[float] = None
    rating_count: int
    total_sold: int
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    is_official_store: bool
    first_seen_at: Optional[datetime] = None
    last_crawled_at: Optional[datetime] = None
    price_stats: Optional[PriceStatsResponse] = None
    ai_insights: Optional[AIInsightsResponse] = None

    model_config = {"from_attributes": True}


class PricePointResponse(BaseModel):
    date: str
    min: int
    max: int
    avg: int


class PriceHistoryStatistics(BaseModel):
    min: int
    max: int
    avg: int
    volatility: Optional[float] = None
    trend: Optional[str] = None
    total_data_points: int


class PriceHistoryResponse(BaseModel):
    product_id: int
    product_name: str
    period: str
    price_points: List[PricePointResponse]
    statistics: PriceHistoryStatistics


class ReviewResponse(BaseModel):
    id: int
    author_name: Optional[str] = None
    rating: Optional[int] = None
    content: Optional[str] = None
    created_date: Optional[datetime] = None
    likes_count: int
    is_purchased: Optional[bool] = None
    sentiment_score: Optional[float] = None
    is_fake: Optional[bool] = None
    fake_confidence: Optional[float] = None

    model_config = {"from_attributes": True}


class RatingDistribution(BaseModel):
    five: int = Field(0, alias="5")
    four: int = Field(0, alias="4")
    three: int = Field(0, alias="3")
    two: int = Field(0, alias="2")
    one: int = Field(0, alias="1")

    model_config = {"populate_by_name": True}


class SentimentSummary(BaseModel):
    positive: float = 0.0
    neutral: float = 0.0
    negative: float = 0.0


class ReviewSummaryResponse(BaseModel):
    total_reviews: int
    avg_rating: Optional[float] = None
    rating_distribution: dict
    fake_review_percent: float = 0.0
    sentiment: SentimentSummary
    reviews: List[ReviewResponse]
