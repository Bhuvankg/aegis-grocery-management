from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory


def get_store_analytics_summary(db: Session) -> dict:
    """
    Computes comprehensive business, inventory valuation, and sales metrics.
    Admin-only: reveals internal costs and profit margins.
    """
    # 1. Total revenue & orders
    completed_orders = db.query(Order).filter(
        Order.status.in_(["confirmed", "out_for_delivery", "delivered"])
    ).all()

    total_revenue = sum((o.total_amount for o in completed_orders), Decimal("0.00"))
    total_orders_count = db.query(func.count(Order.id)).scalar() or 0

    # Orders count by status
    status_counts_raw = (
        db.query(Order.status, func.count(Order.id))
        .group_by(Order.status)
        .all()
    )
    orders_by_status = {status: count for status, count in status_counts_raw}

    # 2. Inventory Valuation
    inv_rows = (
        db.query(Product, Inventory)
        .join(Inventory, Inventory.product_id == Product.id)
        .filter(Product.is_active == True)  # noqa: E712
        .all()
    )

    total_stock_units = 0
    inventory_retail_value = Decimal("0.00")
    inventory_cost_value = Decimal("0.00")

    for prod, inv in inv_rows:
        qty = inv.quantity or 0
        total_stock_units += qty
        inventory_retail_value += (prod.selling_price or Decimal("0.00")) * qty
        cost = prod.cost_price or (prod.selling_price * Decimal("0.70"))  # conservative fallback
        inventory_cost_value += cost * qty

    potential_gross_profit = inventory_retail_value - inventory_cost_value
    overall_margin_pct = (
        round(float((potential_gross_profit / inventory_retail_value) * 100), 1)
        if inventory_retail_value > 0
        else 0.0
    )

    # 3. Top selling products
    top_items_raw = (
        db.query(
            OrderItem.product_name_snapshot,
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.line_total).label("revenue_generated")
        )
        .join(Order, Order.id == OrderItem.order_id)
        .filter(Order.status != "cancelled")
        .group_by(OrderItem.product_name_snapshot)
        .order_by(func.sum(OrderItem.quantity).desc())
        .limit(5)
        .all()
    )

    top_sellers = [
        {
            "product_name": row[0] or "Unknown Product",
            "units_sold": int(row[1] or 0),
            "revenue": float(row[2] or 0.0),
        }
        for row in top_items_raw
    ]

    return {
        "sales_summary": {
            "total_revenue": float(total_revenue),
            "total_orders": total_orders_count,
            "orders_by_status": orders_by_status,
        },
        "inventory_valuation": {
            "total_stock_units": total_stock_units,
            "total_retail_value": float(inventory_retail_value),
            "total_cost_value": float(inventory_cost_value),
            "potential_gross_profit": float(potential_gross_profit),
            "overall_gross_margin_pct": overall_margin_pct,
        },
        "top_selling_products": top_sellers,
    }
