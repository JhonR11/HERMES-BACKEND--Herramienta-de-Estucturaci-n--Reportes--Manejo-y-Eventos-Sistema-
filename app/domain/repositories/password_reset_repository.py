from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class PasswordResetRepository(ABC):
    @abstractmethod
    async def add(self, usuario_id: UUID, token_hash: str, expira_en: datetime) -> None: ...

    @abstractmethod
    async def consume_valid(self, token_hash: str) -> UUID | None: ...