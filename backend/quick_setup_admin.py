"""
Non-interactive script to quickly provision or reset the default admin account.
Run from backend/ with venv:
    .\venv\Scripts\python.exe quick_setup_admin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app.models  # load models
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.auth_service import provision_admin


def main():
    print("Connecting to database and provisioning default admin...")
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Table check notice: {e}")

    db = SessionLocal()
    try:
        admin = provision_admin(
            db=db,
            email="admin@aegis.ai",
            password="Admin@12345",
            full_name="Store Administrator",
        )
        print("\n" + "=" * 50)
        print("✅ Admin account is ready!")
        print("=" * 50)
        print(f"  Email:    admin@aegis.ai")
        print(f"  Password: Admin@12345")
        print("=" * 50)
        print("Go to http://localhost:5173/admin/login and sign in with the exact credentials above.\n")
    except Exception as e:
        print(f"\n❌ Error setting up admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
