from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from models.schemas import AuthenticatedUser
from services.user_service import UserService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> AuthenticatedUser:
    try:
        user = UserService().get_user_from_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not authenticate user.",
        )
    return user
