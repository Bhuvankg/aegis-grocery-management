# Business Requirements Document (BRD)
## AEGIS AI – AI-Powered Grocery Store Management System

**Document status:** Initial baseline  
**Version:** 1.0

## 1. Business background
Small grocery retailers often maintain product availability, sales records, and stock decisions using disconnected or manual processes. AEGIS AI proposes one platform that connects customer orders with store operations and adds data-driven recommendations.

## 2. Business objectives
- Improve visibility of product availability and stock levels.
- Reduce avoidable stockouts and excess stock through better planning.
- Centralize customer orders and their status.
- Help store owners understand sales and product performance.
- Provide an affordable, approachable digital storefront.

## 3. Stakeholders
| Stakeholder | Interest / responsibility |
|---|---|
| Store owner / administrator | Owns store data and controls admin access |
| Store staff (future role) | May process orders and stock under limited permissions |
| Customer | Browses products and places orders |
| Project team | Builds, tests, documents, and demonstrates the system |
| Hackathon judges | Evaluate usefulness, implementation, innovation, and demo |

## 4. Business requirements
| ID | Requirement | Priority |
|---|---|---|
| BR-01 | Customers can browse products without administrator privileges. | Must |
| BR-02 | Customers can place grocery orders. | Must |
| BR-03 | Customers cannot add, edit, delete, or price products. | Must |
| BR-04 | Only authorized administrators can access store-management functions. | Must |
| BR-05 | Administrators can maintain product and inventory records. | Must |
| BR-06 | Administrators can view and update customer orders. | Must |
| BR-07 | The system records order and sales data for reporting. | Must |
| BR-08 | The system identifies low-stock products using configurable thresholds. | Should |
| BR-09 | The system provides ML-assisted demand forecasts when adequate data exists. | Should |
| BR-10 | Customers can read reviews and quality/expiry information entered by the store. | Should |
| BR-11 | The checkout supports COD and a non-real simulated online payment. | Must for demo |

## 5. Business rules
1. An administrator account is provisioned through a controlled setup process; there is no public admin registration.
2. A customer role never grants access to inventory, product mutation, internal costs, profit, or store analytics.
3. Product changes and stock adjustments must be attributable to an administrator account.
4. An order must contain at least one valid item and positive quantities.
5. Stock availability must be checked on the server when an order is submitted.
6. The stock deduction point and order cancellation/restock policy must be implemented consistently and tested.
7. Simulated online payment must be labelled as a demo and must not claim that money was transferred.
8. AI forecasts are advisory and must not silently change stock or place supplier orders.

## 6. Business process overview
- Product setup → customer discovery → cart → checkout → order record → administrator processing → stock/sales reporting → AI analysis.
- Inventory updates should be transactional to avoid overselling when simultaneous orders occur.
- Reviews should be associated with a product and moderated or constrained according to the chosen customer identity model.

## 7. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Unauthorized admin access | Backend role checks, secure password hashing, short-lived access and secure session handling |
| Incorrect stock counts | Transactional updates, audit log, validation and stock reconciliation |
| Weak forecast data | Minimum-data checks, baseline fallback, clear confidence/limitations |
| Fake quality claims | Display source and date of store-entered information; do not imply independent certification |
| Payment misunderstanding | Prominent simulated-payment label; no real card collection |
| Secrets committed to Git | `.env` ignored; use secret manager in deployment |

## 8. Acceptance criteria
The business requirements are accepted when the matching functional requirements and test cases pass, especially the separation between customer and administrator capabilities.
