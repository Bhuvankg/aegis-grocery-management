from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class SimulatedPaymentRequest(BaseModel):
    order_number: str = Field(min_length=5, max_length=50)
    outcome: str = Field(default="success", pattern="^(success|fail)$")
    # Invariant: Never collect card numbers, CVV, or real account details


class PaymentPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_id: int
    method: str
    status: str
    amount: Decimal
    transaction_reference: str | None = None
    created_at: datetime
    is_simulation: bool = True
    disclaimer: str = (
        "SIMULATED PAYMENT NOTICE: This is a simulated transaction for demonstration "
        "and evaluation purposes. No real payment credentials were collected and no real money was transferred."
    )
