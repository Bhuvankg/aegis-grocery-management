# AEGIS AI – AI-Powered Grocery Store Management System

AEGIS AI is a full-stack, AI-powered grocery store platform built with **FastAPI**, **PostgreSQL** (via Supabase), and **React (Vite)**. It provides two strictly separated experiences:
1. **Public Customer Storefront**: Clean, accessible online shopping with zero-trust pricing, real-time inventory checks, shopping cart, cash on delivery (COD), simulated demo online payment, and verified product reviews.
2. **Private Administrator Workspace**: Role-protected management system with JWT authentication, inventory tracking, stock adjustments, order lifecycle controls, sales/margin analytics, and AI/ML demand forecasting and restock recommendations.

---

## 🏗️ Architecture & Features

```
AEGIS_AI/
├── backend/
│   ├── app/
│   │   ├── api/routes/          # Public & private API endpoints
│   │   ├── core/                # Config, JWT tokens, bcrypt security
│   │   ├── db/                  # SQLAlchemy base & session management
│   │   ├── models/              # PostgreSQL models (Products, Orders, Admin, etc.)
│   │   ├── schemas/             # Pydantic schemas (strictly separating public vs admin)
│   │   └── services/            # Business logic (Orders, Auth, Payments, Analytics)
│   ├── ai_engine/               # Demand forecasting, restock recommender, perishables scanner
│   ├── create_admin.py          # Interactive CLI admin provisioner
│   ├── quick_setup_admin.py     # Fast-provision default admin script
│   ├── run_tests.py             # Invariant & boundary regression test suite
│   ├── seed.py                  # Database seeder (categories, products, suppliers, reviews)
│   └── migrate_*.py             # Database schema migrations
└── frontend/
    └── src/
        ├── components/          # ProductCard, Navbar, CartDrawer, StarRating, etc.
        ├── context/             # CartContext (persisted local cart state)
        ├── pages/               # Storefront, Detail, Checkout, Confirmation, Admin
        └── services/            # Axios API clients (public storefront & admin workspace)
```

---

## 🛡️ Core Security & Invariants

1. **Two Distinct Experiences**: Customers never have access to internal cost prices, profit margins, supplier details, or admin dashboards.
2. **No Public Admin Registration**: Store admin accounts can **only** be provisioned via the secure server CLI (`create_admin.py` or `quick_setup_admin.py`).
3. **Backend-Enforced Authorization**: Every admin endpoint validates signed JWTs with `get_current_admin`. Frontend guards are for UX only.
4. **Zero-Trust Pricing**: Cart items and orders recalculate all prices, subtotals, and delivery fees server-side from current database records.
5. **Simulated Payment Disclosure**: The demo online payment flow explicitly discloses that it is a simulation. It never asks for, processes, or stores payment card numbers or CVVs.
6. **Advisory AI Forecasts**: AI demand predictions and restock alerts are purely advisory and never automatically modify stock levels, prices, or orders.

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL database (or Supabase project)

---

### 1. Backend Setup

```powershell
cd backend

# Create & activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and configure your DATABASE_URL and JWT_SECRET_KEY
Copy-Item .env.example .env

# Provision default administrator account
.\venv\Scripts\python.exe quick_setup_admin.py

# Run the backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- Backend API: http://127.0.0.1:8000
- Interactive Swagger Docs: http://127.0.0.1:8000/docs
- Health Check: http://127.0.0.1:8000/api/health

---

### 2. Frontend Setup

In a new terminal:

```powershell
cd frontend

# Install packages
npm install

# Start Vite development server
npm run dev
```

- Storefront: http://localhost:5173/
- Admin Sign In: http://localhost:5173/admin/login
  - **Email:** `admin@aegis.ai`
  - **Password:** `Admin@12345`

---

### 3. Automated Test Suite

Run the full invariant and security test suite:

```powershell
cd backend
.\venv\Scripts\python.exe run_tests.py
```

Tests cover:
- Public schema cost price non-leakage
- Absence of public admin registration endpoints
- Bcrypt password hash verification
- JWT tamper resistance & forged signature rejection
- Payment simulation safety (zero card data collection)
- AI forecasting math & advisory disclaimers
- Restock recommendation logic

---

## 📋 API Summary

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| `GET` | `/api/health` | Public | System health check |
| `GET` | `/api/categories` | Public | Active categories listing |
| `GET` | `/api/products` | Public | Filtered & paginated product catalog |
| `GET` | `/api/products/{id_or_slug}` | Public | Detailed product view with reviews |
| `POST` | `/api/orders` | Public | Submit new customer order (zero-trust calculation) |
| `GET` | `/api/orders/{order_number}` | Public | Order status and confirmation receipt |
| `POST` | `/api/payments/simulate` | Public | Simulated demo payment approval/decline |
| `POST` | `/api/auth/admin/login` | Public | Issue admin JWT access token |
| `GET` | `/api/admin/me` | Admin | Current authenticated admin profile |
| `GET` | `/api/admin/products` | Admin | Complete catalog including cost & profit margins |
| `POST` | `/api/admin/products` | Admin | Create product with initial inventory |
| `POST` | `/api/admin/inventory/adjust` | Admin | Direct stock adjustments with reason tracking |
| `GET` | `/api/admin/orders` | Admin | All store orders with customer & fulfillment details |
| `PATCH` | `/api/admin/orders/{id}/status` | Admin | Order lifecycle transition (Pending -> Processing -> Delivered) |
| `GET` | `/api/admin/ai/forecasts` | Admin | 7-day demand projections & trend signals |
| `GET` | `/api/admin/ai/restock-recommendations` | Admin | Sales velocity & days-of-supply alerts |
| `GET` | `/api/admin/ai/expiry-alerts` | Admin | Perishable shelf-life monitoring |
| `GET` | `/api/admin/analytics/summary` | Admin | Executive summary: revenue, profit margins, inventory valuation |
| `GET` | `/api/admin/sales/history` | Admin | Chronological sales ledger with COGS, gross profit & item breakdown |
| `GET` | `/api/admin/sales/daily-summary` | Admin | Daily revenue & profit time-series aggregation for trend charts |
| `GET` | `/api/admin/sales/product/{id}` | Admin | Per-product lifetime units, revenue, COGS, and daily breakdown |
