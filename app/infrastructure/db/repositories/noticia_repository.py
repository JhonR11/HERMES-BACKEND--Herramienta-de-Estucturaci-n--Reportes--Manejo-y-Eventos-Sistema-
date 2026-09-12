from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.noticia import Noticia
from app.domain.repositories.noticia_repository import NoticiaRepository
from app.infrastructure.db.models.noticia import NoticiaModel


def to_entity(model: NoticiaModel) -> Noticia:
    return Noticia(
        id=model.id,
        titular=model.titular,
        descripcion_noticia=model.descripcion_noticia,
        link_opcional=model.link_opcional,
        foto_url=model.foto_url,
        creado_por=model.creado_por,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyNoticiaRepository(NoticiaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, noticia: Noticia) -> Noticia:
        model = NoticiaModel(
            id=noticia.id,
            titular=noticia.titular,
            descripcion_noticia=noticia.descripcion_noticia,
            link_opcional=noticia.link_opcional,
            foto_url=noticia.foto_url,
            creado_por=noticia.creado_por,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)

    async def update(self, noticia: Noticia) -> Noticia:
        model = await self._session.get(NoticiaModel, noticia.id)
        if model is None:
            raise ValueError("Noticia no encontrada")
        model.titular = noticia.titular
        model.descripcion_noticia = noticia.descripcion_noticia
        model.link_opcional = noticia.link_opcional
        model.foto_url = noticia.foto_url
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)

    async def get_by_id(self, noticia_id: UUID) -> Noticia | None:
        model = await self._session.get(NoticiaModel, noticia_id)
        return to_entity(model) if model else None

    async def delete(self, noticia_id: UUID) -> None:
        await self._session.execute(delete(NoticiaModel).where(NoticiaModel.id == noticia_id))

    async def list_all(self) -> list[Noticia]:
        result = await self._session.execute(select(NoticiaModel).order_by(NoticiaModel.creado_en.desc()))
        return [to_entity(m) for m in result.scalars().all()]
