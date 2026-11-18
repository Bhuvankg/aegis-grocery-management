
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean, DateTime, ForeignKey, Index, Integer,
    Numeric, String, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "products"

    __table_args__ = (
        Index("ix_products_active_category", "is_active", "category_id"),
        Index("ix_products_name", "name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(180), unique=True, index=True, nullable=False
    )
    sku: Mapped[str] = mapped_column(
        String(80), unique=True, index=True, nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text)

    # Public selling price — stored as NUMERIC (never float)
    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), nullable=False
    )
    # cost_price is admin-only; never expose in public schemas
    cost_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    unit: Mapped[str | None] = mapped_column(String(30))   # e.g. "kg", "pcs"
    image_url: Mapped[str | None] = mapped_column(String(500))

    # Store-entered quality / expiry fields (not independently certified)
    quality_notes: Mapped[str | None] = mapped_column(Text)
    expiry_info: Mapped[str | None] = mapped_column(String(200))

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL")
    )
    supplier_id: Mapped[int | None] = mapped_column(
        ForeignKey("suppliers.id", ondelete="SET NULL")
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    category: Mapped["Category | None"] = relationship(  # type: ignore[name-defined]
        "Category", lazy="select"
    )
    inventory: Mapped["Inventory | None"] = relationship(  # type: ignore[name-defined]
        "Inventory", back_populates="product", uselist=False, lazy="select"
    )
    reviews: Mapped[list["Review"]] = relationship(  # type: ignore[name-defined]
        "Review", back_populates="product", lazy="select"
    )
