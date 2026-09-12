from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    async def save(self, *, folder: str, filename: str, content: bytes) -> tuple[str, str]:
        """Persiste el archivo y retorna (ruta_almacenada, url_publica)."""

    @abstractmethod
    async def delete(self, stored_path: str) -> None: ...
