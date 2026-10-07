from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.enums import QualityStatus, Role


class PartialUpdate(BaseModel):
    """Base des schémas de modification : un champ fourni ne peut pas valoir null."""

    @model_validator(mode="after")
    def _reject_explicit_null(self):
        for field in self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} ne peut pas être null")
        return self


# --- Utilisateurs -----------------------------------------------------------

class UserRegister(BaseModel):
    username: Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=80)]
    password: Annotated[str, StringConstraints(min_length=8)]


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: Role


class UserRoleUpdate(BaseModel):
    role: Role


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Jeux de données --------------------------------------------------------

class DatasetCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str = Field(min_length=1, max_length=500)
    source: str = Field(min_length=1, max_length=150)
    format: str = Field(min_length=1, max_length=50)
    is_public: bool = True


class DatasetUpdate(PartialUpdate):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    source: Optional[str] = Field(default=None, min_length=1, max_length=150)
    format: Optional[str] = Field(default=None, min_length=1, max_length=50)
    is_public: Optional[bool] = None


class DatasetRead(DatasetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


# --- Contrôles qualité ------------------------------------------------------

class QualityCheckCreate(BaseModel):
    dataset_id: int
    score: int = Field(ge=0, le=100)
    status: QualityStatus
    comment: str = Field(min_length=1, max_length=500)


class QualityCheckUpdate(PartialUpdate):
    dataset_id: Optional[int] = None
    score: Optional[int] = Field(default=None, ge=0, le=100)
    status: Optional[QualityStatus] = None
    comment: Optional[str] = Field(default=None, min_length=1, max_length=500)


class QualityCheckRead(QualityCheckCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    checked_at: datetime
