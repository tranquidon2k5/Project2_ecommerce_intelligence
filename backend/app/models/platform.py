from datetime import datetime
from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    products: Mapped[list["Product"]] = relationship("Product", back_populates="platform")
    crawl_logs: Mapped[list["CrawlLog"]] = relationship("CrawlLog", back_populates="platform")

    def __repr__(self) -> str:
        return f"<Platform(id={self.id}, name={self.name!r})>"
