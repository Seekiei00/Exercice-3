import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _required(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Variable d'environnement manquante : {name} (voir .env.example)")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret: str
    jwt_algorithm: str
    jwt_expires_minutes: int
    initial_manager_username: str
    initial_manager_password: str


settings = Settings(
    database_url=_required("DATABASE_URL"),
    jwt_secret=_required("JWT_SECRET"),
    jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
    jwt_expires_minutes=int(os.getenv("JWT_EXPIRES_MINUTES", "60")),
    initial_manager_username=_required("INITIAL_MANAGER_USERNAME"),
    initial_manager_password=_required("INITIAL_MANAGER_PASSWORD"),
)
