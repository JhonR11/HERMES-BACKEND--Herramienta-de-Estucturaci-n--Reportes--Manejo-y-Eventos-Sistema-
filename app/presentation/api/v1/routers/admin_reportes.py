from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo import CambiarEstadoReporteRequest, DashboardDTO, ReporteDTO
from app.application.use_cases.reportes.reportes_use_cases import CambiarEstadoReporteUseCase
from app.application.use_cases.reportes_admin.dashboard import DashboardReportesUseCase
from app.domain.entities.usuario import Usuario
from app.infrastructure.db.repositories.reporte_repository import SqlAlchemyReporteRepository
from app.infrastructure.db.session import get_session
from app.presentation.api.v1.dependencies.auth import require_admin

router = APIRouter(prefix="/admin/reportes", tags=["Reportes administrativos"])


@router.get(
    "/dashboard",
    response_model=DashboardDTO,
    summary="Dashboard de reportes por rango de fechas",
)
async def dashboard(
    fecha_inicio: datetime = Query(..., examples=["2026-01-01T00:00:00Z"]),
    fecha_fin: datetime = Query(..., examples=["2026-12-31T23:59:59Z"]),
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> DashboardDTO:
    return await DashboardReportesUseCase(SqlAlchemyReporteRepository(session)).execute(fecha_inicio, fecha_fin)


@router.patch("/{reporte_id}/estado", response_model=ReporteDTO, summary="Activar o deshabilitar reporte")
async def cambiar_estado(
    reporte_id: UUID,
    payload: CambiarEstadoReporteRequest,
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> ReporteDTO:
    return await CambiarEstadoReporteUseCase(SqlAlchemyReporteRepository(session)).execute(reporte_id, payload.estado)
