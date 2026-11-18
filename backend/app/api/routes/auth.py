from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminLogin, Token, AdminProfile
from app.services import auth_service

router = APIRouter(tags=["authentication"])


@router.post("/auth/admin/login", response_model=Token)
def admin_login(credentials: AdminLogin, db: Session = Depends(get_db)):
    """
    Authenticate a provisioned store administrator.
    Public admin registration is strictly disallowed.
    """
    admin = auth_service.authenticate_admin(db, credentials.email, credentials.password)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_service.create_admin_token(admin)


@router.get("/admin/me", response_model=AdminProfile)
def get_current_admin_profile(current_admin: Admin = Depends(get_current_admin)):
    """Return the profile of the currently authenticated administrator."""
    return current_admin


@router.post("/auth/admin/logout")
def admin_logout(current_admin: Admin = Depends(get_current_admin)):
    """Stateless logout confirmation for authenticated administrator."""
    return {"success": True, "message": "Logged out successfully"}
