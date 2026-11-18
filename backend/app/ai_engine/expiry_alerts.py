from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.inventory import Inventory


PERISHABLE_KEYWORDS = [
    "milk", "paneer", "yogurt", "spinach", "bread", "croissant", "fish",
    "salmon", "chicken", "meat", "avocado", "tomato", "mango", "vegetable", "berry"
]

EXPIRY_DISCLAIMER = (
    "NOTICE: Freshness and expiry alerts are compiled from store-declared metadata "
    "and supplier shelf-life declarations. They are not independently lab-certified or verified."
)


def extract_estimated_shelf_life_days(text: str | None) -> int | None:
    """Heuristic extraction of days from strings like 'Best consumed within 2 days'."""
    if not text:
        return None
    lower = text.lower()
    for d in [1, 2, 3, 4, 5, 7, 10, 14, 30]:
        if f"{d} day" in lower or f"{d}-day" in lower:
            return d
        if f"{d} week" in lower:
            return d * 7
    return None


def generate_expiry_freshness_alerts(db: Session) -> list[dict]:
    """
    Scans catalogue for perishable items with store-entered shelf life
    and generates prioritized shelf-life monitoring alerts.
    """
    products = (
        db.query(Product)
        .filter(Product.is_active == True)  # noqa: E712
        .order_by(Product.name)
        .all()
    )

    alerts = []

    for product in products:
        name_lower = product.name.lower()
        is_perishable = any(k in name_lower for k in PERISHABLE_KEYWORDS) or bool(product.expiry_info)
        if not is_perishable:
            continue

        inventory = db.query(Inventory).filter(Inventory.product_id == product.id).first()
        current_stock = inventory.quantity if inventory else 0

        estimated_days = extract_estimated_shelf_life_days(product.expiry_info)
        if estimated_days is None:
            estimated_days = 3 if any(k in name_lower for k in ["milk", "paneer", "spinach", "fish", "chicken"]) else 7

        if estimated_days <= 2:
            alert_level = "critical"
            action_advice = "Fast-track sales or mark for discount clearance within 24-48 hours."
        elif estimated_days <= 5:
            alert_level = "warning"
            action_advice = "Monitor storage refrigeration and FIFO stock rotation."
        else:
            alert_level = "normal"
            action_advice = "Standard perishable storage protocol."

        alerts.append({
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "category_name": product.category.name if product.category else "Perishables",
            "current_stock": current_stock,
            "shelf_life_window_days": estimated_days,
            "alert_level": alert_level,
            "store_quality_notes": product.quality_notes or "Store-declared standard quality",
            "store_expiry_info": product.expiry_info or "Fresh daily replenishment",
            "action_advice": action_advice,
            "disclaimer": EXPIRY_DISCLAIMER,
        })

    # Sort critical items first
    level_order = {"critical": 0, "warning": 1, "normal": 2}
    alerts.sort(key=lambda a: (level_order.get(a["alert_level"], 3), a["shelf_life_window_days"]))

    return alerts
