from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.auth import ActualizarPerfilRequest, CrearDocenteRequest, UsuarioPublicoDTO
from app.application.use_cases.docentes.docentes_use_cases import (
    ActualizarPerfilUseCase,
    CambiarEstadoDocenteUseCase,
    CrearDocenteUseCase,
    ListarDocentesUseCase,
    ObtenerDocenteUseCase,
)
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.session import get_session
from app.presentation.api.v1.dependencies.auth import require_admin, require_authenticated

router = APIRouter(prefix="/docentes", tags=["Docentes"])


@router.post(
    "",
    response_model=UsuarioPublicoDTO,
    status_code=201,
    summary="Crear docente (admin). La contraseña inicial es la cédula.",
    responses={409: {"description": "Correo o cédula duplicados"}},
)
async def crear_docente(
    payload: CrearDocenteRequest,
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> UsuarioPublicoDTO:
    return await CrearDocenteUseCase(SqlAlchemyUsuarioRepository(session)).execute(payload)


@router.get("", response_model=list[UsuarioPublicoDTO], summary="Listar docentes")
async def listar_docentes(
    _: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> list[UsuarioPublicoDTO]:
    return await ListarDocentesUseCase(SqlAlchemyUsuarioRepository(session)).execute()


@router.get("/{docente_id}", response_model=UsuarioPublicoDTO, summary="Obtener docente")
async def obtener_docente(
    docente_id: UUID,
    _: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> UsuarioPublicoDTO:
    return await ObtenerDocenteUseCase(SqlAlchemyUsuarioRepository(session)).execute(docente_id)


@router.patch("/{docente_id}", response_model=UsuarioPublicoDTO, summary="Actualizar perfil")
async def actualizar_docente(
    docente_id: UUID,
    payload: ActualizarPerfilRequest,
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> UsuarioPublicoDTO:
    return await ActualizarPerfilUseCase(SqlAlchemyUsuarioRepository(session)).execute(actor, docente_id, payload)


@router.patch(
    "/{docente_id}/activo",
    response_model=UsuarioPublicoDTO,
    summary="Activar o desactivar docente (admin)",
)
async def cambiar_estado(
    docente_id: UUID,
    activo: bool = Query(...),
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> UsuarioPublicoDTO:
    return await CambiarEstadoDocenteUseCase(SqlAlchemyUsuarioRepository(session)).execute(docente_id, activo)
