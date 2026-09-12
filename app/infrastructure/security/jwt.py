from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt

from app.domain.exceptions import UnauthorizedException
from app.infrastructure.config.settings import get_settings


def create_access_token(*, usuario_id: UUID, rol: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(usuario_id),
        "rol": rol,
        "typ": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise UnauthorizedException("Token inválido o expirado") from exc
    if payload.get("typ") != "access":
        raise UnauthorizedException("Tipo de token inválido")
    return payload
