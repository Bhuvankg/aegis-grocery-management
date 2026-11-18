from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.ai_engine.forecasting import generate_all_forecasts, generate_product_forecast
from app.ai_engine.recommender import generate_restock_recommendations
from app.ai_engine.expiry_alerts import generate_expiry_freshness_alerts

router = APIRouter(prefix="/admin/ai", tags=["admin-ai-intelligence"])


@router.get("/forecasts")
def get_demand_forecasts(
    product_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Returns 7-day chronological demand forecasts.
    Evaluates baseline moving average comparison and sufficiency thresholds.
    Advisory only — never alters stock or prices.
    Requires administrator authorization.
    """
    if product_id:
        return generate_product_forecast(db, product_id)
    return generate_all_forecasts(db)


@router.get("/recommendations")
def get_restock_recommendations(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Returns dynamic restock recommendations based on daily sales velocity,
    reorder thresholds, and days of supply remaining.
    Requires administrator authorization.
    """
    return generate_restock_recommendations(db)


@router.get("/expiry-alerts")
def get_expiry_alerts(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Scans catalogue for perishable items with store-declared shelf-life
    and generates prioritized monitoring alerts.
    Requires administrator authorization.
    """
    return generate_expiry_freshness_alerts(db)
