"""
Public Pydantic schemas for reviews.
Only approved reviews are served by the public API.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ReviewPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rating: int = Field(ge=1, le=5)
    body: str | None = None
    created_at: datetime


class ReviewSubmit(BaseModel):
    """Customer review submission schema."""
    rating: int = Field(ge=1, le=5)
    body: str | None = Field(default=None, max_length=2000)


class PaginatedReviews(BaseModel):
    total: int
    page: int
    page_size: int
    average_rating: float | None = None
    items: list[ReviewPublic]
