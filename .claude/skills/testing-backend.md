---
name: Testing Backend
description: How to write and run pytest tests for the backend API and services
---

# Testing Backend Skill

## When to Use
When you need to write unit or integration tests for the backend.

## Steps

### 1. Setup Test Fixtures

File: `backend/tests/conftest.py`

```python
import asyncio
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import Platform, Category, Product

# Use SQLite in-memory for fast tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_data(db_session):
    """Seed sample data for tests."""
    platform = Platform(name="tiki", base_url="https://tiki.vn")
    db_session.add(platform)
    await db_session.flush()

    category = Category(name="Điện thoại", slug="dien-thoai")
    db_session.add(category)
    await db_session.flush()

    product = Product(
        platform_id=platform.id,
        category_id=category.id,
        external_id="tiki_12345",
        name="iPhone 15 Pro Max 256GB",
        url="https://tiki.vn/iphone-15",
        current_price=28990000,
        original_price=34990000,
        discount_percent=17.15,
        rating_avg=4.8,
        rating_count=1520,
        total_sold=5200,
        is_official_store=True,
    )
    db_session.add(product)
    await db_session.commit()

    return {"platform": platform, "category": category, "product": product}
```

### 2. Write API Endpoint Tests

File: `backend/tests/test_products.py`

```python
import pytest


@pytest.mark.asyncio
class TestProductsAPI:

    async def test_list_products(self, client, sample_data):
        response = await client.get("/api/v1/products")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert isinstance(data["data"], list)
        assert data["meta"]["total"] >= 1

    async def test_list_products_search(self, client, sample_data):
        response = await client.get("/api/v1/products", params={"q": "iPhone"})
        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) >= 1
        assert "iPhone" in data["data"][0]["name"]

    async def test_list_products_filter_platform(self, client, sample_data):
        response = await client.get("/api/v1/products", params={"platform": "tiki"})
        assert response.status_code == 200

    async def test_list_products_pagination(self, client, sample_data):
        response = await client.get("/api/v1/products", params={"page": 1, "per_page": 5})
        assert response.status_code == 200

        data = response.json()
        assert data["meta"]["page"] == 1
        assert data["meta"]["per_page"] == 5

    async def test_get_product_by_id(self, client, sample_data):
        product = sample_data["product"]
        response = await client.get(f"/api/v1/products/{product.id}")
        assert response.status_code == 200

        data = response.json()
        assert data["success"] is True
        assert data["data"]["id"] == product.id
        assert data["data"]["name"] == "iPhone 15 Pro Max 256GB"

    async def test_get_product_not_found(self, client):
        response = await client.get("/api/v1/products/99999")
        assert response.status_code == 404

    async def test_get_price_history(self, client, sample_data):
        product = sample_data["product"]
        response = await client.get(f"/api/v1/products/{product.id}/price-history")
        assert response.status_code == 200

    async def test_invalid_pagination(self, client):
        response = await client.get("/api/v1/products", params={"page": 0})
        assert response.status_code == 422  # Pydantic validation error

    async def test_invalid_per_page(self, client):
        response = await client.get("/api/v1/products", params={"per_page": 200})
        assert response.status_code == 422
```

### 3. Write Service Layer Tests

File: `backend/tests/test_services.py`

```python
import pytest
from app.services.product_service import get_products, get_product_by_id


@pytest.mark.asyncio
class TestProductService:

    async def test_get_products_returns_list(self, db_session, sample_data):
        items, total = await get_products(db_session)
        assert isinstance(items, list)
        assert total >= 1

    async def test_get_products_search_filter(self, db_session, sample_data):
        items, total = await get_products(db_session, q="iPhone")
        assert total >= 1
        assert "iPhone" in items[0].name

    async def test_get_product_by_id_found(self, db_session, sample_data):
        product = sample_data["product"]
        result = await get_product_by_id(db_session, product.id)
        assert result is not None
        assert result.id == product.id

    async def test_get_product_by_id_not_found(self, db_session):
        result = await get_product_by_id(db_session, 99999)
        assert result is None
```

### 4. Write ML Tests

File: `backend/tests/test_ml.py`

```python
import pytest
from app.ml.recommender import BuyRecommender


class TestBuyRecommender:
    def test_strong_buy_signal(self):
        recommender = BuyRecommender()
        signal = recommender.compute_signal(
            price_trend="down",
            anomaly_score=0.1,
            price_vs_avg_30d=-5.0,
        )
        assert signal["signal"] in ["strong_buy", "buy"]
        assert signal["reason"]  # has explanation text

    def test_wait_signal(self):
        recommender = BuyRecommender()
        signal = recommender.compute_signal(
            price_trend="up",
            anomaly_score=0.8,
            price_vs_avg_30d=10.0,
        )
        assert signal["signal"] in ["hold", "wait"]
```

## Running Tests

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run specific file
python -m pytest tests/test_products.py -v

# Run specific test
python -m pytest tests/test_products.py -k "test_list_products" -v

# With coverage
python -m pytest tests/ --cov=app --cov-report=html

# Stop on first failure
python -m pytest tests/ -x
```

## Test Dependencies

Add to `backend/requirements.txt`:
```
pytest
pytest-asyncio
httpx
aiosqlite
pytest-cov
```

## Response Format Assertions

Every API test should verify the standard response format:

```python
data = response.json()
assert "success" in data
assert "data" in data
# For list endpoints:
assert "meta" in data
assert "page" in data["meta"]
assert "total" in data["meta"]
```
