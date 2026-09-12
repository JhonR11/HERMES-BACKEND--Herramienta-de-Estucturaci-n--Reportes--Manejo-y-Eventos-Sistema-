from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.application.dtos.catalogo import ActualizarEventoRequest, CrearEventoRequest, EventoDTO
from app.application.interfaces.event_publisher import EventPublisher
from app.application.interfaces.storage import StorageService
from app.domain.entities.evento import Evento
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import NotFoundException, ValidationException
from app.domain.repositories.evento_repository import EventoRepository
from app.domain.value_objects.enums import EstadoEvento
from app.infrastructure.config.settings import get_settings


def _to_dto(evento: Evento) -> EventoDTO:
    return EventoDTO.model_validate(evento)


def _assert_fechas(inicio: datetime, fin: datetime) -> None:
    if fin <= inicio:
        raise ValidationException("fecha_fin debe ser posterior a fecha_inicio")


class CrearEventoUseCase:
    def __init__(
        self,
        eventos: EventoRepository,
        publisher: EventPublisher,
        storage: StorageService,
    ) -> None:
        self._eventos = eventos
        self._publisher = publisher
        self._storage = storage

    async def execute(
        self,
        actor: Usuario,
        payload: CrearEventoRequest,
        foto: tuple[str, bytes, str] | None,
    ) -> EventoDTO:
        _assert_fechas(payload.fecha_inicio, payload.fecha_fin)
        foto_url = None
        if foto:
            filename, content, content_type = foto
            _validate_image(filename, content, content_type)
            _, foto_url = await self._storage.save(folder="eventos", filename=filename, content=content)
        now = datetime.now(timezone.utc)
        evento = Evento(
            id=uuid4(),
            nombre_evento=payload.nombre_evento,
            descripcion=payload.descripcion,
            foto_url=foto_url,
            fecha_inicio=payload.fecha_inicio,
            fecha_fin=payload.fecha_fin,
            estado=EstadoEvento.ACTIVO,
            creado_por=actor.id,
            creado_en=now,
            actualizado_en=now,
        )
        creado = await self._eventos.add(evento)
        dto = _to_dto(creado)
        await self._publisher.publish("evento.creado", dto.model_dump(mode="json"))
        return dto


class ActualizarEventoUseCase:
    def __init__(
        self,
        eventos: EventoRepository,
        publisher: EventPublisher,
        storage: StorageService,
    ) -> None:
        self._eventos = eventos
        self._publisher = publisher
        self._storage = storage

    async def execute(
        self,
        evento_id: UUID,
        payload: ActualizarEventoRequest,
        foto: tuple[str, bytes, str] | None,
    ) -> EventoDTO:
        evento = await self._eventos.get_by_id(evento_id)
        if evento is None:
            raise NotFoundException("Evento no encontrado")
        if payload.nombre_evento:
            evento.nombre_evento = payload.nombre_evento
        if payload.descripcion:
            evento.descripcion = payload.descripcion
        if payload.fecha_inicio:
            evento.fecha_inicio = payload.fecha_inicio
        if payload.fecha_fin:
            evento.fecha_fin = payload.fecha_fin
        _assert_fechas(evento.fecha_inicio, evento.fecha_fin)
        if payload.estado:
            evento.estado = payload.estado
        if foto:
            filename, content, content_type = foto
            _validate_image(filename, content, content_type)
            _, evento.foto_url = await self._storage.save(folder="eventos", filename=filename, content=content)
        evento.actualizado_en = datetime.now(timezone.utc)
        actualizado = await self._eventos.update(evento)
        dto = _to_dto(actualizado)
        tipo = "evento.deshabilitado" if dto.estado == EstadoEvento.DESHABILITADO else "evento.actualizado"
        await self._publisher.publish(tipo, dto.model_dump(mode="json"))
        return dto


class ListarEventosUseCase:
    def __init__(self, eventos: EventoRepository) -> None:
        self._eventos = eventos

    async def execute(self, *, publicos: bool) -> list[EventoDTO]:
        items = await self._eventos.list_publicos() if publicos else await self._eventos.list_all()
        return [_to_dto(item) for item in items]


class ObtenerEventoUseCase:
    def __init__(self, eventos: EventoRepository) -> None:
        self._eventos = eventos

    async def execute(self, evento_id: UUID) -> EventoDTO:
        evento = await self._eventos.get_by_id(evento_id)
        if evento is None:
            raise NotFoundException("Evento no encontrado")
        return _to_dto(evento)


def _validate_image(filename: str, content: bytes, content_type: str) -> None:
    settings = get_settings()
    lower = filename.lower()
    if content_type not in {"image/jpeg", "image/png", "image/webp"} and not lower.endswith(
        (".jpg", ".jpeg", ".png", ".webp")
    ):
        raise ValidationException("La foto del evento debe ser JPEG, PNG o WEBP")
    if len(content) > settings.max_image_bytes:
        raise ValidationException("La imagen supera el tamaño máximo permitido")
