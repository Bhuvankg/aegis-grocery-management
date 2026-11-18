from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.product import Product
from app.models.inventory import Inventory
from app.ai_engine.forecasting import generate_product_forecast, DISCLAIMER


def generate_restock_recommendations(db: Session) -> list[dict]:
    """
    Computes intelligent restock suggestions by combining current stock
    with predicted 7-day demand velocity.
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)  # noqa: E712
        .order_by(Product.name)
        .all()
    )

    recommendations = []

    for product in products:
        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        current_stock = inventory.quantity if inventory else 0
        reorder_level = inventory.reorder_level if inventory else 10

        forecast_data = generate_product_forecast(db, product.id)
        predicted_7d = forecast_data.get("predicted_demand_7d", 7)
        daily_velocity = max(0.5, predicted_7d / 7.0)

        # Days of supply remaining
        days_of_supply = round(current_stock / daily_velocity, 1)

        # Determine urgency & status
        if current_stock == 0:
            urgency = "immediate"
            stock_status = "stockout"
            reason = "Item is completely sold out. Customers cannot place orders."
            # Target 14 days of supply + safety stock
            suggested_reorder = int(round(daily_velocity * 14)) + reorder_level
        elif days_of_supply <= 2:
            urgency = "immediate"
            stock_status = "critical_low"
            reason = f"Only {days_of_supply} days of supply remaining at current demand velocity."
            suggested_reorder = int(round(daily_velocity * 14)) + reorder_level - current_stock
        elif current_stock <= reorder_level or days_of_supply <= 5:
            urgency = "soon"
            stock_status = "low_stock"
            reason = f"Stock level ({current_stock}) is below reorder threshold ({reorder_level})."
            suggested_reorder = int(round(daily_velocity * 14)) - current_stock
        else:
            urgency = "none"
            stock_status = "adequate"
            reason = f"Healthy inventory ({current_stock} units covers ~{days_of_supply} days)."
            suggested_reorder = 0

        suggested_reorder = max(0, suggested_reorder)

        recommendations.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "category_name": product.category.name if product.category else "General",
            "current_stock": current_stock,
            "reorder_level": reorder_level,
            "daily_velocity": round(daily_velocity, 2),
            "days_of_supply": days_of_supply,
            "stock_status": stock_status,
            "urgency": urgency,
            "reason": reason,
            "suggested_reorder_quantity": suggested_reorder,
            "disclaimer": DISCLAIMER,
        })

    # Sort so most urgent restock items appear first
    urgency_rank = {"immediate": 0, "soon": 1, "none": 2}
    recommendations.sort(key=lambda x: (urgency_rank.get(x["urgency"], 3), x["days_of_supply"]))

    return recommendations
