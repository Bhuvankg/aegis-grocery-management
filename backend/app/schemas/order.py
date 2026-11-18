from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.schemas.payment import PaymentPublic


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, le=50, description="Quantity to purchase")


class OrderCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=150)
    customer_email: EmailStr | None = None
    customer_phone: str = Field(min_length=7, max_length=20)
    delivery_address: str = Field(min_length=5, max_length=500)
    payment_method: str = Field(default="cash_on_delivery")
    items: list[OrderItemCreate] = Field(min_length=1)


class OrderItemPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    product_name_snapshot: str | None = None
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    order_number: str
    status: str
    customer_name: str | None = None
    customer_email: str | None = None
    customer_phone: str | None = None
    delivery_address: str
    payment_method: str
    subtotal: Decimal
    delivery_fee: Decimal
    total_amount: Decimal
    created_at: datetime
    items: list[OrderItemPublic]
    payment: PaymentPublic | None = None


class OrderStatusUpdate(BaseModel):
    status: str = Field(pattern="^(pending|confirmed|out_for_delivery|delivered|cancelled)$")
