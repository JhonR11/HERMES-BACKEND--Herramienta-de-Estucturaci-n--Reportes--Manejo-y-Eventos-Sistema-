from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.evento import Evento
from app.domain.repositories.evento_repository import EventoRepository
from app.domain.value_objects.enums import EstadoEvento
from app.infrastructure.db.models.evento import EventoModel


def to_entity(model: EventoModel) -> Evento:
    return Evento(
        id=model.id,
        nombre_evento=model.nombre_evento,
        descripcion=model.descripcion,
        foto_url=model.foto_url,
        fecha_inicio=model.fecha_inicio,
        fecha_fin=model.fecha_fin,
        estado=model.estado,
        creado_por=model.creado_por,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyEventoRepository(EventoRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, evento: Evento) -> Evento:
        model = EventoModel(
            id=evento.id,
            nombre_evento=evento.nombre_evento,
            descripcion=evento.descripcion,
            foto_url=evento.foto_url,
            fecha_inicio=evento.fecha_inicio,
            fecha_fin=evento.fecha_fin,
            estado=evento.estado,
            creado_por=evento.creado_por,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)

    async def update(self, evento: Evento) -> Evento:
        model = await self._session.get(EventoModel, evento.id)
        if model is None:
            raise ValueError("Evento no encontrado")
        model.nombre_evento = evento.nombre_evento
        model.descripcion = evento.descripcion
        model.foto_url = evento.foto_url
        model.fecha_inicio = evento.fecha_inicio
        model.fecha_fin = evento.fecha_fin
        model.estado = evento.estado
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)

    async def get_by_id(self, evento_id: UUID) -> Evento | None:
        model = await self._session.get(EventoModel, evento_id)
        return to_entity(model) if model else None

    async def list_all(self) -> list[Evento]:
        result = await self._session.execute(select(EventoModel).order_by(EventoModel.fecha_inicio.desc()))
        return [to_entity(m) for m in result.scalars().all()]

    async def list_publicos(self) -> list[Evento]:
        now = func.now()
        result = await self._session.execute(
            select(EventoModel)
            .where(EventoModel.estado == EstadoEvento.ACTIVO, EventoModel.fecha_fin > now)
            .order_by(EventoModel.fecha_inicio.asc())
        )
        return [to_entity(m) for m in result.scalars().all()]

    async def deshabilitar_vencidos(self) -> int:
        result = await self._session.execute(
            update(EventoModel)
            .where(EventoModel.estado == EstadoEvento.ACTIVO, EventoModel.fecha_fin <= func.now())
            .values(estado=EstadoEvento.DESHABILITADO)
        )
        return result.rowcount or 0
