from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.order import Order
from app.models.payment import Payment
from app.schemas.payment import SimulatedPaymentRequest, PaymentPublic
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/simulate", response_model=PaymentPublic)
def simulate_payment(
    payload: SimulatedPaymentRequest,
    db: Session = Depends(get_db)
):
    """
    Process simulated payment for an existing order.
    Complies with project invariant: never request or store card/CVV data.
    """
    return payment_service.process_simulated_payment(
        db, order_number=payload.order_number, outcome=payload.outcome
    )


@router.get("/{order_number}", response_model=PaymentPublic)
def get_payment_details(order_number: str, db: Session = Depends(get_db)):
    """Retrieve payment attempt record for an order reference."""
    order = db.query(Order).filter(Order.order_number == order_number.strip()).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    payment = db.query(Payment).filter(Payment.order_id == order.id).first()
    if not payment:
        raise HTTPException(status_code=404, detail="No payment record found for this order")

    return payment
