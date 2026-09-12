from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from uuid import UUID

from app.application.dtos.auth import TokenResponse, UsuarioPublicoDTO
from app.domain.exceptions import UnauthorizedException
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.config.settings import get_settings
from app.infrastructure.security.jwt import create_access_token
from app.infrastructure.security.password import verify_password


def _to_dto(usuario) -> UsuarioPublicoDTO:
    return UsuarioPublicoDTO.model_validate(usuario)


class LoginUseCase:
    def __init__(self, usuarios: UsuarioRepository, refresh_tokens: RefreshTokenRepository) -> None:
        self._usuarios = usuarios
        self._refresh = refresh_tokens

    async def execute(self, correo: str, password: str) -> TokenResponse:
        usuario = await self._usuarios.get_by_correo(correo)
        if usuario is None or not usuario.activo or not verify_password(password, usuario.password_hash):
            raise UnauthorizedException("Credenciales inválidas")
        return await self._issue(usuario.id, usuario.rol.value)

    async def _issue(self, usuario_id: UUID, rol: str) -> TokenResponse:
        settings = get_settings()
        access = create_access_token(usuario_id=usuario_id, rol=rol)
        refresh = token_urlsafe(48)
        expira = datetime.now(timezone.utc) + timedelta(days=settings.jwt_refresh_token_expire_days)
        await self._refresh.add(usuario_id, refresh, expira)
        return TokenResponse(access_token=access, refresh_token=refresh)


class RefreshTokenUseCase:
    def __init__(self, usuarios: UsuarioRepository, refresh_tokens: RefreshTokenRepository) -> None:
        self._usuarios = usuarios
        self._refresh = refresh_tokens

    async def execute(self, refresh_token: str) -> TokenResponse:
        usuario_id = await self._refresh.get_valid(refresh_token)
        if usuario_id is None:
            raise UnauthorizedException("Refresh token inválido o expirado")
        usuario = await self._usuarios.get_by_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise UnauthorizedException("Usuario no disponible")
        await self._refresh.revoke(refresh_token)
        login = LoginUseCase(self._usuarios, self._refresh)
        return await login._issue(usuario.id, usuario.rol.value)


class LogoutUseCase:
    def __init__(self, refresh_tokens: RefreshTokenRepository) -> None:
        self._refresh = refresh_tokens

    async def execute(self, refresh_token: str) -> None:
        await self._refresh.revoke(refresh_token)


class GetMeUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(self, usuario_id: UUID) -> UsuarioPublicoDTO:
        usuario = await self._usuarios.get_by_id(usuario_id)
        if usuario is None:
            raise UnauthorizedException("Usuario no encontrado")
        return _to_dto(usuario)
