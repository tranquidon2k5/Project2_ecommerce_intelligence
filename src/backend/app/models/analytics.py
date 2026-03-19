from datetime import datetime, date
from typing import Optional
from sqlalchemy import (
    String, Integer, BigInteger, DateTime, Date,
    Numeric, ForeignKey, Index, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class ProductAnalytics(Base):
    __tablename__ = "product_analytics"
    __table_args__ = (
        UniqueConstraint("product_id", "date", name="uq_analytics_product_date"),
        Index("idx_analytics_product_date", "product_id", "date"),
        Index("idx_analytics_signal", "buy_signal"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    min_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    avg_price: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    price_volatility: Mapped[Optional[float]] = mapped_column(Numeric(8, 4), nullable=True)
    trend_direction: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # 'up', 'down', 'stable'
    predicted_price_7d: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    anomaly_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 3), nullable=True)
    buy_signal: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # 'strong_buy', 'buy', 'hold', 'wait'
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="analytics")

    def __repr__(self) -> str:
        return f"<ProductAnalytics(id={self.id}, product_id={self.product_id}, date={self.date})>"
