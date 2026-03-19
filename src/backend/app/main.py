from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    async with engine.begin() as conn:
        # Tables are created via Alembic migrations in production
        # In dev, we can create them here if needed
        pass
    from .scheduler import start_scheduler
    start_scheduler()
    yield
    # Shutdown
    from .scheduler import stop_scheduler
    stop_scheduler()
    await engine.dispose()


app = FastAPI(
    title="ShopSmart Analytics API",
    description="E-commerce intelligence platform — track prices, detect anomalies, get AI-powered buy recommendations across Vietnamese e-commerce platforms.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": "1.0.0"}


# Include routers (will be added as we build them)
try:
    from .api.router import router
    app.include_router(router, prefix=settings.api_v1_prefix)
except ImportError:
    pass  # Router not yet created
