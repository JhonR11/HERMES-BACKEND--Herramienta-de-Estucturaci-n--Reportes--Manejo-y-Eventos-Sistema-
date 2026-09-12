from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.usuario import Usuario


class UsuarioRepository(ABC):
    @abstractmethod
    async def get_by_id(self, usuario_id: UUID) -> Usuario | None: ...

    @abstractmethod
    async def get_by_correo(self, correo: str) -> Usuario | None: ...

    @abstractmethod
    async def get_by_cedula(self, cedula: str) -> Usuario | None: ...

    @abstractmethod
    async def list_docentes(self) -> list[Usuario]: ...

    @abstractmethod
    async def add(self, usuario: Usuario) -> Usuario: ...

    @abstractmethod
    async def update(self, usuario: Usuario) -> Usuario: ...
