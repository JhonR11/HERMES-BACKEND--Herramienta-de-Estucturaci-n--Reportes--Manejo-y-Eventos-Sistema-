from collections import Counter, defaultdict
from datetime import datetime
from uuid import UUID

from app.application.dtos.catalogo import (
    AgregadoCategoria,
    AgregadoDocente,
    ArchivoDTO,
    DashboardDTO,
    EvolucionTemporal,
    ReporteDTO,
)
from app.domain.exceptions import ValidationException
from app.domain.repositories.reporte_repository import ReporteRepository


class DashboardReportesUseCase:
    def __init__(self, reportes: ReporteRepository) -> None:
        self._reportes = reportes

    async def execute(self, fecha_inicio: datetime, fecha_fin: datetime) -> DashboardDTO:
        if fecha_fin <= fecha_inicio:
            raise ValidationException("fecha_fin debe ser posterior a fecha_inicio")
        items = await self._reportes.list_en_rango(fecha_inicio, fecha_fin)
        por_categoria: dict[UUID, AgregadoCategoria] = {}
        por_docente: Counter[UUID] = Counter()
        por_dia: dict[str, int] = defaultdict(int)

        dtos: list[ReporteDTO] = []
        for item in items:
            nombre = item.categoria_nombre or "Sin categoría"
            if item.categoria_id not in por_categoria:
                por_categoria[item.categoria_id] = AgregadoCategoria(
                    categoria_id=item.categoria_id, categoria_nombre=nombre, cantidad=0
                )
            por_categoria[item.categoria_id].cantidad += 1
            por_docente[item.creado_por] += 1
            por_dia[item.creado_en.date().isoformat()] += 1
            dtos.append(
                ReporteDTO(
                    id=item.id,
                    nombre_reporte=item.nombre_reporte,
                    descripcion_detallada=item.descripcion_detallada,
                    categoria_id=item.categoria_id,
                    categoria_nombre=item.categoria_nombre,
                    creado_por=item.creado_por,
                    estado=item.estado,
                    docentes_ids=item.docentes_ids,
                    archivos=[ArchivoDTO.model_validate(a) for a in item.archivos],
                    creado_en=item.creado_en,
                    actualizado_en=item.actualizado_en,
                )
            )

        return DashboardDTO(
            total_reportes=len(items),
            por_categoria=list(por_categoria.values()),
            por_docente=[AgregadoDocente(docente_id=k, cantidad=v) for k, v in por_docente.items()],
            evolucion_temporal=[EvolucionTemporal(fecha=k, cantidad=v) for k, v in sorted(por_dia.items())],
            reportes=dtos,
        )
