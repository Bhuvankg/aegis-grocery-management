from sqlalchemy.orm import Session

from app.core.security import verify_password, hash_password, create_access_token
from app.models.admin import Admin
from app.schemas.admin import Token, AdminProfile


def authenticate_admin(db: Session, email: str, password: str) -> Admin | None:
    """Validate administrator credentials."""
    admin = db.query(Admin).filter(Admin.email == email.strip().lower()).first()
    if not admin:
        return None
    if not verify_password(password, admin.password_hash):
        return None
    if not admin.is_active:
        return None
    return admin


def create_admin_token(admin: Admin) -> Token:
    """Issue a JWT token for the authenticated administrator."""
    access_token = create_access_token(
        subject=admin.id,
        extra_claims={"email": admin.email, "role": "admin"}
    )
    return Token(
        access_token=access_token,
        token_type="bearer",
        admin=AdminProfile.model_validate(admin)
    )


def provision_admin(db: Session, email: str, password: str, full_name: str) -> Admin:
    """Provision a new administrator account (CLI / seed only, never exposed publicly)."""
    clean_email = email.strip().lower()
    existing = db.query(Admin).filter(Admin.email == clean_email).first()
    if existing:
        existing.password_hash = hash_password(password)
        existing.full_name = full_name
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    admin = Admin(
        email=clean_email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin
