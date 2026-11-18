# API specification – planned contract

Base prefix: `/api/v1` (the current Phase 1 health route remains `/api/health` until the versioned router is introduced).

## Public endpoints (planned)
| Method | Path | Purpose |
|---|---|---|
| GET | `/products` | Paginated active catalogue |
| GET | `/products/{product_id}` | Public product detail |
| GET | `/categories` | Active categories |
| GET | `/products/{product_id}/reviews` | Published reviews |
| POST | `/orders` | Create order after server-side validation |
| GET | `/orders/{public_order_ref}` | Secure customer order lookup, if guest checkout is enabled |

## Administrator endpoints (all require backend admin authorization)
| Method | Path | Purpose |
|---|---|---|
| POST | `/auth/admin/login` | Authenticate provisioned administrator |
| POST | `/auth/admin/logout` | End session/revoke refresh credential |
| GET | `/admin/me` | Current administrator |
| POST | `/admin/products` | Create product |
| PATCH | `/admin/products/{id}` | Update product |
| DELETE | `/admin/products/{id}` | Deactivate product |
| GET | `/admin/inventory` | Inventory list |
| POST | `/admin/inventory/movements` | Record stock movement |
| GET | `/admin/orders` | List all orders |
| PATCH | `/admin/orders/{id}/status` | Update order status |
| GET | `/admin/analytics/summary` | Sales and stock summary |
| GET | `/admin/ai/forecasts` | ML forecasts and recommendations |

## API rules
- Validate every request with Pydantic schemas.
- Use pagination for list endpoints.
- Never accept admin role, calculated totals, or authoritative prices from the browser.
- Use 401 for missing/invalid authentication and 403 for authenticated non-admin users.
- Keep public and admin response schemas separate.
- Add request IDs and structured server logs; do not log passwords, tokens, or payment secrets.
