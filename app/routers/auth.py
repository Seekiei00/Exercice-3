from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import DbSession
from app.enums import Role
from app.models import User
from app.schemas import TokenResponse, UserLogin, UserRead, UserRegister
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: DbSession):
    # Le rôle n'est jamais choisi par l'utilisateur : toujours viewer.
    user = User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role=Role.VIEWER.value,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilisateur déjà existant")
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: DbSession):
    user = db.scalar(select(User).where(User.username == payload.username))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=create_access_token(subject=user.username, role=user.role))
