from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.db.session import get_db
from app.models.admin import Admin
from app.schemas.admin import (
    AdminProductDetail,
    AdminProductCreate,
    AdminProductUpdate,
    AdminStockAdjustment,
)
from app.services import admin_service

router = APIRouter(prefix="/admin/products", tags=["admin-products"])


@router.get("", response_model=list[AdminProductDetail])
def list_products_for_admin(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    List catalogue for administrators.
    Includes cost prices, margins, inactive products, and exact stock counts.
    Requires administrator authorization.
    """
    total, items = admin_service.list_admin_products(
        db,
        page=page,
        page_size=page_size,
        search=search,
        category_id=category_id,
        is_active=is_active,
    )
    return items


@router.post("", response_model=AdminProductDetail, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: AdminProductCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Create a new product with initial stock and cost price.
    Requires administrator authorization.
    """
    return admin_service.create_product(db, payload)


@router.patch("/{product_id}", response_model=AdminProductDetail)
def update_product(
    product_id: int,
    payload: AdminProductUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Update price, details, or status of a product.
    Requires administrator authorization.
    """
    product = admin_service.update_product(db, product_id, payload)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.delete("/{product_id}")
def deactivate_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Deactivate / soft-delete a product.
    Requires administrator authorization.
    """
    success = admin_service.deactivate_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"success": True, "message": "Product deactivated successfully"}


@router.post("/{product_id}/stock")
def adjust_inventory_stock(
    product_id: int,
    payload: AdminStockAdjustment,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
):
    """
    Adjust product stock quantity.
    Requires administrator authorization.
    """
    inv = admin_service.adjust_stock(db, product_id, payload.quantity_delta, payload.reason)
    if not inv:
        raise HTTPException(status_code=404, detail="Product inventory record not found")
    return {
        "success": True,
        "product_id": product_id,
        "quantity": inv.quantity,
        "message": f"Stock adjusted by {payload.quantity_delta:+d} (reason: {payload.reason})",
    }
