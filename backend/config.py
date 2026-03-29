import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent


def _split_origins(value: str | None) -> list[str]:
    if not value:
        value = ",".join(
            [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:5174",
                "http://127.0.0.1:5174",
                "http://localhost:5175",
                "http://127.0.0.1:5175",
                "http://localhost:5176",
                "http://127.0.0.1:5176",
            ]
        )
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(slots=True)
class Settings:
    project_name: str = "Dalalyst AI"
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "240"))
    sqlite_path: Path = Path(os.getenv("SQLITE_PATH", "backend/dalalyst.db"))
    cors_origins: list[str] = None  # type: ignore[assignment]

    def __post_init__(self):
        if not self.sqlite_path.is_absolute():
            self.sqlite_path = (PROJECT_ROOT / self.sqlite_path).resolve()
        self.cors_origins = _split_origins(os.getenv("CORS_ORIGINS"))


settings = Settings()
