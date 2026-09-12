from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo import (
    ActualizarReporteRequest,
    ArchivoDTO,
    CategoriaDTO,
    CrearReporteRequest,
    ReporteDTO,
)
from app.application.use_cases.reportes.categorias import ListarCategoriasUseCase
from app.application.use_cases.reportes.reportes_use_cases import (
    ActualizarReporteUseCase,
    CrearReporteUseCase,
    EliminarArchivoReporteUseCase,
    ListarReportesUseCase,
    ObtenerReporteUseCase,
    SubirArchivoReporteUseCase,
)
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.categoria_repository import SqlAlchemyCategoriaRepository
from app.infrastructure.db.repositories.reporte_repository import SqlAlchemyReporteRepository
from app.infrastructure.db.repositories.usuario_repository import SqlAlchemyUsuarioRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.storage.local import LocalStorageService
from app.presentation.api.v1.dependencies.auth import require_authenticated, require_docente

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/categorias", response_model=list[CategoriaDTO], summary="Listar tipos de reporte")
async def listar_categorias(
    _: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> list[CategoriaDTO]:
    return await ListarCategoriasUseCase(SqlAlchemyCategoriaRepository(session)).execute()


@router.post("", response_model=ReporteDTO, status_code=201, summary="Crear reporte (docente)")
async def crear_reporte(
    payload: CrearReporteRequest,
    actor: Usuario = Depends(require_docente),
    session: AsyncSession = Depends(get_session),
) -> ReporteDTO:
    return await CrearReporteUseCase(
        SqlAlchemyReporteRepository(session),
        SqlAlchemyCategoriaRepository(session),
        SqlAlchemyUsuarioRepository(session),
    ).execute(actor, payload)


@router.get("", response_model=list[ReporteDTO], summary="Listar reportes visibles para el usuario")
async def listar_reportes(
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> list[ReporteDTO]:
    return await ListarReportesUseCase(SqlAlchemyReporteRepository(session)).execute(actor)


@router.get("/{reporte_id}", response_model=ReporteDTO, summary="Obtener reporte")
async def obtener_reporte(
    reporte_id: UUID,
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> ReporteDTO:
    return await ObtenerReporteUseCase(SqlAlchemyReporteRepository(session)).execute(actor, reporte_id)


@router.patch("/{reporte_id}", response_model=ReporteDTO, summary="Editar reporte")
async def actualizar_reporte(
    reporte_id: UUID,
    payload: ActualizarReporteRequest,
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> ReporteDTO:
    return await ActualizarReporteUseCase(
        SqlAlchemyReporteRepository(session),
        SqlAlchemyCategoriaRepository(session),
        SqlAlchemyUsuarioRepository(session),
    ).execute(actor, reporte_id, payload)


@router.post(
    "/{reporte_id}/archivos",
    response_model=ArchivoDTO,
    status_code=201,
    summary="Adjuntar imagen o PDF (máximo un PDF)",
)
async def subir_archivo(
    reporte_id: UUID,
    archivo: UploadFile = File(...),
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> ArchivoDTO:
    content = await archivo.read()
    return await SubirArchivoReporteUseCase(SqlAlchemyReporteRepository(session), LocalStorageService()).execute(
        actor,
        reporte_id,
        filename=archivo.filename or "archivo",
        content=content,
        content_type=archivo.content_type or "application/octet-stream",
    )


@router.delete("/archivos/{archivo_id}", status_code=204, summary="Eliminar archivo adjunto")
async def eliminar_archivo(
    archivo_id: UUID,
    actor: Usuario = Depends(require_authenticated),
    session: AsyncSession = Depends(get_session),
) -> None:
    await EliminarArchivoReporteUseCase(SqlAlchemyReporteRepository(session), LocalStorageService()).execute(
        actor, archivo_id
    )
