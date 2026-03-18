# Testing Agent

## Role
Bạn là agent chuyên viết và chạy tests cho ShopSmart Analytics.

## Context
Đọc codebase hiện tại để hiểu implementation, sau đó viết tests.

## Tasks

### 1. Backend Tests
`backend/tests/conftest.py`:
- Pytest fixtures: test database, test client, sample data
- Use SQLite in-memory hoặc test PostgreSQL container

`backend/tests/test_products.py`:
- Test GET /products (search, filter, sort, pagination)
- Test GET /products/{id}
- Test GET /products/{id}/price-history
- Test 404 cases, validation errors

`backend/tests/test_analytics.py`:
- Test trending, price comparison, market overview
- Test with empty data, edge cases

`backend/tests/test_ml.py`:
- Test price predictor (with sufficient data, with insufficient data)
- Test anomaly detector
- Test review analyzer
- Test buy signal logic

### 2. Crawler Tests
`crawler/tests/test_spiders.py`:
- Test item parsing from sample responses
- Test data cleaning pipeline
- Mock HTTP responses

`crawler/tests/test_pipelines.py`:
- Test CleaningPipeline
- Test PostgresPipeline (mock DB)

### 3. Frontend Tests (Optional)
- Component rendering tests
- API service mocking

## Tools
- pytest, pytest-asyncio (backend)
- Jest, React Testing Library (frontend, optional)
