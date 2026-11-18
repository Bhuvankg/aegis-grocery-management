"""
Category service — business logic for the categories domain.
"""
from sqlalchemy.orm import Session

from app.models.category import Category


def list_active_categories(db: Session) -> list[Category]:
    return (
        db.query(Category)
        .filter(Category.is_active == True)  # noqa: E712
        .order_by(Category.name)
        .all()
    )


def get_category_by_slug(db: Session, slug: str) -> Category | None:
    return (
        db.query(Category)
        .filter(Category.slug == slug, Category.is_active == True)  # noqa: E712
        .first()
    )
