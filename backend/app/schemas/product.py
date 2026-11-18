"""
Public Pydantic schemas for products.
IMPORTANT: cost_price and supplier details are NEVER included here.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.schemas.category import CategoryPublic


class InventoryPublic(BaseModel):
    """Stock availability — quantity only, no internal cost/movement details."""
    model_config = ConfigDict(from_attributes=True)

    quantity: int
    reorder_level: int


class ProductPublic(BaseModel):
    """Public product response — safe for all visitors."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sku: str
    description: str | None = None
    selling_price: Decimal
    unit: str | None = None
    image_url: str | None = None
    # Store-entered quality/expiry fields — not independently certified
    quality_notes: str | None = None
    expiry_info: str | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    category: CategoryPublic | None = None
    inventory: InventoryPublic | None = None


class ProductListItem(BaseModel):
    """Lightweight product card for list/catalogue views."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    selling_price: Decimal
    unit: str | None = None
    image_url: str | None = None
    is_active: bool
    category: CategoryPublic | None = None
    inventory: InventoryPublic | None = None


class PaginatedProducts(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductListItem]
