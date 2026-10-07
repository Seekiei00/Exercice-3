from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose.exceptions import ExpiredSignatureError, JWTError
from sqlalchemy import select

from app.database import DbSession
from app.enums import Role
from app.models import User
from app.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: DbSession,
) -> User:
    """401 si le token est absent, invalide ou expiré."""
    if credentials is None:
        raise _unauthorized("Token invalide ou expiré.")

    try:
        payload = decode_access_token(credentials.credentials)
    except ExpiredSignatureError:
        raise _unauthorized("Token expiré")
    except JWTError:
        raise _unauthorized("Token invalide")

    username = payload.get("sub")
    user = db.scalar(select(User).where(User.username == username)) if username else None
    if user is None:
        raise _unauthorized("Token invalide")
    return user


def require_roles(*allowed_roles: Role):
    """403 si l'utilisateur authentifié n'a pas l'un des rôles autorisés."""
    autoriser = {role.value for role in allowed_roles}

    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in autoriser:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rôle non autorisé pour cette action")
        return current_user

    return dependency


require_analyst = require_roles(Role.ANALYST, Role.MANAGER)
require_manager = require_roles(Role.MANAGER)



