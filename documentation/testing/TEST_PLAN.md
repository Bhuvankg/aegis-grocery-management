# Test plan

## Authentication and access control
- Anonymous request to admin endpoint returns 401.
- Customer-authenticated request to admin endpoint returns 403.
- Admin can access permitted admin endpoints.
- Public admin registration does not exist.
- Expired/revoked session is rejected.
- Failed-login rate limit is enforced.

## Storefront and catalogue
- Only active products are public.
- Search and category filters work.
- Public product response omits internal cost and profit fields.
- Reviews shown publicly meet publication/moderation rules.

## Orders and inventory
- Empty order is rejected.
- Zero/negative quantity is rejected.
- Server recalculates totals and validates current prices.
- Insufficient stock prevents order creation.
- Concurrent orders do not oversell stock.
- Inventory movements are auditable.
- Cancellation/restock behavior follows documented policy.

## Payments
- COD order is recorded correctly.
- Demo payment is explicitly marked simulated.
- No card details are requested or stored.
- Simulated success/failure does not claim a real bank transfer.

## AI/ML
- Insufficient history returns an explanatory fallback.
- Forecast is reproducible for a fixed dataset/model configuration.
- Forecast includes horizon and source data window.
- Forecast is advisory and does not mutate inventory.

## Frontend
- Responsive layout works on mobile and desktop.
- Forms have labels and validation messages.
- Customer UI has no product-management controls.
- Directly navigating to admin UI without authentication does not expose admin data.
