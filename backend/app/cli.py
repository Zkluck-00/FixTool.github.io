from getpass import getpass
from uuid import uuid4

from sqlalchemy import select

from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def create_admin() -> None:
    username = input("Usuario administrador (3-50 caracteres): ").strip().lower()
    full_name = input("Nombre completo: ").strip()
    password = getpass("Contraseña (mínimo 10 caracteres): ")
    confirmation = getpass("Repite la contraseña: ")
    if not (3 <= len(username) <= 50) or not (2 <= len(full_name) <= 120) or len(password) < 10 or not password.strip() or password != confirmation:
        raise SystemExit("Datos inválidos: revisa los campos y confirma la contraseña.")
    if any(character not in "abcdefghijklmnopqrstuvwxyz0123456789._-" for character in username):
        raise SystemExit("El usuario solo puede contener letras sin tilde, números, punto, guion y guion bajo.")
    with SessionLocal() as db:
        if db.scalar(select(User.id).where(User.username == username)):
            raise SystemExit("Ese nombre de usuario ya existe.")
        db.add(
            User(
                id=uuid4(),
                username=username,
                full_name=full_name,
                password_hash=hash_password(password),
                role="admin",
                active=True,
            )
        )
        db.commit()
    print(f"Administrador {username} creado correctamente.")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2 or sys.argv[1] != "create-admin":
        raise SystemExit("Uso: python -m app.cli create-admin")
    create_admin()

