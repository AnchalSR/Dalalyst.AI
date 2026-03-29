from auth.security import create_access_token, decode_access_token, hash_password, verify_password
from database import get_db
from models.schemas import AuthenticatedUser


class UserService:
    def create_user(self, email: str, password: str) -> AuthenticatedUser:
        with get_db() as connection:
            existing = connection.execute(
                "SELECT id FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()
            if existing:
                raise ValueError("An account with this email already exists.")

            cursor = connection.execute(
                "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                (email.lower(), hash_password(password)),
            )
            return AuthenticatedUser(id=cursor.lastrowid, email=email.lower())

    def authenticate(self, email: str, password: str) -> tuple[str, AuthenticatedUser]:
        with get_db() as connection:
            row = connection.execute(
                "SELECT id, email, password_hash FROM users WHERE email = ?",
                (email.lower(),),
            ).fetchone()

        if not row or not verify_password(password, row["password_hash"]):
            raise ValueError("Invalid email or password.")

        user = AuthenticatedUser(id=row["id"], email=row["email"])
        token = create_access_token(str(row["id"]))
        return token, user

    def get_user_from_token(self, token: str) -> AuthenticatedUser | None:
        user_id = int(decode_access_token(token))
        with get_db() as connection:
            row = connection.execute(
                "SELECT id, email FROM users WHERE id = ?",
                (user_id,),
            ).fetchone()

        if not row:
            return None
        return AuthenticatedUser(id=row["id"], email=row["email"])
