from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime, Text,
    Numeric, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import BIGINT
from ..database import Base


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        UniqueConstraint("platform_id", "external_id", name="uq_products_platform_external"),
        Index("idx_products_platform", "platform_id"),
        Index("idx_products_category", "category_id"),
        Index("idx_products_price", "current_price"),
        Index("idx_products_rating", "rating_avg"),
        Index("idx_products_last_crawled", "last_crawled_at"),
        # GIN trigram index created in migration (requires pg_trgm extension)
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[int] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    external_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seller_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    seller_rating: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    current_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    discount_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    rating_avg: Mapped[Optional[float]] = mapped_column(Numeric(3, 2), nullable=True)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)
    total_sold: Mapped[int] = mapped_column(Integer, default=0)
    is_official_store: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_crawled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    platform: Mapped["Platform"] = relationship("Platform", back_populates="products")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="products")
    price_history: Mapped[list["PriceHistory"]] = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    analytics: Mapped[list["ProductAnalytics"]] = relationship("ProductAnalytics", back_populates="product", cascade="all, delete-orphan")
    alerts: Mapped[list["PriceAlert"]] = relationship("PriceAlert", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name[:50]!r}, price={self.current_price})>"


class PriceHistory(Base):
    __tablename__ = "price_history"
    __table_args__ = (
        Index("idx_price_history_product_time", "product_id", "crawled_at"),
        # BRIN index created in migration for crawled_at (space-efficient for time-series)
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    original_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    discount_percent: Mapped[Optional[float]] = mapped_column(Numeric(5, 2), nullable=True)
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="price_history")

    def __repr__(self) -> str:
        return f"<PriceHistory(id={self.id}, product_id={self.product_id}, price={self.price})>"
