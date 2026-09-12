from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from app.application.dtos.auth import ConfirmarCambioPasswordRequest
from app.application.interfaces.email import EmailService
from app.domain.exceptions import ValidationException
from app.domain.repositories.password_reset_repository import PasswordResetRepository
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.config.settings import get_settings
from app.infrastructure.db.repositories.password_reset_repository import hash_reset_token
from app.infrastructure.security.password import hash_password


class SolicitarCambioPasswordUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        tokens: PasswordResetRepository,
        email: EmailService,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens
        self._email = email

    async def execute(self, correo: str) -> None:
        usuario = await self._usuarios.get_by_correo(correo)
        if usuario is None or not usuario.activo:
            return
        settings = get_settings()
        token = token_urlsafe(48)
        expira_en = datetime.now(timezone.utc) + timedelta(
            minutes=settings.password_reset_token_expire_minutes
        )
        await self._tokens.add(usuario.id, hash_reset_token(token), expira_en)
        reset_url = f"{settings.resolved_base_url}/reset-password?token={token}"
        await self._email.send_password_reset(usuario.correo_institucional, reset_url)


class ConfirmarCambioPasswordUseCase:
    def __init__(
        self,
        usuarios: UsuarioRepository,
        tokens: PasswordResetRepository,
        refresh_tokens: RefreshTokenRepository,
    ) -> None:
        self._usuarios = usuarios
        self._tokens = tokens
        self._refresh_tokens = refresh_tokens

    async def execute(self, payload: ConfirmarCambioPasswordRequest) -> None:
        usuario_id = await self._tokens.consume_valid(hash_reset_token(payload.token))
        if usuario_id is None:
            raise ValidationException("El enlace es inválido o expiró")
        usuario = await self._usuarios.get_by_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise ValidationException("El enlace es inválido o expiró")
        usuario.password_hash = hash_password(payload.password_nueva)
        usuario.actualizado_en = datetime.now(timezone.utc)
        await self._usuarios.update(usuario)
        await self._refresh_tokens.revoke_all_for_user(usuario.id)