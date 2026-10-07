from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.database import DbSession
from app.dependencies import require_manager
from app.models import User
from app.schemas import UserRead, UserRoleUpdate

# Tout le routeur est réservé au manager.
router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_manager)])


@router.get("/users", response_model=list[UserRead])
def list_users(db: DbSession):
    return db.scalars(select(User).order_by(User.id)).all()


@router.patch("/users/{user_id}/role", response_model=UserRead)
def update_user_role(user_id: int, payload: UserRoleUpdate, db: DbSession):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    user.role = payload.role.value
    db.commit()
    return user
