from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password + settings.PASSWORD_PEPPER)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password + settings.PASSWORD_PEPPER, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.JWT_REFRESH_TOKEN_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")


def decode_token(token: str) -> dict | None:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=["HS256"]
        )
        return payload
    except JWTError:
        return None
