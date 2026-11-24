from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


def clean_required_text(value: str) -> str:
    cleaned = " ".join(value.split())
    if len(cleaned) < 2:
        raise ValueError("Ingresa al menos 2 caracteres válidos.")
    return cleaned


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")
    password: str = Field(min_length=1, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La contraseña es obligatoria.")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    role: Literal["admin", "seller"]
    full_name: str


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9._-]+$")
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=10, max_length=128)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("full_name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return clean_required_text(value)

    @field_validator("password")
    @classmethod
    def reject_blank_password(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("La contraseña es obligatoria.")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    full_name: str
    role: Literal["admin", "seller"]
    active: bool
    created_at: datetime


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    sku: str = Field(min_length=2, max_length=40, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    category: str = Field(min_length=2, max_length=60)
    description: str | None = Field(default=None, max_length=1000)
    cost_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    sale_price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(ge=0, le=1_000_000)
    min_stock: int = Field(ge=0, le=1_000_000)

    @field_validator("name", "category")
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return clean_required_text(value)

    @field_validator("sku")
    @classmethod
    def normalize_sku(cls, value: str) -> str:
        return value.strip().upper()

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class ProductOut(ProductCreate):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    active: bool
    created_at: datetime
    updated_at: datetime


class ProductCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    sku: str
    category: str
    description: str | None
    sale_price: Decimal
    stock: int
    min_stock: int
    active: bool


class SaleItemCreate(BaseModel):
    product_id: UUID
    quantity: int = Field(ge=1, le=10_000)


class SaleCreate(BaseModel):
    items: list[SaleItemCreate] = Field(min_length=1, max_length=100)
    payment_method: Literal["cash", "card", "yape", "plin", "transfer"]
    amount_received: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)


class SaleItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    product_id: UUID
    product_name: str
    sku: str
    quantity: int
    unit_price: Decimal


class SaleOut(BaseModel):
    id: UUID
    seller_id: UUID
    seller_name: str
    total: Decimal
    payment_method: str
    amount_received: Decimal
    change_due: Decimal
    created_at: datetime
    items: list[SaleItemOut]


class DashboardSummary(BaseModel):
    active_products: int
    low_stock_products: int
    sales_today: int
    revenue_today: Decimal
    recent_sales: list[SaleOut]

