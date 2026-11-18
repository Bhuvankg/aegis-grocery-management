# Deployment checklist

## Before deployment
- Set production `DATABASE_URL` through the hosting provider's secret manager.
- Set exact production frontend origin for CORS.
- Use HTTPS.
- Use a managed PostgreSQL database with backups.
- Apply Alembic migrations.
- Provision the first administrator securely; never enable public admin signup.
- Configure secure cookie settings / token expiry and CSRF protection as applicable.
- Disable debug mode and avoid exposing stack traces.
- Configure logs, health checks, monitoring, and backup restoration.
- Verify all admin API authorization tests.
- Label demo online payment clearly; do not enable it as a real payment gateway.

## Environment values
See `backend/.env.example` and `frontend/.env.example`. Do not commit real `.env` files.
