from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.services import sales_service

router = APIRouter(prefix="/admin/sales", tags=["admin-sales"])


@router.get("/history")
def get_sales_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    date_from: str | None = Query(default=None, description="Start date (YYYY-MM-DD)"),
    date_to: str | None = Query(default=None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Chronological sales ledger with per-order revenue, COGS, and profit.
    Reveals internal cost data — requires administrator authorization.
    """
    return sales_service.get_sales_history(
        db, page=page, page_size=page_size,
        date_from=date_from, date_to=date_to
    )


@router.get("/daily-summary")
def get_daily_sales_summary(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Daily revenue, COGS, and profit aggregation for trend charts.
    Requires administrator authorization.
    """
    return sales_service.get_daily_sales_summary(db, days=days)


@router.get("/product/{product_id}")
def get_product_sales(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Per-product lifetime sales: units sold, revenue, COGS, profit, and daily breakdown.
    Requires administrator authorization.
    """
    return sales_service.get_product_sales_history(db, product_id)
