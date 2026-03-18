from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://shopsmart:shopsmart123@localhost:5432/shopsmart_db"
    sync_database_url: str = "postgresql://shopsmart:shopsmart123@localhost:5432/shopsmart_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # App
    app_env: str = "development"
    secret_key: str = "dev-secret-key"
    debug: bool = True

    # API
    api_v1_prefix: str = "/api/v1"

    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100

    # Cache TTLs (seconds)
    cache_ttl_products: int = 300      # 5 minutes
    cache_ttl_analytics: int = 600     # 10 minutes
    cache_ttl_trending: int = 300      # 5 minutes

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
