import sys
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure the backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.api.routes.health import router as health_router
from app.api.routes.categories import router as categories_router
from app.api.routes.products import router as products_router
from app.api.routes.auth import router as auth_router
from app.api.routes.admin_products import router as admin_products_router
from app.api.routes.orders import router as orders_router
from app.api.routes.admin_orders import router as admin_orders_router
from app.api.routes.payments import router as payments_router
from app.api.routes.ai_analytics import router as ai_analytics_router
from app.api.routes.admin_analytics import router as admin_analytics_router
from app.api.routes.admin_sales import router as admin_sales_router
from app.core.config import (
    APP_NAME,
    API_V1_PREFIX,
    FRONTEND_ORIGIN,
)

app = FastAPI(
    title=APP_NAME,
    description="AEGIS AI - AI-Powered Grocery Store Management System API",
    version="0.1.0",
)

# CORS configuration
origins = [
    FRONTEND_ORIGIN,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["root"])
def root():
    return {
        "success": True,
        "service": APP_NAME,
        "status": "running",
        "docs_url": "/docs",
    }


# Include route modules
app.include_router(health_router, prefix=API_V1_PREFIX)
app.include_router(categories_router, prefix=API_V1_PREFIX)
app.include_router(products_router, prefix=API_V1_PREFIX)
app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(admin_products_router, prefix=API_V1_PREFIX)
app.include_router(orders_router, prefix=API_V1_PREFIX)
app.include_router(admin_orders_router, prefix=API_V1_PREFIX)
app.include_router(payments_router, prefix=API_V1_PREFIX)
app.include_router(ai_analytics_router, prefix=API_V1_PREFIX)
app.include_router(admin_analytics_router, prefix=API_V1_PREFIX)
app.include_router(admin_sales_router, prefix=API_V1_PREFIX)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
