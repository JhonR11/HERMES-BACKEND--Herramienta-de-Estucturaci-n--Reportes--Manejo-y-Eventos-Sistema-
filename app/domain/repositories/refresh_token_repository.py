from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class RefreshTokenRepository(ABC):
    @abstractmethod
    async def add(self, usuario_id: UUID, token: str, expira_en: datetime) -> None: ...

    @abstractmethod
    async def get_valid(self, token: str) -> UUID | None: ...

    @abstractmethod
    async def revoke(self, token: str) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, usuario_id: UUID) -> None: ...
