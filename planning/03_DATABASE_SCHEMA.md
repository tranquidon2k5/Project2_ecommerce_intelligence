# 🗄️ Database Schema - ShopSmart Analytics

---

## 1. ER Diagram

```
┌─────────────────────┐       ┌─────────────────────────┐
│     platforms        │       │       categories         │
│─────────────────────│       │─────────────────────────│
│ id (PK)             │       │ id (PK)                  │
│ name                │       │ name                     │
│ base_url            │       │ slug                     │
│ is_active           │       │ parent_id (FK self)      │
│ created_at          │       │ created_at               │
└────────┬────────────┘       └────────────┬─────────────┘
         │                                  │
         │ 1:N                              │ 1:N
         │                                  │
┌────────┴──────────────────────────────────┴─────────────┐
│                      products                            │
│─────────────────────────────────────────────────────────│
│ id (PK)                                                  │
│ platform_id (FK → platforms)                             │
│ category_id (FK → categories)                            │
│ external_id (unique per platform)                        │
│ name                                                     │
│ slug                                                     │
│ url                                                      │
│ image_url                                                │
│ seller_name                                              │
│ seller_rating                                            │
│ current_price                                            │
│ original_price                                           │
│ discount_percent                                         │
│ rating_avg                                               │
│ rating_count                                             │
│ total_sold                                               │
│ is_official_store                                        │
│ is_active                                                │
│ first_seen_at                                            │
│ last_crawled_at                                          │
│ created_at                                               │
│ updated_at                                               │
└──┬──────────────────┬────────────────────┬──────────────┘
   │                  │                    │
   │ 1:N              │ 1:N               │ 1:N
   │                  │                   │
┌──┴───────────┐ ┌────┴──────────┐  ┌─────┴──────────────┐
│price_history │ │   reviews     │  │  product_analytics │
│──────────────│ │───────────────│  │────────────────────│
│ id (PK)      │ │ id (PK)       │  │ id (PK)            │
│ product_id   │ │ product_id    │  │ product_id (FK)    │
│ (FK)         │ │ (FK)          │  │ date               │
│ price        │ │ external_id   │  │ min_price          │
│ original_    │ │ author_name   │  │ max_price          │
│  price       │ │ rating        │  │ avg_price          │
│ discount_    │ │ content       │  │ price_volatility   │
│  percent     │ │ created_date  │  │ trend_direction    │
│ in_stock     │ │ likes_count   │  │ predicted_price_7d │
│ crawled_at   │ │ is_purchased  │  │ anomaly_score      │
│ created_at   │ │ sentiment_    │  │ buy_signal         │
└──────────────┘ │  score        │  │ created_at         │
                 │ is_fake       │  └────────────────────┘
                 │ fake_         │
                 │  confidence   │
                 │ crawled_at    │
                 │ created_at    │
                 └───────────────┘

┌─────────────────────────┐     ┌─────────────────────────┐
│     price_alerts        │     │     crawl_logs          │
│─────────────────────────│     │─────────────────────────│
│ id (PK)                 │     │ id (PK)                  │
│ product_id (FK)         │     │ platform_id (FK)         │
│ user_email              │     │ spider_name              │
│ target_price            │     │ status (success/fail)    │
│ alert_type              │     │ products_crawled         │
│  (below/above/any)      │     │ products_new             │
│ is_triggered            │     │ products_updated         │
│ triggered_at            │     │ errors_count             │
│ is_active               │     │ duration_seconds         │
│ created_at              │     │ started_at               │
│ updated_at              │     │ finished_at              │
└─────────────────────────┘     │ created_at               │
                                └──────────────────────────┘

┌─────────────────────────┐
│   ml_model_metrics      │
│─────────────────────────│
│ id (PK)                  │
│ model_name               │
│ model_version            │
│ metric_name              │
│ metric_value             │
│ training_samples         │
│ trained_at               │
│ created_at               │
└──────────────────────────┘
```

## 2. SQL Migration Scripts

### Table: platforms
```sql
CREATE TABLE platforms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    base_url VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO platforms (name, base_url) VALUES
    ('shopee', 'https://shopee.vn'),
    ('tiki', 'https://tiki.vn'),
    ('lazada', 'https://lazada.vn');
```

