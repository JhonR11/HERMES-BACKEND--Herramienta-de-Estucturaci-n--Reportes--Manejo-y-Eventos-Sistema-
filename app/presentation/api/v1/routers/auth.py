from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.auth import (
    ConfirmarCambioPasswordRequest,
    EnviarVistaCorreoRequest,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    SolicitarCambioPasswordRequest,
    TokenResponse,
    UsuarioPublicoDTO,
)
from app.application.use_cases.auth.auth_use_cases import GetMeUseCase, LoginUseCase, LogoutUseCase, RefreshTokenUseCase
from app.application.use_cases.auth.password_reset import (
    ConfirmarCambioPasswordUseCase,
    SolicitarCambioPasswordUseCase,
)
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from app.infrastructure.db.repositories.password_reset_repository import SqlAlchemyPasswordResetRepository
from app.infrastructure.db.repositories.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.config.settings import get_settings
from app.infrastructure.email.smtp import SmtpEmailService
from app.presentation.api.v1.dependencies.auth import require_admin, require_authenticated

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post(
    "/password-reset/preview",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Enviar vista de correo de cambio de contraseña (admin)",
)
async def send_password_reset_preview(
    payload: EnviarVistaCorreoRequest,
    _: Usuario = Depends(require_admin),
) -> None:
    settings = get_settings()
    preview_url = f"{settings.resolved_base_url}/reset-password?token=preview-token"
    await SmtpEmailService().send_password_reset_preview(str(payload.correo_destino), preview_url)


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Solicitar cambio de contraseña por correo",
)
async def request_password_reset(
    payload: SolicitarCambioPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> None:
    await SolicitarCambioPasswordUseCase(
        SqlAlchemyUsuarioRepository(session),
        SqlAlchemyPasswordResetRepository(session),
        SmtpEmailService(),
    ).execute(str(payload.correo_institucional))


@router.post(
    "/password-reset/confirm",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Confirmar cambio de contraseña",
)
async def confirm_password_reset(
    payload: ConfirmarCambioPasswordRequest,
    session: AsyncSession = Depends(get_session),
) -> None:
    await ConfirmarCambioPasswordUseCase(
        SqlAlchemyUsuarioRepository(session),
        SqlAlchemyPasswordResetRepository(session),
        SqlAlchemyRefreshTokenRepository(session),
    ).execute(payload)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesión",
    responses={401: {"description": "Credenciales inválidas"}},
)
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    return await LoginUseCase(
        SqlAlchemyUsuarioRepository(session),
        SqlAlchemyRefreshTokenRepository(session),
    ).execute(str(payload.correo_institucional), payload.password)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Renovar access token",
    responses={401: {"description": "Refresh token inválido"}},
)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> TokenResponse:
    return await RefreshTokenUseCase(
        SqlAlchemyUsuarioRepository(session),
        SqlAlchemyRefreshTokenRepository(session),
    ).execute(payload.refresh_token)


@router.post("/logout", status_code=204, summary="Cerrar sesión")
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_session)) -> None:
    await LogoutUseCase(SqlAlchemyRefreshTokenRepository(session)).execute(payload.refresh_token)


@router.get("/me", response_model=UsuarioPublicoDTO, summary="Perfil autenticado")
async def me(
    user: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> UsuarioPublicoDTO:
    return await GetMeUseCase(SqlAlchemyUsuarioRepository(session)).execute(user.id)
