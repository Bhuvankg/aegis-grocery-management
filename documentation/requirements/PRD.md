# Product Requirements Document (PRD)
## AEGIS AI – AI-Powered Grocery Store Management System

**Document status:** Initial baseline  
**Version:** 1.0  
**Product scope:** Hackathon MVP, designed for future extension

## 1. Product summary
AEGIS AI is a web platform for small grocery stores. It provides a public customer shopping experience and a private store-administration workspace. It aims to reduce manual inventory work, improve order visibility, and turn store sales history into understandable business insights.

## 2. Problem statement
Small grocery stores lack affordable and intelligent tools to manage inventory, track sales, and analyze business performance, resulting in operational inefficiencies, stock-related problems, and poor business decisions.

## 3. Product goals
1. Let customers discover products, review product information, read reviews, and place orders online.
2. Give authorized administrators control over products, stock, orders, and store reporting.
3. Provide useful AI/ML forecasts and stock recommendations based on available historical data.
4. Make the application responsive and usable on common mobile and desktop screens.
5. Enforce role permissions in the backend, not only in the user interface.

## 4. Non-goals for the first MVP
- Multi-store franchise management.
- Real payment gateway settlement or storage of card data.
- Automated supplier purchasing.
- Guaranteed food-safety certification or laboratory quality verification.
- Production-grade tax/accounting compliance without a separate requirements review.

## 5. User roles
### Guest/customer
- Browse public product catalogue and categories.
- View price, description, available stock status, quality/expiry information supplied by the store, and reviews.
- Add products to a cart and submit an order.
- View only their own order information where customer identity/order lookup is implemented.

### Administrator
- Sign in through a non-publicly advertised admin entry point.
- Create, update, deactivate, and manage products and categories.
- Maintain stock and batch/expiry information.
- View and process orders.
- Review sales summaries, inventory alerts, and AI recommendations.
- Manage moderation of reviews if that capability is enabled.

## 6. Core user journeys
### Customer journey
1. Open the storefront.
2. Search or browse categories.
3. Open a product and inspect details and reviews.
4. Add available quantity to cart.
5. Provide required order/contact/delivery information.
6. Choose cash on delivery or clearly labelled simulated online payment.
7. Submit order and receive an order reference/status.

### Administrator journey
1. Navigate to the admin sign-in route.
2. Authenticate with administrator credentials.
3. Backend verifies identity, active status, and administrator role.
4. View dashboard.
5. Manage products, stock, and orders.
6. Review analytics and AI recommendations.
7. Sign out; server-side session/token is invalidated or expires.

## 7. Functional scope
- Public storefront and product catalogue.
- Product details and customer reviews.
- Cart and order placement.
- Admin authentication and authorization.
- Product/category CRUD for administrators.
- Inventory adjustments and stock alerts.
- Order lifecycle management.
- COD and simulated online payment flow.
- Sales and inventory dashboards.
- ML demand forecasting and recommendations.
- Audit trail for sensitive administrator actions.

## 8. Non-functional requirements
- Security: server-side authorization for every protected endpoint; password hashing; secrets kept outside source control.
- Privacy: collect only necessary customer data; restrict access to customer order data.
- Reliability: validate input and handle database/API errors safely.
- Performance: paginate catalogue/order lists; index frequently filtered database fields.
- Accessibility: semantic controls, keyboard navigation, readable contrast and form labels.
- Responsiveness: support mobile, tablet and desktop.
- Maintainability: separate API routes, schemas, models, services, and ML code.
- Explainability: show the data window and basic rationale behind forecasts; do not present estimates as certainty.

## 9. Success measures for the hackathon MVP
- Customer can complete an order in a test environment.
- Customer cannot create or modify products or access admin analytics.
- Unauthenticated and non-admin requests to protected admin APIs are rejected.
- Admin can update stock and process an order.
- Forecast endpoint returns a documented prediction when sufficient sample data exists and a safe fallback when it does not.
- Core flows pass the test plan.

## 10. Assumptions and open decisions
- Initial deployment targets one grocery store.
- Product quality and expiry details are entered by the store; the application does not independently certify quality.
- Customer account requirement (guest checkout versus mandatory registration) must be finalized before checkout implementation.
- Currency, tax rules, delivery zones, cancellation/refund policy, and retention period must be confirmed for the target store.
- The online payment option in the hackathon build is a simulation only.