### Table: categories
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    parent_id INTEGER REFERENCES categories(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_slug ON categories(slug);
```

### Table: products
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER NOT NULL REFERENCES platforms(id),
    category_id INTEGER REFERENCES categories(id),
    external_id VARCHAR(100) NOT NULL,
    name VARCHAR(500) NOT NULL,
    slug VARCHAR(500),
    url TEXT NOT NULL,
    image_url TEXT,
    seller_name VARCHAR(200),
    seller_rating DECIMAL(3,2),
    current_price BIGINT NOT NULL,        -- Giá VND (không dùng float)
    original_price BIGINT,
    discount_percent DECIMAL(5,2),
    rating_avg DECIMAL(3,2),
    rating_count INTEGER DEFAULT 0,
    total_sold INTEGER DEFAULT 0,
    is_official_store BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    first_seen_at TIMESTAMP DEFAULT NOW(),
    last_crawled_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(platform_id, external_id)
);

CREATE INDEX idx_products_platform ON products(platform_id);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_price ON products(current_price);
CREATE INDEX idx_products_rating ON products(rating_avg);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops);
CREATE INDEX idx_products_last_crawled ON products(last_crawled_at);
```

### Table: price_history
```sql
CREATE TABLE price_history (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    price BIGINT NOT NULL,
    original_price BIGINT,
    discount_percent DECIMAL(5,2),
    in_stock BOOLEAN DEFAULT TRUE,
    crawled_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Partition by month for performance (Big Data optimization)
-- Trong thực tế, sẽ dùng partitioning. MVP dùng index.
CREATE INDEX idx_price_history_product_time ON price_history(product_id, crawled_at DESC);
CREATE INDEX idx_price_history_crawled ON price_history(crawled_at);
```

### Table: reviews
```sql
CREATE TABLE reviews (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    external_id VARCHAR(100),
    author_name VARCHAR(200),
    rating SMALLINT CHECK (rating >= 1 AND rating <= 5),
    content TEXT,
    created_date TIMESTAMP,
    likes_count INTEGER DEFAULT 0,
    is_purchased BOOLEAN,
    sentiment_score DECIMAL(4,3),      -- -1.0 to 1.0
    is_fake BOOLEAN,
    fake_confidence DECIMAL(4,3),      -- 0.0 to 1.0
    crawled_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(product_id, external_id)
);

CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_reviews_fake ON reviews(is_fake) WHERE is_fake = TRUE;
CREATE INDEX idx_reviews_sentiment ON reviews(sentiment_score);
```

### Table: product_analytics
```sql
CREATE TABLE product_analytics (
    id BIGSERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    min_price BIGINT,
    max_price BIGINT,
    avg_price BIGINT,
    price_volatility DECIMAL(8,4),     -- Standard deviation
    trend_direction VARCHAR(10),        -- 'up', 'down', 'stable'
    predicted_price_7d BIGINT,
    anomaly_score DECIMAL(4,3),        -- 0.0 to 1.0
    buy_signal VARCHAR(20),            -- 'strong_buy', 'buy', 'hold', 'wait'
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(product_id, date)
);

CREATE INDEX idx_analytics_product_date ON product_analytics(product_id, date DESC);
CREATE INDEX idx_analytics_signal ON product_analytics(buy_signal);
```

### Table: price_alerts
```sql
CREATE TABLE price_alerts (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    user_email VARCHAR(255) NOT NULL,
    target_price BIGINT NOT NULL,
    alert_type VARCHAR(10) NOT NULL DEFAULT 'below'
        CHECK (alert_type IN ('below', 'above', 'any_change')),
    is_triggered BOOLEAN DEFAULT FALSE,
    triggered_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_alerts_product ON price_alerts(product_id);
CREATE INDEX idx_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE;
```

### Table: crawl_logs
```sql
CREATE TABLE crawl_logs (
    id SERIAL PRIMARY KEY,
    platform_id INTEGER REFERENCES platforms(id),
    spider_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'running'
        CHECK (status IN ('running', 'success', 'failed', 'partial')),
    products_crawled INTEGER DEFAULT 0,
    products_new INTEGER DEFAULT 0,
    products_updated INTEGER DEFAULT 0,
    errors_count INTEGER DEFAULT 0,
    duration_seconds DECIMAL(10,2),
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_crawl_logs_status ON crawl_logs(status, started_at DESC);
```

### Table: ml_model_metrics
```sql
CREATE TABLE ml_model_metrics (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    metric_name VARCHAR(50) NOT NULL,
    metric_value DECIMAL(10,6),
    training_samples INTEGER,
    trained_at TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ml_metrics_model ON ml_model_metrics(model_name, trained_at DESC);
```

## 3. Useful Queries (Cho reference)

### Lịch sử giá 30 ngày
```sql
SELECT 
    ph.crawled_at::DATE as date,
    MIN(ph.price) as min_price,
    MAX(ph.price) as max_price,
    AVG(ph.price)::BIGINT as avg_price
FROM price_history ph
WHERE ph.product_id = :product_id
    AND ph.crawled_at >= NOW() - INTERVAL '30 days'
GROUP BY ph.crawled_at::DATE
ORDER BY date;
```

### Top sản phẩm giảm giá mạnh nhất hôm nay
```sql
SELECT 
    p.name, p.current_price, p.original_price, p.discount_percent,
    pl.name as platform
FROM products p
JOIN platforms pl ON p.platform_id = pl.id
WHERE p.discount_percent > 20
    AND p.is_active = TRUE
ORDER BY p.discount_percent DESC
LIMIT 20;
```

### Phát hiện giá bất thường
```sql
SELECT 
    p.name, pa.date, pa.anomaly_score, pa.avg_price,
    pa.predicted_price_7d
FROM product_analytics pa
JOIN products p ON pa.product_id = p.id
WHERE pa.anomaly_score > 0.8
    AND pa.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY pa.anomaly_score DESC;
```
