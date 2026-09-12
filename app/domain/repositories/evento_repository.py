from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.evento import Evento


class EventoRepository(ABC):
    @abstractmethod
    async def add(self, evento: Evento) -> Evento: ...

    @abstractmethod
    async def update(self, evento: Evento) -> Evento: ...

    @abstractmethod
    async def get_by_id(self, evento_id: UUID) -> Evento | None: ...

    @abstractmethod
    async def list_all(self) -> list[Evento]: ...

    @abstractmethod
    async def list_publicos(self) -> list[Evento]: ...

    @abstractmethod
    async def deshabilitar_vencidos(self) -> int: ...
