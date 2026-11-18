"""
Public categories endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.category import CategoryPublic
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=list[CategoryPublic])
def list_categories(db: Session = Depends(get_db)):
    """Return all active categories."""
    return category_service.list_active_categories(db)


@router.get("/{slug}", response_model=CategoryPublic)
def get_category(slug: str, db: Session = Depends(get_db)):
    """Return a single active category by slug."""
    category = category_service.get_category_by_slug(db, slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
