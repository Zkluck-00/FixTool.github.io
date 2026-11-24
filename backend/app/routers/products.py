import logging
from typing import Annotated
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import Product, User
from app.schemas import ProductCatalogOut, ProductCreate, ProductOut

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/products", tags=["Productos"])


def _commit_product(db: Session) -> None:
    """Commit product changes and translate database errors into HTTP errors."""
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        sqlstate = getattr(exc.orig, "sqlstate", None)
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", None)
        logger.warning("Error de integridad en productos: SQLSTATE=%s, constraint=%s", sqlstate, constraint)

        if sqlstate == "23505":
            detail = (
                "El código SKU ya está registrado."
                if constraint in {"ix_products_sku", "products_sku_key"}
                else "El producto incumple una restricción de unicidad."
            )
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El producto incumple una restricción de la base de datos.",
        ) from exc
    except SQLAlchemyError as exc:
        db.rollback()
        logger.error(
            "Error al guardar producto: %s, SQLSTATE=%s",
            type(exc).__name__,
            getattr(getattr(exc, "orig", None), "sqlstate", None),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error de base de datos al guardar el producto.",
        ) from exc


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
    _commit_product(db)
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
    _commit_product(db)
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
    _commit_product(db)
