from decimal import Decimal
from sqlalchemy.orm import Session, joinedload

from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.admin import AdminProductCreate, AdminProductUpdate


def list_admin_products(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    category_id: int | None = None,
    is_active: bool | None = None,
) -> tuple[int, list[Product]]:
    """List products with full admin details (costs, margins, inactive products)."""
    q = (
        db.query(Product)
        .options(
            joinedload(Product.category),
            joinedload(Product.inventory),
        )
    )

    if is_active is not None:
        q = q.filter(Product.is_active == is_active)

    if category_id is not None:
        q = q.filter(Product.category_id == category_id)

    if search:
        term = f"%{search.strip()}%"
        q = q.filter(Product.name.ilike(term) | Product.sku.ilike(term))

    total = q.count()
    items = (
        q.order_by(Product.name)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return total, items


def create_product(db: Session, data: AdminProductCreate) -> Product:
    """Create a new product and its initial inventory record."""
    product = Product(
        name=data.name,
        slug=data.slug,
        sku=data.sku,
        description=data.description,
        selling_price=data.selling_price,
        cost_price=data.cost_price,
        unit=data.unit,
        image_url=data.image_url,
        quality_notes=data.quality_notes,
        expiry_info=data.expiry_info,
        category_id=data.category_id,
        supplier_id=data.supplier_id,
        is_active=True,
    )
    db.add(product)
    db.flush()

    inventory = Inventory(
        product_id=product.id,
        quantity=data.initial_stock,
        reorder_level=data.reorder_level,
    )
    db.add(inventory)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: AdminProductUpdate) -> Product | None:
    """Update fields on a product."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None

    update_dict = data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(product, key, value)

    db.commit()
    db.refresh(product)
    return product


def deactivate_product(db: Session, product_id: int) -> bool:
    """Soft-delete / deactivate a product to preserve order history."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return False
    product.is_active = False
    db.commit()
    return True


def adjust_stock(db: Session, product_id: int, delta: int, reason: str = "") -> Inventory | None:
    """Adjust inventory stock for a product."""
    inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    if not inv:
        return None

    new_qty = inv.quantity + delta
    if new_qty < 0:
        new_qty = 0
    inv.quantity = new_qty
    db.commit()
    db.refresh(inv)
    return inv
