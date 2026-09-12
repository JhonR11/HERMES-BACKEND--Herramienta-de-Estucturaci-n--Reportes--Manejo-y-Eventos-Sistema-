from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenResponse, UsuarioPublicoDTO
from app.application.use_cases.auth.auth_use_cases import GetMeUseCase, LoginUseCase, LogoutUseCase, RefreshTokenUseCase
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.refresh_token_repository import SqlAlchemyRefreshTokenRepository
from app.infrastructure.db.repositories.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.session import get_session
from app.presentation.api.v1.dependencies.auth import require_authenticated

router = APIRouter(prefix="/auth", tags=["Autenticación"])


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
