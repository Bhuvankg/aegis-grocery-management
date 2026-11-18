"""
Public Pydantic schemas for categories.
Never expose internal/admin fields here.
"""
from pydantic import BaseModel, ConfigDict


class CategoryPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    description: str | None = None
    is_active: bool
