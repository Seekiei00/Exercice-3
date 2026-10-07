from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.enums import Role


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default=Role.VIEWER.value)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(String(150))
    format: Mapped[str] = mapped_column(String(50))
    is_public: Mapped[bool] = mapped_column(Boolean, default=True)


class QualityCheck(Base):
    __tablename__ = "quality_checks"

    id: Mapped[int] = mapped_column(primary_key=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.id"))
    checked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    score: Mapped[int]
    status: Mapped[str] = mapped_column(String(20))
    comment: Mapped[str] = mapped_column(String(500))
