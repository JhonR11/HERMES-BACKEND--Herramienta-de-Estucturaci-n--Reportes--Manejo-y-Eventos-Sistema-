from dataclasses import dataclass
from uuid import UUID


@dataclass
class CategoriaReporte:
    id: UUID
    nombre: str
    descripcion: str | None
