from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ForbiddenException, UnauthorizedException
from app.domain.value_objects.enums import RolUsuario
from app.infrastructure.db.repositories.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.security.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_session),
) -> Usuario:
    if credentials is None:
        raise UnauthorizedException("Token de acceso requerido")
    payload = decode_access_token(credentials.credentials)
    usuario_id = UUID(payload["sub"])
    usuario = await SqlAlchemyUsuarioRepository(session).get_by_id(usuario_id)
    if usuario is None or not usuario.activo:
        raise UnauthorizedException("Usuario no disponible")
    return usuario


async def require_authenticated(user: Usuario = Depends(get_current_user)) -> Usuario:
    return user


async def require_admin(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.rol != RolUsuario.ADMINISTRADOR:
        raise ForbiddenException("Se requiere rol de administrador")
    return user


async def require_docente(user: Usuario = Depends(get_current_user)) -> Usuario:
    if user.rol != RolUsuario.DOCENTE:
        raise ForbiddenException("Se requiere rol de docente")
    return user
