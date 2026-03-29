from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class AuthenticatedUser(BaseModel):
    id: int
    email: EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: AuthenticatedUser


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    symbol: str | None = None


class PortfolioStockRequest(BaseModel):
    stock: str = Field(min_length=1, max_length=16)


class VideoSlide(BaseModel):
    title: str
    bullets: list[str]
    narration: str
    visual: str
