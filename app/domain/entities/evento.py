from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.enums import EstadoEvento


@dataclass
class Evento:
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
