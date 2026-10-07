from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select

from app.database import DbSession
from app.dependencies import require_manager
from app.models import Dataset, QualityCheck
from app.schemas import DatasetCreate, DatasetRead, DatasetUpdate

router = APIRouter(prefix="/datasets", tags=["datasets"])


def _get_dataset_or_404(db: DbSession, dataset_id: int) -> Dataset:
    dataset = db.get(Dataset, dataset_id)
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return dataset


# --- Lecture publique : uniquement les datasets is_public = true ------------

@router.get("", response_model=list[DatasetRead])
def list_datasets(db: DbSession):
    return db.scalars(select(Dataset).where(Dataset.is_public.is_(True)).order_by(Dataset.id)).all()


@router.get("/{dataset_id}", response_model=DatasetRead)
def get_dataset(dataset_id: int, db: DbSession):
    dataset = db.scalar(
        select(Dataset).where(Dataset.id == dataset_id, Dataset.is_public.is_(True))
    )
    if dataset is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return dataset


# --- Écriture : réservée au manager -----------------------------------------

@router.post(
    "",
    response_model=DatasetRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_manager)],
)
def create_dataset(payload: DatasetCreate, db: DbSession):
    dataset = Dataset(**payload.model_dump())
    db.add(dataset)
    db.commit()
    return dataset


@router.put(
    "/{dataset_id}",
    response_model=DatasetRead,
    dependencies=[Depends(require_manager)],
)
def update_dataset(dataset_id: int, payload: DatasetUpdate, db: DbSession):
    dataset = _get_dataset_or_404(db, dataset_id)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(dataset, field, value)
    db.commit()
    return dataset


@router.delete(
    "/{dataset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_manager)],
)
def delete_dataset(dataset_id: int, db: DbSession):
    dataset = _get_dataset_or_404(db, dataset_id)
    has_checks = db.scalar(
        select(QualityCheck.id).where(QualityCheck.dataset_id == dataset_id).limit(1)
    )
    if has_checks is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Jeu de données utilisé par au moins un contrôle qualité, suppression impossible.",
        )
    db.delete(dataset)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
