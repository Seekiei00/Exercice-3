from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.database import DbSession
from app.dependencies import get_current_user, require_analyst, require_manager
from app.models import Dataset, QualityCheck
from app.schemas import QualityCheckCreate, QualityCheckRead, QualityCheckUpdate

router = APIRouter(prefix="/quality-checks", tags=["quality-checks"])


def _get_quality_check_or_404(db: DbSession, quality_check_id: int) -> QualityCheck:
    quality_check = db.get(QualityCheck, quality_check_id)
    if quality_check is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contrôle qualité introuvable")
    return quality_check


def _ensure_dataset_exists(db: DbSession, dataset_id: int) -> None:
    if db.get(Dataset, dataset_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Jeu de données introuvable")


# --- Consultation : tout utilisateur authentifié ----------------------------

@router.get(
    "",
    response_model=list[QualityCheckRead],
    dependencies=[Depends(get_current_user)],
)
def list_quality_checks(db: DbSession):
    return db.scalars(select(QualityCheck).order_by(QualityCheck.checked_at.desc())).all()


@router.get(
    "/{quality_check_id}",
    response_model=QualityCheckRead,
    dependencies=[Depends(get_current_user)],
)
def get_quality_check(quality_check_id: int, db: DbSession):
    return _get_quality_check_or_404(db, quality_check_id)


# --- Création et modification : analyst ou manager --------------------------

@router.post(
    "",
    response_model=QualityCheckRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_analyst)],
)
def create_quality_check(payload: QualityCheckCreate, db: DbSession):
    _ensure_dataset_exists(db, payload.dataset_id)
    quality_check = QualityCheck(**payload.model_dump())
    db.add(quality_check)
    db.commit()
    return quality_check


@router.put(
    "/{quality_check_id}",
    response_model=QualityCheckRead,
    dependencies=[Depends(require_analyst)],
)
def update_quality_check(quality_check_id: int, payload: QualityCheckUpdate, db: DbSession):
    quality_check = _get_quality_check_or_404(db, quality_check_id)
    changes = payload.model_dump(exclude_unset=True)
    if "dataset_id" in changes:
        _ensure_dataset_exists(db, changes["dataset_id"])
    for field, value in changes.items():
        setattr(quality_check, field, value)
    db.commit()
    return quality_check


# --- Suppression : manager uniquement ---------------------------------------

@router.delete(
    "/{quality_check_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_manager)],
)
def delete_quality_check(quality_check_id: int, db: DbSession):
    quality_check = _get_quality_check_or_404(db, quality_check_id)
    db.delete(quality_check)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
