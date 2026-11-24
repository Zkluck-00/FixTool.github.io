from decimal import Decimal
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Numeric, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'seller')", name="ck_users_role"),
        CheckConstraint("username ~ '^[a-z0-9._-]+$'", name="ck_users_username_characters"),
        CheckConstraint("length(btrim(full_name)) >= 2", name="ck_users_full_name_nonblank"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    sales: Mapped[list["Sale"]] = relationship(back_populates="seller")


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("sale_price > 0", name="ck_products_sale_price_positive"),
        CheckConstraint("cost_price >= 0", name="ck_products_cost_price_nonnegative"),
        CheckConstraint("stock >= 0", name="ck_products_stock_nonnegative"),
        CheckConstraint("min_stock >= 0", name="ck_products_min_stock_nonnegative"),
        CheckConstraint("sku ~ '^[A-Z0-9][A-Z0-9._-]*$'", name="ck_products_sku_characters"),
        CheckConstraint("length(btrim(name)) >= 2", name="ck_products_name_nonblank"),
        CheckConstraint("length(btrim(category)) >= 2", name="ck_products_category_nonblank"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    sku: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(60), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cost_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sale_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    min_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        CheckConstraint("payment_method IN ('cash', 'card', 'yape', 'plin', 'transfer')", name="ck_sales_payment_method"),
        CheckConstraint("total >= 0", name="ck_sales_total_nonnegative"),
        CheckConstraint("amount_received >= total", name="ck_sales_amount_received"),
        CheckConstraint("change_due >= 0", name="ck_sales_change_nonnegative"),
        CheckConstraint(
            "(payment_method = 'cash' AND change_due = amount_received - total) OR "
            "(payment_method <> 'cash' AND amount_received = total AND change_due = 0)",
            name="ck_sales_payment_amounts",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    seller_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), index=True, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(16), nullable=False)
    amount_received: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    change_due: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    seller: Mapped[User] = relationship(back_populates="sales")
    items: Mapped[list["SaleItem"]] = relationship(back_populates="sale", cascade="all, delete-orphan", lazy="selectin")


class SaleItem(Base):
    __tablename__ = "sale_items"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_sale_items_quantity_positive"),
        CheckConstraint("unit_price > 0", name="ck_sale_items_unit_price_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    sale_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("sales.id", ondelete="CASCADE"), index=True, nullable=False)
    product_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), ForeignKey("products.id", ondelete="RESTRICT"), index=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(120), nullable=False)
    sku: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    sale: Mapped[Sale] = relationship(back_populates="items")

