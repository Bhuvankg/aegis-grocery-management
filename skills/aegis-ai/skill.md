# AEGIS AI Project Skill

## Purpose
This skill guides AI coding assistants and developers working on AEGIS AI, an AI-powered grocery store management system.

## Product invariants
1. There are two experiences: public customer storefront and private administrator workspace.
2. Customers may browse products, read published reviews and store-entered quality details, and place orders.
3. Customers must never create/edit/delete products, change prices, adjust inventory, view internal costs/profit, see all orders, or access admin analytics.
4. Only provisioned administrators may use admin capabilities.
5. Every protected operation must be authorized by the backend. Frontend route guards are not security.
6. Do not add public administrator registration.
7. Online payment in the hackathon MVP is a simulation only. Never request or store card numbers/CVV; never claim real money moved.
8. AI forecasts are advisory and must not automatically change stock, prices, or orders.
9. Store-entered quality and expiry information must not be described as independently certified or verified.
10. Do not commit secrets, credentials, tokens, or real customer data.

## Technology choices
- Frontend: React + Vite + JavaScript + CSS/Tailwind as selected.
- Backend: Python + FastAPI.
- Database: PostgreSQL + SQLAlchemy; use Alembic for schema migrations.
- Validation: Pydantic.
- ML: Python, pandas, scikit-learn; evaluate a simple baseline before selecting a more complex model.
- Charts: Recharts or an equivalent React chart library.

## Architecture conventions
- Keep API routes thin; put business logic in services.
- Keep SQLAlchemy models separate from Pydantic request/response schemas.
- Separate public schemas from admin schemas.
- Use dependency injection for database sessions and authenticated admin identity.
- Use transactions for order creation, stock deduction, and inventory movement.
- Store currency as NUMERIC/Decimal.
- Use UTC timestamps.
- Paginate list endpoints.
- Add tests for permission boundaries and business rules.

## AI/ML conventions
- Define target, features, training window, forecast horizon, and evaluation metric before model implementation.
- Split time-series data chronologically; do not randomly shuffle future/past observations.
- Compare the model with a naive or moving-average baseline.
- Check minimum history and missing dates.
- Return a safe insufficient-data result when history is inadequate.
- Record model version, data window, generated time, and forecast horizon.
- Explain that forecasts are estimates, not guarantees.

## Coding workflow
1. Inspect existing files before editing; preserve working code and folder conventions.
2. Implement one phase at a time.
3. State files created/changed and exact run/test commands.
4. Do not invent environment values or credentials.
5. Never weaken authorization to make a demo work.
6. Add migrations and tests when adding database entities or protected features.
7. Report assumptions and unfinished items explicitly.

## Definition of done
- Feature works through the intended UI and API.
- Server-side validation and authorization are implemented.
- Relevant tests pass.
- No secrets are committed.
- Error cases are handled.
- Documentation and setup instructions are updated.
