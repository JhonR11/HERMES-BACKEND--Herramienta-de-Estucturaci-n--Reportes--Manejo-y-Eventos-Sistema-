from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.infrastructure.db.models.refresh_token import RefreshTokenModel


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, usuario_id: UUID, token: str, expira_en: datetime) -> None:
        self._session.add(RefreshTokenModel(usuario_id=usuario_id, token=token, expira_en=expira_en))
        await self._session.flush()

    async def get_valid(self, token: str) -> UUID | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(
                RefreshTokenModel.token == token,
                RefreshTokenModel.revocado.is_(False),
                RefreshTokenModel.expira_en > datetime.now(timezone.utc),
            )
        )
        model = result.scalar_one_or_none()
        return model.usuario_id if model else None

    async def revoke(self, token: str) -> None:
        await self._session.execute(
            update(RefreshTokenModel).where(RefreshTokenModel.token == token).values(revocado=True)
        )

    async def revoke_all_for_user(self, usuario_id: UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel).where(RefreshTokenModel.usuario_id == usuario_id).values(revocado=True)
        )
