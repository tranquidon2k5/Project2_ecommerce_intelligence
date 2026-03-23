from fastapi import APIRouter

from .products import router as products_router

router = APIRouter()

router.include_router(products_router)

# Will include more routers as they are created
try:
    from .analytics import router as analytics_router
    router.include_router(analytics_router)
except ImportError:
    pass

try:
    from .alerts import router as alerts_router
    router.include_router(alerts_router)
except ImportError:
    pass

try:
    from .system import router as system_router
    router.include_router(system_router)
except ImportError:
    pass

try:
    from .ai_insights import router as ai_router
    router.include_router(ai_router)
except ImportError:
    pass

try:
    from .export import router as export_router
    router.include_router(export_router)
except ImportError:
    pass
