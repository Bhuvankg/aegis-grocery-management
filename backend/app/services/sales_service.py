from decimal import Decimal
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.models.order import Order, OrderItem
from app.models.product import Product


def get_sales_history(
    db: Session,
    page: int = 1,
    page_size: int = 25,
    date_from: str | None = None,
    date_to: str | None = None,
) -> dict:
    """
    Returns a chronological list of completed sales with per-order cost/profit breakdown.
    Admin-only: reveals internal COGS and profit per transaction.
    """
    query = (
        db.query(Order)
        .filter(Order.status.in_(["confirmed", "out_for_delivery", "delivered"]))
        .order_by(Order.created_at.desc())
    )

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from).replace(tzinfo=timezone.utc)
            query = query.filter(Order.created_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to).replace(tzinfo=timezone.utc)
            # Include the entire end day
            dt_to = dt_to + timedelta(days=1)
            query = query.filter(Order.created_at < dt_to)
        except ValueError:
            pass

    total_count = query.count()
    orders = query.offset((page - 1) * page_size).limit(page_size).all()

    sales_records = []
    for order in orders:
        # Calculate cost of goods sold (COGS) for this order
        order_cogs = Decimal("0.00")
        item_details = []

        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            unit_cost = Decimal("0.00")
            if product and product.cost_price:
                unit_cost = product.cost_price
            elif product and product.selling_price:
                # Conservative fallback: assume 70% of selling price as cost
                unit_cost = product.selling_price * Decimal("0.70")

            item_cogs = unit_cost * item.quantity
            order_cogs += item_cogs
            item_line_total = item.line_total or (item.unit_price * item.quantity)

            item_details.append({
                "product_name": item.product_name_snapshot or (product.name if product else "Unknown"),
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": float(item_line_total),
                "unit_cost": float(unit_cost),
                "item_cogs": float(item_cogs),
                "item_profit": float(item_line_total - item_cogs),
            })

        order_revenue = order.total_amount or Decimal("0.00")
        order_profit = order_revenue - order.delivery_fee - order_cogs
        margin_pct = (
            round(float((order_profit / (order_revenue - order.delivery_fee)) * 100), 1)
            if (order_revenue - order.delivery_fee) > 0
            else 0.0
        )

        sales_records.append({
            "order_id": order.id,
            "order_number": order.order_number,
            "customer_name": order.customer_name or "Guest",
            "customer_phone": order.customer_phone,
            "status": order.status,
            "payment_method": order.payment_method or "cash_on_delivery",
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "subtotal": float(order.subtotal or Decimal("0.00")),
            "delivery_fee": float(order.delivery_fee or Decimal("0.00")),
            "total_amount": float(order_revenue),
            "cogs": float(order_cogs),
            "gross_profit": float(order_profit),
            "gross_margin_pct": margin_pct,
            "items": item_details,
            "item_count": len(item_details),
        })

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "sales": sales_records,
    }


def get_daily_sales_summary(
    db: Session,
    days: int = 30,
) -> dict:
    """
    Aggregates sales revenue, COGS, and profit by calendar date for the last N days.
    Used for daily trend charts in the admin dashboard.
    """
    now_utc = datetime.now(timezone.utc)
    start_date = now_utc - timedelta(days=days)

    # Get all completed orders in the range
    orders = (
        db.query(Order)
        .filter(
            Order.status.in_(["confirmed", "out_for_delivery", "delivered"]),
            Order.created_at >= start_date,
        )
        .order_by(Order.created_at)
        .all()
    )

    # Aggregate by date
    daily_map: dict[str, dict] = {}
    grand_revenue = Decimal("0.00")
    grand_cogs = Decimal("0.00")
    grand_orders = 0
    grand_units = 0

    for order in orders:
        date_key = order.created_at.strftime("%Y-%m-%d") if order.created_at else "unknown"
        if date_key not in daily_map:
            daily_map[date_key] = {
                "date": date_key,
                "revenue": Decimal("0.00"),
                "cogs": Decimal("0.00"),
                "profit": Decimal("0.00"),
                "order_count": 0,
                "units_sold": 0,
            }

        entry = daily_map[date_key]
        order_revenue = order.total_amount or Decimal("0.00")
        delivery = order.delivery_fee or Decimal("0.00")

        # Calculate COGS for this order
        order_cogs = Decimal("0.00")
        order_units = 0
        for item in order.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            unit_cost = Decimal("0.00")
            if product and product.cost_price:
                unit_cost = product.cost_price
            elif product and product.selling_price:
                unit_cost = product.selling_price * Decimal("0.70")
            order_cogs += unit_cost * item.quantity
            order_units += item.quantity

        order_profit = order_revenue - delivery - order_cogs

        entry["revenue"] += order_revenue
        entry["cogs"] += order_cogs
        entry["profit"] += order_profit
        entry["order_count"] += 1
        entry["units_sold"] += order_units

        grand_revenue += order_revenue
        grand_cogs += order_cogs
        grand_orders += 1
        grand_units += order_units

    # Convert to sorted list and floats
    daily_list = []
    for key in sorted(daily_map.keys()):
        d = daily_map[key]
        daily_list.append({
            "date": d["date"],
            "day_of_week": datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a"),
            "revenue": float(d["revenue"]),
            "cogs": float(d["cogs"]),
            "profit": float(d["profit"]),
            "order_count": d["order_count"],
            "units_sold": d["units_sold"],
        })

    grand_profit = grand_revenue - grand_cogs
    avg_order_value = float(grand_revenue / grand_orders) if grand_orders > 0 else 0.0

    return {
        "period_days": days,
        "period_start": start_date.strftime("%Y-%m-%d"),
        "period_end": now_utc.strftime("%Y-%m-%d"),
        "totals": {
            "revenue": float(grand_revenue),
            "cogs": float(grand_cogs),
            "profit": float(grand_profit),
            "total_orders": grand_orders,
            "total_units_sold": grand_units,
            "avg_order_value": round(avg_order_value, 2),
            "overall_margin_pct": (
                round(float((grand_profit / grand_revenue) * 100), 1)
                if grand_revenue > 0
                else 0.0
            ),
        },
        "daily": daily_list,
    }


def get_product_sales_history(db: Session, product_id: int) -> dict:
    """
    Returns the per-product sales history: total units, revenue, and daily breakdown.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}

    rows = (
        db.query(
            func.date(Order.created_at).label("sale_date"),
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.line_total).label("revenue"),
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(
            OrderItem.product_id == product_id,
            Order.status.in_(["confirmed", "out_for_delivery", "delivered"]),
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    total_units = sum(int(r.units_sold or 0) for r in rows)
    total_revenue = sum(float(r.revenue or 0) for r in rows)
    unit_cost = float(product.cost_price) if product.cost_price else float(product.selling_price) * 0.70
    total_cogs = unit_cost * total_units
    total_profit = total_revenue - total_cogs

    daily = [
        {
            "date": str(r.sale_date),
            "units_sold": int(r.units_sold or 0),
            "revenue": float(r.revenue or 0),
        }
        for r in rows
    ]

    return {
        "product_id": product.id,
        "product_name": product.name,
        "sku": product.sku,
        "unit_selling_price": float(product.selling_price),
        "unit_cost_price": unit_cost,
        "lifetime_units_sold": total_units,
        "lifetime_revenue": round(total_revenue, 2),
        "lifetime_cogs": round(total_cogs, 2),
        "lifetime_profit": round(total_profit, 2),
        "daily_sales": daily,
    }
