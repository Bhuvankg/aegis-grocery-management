from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.services import analytics_service

router = APIRouter(prefix="/admin/analytics", tags=["admin-analytics"])


@router.get("/summary")
def get_store_analytics(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Returns store revenue, order breakdowns, inventory valuation, and top sellers.
    Reveals commercial cost & profit metrics.
    Requires administrator authorization.
    """
    return analytics_service.get_store_analytics_summary(db)
