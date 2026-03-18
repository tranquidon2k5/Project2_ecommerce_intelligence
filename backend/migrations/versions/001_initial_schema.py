"""initial_schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pg_trgm extension for fuzzy text search
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # platforms
    op.create_table('platforms',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('base_url', sa.String(255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )

    # categories
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug'),
    )
    op.create_index('idx_categories_parent', 'categories', ['parent_id'])
    op.create_index('idx_categories_slug', 'categories', ['slug'])

    # products
    op.create_table('products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(100), nullable=False),
        sa.Column('name', sa.String(500), nullable=False),
        sa.Column('slug', sa.String(500), nullable=True),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('image_url', sa.Text(), nullable=True),
        sa.Column('seller_name', sa.String(200), nullable=True),
        sa.Column('seller_rating', sa.Numeric(3, 2), nullable=True),
        sa.Column('current_price', sa.BigInteger(), nullable=False),
        sa.Column('original_price', sa.BigInteger(), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('rating_avg', sa.Numeric(3, 2), nullable=True),
        sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('total_sold', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_official_store', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('first_seen_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('last_crawled_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id']),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('platform_id', 'external_id', name='uq_products_platform_external'),
    )
    op.create_index('idx_products_platform', 'products', ['platform_id'])
    op.create_index('idx_products_category', 'products', ['category_id'])
    op.create_index('idx_products_price', 'products', ['current_price'])
    op.create_index('idx_products_rating', 'products', ['rating_avg'])
    op.create_index('idx_products_last_crawled', 'products', ['last_crawled_at'])
    # GIN trigram index for full-text search
    op.execute("CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops)")

    # price_history
    op.create_table('price_history',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.BigInteger(), nullable=False),
        sa.Column('original_price', sa.BigInteger(), nullable=True),
        sa.Column('discount_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('in_stock', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('crawled_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_price_history_product_time', 'price_history', ['product_id', 'crawled_at'])
    # BRIN index — space-efficient for time-series data
    op.execute("CREATE INDEX idx_price_history_crawled_brin ON price_history USING brin(crawled_at)")

    # reviews
    op.create_table('reviews',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.String(100), nullable=True),
        sa.Column('author_name', sa.String(200), nullable=True),
        sa.Column('rating', sa.SmallInteger(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created_date', sa.DateTime(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_purchased', sa.Boolean(), nullable=True),
        sa.Column('sentiment_score', sa.Numeric(4, 3), nullable=True),
        sa.Column('is_fake', sa.Boolean(), nullable=True),
        sa.Column('fake_confidence', sa.Numeric(4, 3), nullable=True),
        sa.Column('crawled_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'external_id', name='uq_reviews_product_external'),
    )
    op.create_index('idx_reviews_product', 'reviews', ['product_id'])
    op.create_index('idx_reviews_sentiment', 'reviews', ['sentiment_score'])
    op.execute("CREATE INDEX idx_reviews_fake ON reviews(is_fake) WHERE is_fake = TRUE")

    # product_analytics
    op.create_table('product_analytics',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('min_price', sa.BigInteger(), nullable=True),
        sa.Column('max_price', sa.BigInteger(), nullable=True),
        sa.Column('avg_price', sa.BigInteger(), nullable=True),
        sa.Column('price_volatility', sa.Numeric(8, 4), nullable=True),
        sa.Column('trend_direction', sa.String(10), nullable=True),
        sa.Column('predicted_price_7d', sa.BigInteger(), nullable=True),
        sa.Column('anomaly_score', sa.Numeric(4, 3), nullable=True),
        sa.Column('buy_signal', sa.String(20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('product_id', 'date', name='uq_analytics_product_date'),
    )
    op.create_index('idx_analytics_product_date', 'product_analytics', ['product_id', 'date'])
    op.create_index('idx_analytics_signal', 'product_analytics', ['buy_signal'])

    # price_alerts
    op.create_table('price_alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(255), nullable=False),
        sa.Column('target_price', sa.BigInteger(), nullable=False),
        sa.Column('alert_type', sa.String(10), nullable=False, server_default='below'),
        sa.Column('is_triggered', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('triggered_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("alert_type IN ('below', 'above', 'any_change')", name='ck_alerts_type'),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_alerts_product', 'price_alerts', ['product_id'])
    op.create_index('idx_alerts_email', 'price_alerts', ['user_email'])
    op.execute("CREATE INDEX idx_alerts_active ON price_alerts(is_active) WHERE is_active = TRUE")

    # crawl_logs
    op.create_table('crawl_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_id', sa.Integer(), nullable=True),
        sa.Column('spider_name', sa.String(100), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='running'),
        sa.Column('products_crawled', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('products_new', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('products_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('errors_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('duration_seconds', sa.Numeric(10, 2), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('finished_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint("status IN ('running', 'success', 'failed', 'partial')", name='ck_crawl_logs_status'),
        sa.ForeignKeyConstraint(['platform_id'], ['platforms.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_crawl_logs_status', 'crawl_logs', ['status', 'started_at'])

    # ml_model_metrics
    op.create_table('ml_model_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False),
        sa.Column('metric_name', sa.String(50), nullable=False),
        sa.Column('metric_value', sa.Numeric(10, 6), nullable=True),
        sa.Column('training_samples', sa.Integer(), nullable=True),
        sa.Column('trained_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_ml_metrics_model', 'ml_model_metrics', ['model_name', 'trained_at'])


def downgrade() -> None:
    op.drop_table('ml_model_metrics')
    op.drop_table('crawl_logs')
    op.drop_table('price_alerts')
    op.drop_table('product_analytics')
    op.drop_table('reviews')
    op.drop_table('price_history')
    op.drop_table('products')
    op.drop_table('categories')
    op.drop_table('platforms')
    op.execute("DROP EXTENSION IF EXISTS pg_trgm")
