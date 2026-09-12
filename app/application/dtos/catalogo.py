from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.value_objects.enums import EstadoEvento, EstadoReporte, TipoArchivo


class CategoriaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre: str
    descripcion: str | None = None


class ArchivoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    tipo_archivo: TipoArchivo
    nombre_original: str
    url_publica: str | None
    tamano_bytes: int | None
    subido_en: datetime


class CrearReporteRequest(BaseModel):
    nombre_reporte: str = Field(min_length=3, max_length=200)
    descripcion_detallada: str = Field(min_length=10)
    categoria_id: UUID
    docentes_asociados: list[UUID] = Field(default_factory=list)


class ActualizarReporteRequest(BaseModel):
    nombre_reporte: str | None = Field(default=None, min_length=3, max_length=200)
    descripcion_detallada: str | None = Field(default=None, min_length=10)
    categoria_id: UUID | None = None
    docentes_asociados: list[UUID] | None = None


class CambiarEstadoReporteRequest(BaseModel):
    estado: EstadoReporte


class ReporteDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre_reporte: str
    descripcion_detallada: str
    categoria_id: UUID
    categoria_nombre: str | None = None
    creado_por: UUID
    estado: EstadoReporte
    docentes_ids: list[UUID]
    archivos: list[ArchivoDTO]
    creado_en: datetime
    actualizado_en: datetime


class CrearEventoRequest(BaseModel):
    nombre_evento: str = Field(min_length=3, max_length=200)
    descripcion: str = Field(min_length=10)
    fecha_inicio: datetime
    fecha_fin: datetime


class ActualizarEventoRequest(BaseModel):
    nombre_evento: str | None = Field(default=None, min_length=3, max_length=200)
    descripcion: str | None = Field(default=None, min_length=10)
    fecha_inicio: datetime | None = None
    fecha_fin: datetime | None = None
    estado: EstadoEvento | None = None


class EventoDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nombre_evento: str
    descripcion: str
    foto_url: str | None
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: EstadoEvento
    creado_por: UUID
    creado_en: datetime
    actualizado_en: datetime


class CrearNoticiaRequest(BaseModel):
    titular: str = Field(min_length=3, max_length=200)
    descripcion_noticia: str = Field(min_length=10)
    link_opcional: str | None = Field(default=None, max_length=500)


class ActualizarNoticiaRequest(BaseModel):
    titular: str | None = Field(default=None, min_length=3, max_length=200)
    descripcion_noticia: str | None = Field(default=None, min_length=10)
    link_opcional: str | None = Field(default=None, max_length=500)


class NoticiaDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    titular: str
    descripcion_noticia: str
    link_opcional: str | None
    foto_url: str | None
    creado_por: UUID
    creado_en: datetime
    actualizado_en: datetime


class DashboardFiltro(BaseModel):
    fecha_inicio: datetime
    fecha_fin: datetime


class AgregadoCategoria(BaseModel):
    categoria_id: UUID
    categoria_nombre: str
    cantidad: int


class AgregadoDocente(BaseModel):
    docente_id: UUID
    cantidad: int


class EvolucionTemporal(BaseModel):
    fecha: str
    cantidad: int


class DashboardDTO(BaseModel):
    total_reportes: int
    por_categoria: list[AgregadoCategoria]
    por_docente: list[AgregadoDocente]
    evolucion_temporal: list[EvolucionTemporal]
    reportes: list[ReporteDTO]
