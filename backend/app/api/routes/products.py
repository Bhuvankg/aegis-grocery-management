"""
Public products endpoints.
Enforces public schema rules — cost_price and supplier data are NEVER returned.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import PaginatedProducts, ProductListItem, ProductPublic
from app.schemas.review import PaginatedReviews, ReviewSubmit
from app.services import product_service, review_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=PaginatedProducts)
def list_products(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category_id: int | None = Query(default=None),
    search: str | None = Query(default=None, max_length=100),
    db: Session = Depends(get_db),
):
    """
    Paginated active product catalogue.
    Supports optional category filter and name search.
    """
    total, items = product_service.list_products(
        db,
        page=page,
        page_size=page_size,
        category_id=category_id,
        search=search,
    )
    return PaginatedProducts(
        total=total,
        page=page,
        page_size=page_size,
        items=[ProductListItem.model_validate(p) for p in items],
    )


@router.get("/{slug}", response_model=ProductPublic)
def get_product(slug: str, db: Session = Depends(get_db)):
    """
    Return full public detail for a single active product by slug.
    cost_price and internal supplier info are excluded from the response schema.
    """
    product = product_service.get_product_by_slug(db, slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/{product_id}/reviews", response_model=PaginatedReviews)
def list_product_reviews(
    product_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """List published (approved) reviews for a product."""
    # Verify product exists and is active
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    total, average_rating, items = review_service.list_approved_reviews(
        db, product_id=product_id, page=page, page_size=page_size
    )
    return PaginatedReviews(
        total=total,
        page=page,
        page_size=page_size,
        average_rating=average_rating,
        items=items,
    )


@router.post("/{product_id}/reviews", status_code=201)
def submit_review(
    product_id: int,
    payload: ReviewSubmit,
    db: Session = Depends(get_db),
):
    """
    Submit a review for a product.
    Reviews are pending moderation (is_approved=False) until an admin approves them.
    """
    product = product_service.get_product_by_id(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    review_service.submit_review(
        db,
        product_id=product_id,
        rating=payload.rating,
        body=payload.body,
    )
    return {"success": True, "message": "Review submitted and pending approval"}
