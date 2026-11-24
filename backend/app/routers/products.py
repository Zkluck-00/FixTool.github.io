from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Product, User
from app.schemas import ProductCatalogOut, ProductCreate, ProductOut

router = APIRouter(prefix="/products", tags=["Productos"])


@router.get("", response_model=list[ProductOut])
def list_products(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
    q: str | None = Query(default=None, max_length=100),
    available: bool = False,
) -> list[Product]:
    query = select(Product).where(Product.active.is_(True))
    if available:
        query = query.where(Product.stock > 0)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(or_(Product.name.ilike(term), Product.sku.ilike(term), Product.category.ilike(term)))
    return list(db.scalars(query.order_by(Product.name)).all())


@router.get("/catalog", response_model=list[ProductCatalogOut])
def list_catalog(
    db: Annotated[Session, Depends(get_db)],
    _user: Annotated[User, Depends(get_current_user)],
    q: str | None = Query(default=None, max_length=100),
    available: bool = True,
) -> list[Product]:
    query = select(Product).where(Product.active.is_(True))
    if available:
        query = query.where(Product.stock > 0)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.where(or_(Product.name.ilike(term), Product.sku.ilike(term), Product.category.ilike(term)))
    return list(db.scalars(query.order_by(Product.name)).all())


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> Product:
    product = Product(id=uuid4(), **payload.model_dump())
    db.add(product)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código SKU ya está registrado.")
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(
    product_id: UUID,
    payload: ProductCreate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> Product:
    product = db.get(Product, product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    for key, value in payload.model_dump().items():
        setattr(product, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El código SKU ya está registrado.")
    db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def archive_product(
    product_id: UUID,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> None:
    product = db.get(Product, product_id)
    if product is None or not product.active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado.")
    product.active = False
    db.commit()

