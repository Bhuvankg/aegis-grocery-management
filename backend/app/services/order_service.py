import random
import string
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.order import OrderCreate


def generate_order_number() -> str:
    """Generate a unique order reference: AEGIS-YYYY-XXXXXX."""
    year = datetime.now(timezone.utc).year
    rand_chars = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"AEGIS-{year}-{rand_chars}"


def create_order(db: Session, order_in: OrderCreate) -> Order:
    """
    Atomic transaction:
    1. Validates each product exists and is active.
    2. Validates stock availability.
    3. Locks and decrements inventory.
    4. Calculates line totals and subtotal strictly from DB prices.
    5. Creates Order and OrderItem records.
    """
    product_ids = [item.product_id for item in order_in.items]
    if len(product_ids) != len(set(product_ids)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Duplicate products found in cart items",
        )

    products = db.query(Product).filter(
        Product.id.in_(product_ids),
        Product.is_active == True  # noqa: E712
    ).all()
    prod_map = {p.id: p for p in products}

    if len(prod_map) != len(product_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more selected products are inactive or no longer available",
        )

    # Check inventory stock for all items
    inventories = db.query(Inventory).filter(Inventory.product_id.in_(product_ids)).with_for_update().all()
    inv_map = {inv.product_id: inv for inv in inventories}

    for item in order_in.items:
        inv = inv_map.get(item.product_id)
        if not inv or inv.quantity < item.quantity:
            prod_name = prod_map[item.product_id].name
            available = inv.quantity if inv else 0
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Insufficient stock for '{prod_name}'. Requested: {item.quantity}, Available: {available}",
            )

    # Calculate totals securely on server
    subtotal = Decimal("0.00")
    order_items_to_create = []

    for item in order_in.items:
        product = prod_map[item.product_id]
        unit_price = product.selling_price
        line_total = unit_price * item.quantity
        subtotal += line_total

        # Decrement inventory stock
        inv = inv_map[item.product_id]
        inv.quantity -= item.quantity

        order_items_to_create.append(
            OrderItem(
                product_id=product.id,
                product_name_snapshot=product.name,
                quantity=item.quantity,
                unit_price=unit_price,
                line_total=line_total,
            )
        )

    delivery_fee = Decimal("0.00") if subtotal >= Decimal("500.00") else Decimal("40.00")
    total_amount = subtotal + delivery_fee

    order = Order(
        order_number=generate_order_number(),
        customer_name=order_in.customer_name.strip(),
        customer_email=order_in.customer_email.strip().lower() if order_in.customer_email else None,
        customer_phone=order_in.customer_phone.strip(),
        delivery_address=order_in.delivery_address.strip(),
        payment_method=order_in.payment_method,
        status="confirmed" if order_in.payment_method == "cash_on_delivery" else "pending",
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        total_amount=total_amount,
    )
    db.add(order)
    db.flush()

    for oi in order_items_to_create:
        oi.order_id = order.id
        db.add(oi)

    db.commit()
    db.refresh(order)
    return order


def get_order_by_number(db: Session, order_number: str) -> Order | None:
    """Customer lookup by unguessable order reference."""
    return (
        db.query(Order)
        .options(joinedload(Order.items))
        .filter(Order.order_number == order_number.strip())
        .first()
    )


def list_admin_orders(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    status_filter: str | None = None,
) -> tuple[int, list[Order]]:
    """List orders for administrators with status filtering."""
    q = db.query(Order).options(joinedload(Order.items))
    if status_filter:
        q = q.filter(Order.status == status_filter)

    total = q.count()
    items = (
        q.order_by(Order.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def update_order_status(db: Session, order_id: int, new_status: str) -> Order | None:
    """
    Update order status through lifecycle.
    If transitioning to 'cancelled' from a non-cancelled state, restore inventory stock.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        return None

    old_status = order.status
    if old_status == new_status:
        return order

    # If cancelling, restore stock
    if new_status == "cancelled" and old_status != "cancelled":
        for item in order.items:
            inv = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
            if inv:
                inv.quantity += item.quantity

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
