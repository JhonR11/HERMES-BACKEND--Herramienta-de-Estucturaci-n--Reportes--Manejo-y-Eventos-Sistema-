from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.application.dtos.catalogo import ActualizarNoticiaRequest, CrearNoticiaRequest, NoticiaDTO
from app.application.interfaces.storage import StorageService
from app.domain.entities.noticia import Noticia
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import NotFoundException, ValidationException
from app.domain.repositories.noticia_repository import NoticiaRepository
from app.infrastructure.config.settings import get_settings


def _to_dto(noticia: Noticia) -> NoticiaDTO:
    return NoticiaDTO.model_validate(noticia)


class CrearNoticiaUseCase:
    def __init__(self, noticias: NoticiaRepository, storage: StorageService) -> None:
        self._noticias = noticias
        self._storage = storage

    async def execute(
        self,
        actor: Usuario,
        payload: CrearNoticiaRequest,
        foto: tuple[str, bytes, str] | None,
    ) -> NoticiaDTO:
        foto_url = None
        if foto:
            filename, content, content_type = foto
            _validate_image(filename, content, content_type)
            _, foto_url = await self._storage.save(folder="noticias", filename=filename, content=content)
        now = datetime.now(timezone.utc)
        noticia = Noticia(
            id=uuid4(),
            titular=payload.titular,
            descripcion_noticia=payload.descripcion_noticia,
            link_opcional=payload.link_opcional,
            foto_url=foto_url,
            creado_por=actor.id,
            creado_en=now,
            actualizado_en=now,
        )
        return _to_dto(await self._noticias.add(noticia))


class ActualizarNoticiaUseCase:
    def __init__(self, noticias: NoticiaRepository, storage: StorageService) -> None:
        self._noticias = noticias
        self._storage = storage

    async def execute(
        self,
        noticia_id: UUID,
        payload: ActualizarNoticiaRequest,
        foto: tuple[str, bytes, str] | None,
    ) -> NoticiaDTO:
        noticia = await self._noticias.get_by_id(noticia_id)
        if noticia is None:
            raise NotFoundException("Noticia no encontrada")
        if payload.titular:
            noticia.titular = payload.titular
        if payload.descripcion_noticia:
            noticia.descripcion_noticia = payload.descripcion_noticia
        if payload.link_opcional is not None:
            noticia.link_opcional = payload.link_opcional
        if foto:
            filename, content, content_type = foto
            _validate_image(filename, content, content_type)
            _, noticia.foto_url = await self._storage.save(folder="noticias", filename=filename, content=content)
        noticia.actualizado_en = datetime.now(timezone.utc)
        return _to_dto(await self._noticias.update(noticia))


class ListarNoticiasUseCase:
    def __init__(self, noticias: NoticiaRepository) -> None:
        self._noticias = noticias

    async def execute(self) -> list[NoticiaDTO]:
        return [_to_dto(item) for item in await self._noticias.list_all()]


class ObtenerNoticiaUseCase:
    def __init__(self, noticias: NoticiaRepository) -> None:
        self._noticias = noticias

    async def execute(self, noticia_id: UUID) -> NoticiaDTO:
        noticia = await self._noticias.get_by_id(noticia_id)
        if noticia is None:
            raise NotFoundException("Noticia no encontrada")
        return _to_dto(noticia)


class EliminarNoticiaUseCase:
    def __init__(self, noticias: NoticiaRepository) -> None:
        self._noticias = noticias

    async def execute(self, noticia_id: UUID) -> None:
        noticia = await self._noticias.get_by_id(noticia_id)
        if noticia is None:
            raise NotFoundException("Noticia no encontrada")
        await self._noticias.delete(noticia_id)


def _validate_image(filename: str, content: bytes, content_type: str) -> None:
    settings = get_settings()
    lower = filename.lower()
    if content_type not in {"image/jpeg", "image/png", "image/webp"} and not lower.endswith(
        (".jpg", ".jpeg", ".png", ".webp")
    ):
        raise ValidationException("La foto de la noticia debe ser JPEG, PNG o WEBP")
    if len(content) > settings.max_image_bytes:
        raise ValidationException("La imagen supera el tamaño máximo permitido")
