# Functional Requirements Document (FRD)
## AEGIS AI – AI-Powered Grocery Store Management System

**Document status:** Initial baseline  
**Version:** 1.0

## 1. Scope
This document describes observable application behavior. Detailed API paths and schemas may evolve during implementation, but the authorization and business rules below are mandatory.

## 2. Functional requirements

### 2.1 Public storefront
- FR-001: The system shall display active products and categories to visitors.
- FR-002: The system shall support product search and category filtering.
- FR-003: Product detail shall show name, description, price, image, availability, and store-entered quality/expiry fields where present.
- FR-004: The system shall display published reviews and ratings.
- FR-005: The system shall not expose internal purchase cost, supplier notes, profit, or private inventory audit data.

### 2.2 Cart and checkout
- FR-010: A visitor/customer shall add, update, and remove cart items.
- FR-011: The server shall revalidate product status, price, and stock at order submission.
- FR-012: The server shall calculate totals; it shall not trust totals supplied by the browser.
- FR-013: Checkout shall support cash on delivery.
- FR-014: Demo online payment shall create a simulated payment result only and clearly disclose that no real transaction occurs.
- FR-015: The system shall generate an order reference and initial status after successful order creation.
- FR-016: Customers shall only access their own order details, or use a secure, unguessable order lookup mechanism if guest checkout is selected.

### 2.3 Administrator authentication and authorization
- FR-020: The system shall provide an administrator sign-in page at a non-advertised route.
- FR-021: The system shall not provide public administrator registration.
- FR-022: Passwords shall be stored using a modern password-hashing algorithm such as Argon2id or bcrypt with appropriate parameters.
- FR-023: The backend shall validate administrator identity and role for every protected request.
- FR-024: A hidden link or frontend route guard shall not be treated as an authorization control.
- FR-025: The system shall support sign-out and token/session expiry/revocation.
- FR-026: Repeated failed login attempts should be rate-limited and security events logged without storing passwords.

### 2.4 Product and category management
- FR-030: An administrator shall create, edit, deactivate, and view products.
- FR-031: An administrator shall manage categories.
- FR-032: The server shall validate price, quantity, identifiers, and required fields.
- FR-033: Product deletion should normally be soft deletion/deactivation when order history refers to the product.

### 2.5 Inventory
- FR-040: An administrator shall view current stock.
- FR-041: An administrator shall record stock receipts, corrections, and adjustments with a reason.
- FR-042: The system shall maintain an inventory movement history.
- FR-043: The system shall generate low-stock alerts using a configurable reorder threshold.
- FR-044: Batch/expiry tracking shall be supported for perishable goods where the store provides the data.

### 2.6 Orders
- FR-050: An administrator shall list and view orders.
- FR-051: An administrator shall update orders through allowed statuses.
- FR-052: The system shall prevent invalid status transitions.
- FR-053: Cancellation and stock restoration shall follow one consistent server-side transaction policy.

### 2.7 Reviews
- FR-060: Customers shall read published reviews.
- FR-061: Review submission shall be constrained by the selected customer identity/purchase-verification policy.
- FR-062: Administrators may moderate reported or inappropriate reviews if enabled.

### 2.8 Analytics and AI
- FR-070: Administrators shall view sales totals for selected periods.
- FR-071: Administrators shall view product performance and stock summaries.
- FR-072: The system shall calculate forecasts from historical sales data using a reproducible Python ML pipeline.
- FR-073: The forecast service shall validate data sufficiency and return a baseline/fallback result if data is insufficient.
- FR-074: AI output shall include forecast horizon, generation time, input period, and a clear advisory disclaimer.
- FR-075: AI shall not autonomously edit stock, prices, or orders.

## 3. Authorization matrix
| Capability | Guest/customer | Administrator |
|---|---:|---:|
| View active products | Yes | Yes |
| View public reviews | Yes | Yes |
| Place an order | Yes, subject to checkout rules | Optional |
| Submit a review | Per review policy | Moderate |
| Create/edit/deactivate products | No | Yes |
| Change prices | No | Yes |
| View internal cost/profit | No | Yes |
| Adjust inventory | No | Yes |
| View all customer orders | No | Yes |
| View sales analytics/AI insights | No | Yes |
| Manage admin accounts | No | Controlled provisioning only |

## 4. Error handling
- Invalid input: return a clear validation error without exposing stack traces.
- Unauthenticated protected request: HTTP 401.
- Authenticated non-admin request: HTTP 403.
- Missing resource: HTTP 404.
- Stock conflict: return a conflict response and explain that availability changed.
- Unexpected server error: generic message to client; detailed diagnostic only in protected server logs.

## 5. Key data entities
Admin, Customer, Category, Product, InventoryBatch, InventoryMovement, Order, OrderItem, PaymentAttempt, Review, StockAlert, ForecastRun, AuditLog.

## 6. Acceptance tests
- Guest cannot call any admin mutation endpoint.
- Customer cannot read profit/cost/forecast endpoints.
- Admin can manage products and inventory after authentication.
- Order totals and stock are recalculated on the backend.
- Two simultaneous orders cannot oversell stock.
- Demo payment never represents a real payment.
- Forecast endpoint returns a valid result or a documented insufficient-data response.
