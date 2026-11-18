"""
Review service — business logic for the reviews domain.
Only approved reviews are exposed publicly.
"""
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.review import Review


def list_approved_reviews(
    db: Session,
    product_id: int,
    page: int = 1,
    page_size: int = 10,
) -> tuple[int, float | None, list[Review]]:
    """
    Returns (total, average_rating, page_of_reviews) for a product.
    Only approved reviews are included.
    """
    page_size = min(page_size, 50)
    q = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
            Review.is_approved == True,  # noqa: E712
        )
    )

    total = q.count()

    avg_row = (
        db.query(func.avg(Review.rating))
        .filter(
            Review.product_id == product_id,
            Review.is_approved == True,  # noqa: E712
        )
        .scalar()
    )
    average_rating = round(float(avg_row), 2) if avg_row is not None else None

    items = (
        q.order_by(Review.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, average_rating, items


def submit_review(
    db: Session,
    product_id: int,
    rating: int,
    body: str | None,
    customer_id: int | None = None,
) -> Review:
    """
    Create a review pending approval (is_approved=False by default).
    Returns the new Review instance.
    """
    review = Review(
        product_id=product_id,
        customer_id=customer_id,
        rating=rating,
        body=body,
        is_approved=False,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
