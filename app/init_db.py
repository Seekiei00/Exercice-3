import logging

from sqlalchemy import select

from app import models  # noqa: F401  (enregistre les modèles dans Base.metadata)
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.enums import Role
from app.models import User
from app.security import hash_password

logger = logging.getLogger(__name__)


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)


def ensure_initial_manager() -> None:
    """Crée le premier manager (identifiants lus dans .env) s'il n'existe pas encore."""
    with SessionLocal() as db:
        username = settings.initial_manager_username
        if db.scalar(select(User).where(User.username == username)) is not None:
            return

        db.add(
            User(
                username=username,
                password_hash=hash_password(settings.initial_manager_password),
                role=Role.MANAGER.value,
            )
        )
        db.commit()
        logger.info("Manager initial '%s' créé.", username)
