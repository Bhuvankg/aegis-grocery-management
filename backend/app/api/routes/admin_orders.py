from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.order import OrderPublic, OrderStatusUpdate
from app.services import order_service

router = APIRouter(prefix="/admin/orders", tags=["admin-orders"])


@router.get("", response_model=list[OrderPublic])
def list_orders_for_admin(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    List customer orders for store administrators.
    Requires administrator authorization.
    """
    total, orders = order_service.list_admin_orders(
        db, page=page, page_size=page_size, status_filter=status
    )
    return orders


@router.patch("/{order_id}/status", response_model=OrderPublic)
def update_order_status(
    order_id: int,
    payload: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Update order lifecycle status.
    If order is cancelled, inventory quantities are automatically restored.
    Requires administrator authorization.
    """
    order = order_service.update_order_status(db, order_id, payload.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )
    return order
