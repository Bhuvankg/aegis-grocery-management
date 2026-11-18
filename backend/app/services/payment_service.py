import random
import string
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.order import Order
from app.models.payment import Payment


def generate_simulation_reference() -> str:
    """Generate unguessable simulated transaction ID: SIM-TXN-XXXXXXXX."""
    rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"SIM-TXN-{rand}"


def process_simulated_payment(
    db: Session,
    order_number: str,
    outcome: str = "success"
) -> Payment:
    """
    Executes simulated payment:
    Strict invariant: Never request, handle or store real credit card numbers, CVVs, or bank logins.
    """
    order = db.query(Order).filter(Order.order_number == order_number.strip()).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order '{order_number}' not found",
        )

    # Check if a payment record already exists
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()

    if outcome == "success":
        txn_ref = generate_simulation_reference()
        if not payment:
            payment = Payment(
                order_id=order.id,
                method="simulated_card",
                status="success",
                amount=order.total_amount,
                transaction_reference=txn_ref,
            )
            db.add(payment)
        else:
            payment.status = "success"
            payment.transaction_reference = txn_ref
            payment.amount = order.total_amount

        # Update order status to confirmed
        order.status = "confirmed"
        order.payment_method = "simulated_online"
        db.commit()
        db.refresh(payment)
        return payment

    else:
        # Simulate payment decline / failure
        txn_ref = generate_simulation_reference()
        if not payment:
            payment = Payment(
                order_id=order.id,
                method="simulated_card",
                status="failed",
                amount=order.total_amount,
                transaction_reference=txn_ref,
            )
            db.add(payment)
        else:
            payment.status = "failed"
            payment.transaction_reference = txn_ref

        db.commit()
        db.refresh(payment)
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Simulated payment was declined by the demo payment test runner.",
        )
