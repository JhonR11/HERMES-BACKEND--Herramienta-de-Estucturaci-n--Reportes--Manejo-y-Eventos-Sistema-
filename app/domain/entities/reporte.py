from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.enums import EstadoReporte, TipoArchivo


@dataclass
class ReporteArchivo:
    id: UUID
    reporte_id: UUID
    tipo_archivo: TipoArchivo
    nombre_original: str
    ruta_almacenada: str
    url_publica: str | None
    tamano_bytes: int | None
    subido_en: datetime


@dataclass
class Reporte:
    id: UUID
    nombre_reporte: str
    descripcion_detallada: str
    categoria_id: UUID
    creado_por: UUID
    estado: EstadoReporte
    creado_en: datetime
    actualizado_en: datetime
    docentes_ids: list[UUID] = field(default_factory=list)
    archivos: list[ReporteArchivo] = field(default_factory=list)
    categoria_nombre: str | None = None
