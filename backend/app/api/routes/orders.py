from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderPublic
from app.services import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderPublic, status_code=status.HTTP_201_CREATED)
def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """
    Public order checkout endpoint.
    - Server revalidates all prices and inventory quantities.
    - Stock is decremented in an atomic transaction.
    - Totals are computed server-side.
    """
    return order_service.create_order(db, order_data)


@router.get("/{order_number}", response_model=OrderPublic)
def get_order_confirmation(order_number: str, db: Session = Depends(get_db)):
    """Customer lookup of their order receipt using unique unguessable reference."""
    order = order_service.get_order_by_number(db, order_number)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found. Please verify the order reference.",
        )
    return order
