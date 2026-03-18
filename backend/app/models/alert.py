from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, BigInteger, Boolean, DateTime,
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class PriceAlert(Base):
    __tablename__ = "price_alerts"
    __table_args__ = (
        CheckConstraint("alert_type IN ('below', 'above', 'any_change')", name="ck_alerts_type"),
        Index("idx_alerts_product", "product_id"),
        Index("idx_alerts_email", "user_email"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    target_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    alert_type: Mapped[str] = mapped_column(String(10), default="below", nullable=False)
    is_triggered: Mapped[bool] = mapped_column(Boolean, default=False)
    triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product: Mapped["Product"] = relationship("Product", back_populates="alerts")

    def __repr__(self) -> str:
        return f"<PriceAlert(id={self.id}, product_id={self.product_id}, email={self.user_email!r})>"
