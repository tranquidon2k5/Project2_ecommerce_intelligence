from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..database import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("categories.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Self-referencing relationship
    parent: Mapped[Optional["Category"]] = relationship("Category", remote_side="Category.id", back_populates="children")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")

    # Products
    products: Mapped[list["Product"]] = relationship("Product", back_populates="category")

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name={self.name!r}, slug={self.slug!r})>"
