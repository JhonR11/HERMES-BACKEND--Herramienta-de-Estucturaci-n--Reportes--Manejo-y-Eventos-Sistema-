from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.noticia import Noticia


class NoticiaRepository(ABC):
    @abstractmethod
    async def add(self, noticia: Noticia) -> Noticia: ...

    @abstractmethod
    async def update(self, noticia: Noticia) -> Noticia: ...

    @abstractmethod
    async def get_by_id(self, noticia_id: UUID) -> Noticia | None: ...

    @abstractmethod
    async def delete(self, noticia_id: UUID) -> None: ...

    @abstractmethod
    async def list_all(self) -> list[Noticia]: ...
