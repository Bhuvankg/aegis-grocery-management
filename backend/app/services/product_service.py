"""
Product service — business logic for the products domain.
Applies public visibility rules: only active products are served.
"""
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.inventory import Inventory


def _base_public_query(db: Session):
    """Active products with related category and inventory eagerly loaded."""
    return (
        db.query(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.inventory),
        )
        .filter(Product.is_active == True)  # noqa: E712
    )


def list_products(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    category_id: int | None = None,
    search: str | None = None,
) -> tuple[int, list[Product]]:
    """
    Returns (total_count, page_of_products) for active products.
    page is 1-indexed.
    """
    page_size = min(page_size, 100)  # cap to prevent abuse
    q = _base_public_query(db)

    if category_id is not None:
        q = q.filter(Product.category_id == category_id)

    if search:
        term = f"%{search.strip()}%"
        q = q.filter(Product.name.ilike(term))

    total = q.count()
    items = (
        q.order_by(Product.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def get_product_by_slug(db: Session, slug: str) -> Product | None:
    return (
        _base_public_query(db)
        .filter(Product.slug == slug)
        .first()
    )


def get_product_by_id(db: Session, product_id: int) -> Product | None:
    return (
        _base_public_query(db)
        .filter(Product.id == product_id)
        .first()
    )
