from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo import EventoDTO, NoticiaDTO, ReporteDTO
from app.application.use_cases.eventos.eventos_use_cases import ListarEventosUseCase
from app.application.use_cases.noticias.noticias_use_cases import ListarNoticiasUseCase
from app.application.use_cases.reportes.reportes_use_cases import ListarReportesPublicosUseCase
from app.infrastructure.db.repositories.evento_repository import SqlAlchemyEventoRepository
from app.infrastructure.db.repositories.noticia_repository import SqlAlchemyNoticiaRepository
from app.infrastructure.db.repositories.reporte_repository import SqlAlchemyReporteRepository
from app.infrastructure.db.session import get_session

router = APIRouter(prefix="/public", tags=["Público"])


@router.get("/reportes", response_model=list[ReporteDTO], summary="Reportes activos (sin autenticación)")
async def reportes_publicos(session: AsyncSession = Depends(get_session)) -> list[ReporteDTO]:
    return await ListarReportesPublicosUseCase(SqlAlchemyReporteRepository(session)).execute()


@router.get("/eventos", response_model=list[EventoDTO], summary="Eventos activos no vencidos")
async def eventos_publicos(session: AsyncSession = Depends(get_session)) -> list[EventoDTO]:
    return await ListarEventosUseCase(SqlAlchemyEventoRepository(session)).execute(publicos=True)


@router.get("/noticias", response_model=list[NoticiaDTO], summary="Noticias institucionales")
async def noticias_publicas(session: AsyncSession = Depends(get_session)) -> list[NoticiaDTO]:
    return await ListarNoticiasUseCase(SqlAlchemyNoticiaRepository(session)).execute()
