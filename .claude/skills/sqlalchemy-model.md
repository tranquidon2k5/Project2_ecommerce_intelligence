---
name: SQLAlchemy Model
description: How to create or modify SQLAlchemy models and run Alembic migrations
---

# SQLAlchemy Model Skill

## When to Use
When you need to create a new database table or modify an existing one.

## Steps

### 1. Define Model

File: `backend/app/models/<entity>.py`

```python
from sqlalchemy import (
    Column, Integer, BigInteger, String, Boolean, DateTime,
    ForeignKey, DECIMAL, Text, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class NewEntity(Base):
    __tablename__ = "new_entities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    # VND prices → BIGINT, never Float
    price = Column(BigInteger, nullable=False)
    # Decimals for scores/percentages
    score = Column(DECIMAL(4, 3))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Foreign key
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)

    # Relationship
    product = relationship("Product", back_populates="new_entities")

    # Indexes
    __table_args__ = (
        Index("idx_new_entities_product", "product_id"),
        Index("idx_new_entities_active", "is_active", postgresql_where=(is_active == True)),
    )

    def __repr__(self):
        return f"<NewEntity(id={self.id}, name='{self.name}')>"
```

### 2. Register in `__init__.py`

File: `backend/app/models/__init__.py`

```python
from app.models.new_entity import NewEntity  # add this line
```

### 3. Add Back-Reference (if FK exists)

In the related model (e.g., `backend/app/models/product.py`):

```python
new_entities = relationship("NewEntity", back_populates="product", cascade="all, delete-orphan")
```

### 4. Generate Migration

```bash
cd backend
alembic revision --autogenerate -m "add_new_entities_table"
```

Review the generated file in `backend/migrations/versions/`.

### 5. Apply Migration

```bash
alembic upgrade head
```

## Project Conventions

| Convention | Rule |
|------------|------|
| **VND prices** | Always `BigInteger` (BIGINT), never Float |
| **Time-series data** | Use BRIN index on timestamp columns |
| **Text search** | GIN trigram index: `Index('idx_name_trgm', 'name', postgresql_using='gin', postgresql_ops={'name': 'gin_trgm_ops'})` |
| **Partitioning** | `price_history` uses range partitioning by month on `crawled_at` |
| **Soft delete** | Use `is_active` Boolean flag |
| **Timestamps** | Always include `created_at` with `server_default=func.now()` |
| **Cascades** | FK with `ondelete="CASCADE"` for child tables |

## Verify

```bash
# Check migration SQL (dry run)
alembic upgrade head --sql

# Verify table exists
python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.get_columns('new_entities'))
"
```
