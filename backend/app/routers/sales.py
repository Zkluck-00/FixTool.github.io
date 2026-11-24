from datetime import UTC, datetime, time, timedelta
from decimal import Decimal
from typing import Annotated
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.core.config import settings
from app.dependencies import get_current_user, require_admin
from app.models import Product, Sale, SaleItem, User
from app.schemas import DashboardSummary, SaleCreate, SaleItemOut, SaleOut

router = APIRouter(prefix="/sales", tags=["Ventas"])
dashboard_router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def serialize_sale(sale: Sale) -> SaleOut:
    return SaleOut(
        id=sale.id,
        seller_id=sale.seller_id,
        seller_name=sale.seller.full_name,
        total=sale.total,
        payment_method=sale.payment_method,
        amount_received=sale.amount_received,
        change_due=sale.change_due,
        created_at=sale.created_at,
        items=[SaleItemOut.model_validate(item) for item in sale.items],
    )


@router.get("", response_model=list[SaleOut])
def list_sales(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
    limit: int = Query(default=100, ge=1, le=500),
) -> list[SaleOut]:
    query = select(Sale).options(selectinload(Sale.items), selectinload(Sale.seller)).order_by(Sale.created_at.desc()).limit(limit)
    return [serialize_sale(sale) for sale in db.scalars(query).all()]


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(
    payload: SaleCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
) -> SaleOut:
    quantities: dict[UUID, int] = {}
    for item in payload.items:
        quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity

    products = list(
        db.scalars(
            select(Product)
            .where(Product.id.in_(list(quantities)), Product.active.is_(True))
            .order_by(Product.id)
            .with_for_update()
        ).all()
    )
    by_id = {product.id: product for product in products}
    if len(by_id) != len(quantities):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Uno o más productos ya no están disponibles.")

    for product_id, quantity in quantities.items():
        product = by_id[product_id]
        if product.stock < quantity:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Stock insuficiente para {product.name}. Disponible: {product.stock}.",
            )

    total = sum((by_id[item.product_id].sale_price * item.quantity for item in payload.items), Decimal("0.00"))
    if payload.payment_method == "cash":
        if payload.amount_received is None or payload.amount_received < total:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El efectivo recibido debe cubrir el total.")
        amount_received = payload.amount_received
    else:
        if payload.amount_received is not None and payload.amount_received < total:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="El pago registrado debe cubrir el total.")
        amount_received = total
    change_due = amount_received - total if payload.payment_method == "cash" else Decimal("0.00")

    sale = Sale(
        id=uuid4(),
        seller_id=user.id,
        total=total,
        payment_method=payload.payment_method,
        amount_received=amount_received,
        change_due=change_due,
    )
    for item in payload.items:
        product = by_id[item.product_id]
        product.stock -= item.quantity
        sale.items.append(
            SaleItem(
                id=uuid4(),
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                quantity=item.quantity,
                unit_price=product.sale_price,
            )
        )
    db.add(sale)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    sale = db.scalar(
        select(Sale)
        .where(Sale.id == sale.id)
        .options(selectinload(Sale.items), selectinload(Sale.seller))
    )
    return serialize_sale(sale)


@dashboard_router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> DashboardSummary:
    local_timezone = ZoneInfo(settings.app_timezone)
    local_day_start = datetime.combine(datetime.now(local_timezone).date(), time.min, tzinfo=local_timezone)
    day_start = local_day_start.astimezone(UTC)
    day_end = (local_day_start + timedelta(days=1)).astimezone(UTC)
    active_products = db.scalar(select(func.count(Product.id)).where(Product.active.is_(True))) or 0
    low_stock = db.scalar(
        select(func.count(Product.id)).where(Product.active.is_(True), Product.stock <= Product.min_stock)
    ) or 0
    sales_today = db.scalar(
        select(func.count(Sale.id)).where(Sale.created_at >= day_start, Sale.created_at < day_end)
    ) or 0
    revenue_today = db.scalar(
        select(func.coalesce(func.sum(Sale.total), 0)).where(Sale.created_at >= day_start, Sale.created_at < day_end)
    ) or Decimal("0.00")
    recent = db.scalars(
        select(Sale)
        .options(selectinload(Sale.items), selectinload(Sale.seller))
        .order_by(Sale.created_at.desc())
        .limit(8)
    ).all()
    return DashboardSummary(
        active_products=active_products,
        low_stock_products=low_stock,
        sales_today=sales_today,
        revenue_today=revenue_today,
        recent_sales=[serialize_sale(sale) for sale in recent],
    )

