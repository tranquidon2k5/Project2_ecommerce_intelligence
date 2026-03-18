from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime, Text,
    SmallInteger, Numeric, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        UniqueConstraint("product_id", "external_id", name="uq_reviews_product_external"),
        Index("idx_reviews_product", "product_id"),
        Index("idx_reviews_sentiment", "sentiment_score"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    external_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    author_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    rating: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    is_purchased: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    is_fake: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    fake_confidence: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="reviews")

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, product_id={self.product_id}, rating={self.rating})>"
