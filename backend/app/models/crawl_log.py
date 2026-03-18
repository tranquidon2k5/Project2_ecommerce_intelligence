from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String, Integer, DateTime, Numeric,
    ForeignKey, Index, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class CrawlLog(Base):
    __tablename__ = "crawl_logs"
    __table_args__ = (
        CheckConstraint("status IN ('running', 'success', 'failed', 'partial')", name="ck_crawl_logs_status"),
        Index("idx_crawl_logs_status", "status", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    platform_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("platforms.id"), nullable=True)
    spider_name: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="running", nullable=False)
    products_crawled: Mapped[int] = mapped_column(Integer, default=0)
    products_new: Mapped[int] = mapped_column(Integer, default=0)
    products_updated: Mapped[int] = mapped_column(Integer, default=0)
    errors_count: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Numeric(10, 2), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    platform: Mapped[Optional["Platform"]] = relationship("Platform", back_populates="crawl_logs")

    def __repr__(self) -> str:
        return f"<CrawlLog(id={self.id}, spider={self.spider_name!r}, status={self.status!r})>"


class MLModelMetrics(Base):
    __tablename__ = "ml_model_metrics"
    __table_args__ = (
        Index("idx_ml_metrics_model", "model_name", "trained_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_name: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_value: Mapped[Optional[float]] = mapped_column(Numeric(10, 6), nullable=True)
    training_samples: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    trained_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<MLModelMetrics(id={self.id}, model={self.model_name!r}, metric={self.metric_name!r})>"
