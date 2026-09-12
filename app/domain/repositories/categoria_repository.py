from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.categoria import CategoriaReporte


class CategoriaRepository(ABC):
    @abstractmethod
    async def list_all(self) -> list[CategoriaReporte]: ...

    @abstractmethod
    async def get_by_id(self, categoria_id: UUID) -> CategoriaReporte | None: ...
