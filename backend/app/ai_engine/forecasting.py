import math
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.order import Order, OrderItem
from app.models.product import Product
from app.models.inventory import Inventory


MODEL_VERSION = "1.0.0-advisory"
FORECAST_HORIZON_DAYS = 7
MIN_HISTORICAL_DAYS = 3
DISCLAIMER = (
    "AI forecasts and restock suggestions are advisory estimates based on statistical models "
    "and historical store activity. They do not represent financial guarantees and must never "
    "automatically alter inventory stock, pricing, or purchase orders without human verification."
)


def calculate_linear_regression(x: list[float], y: list[float]) -> tuple[float, float]:
    """Calculate slope (m) and intercept (b) using ordinary least squares."""
    n = len(x)
    if n < 2:
        return 0.0, y[0] if y else 0.0

    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)

    denominator = (n * sum_x2 - sum_x ** 2)
    if denominator == 0:
        return 0.0, sum_y / n

    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def generate_product_forecast(db: Session, product_id: int) -> dict:
    """
    Generate chronological 7-day demand forecast for a single product.
    Includes baseline moving average comparison and sufficiency checks.
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return {"error": "Product not found"}

    now_utc = datetime.now(timezone.utc)
    lookback_start = now_utc - timedelta(days=30)

    # Query chronological daily sales
    # group by date(orders.created_at)
    rows = (
        db.query(
            func.date(Order.created_at).label("sale_date"),
            func.sum(OrderItem.quantity).label("units_sold")
        )
        .join(OrderItem, OrderItem.order_id == Order.id)
        .filter(
            OrderItem.product_id == product_id,
            Order.status.in_(["confirmed", "out_for_delivery", "delivered"]),
            Order.created_at >= lookback_start
        )
        .group_by(func.date(Order.created_at))
        .order_by(func.date(Order.created_at))
        .all()
    )

    data_points = len(rows)
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    current_stock = inventory.quantity if inventory else 0

    # Data sufficiency check
    if data_points < MIN_HISTORICAL_DAYS:
        # Insufficient data response (Mandatory requirement)
        daily_units = [float(r.units_sold) for r in rows] if rows else [0.0]
        avg_units = round(sum(daily_units) / len(daily_units), 1) if rows else 1.0

        daily_predictions = []
        for d in range(1, FORECAST_HORIZON_DAYS + 1):
            future_date = (now_utc + timedelta(days=d)).strftime("%Y-%m-%d")
            daily_predictions.append({
                "date": future_date,
                "predicted_units": max(1, int(round(avg_units))),
                "day_of_week": (now_utc + timedelta(days=d)).strftime("%a"),
            })

        predicted_total_7d = sum(p["predicted_units"] for p in daily_predictions)

        return {
            "product_id": product.id,
            "product_name": product.name,
            "sku": product.sku,
            "status": "insufficient_data",
            "status_message": (
                f"Historical order volume ({data_points} day(s)) is below the {MIN_HISTORICAL_DAYS}-day threshold. "
                "Displaying conservative moving-average baseline."
            ),
            "model_name": "Conservative Moving Average Baseline",
            "model_version": MODEL_VERSION,
            "forecast_horizon_days": FORECAST_HORIZON_DAYS,
            "current_stock": current_stock,
            "predicted_demand_7d": predicted_total_7d,
            "daily_forecast": daily_predictions,
            "baseline_mae": None,
            "disclaimer": DISCLAIMER,
            "generated_at": now_utc.isoformat(),
        }

    # If sufficient data:
    x_indices = [float(i) for i in range(len(rows))]
    y_units = [float(r.units_sold) for r in rows]

    # Baseline 1: 7-day Simple Moving Average
    window = min(7, len(y_units))
    baseline_ma = sum(y_units[-window:]) / window

    # Model: Trend-adjusted Linear Progression
    slope, intercept = calculate_linear_regression(x_indices, y_units)

    # Chronological Out-of-sample Forecast
    daily_predictions = []
    n = len(rows)
    mae_sum = 0.0

    # Backtest baseline MAE
    for idx, actual in enumerate(y_units):
        pred = max(0.0, slope * idx + intercept)
        mae_sum += abs(actual - pred)
    backtest_mae = round(mae_sum / len(y_units), 2)

    for d in range(1, FORECAST_HORIZON_DAYS + 1):
        future_idx = n + d - 1
        predicted_val = slope * future_idx + intercept
        # Weighted blend of Trend (60%) and Moving Average Baseline (40%)
        blended = (0.6 * predicted_val) + (0.4 * baseline_ma)
        predicted_units = max(0, int(round(blended)))

        future_date = (now_utc + timedelta(days=d)).strftime("%Y-%m-%d")
        daily_predictions.append({
            "date": future_date,
            "predicted_units": predicted_units,
            "day_of_week": (now_utc + timedelta(days=d)).strftime("%a"),
        })

    predicted_total_7d = sum(p["predicted_units"] for p in daily_predictions)

    return {
        "product_id": product.id,
        "product_name": product.name,
        "sku": product.sku,
        "status": "active_forecast",
        "model_name": "Trend-Adjusted Moving Average (60/40 Ensemble)",
        "model_version": MODEL_VERSION,
        "forecast_horizon_days": FORECAST_HORIZON_DAYS,
        "training_window_days": len(rows),
        "current_stock": current_stock,
        "predicted_demand_7d": predicted_total_7d,
        "baseline_mae": backtest_mae,
        "daily_forecast": daily_predictions,
        "disclaimer": DISCLAIMER,
        "generated_at": now_utc.isoformat(),
    }


def generate_all_forecasts(db: Session) -> list[dict]:
    """Generate forecasts across all active catalogue items."""
    products = db.query(Product).filter(Product.is_active == True).order_by(Product.name).all()  # noqa: E712
    return [generate_product_forecast(db, p.id) for p in products]
