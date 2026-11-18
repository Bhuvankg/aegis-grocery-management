from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.category import CategoryPublic


class AdminLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class AdminProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    is_active: bool
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin: AdminProfile


class AdminInventoryItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    product_id: int
    quantity: int
    reorder_level: int
    updated_at: datetime


class AdminProductDetail(BaseModel):
    """
    Administrator product response.
    Includes sensitive commercial data (cost_price) and internal IDs.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sku: str
    description: str | None = None
    selling_price: Decimal
    cost_price: Decimal | None = None
    unit: str | None = None
    image_url: str | None = None
    quality_notes: str | None = None
    expiry_info: str | None = None
    is_active: bool
    category_id: int | None = None
    supplier_id: int | None = None
    created_at: datetime
    updated_at: datetime

    category: CategoryPublic | None = None
    inventory: AdminInventoryItem | None = None


class AdminProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    slug: str = Field(min_length=2, max_length=180)
    sku: str = Field(min_length=2, max_length=80)
    description: str | None = None
    selling_price: Decimal = Field(gt=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    unit: str | None = Field(default=None, max_length=30)
    image_url: str | None = None
    quality_notes: str | None = None
    expiry_info: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    initial_stock: int = Field(default=0, ge=0)
    reorder_level: int = Field(default=10, ge=0)


class AdminProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    selling_price: Decimal | None = Field(default=None, gt=0)
    cost_price: Decimal | None = Field(default=None, ge=0)
    unit: str | None = None
    image_url: str | None = None
    quality_notes: str | None = None
    expiry_info: str | None = None
    category_id: int | None = None
    supplier_id: int | None = None
    is_active: bool | None = None


class AdminStockAdjustment(BaseModel):
    quantity_delta: int = Field(description="Amount to add (positive) or deduct (negative)")
    reason: str = Field(default="Manual adjustment", max_length=255)
