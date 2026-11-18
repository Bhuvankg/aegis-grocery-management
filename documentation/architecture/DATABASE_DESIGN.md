# Database design – initial logical model

PostgreSQL is the selected database. Use SQLAlchemy models and Alembic migrations; do not rely on production `create_all()` as a migration strategy.

## Entities and key fields
- `admins`: id, email (unique), password_hash, is_active, created_at, last_login_at.
- `customers`: id, name, email/phone as needed, created_at.
- `categories`: id, name, slug (unique), is_active.
- `products`: id, category_id, name, slug, description, selling_price, optional cost_price (admin-only), unit, image_url, is_active, created_at, updated_at.
- `inventory_batches`: id, product_id, batch_code, quantity, expiry_date, received_at.
- `inventory_movements`: id, product_id, batch_id nullable, movement_type, quantity_delta, reason, actor_admin_id, created_at.
- `orders`: id, public_order_ref (unique random reference), customer_id nullable for guest flow, customer contact/delivery snapshot, status, subtotal, delivery_fee, total, created_at.
- `order_items`: id, order_id, product_id, product_name_snapshot, unit_price_snapshot, quantity, line_total.
- `payment_attempts`: id, order_id, method, status, demo_reference nullable, created_at.
- `reviews`: id, product_id, customer_id nullable, rating, body, status, created_at.
- `stock_alerts`: id, product_id, alert_type, threshold, observed_quantity, status, created_at.
- `forecast_runs`: id, product_id, model_name, training_window_start, training_window_end, horizon_days, prediction_json, metrics_json, created_at.
- `audit_logs`: id, actor_admin_id, action, entity_type, entity_id, metadata_json, created_at.

## Data rules
- Store money as `NUMERIC`, never binary floating point.
- Use UTC timestamps in storage.
- Add indexes for product active/category/name search, order creation/status, order item product, inventory product/expiry.
- Keep order item name and price snapshots so historical orders do not change when product details change.
- Use database transactions for order creation and stock movements.
- Restrict `cost_price`, audit logs, and forecast details to administrators.
- Define deletion behavior explicitly; prefer deactivation for products referenced by orders.
