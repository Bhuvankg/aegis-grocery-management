# AEGIS AI architecture

## User experiences
- Customer: public product discovery, reviews, cart, checkout, order tracking.
- Administrator: private authentication and protected inventory, product, order, sales and AI tools.

## Backend layers
- `api/routes`: HTTP endpoints
- `models`: SQLAlchemy database models (introduced in Phase 2 onward)
- `schemas`: request/response validation
- `services`: business rules
- `ai_engine`: forecasting and recommendation logic
- `security`: password hashing, sessions/tokens, roles and authorization

## Security rule
Frontend route hiding is only a usability feature. Every administrator API must verify a valid authenticated administrator on the server. There will be no public admin registration endpoint.
