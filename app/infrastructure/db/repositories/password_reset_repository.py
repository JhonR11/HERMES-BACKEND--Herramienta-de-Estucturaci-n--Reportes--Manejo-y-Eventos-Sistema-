from datetime import datetime, timezone
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.password_reset_repository import PasswordResetRepository
from app.infrastructure.db.models.password_reset import PasswordResetTokenModel


class SqlAlchemyPasswordResetRepository(PasswordResetRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, usuario_id: UUID, token_hash: str, expira_en: datetime) -> None:
        self._session.add(
            PasswordResetTokenModel(usuario_id=usuario_id, token_hash=token_hash, expira_en=expira_en)
        )
        await self._session.flush()

    async def consume_valid(self, token_hash: str) -> UUID | None:
        now = datetime.now(timezone.utc)
        result = await self._session.execute(
            select(PasswordResetTokenModel.usuario_id).where(
                PasswordResetTokenModel.token_hash == token_hash,
                PasswordResetTokenModel.usado.is_(False),
                PasswordResetTokenModel.expira_en > now,
            )
        )
        usuario_id = result.scalar_one_or_none()
        if usuario_id is None:
            return None
        updated = await self._session.execute(
            update(PasswordResetTokenModel)
            .where(
                PasswordResetTokenModel.token_hash == token_hash,
                PasswordResetTokenModel.usado.is_(False),
                PasswordResetTokenModel.expira_en > now,
            )
            .values(usado=True)
        )
        if updated.rowcount != 1:
            return None
        return usuario_id


def hash_reset_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()