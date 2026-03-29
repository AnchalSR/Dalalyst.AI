from fastapi import APIRouter, Depends, HTTPException, status

from auth.dependencies import get_current_user
from models.schemas import TokenResponse, UserLoginRequest, UserRegisterRequest
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    try:
        user_service.create_user(payload.email, payload.password)
        token, user = user_service.authenticate(payload.email, payload.password)
        return TokenResponse(access_token=token, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/login", response_model=TokenResponse)
async def login(payload: UserLoginRequest):
    try:
        token, user = user_service.authenticate(payload.email, payload.password)
        return TokenResponse(access_token=token, user=user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return current_user
