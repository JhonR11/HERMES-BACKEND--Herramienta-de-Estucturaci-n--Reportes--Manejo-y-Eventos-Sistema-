from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo import ActualizarNoticiaRequest, CrearNoticiaRequest, NoticiaDTO
from app.application.use_cases.noticias.noticias_use_cases import (
    ActualizarNoticiaUseCase,
    CrearNoticiaUseCase,
    EliminarNoticiaUseCase,
    ListarNoticiasUseCase,
    ObtenerNoticiaUseCase,
)
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.noticia_repository import SqlAlchemyNoticiaRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.storage.local import LocalStorageService
from app.presentation.api.v1.dependencies.auth import require_admin

router = APIRouter(prefix="/noticias", tags=["Noticias"])


async def _foto(file: UploadFile | None) -> tuple[str, bytes, str] | None:
    if file is None:
        return None
    content = await file.read()
    if not content:
        return None
    return file.filename or "foto.jpg", content, file.content_type or "image/jpeg"


@router.post("", response_model=NoticiaDTO, status_code=201, summary="Crear noticia (admin)")
async def crear_noticia(
    titular: str = Form(..., min_length=3, max_length=200),
    descripcion_noticia: str = Form(..., min_length=10),
    link_opcional: str | None = Form(default=None),
    foto: UploadFile | None = File(default=None),
    actor: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> NoticiaDTO:
    payload = CrearNoticiaRequest(
        titular=titular, descripcion_noticia=descripcion_noticia, link_opcional=link_opcional
    )
    return await CrearNoticiaUseCase(SqlAlchemyNoticiaRepository(session), LocalStorageService()).execute(
        actor, payload, await _foto(foto)
    )


@router.get("", response_model=list[NoticiaDTO], summary="Listar noticias (admin)")
async def listar_noticias(
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[NoticiaDTO]:
    return await ListarNoticiasUseCase(SqlAlchemyNoticiaRepository(session)).execute()


@router.get("/{noticia_id}", response_model=NoticiaDTO, summary="Obtener noticia")
async def obtener_noticia(
    noticia_id: UUID,
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> NoticiaDTO:
    return await ObtenerNoticiaUseCase(SqlAlchemyNoticiaRepository(session)).execute(noticia_id)


@router.patch("/{noticia_id}", response_model=NoticiaDTO, summary="Actualizar noticia")
async def actualizar_noticia(
    noticia_id: UUID,
    titular: str | None = Form(default=None),
    descripcion_noticia: str | None = Form(default=None),
    link_opcional: str | None = Form(default=None),
    foto: UploadFile | None = File(default=None),
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> NoticiaDTO:
    payload = ActualizarNoticiaRequest(
        titular=titular, descripcion_noticia=descripcion_noticia, link_opcional=link_opcional
    )
    return await ActualizarNoticiaUseCase(SqlAlchemyNoticiaRepository(session), LocalStorageService()).execute(
        noticia_id, payload, await _foto(foto)
    )


@router.delete("/{noticia_id}", status_code=204, summary="Eliminar noticia")
async def eliminar_noticia(
    noticia_id: UUID,
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> None:
    await EliminarNoticiaUseCase(SqlAlchemyNoticiaRepository(session)).execute(noticia_id)
