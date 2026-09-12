from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Noticia:
    id: UUID
    titular: str
    descripcion_noticia: str
    link_opcional: str | None
    foto_url: str | None
    creado_por: UUID
    creado_en: datetime
    actualizado_en: datetime
