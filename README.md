# ShopSmart Analytics

> E-commerce intelligence platform — track prices, detect anomalies, get AI-powered buy recommendations.

## Overview

ShopSmart Analytics crawls product data from Vietnamese e-commerce platforms (Shopee, Tiki, Lazada), analyzes price trends, detects fake reviews, and provides smart buy recommendations via an interactive dashboard.

## Quick Start

```bash
cp .env.example .env
docker-compose up
```

Open http://localhost:3000 for the dashboard, http://localhost:8000/docs for the API.

## Tech Stack

- **Backend:** FastAPI + SQLAlchemy async + PostgreSQL 16 + Redis 7
- **Frontend:** React 18 + Vite + TailwindCSS + Recharts
- **Crawler:** Scrapy + Playwright
- **ML:** Prophet (price prediction) + IsolationForest (anomaly) + Random Forest (fake reviews)

## Features

- Real-time price tracking across Shopee, Tiki, Lazada
- Price history charts with AI predictions
- Anomaly detection (fake discounts, price manipulation)
- Fake review detection (NLP)
- Price drop alerts via email
- Market overview dashboard

## Documentation

See `planning/` for architecture, database schema, and API design docs.
