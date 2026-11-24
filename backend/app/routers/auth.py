from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, require_admin
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserCreate, UserOut
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])
users_router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> TokenResponse:
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not user.active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos.")
    return TokenResponse(
        access_token=create_access_token(user.id, user.role),
        role=user.role,
        full_name=user.full_name,
    )


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]) -> User:
    return user


@users_router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_seller(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> User:
    existing = db.scalar(select(User).where(User.username == payload.username))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ese nombre de usuario ya está registrado.")
    user = User(
        id=uuid4(),
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role="seller",
        active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@users_router.get("", response_model=list[UserOut])
def list_users(
    db: Annotated[Session, Depends(get_db)],
    _admin: Annotated[User, Depends(require_admin)],
) -> list[User]:
    return list(db.scalars(select(User).order_by(User.full_name)).all())

