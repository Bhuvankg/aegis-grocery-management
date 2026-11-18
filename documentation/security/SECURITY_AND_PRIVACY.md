# Security and privacy baseline

1. Administrator accounts are provisioned by a trusted setup process; no public signup.
2. Hash passwords with Argon2id (preferred) or bcrypt; never encrypt or store plaintext passwords.
3. Enforce role checks in FastAPI dependencies on every admin endpoint.
4. Use secure, HttpOnly, SameSite cookies for browser sessions where practical; configure CSRF protection for cookie-authenticated state-changing requests. If bearer tokens are used, keep access tokens short-lived and protect refresh-token handling.
5. Apply login rate limiting, generic login failure messages, and audit security events.
6. Validate and normalize inputs; use ORM parameterization; avoid raw SQL string interpolation.
7. Keep `.env` out of Git; use environment secrets in deployment.
8. Enforce HTTPS in production and configure trusted CORS origins narrowly.
9. Do not collect card numbers or CVVs for the demo payment simulation.
10. Restrict customer data to the minimum needed for fulfillment; restrict each customer to their own order data.
11. Do not expose cost price, profit, internal stock movement history, audit logs, or AI admin insights publicly.
12. Back up the database and document restore procedures before production use.
13. Keep dependencies updated and run security checks before deployment.
