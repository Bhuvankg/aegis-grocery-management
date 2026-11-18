"""
CLI script to securely provision an initial Administrator account.
Run from backend/ with venv active:
    .\venv\Scripts\python.exe create_admin.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import app.models  # register all models with Base.metadata
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.services.auth_service import provision_admin


def main():
    print("=" * 55)
    print("  AEGIS AI - Administrator Account Provisioning")
    print("=" * 55)

    # Ensure admins table exists in database
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"⚠️  Note on table check: {e}")

    email = input("Admin Email [default: admin@aegis.ai]: ").strip() or "admin@aegis.ai"
    full_name = input("Admin Full Name [default: Store Administrator]: ").strip() or "Store Administrator"
    password = input("Admin Password [default: Admin@12345]: ").strip() or "Admin@12345"

    if len(password) < 6:
        print("❌ Error: Password must be at least 6 characters.")
        sys.exit(1)

    db = SessionLocal()
    try:
        admin = provision_admin(db, email=email, password=password, full_name=full_name)
        print(f"\n✅ Administrator successfully provisioned!")
        print(f"   ID:        {admin.id}")
        print(f"   Email:     {admin.email}")
        print(f"   Name:      {admin.full_name}")
        print(f"   Active:    {admin.is_active}")
        print(f"\n🔑 Sign In Credentials:")
        print(f"   Email:    {admin.email}")
        print(f"   Password: {password}")
        print(f"\nYou can now sign in at http://localhost:5173/admin/login")
    except Exception as e:
        print(f"\n❌ Failed to provision admin: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

