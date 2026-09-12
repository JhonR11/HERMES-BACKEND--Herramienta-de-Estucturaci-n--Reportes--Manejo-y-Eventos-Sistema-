from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.catalogo import ActualizarEventoRequest, CrearEventoRequest, EventoDTO
from app.application.use_cases.eventos.eventos_use_cases import (
    ActualizarEventoUseCase,
    CrearEventoUseCase,
    ListarEventosUseCase,
    ObtenerEventoUseCase,
)
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ValidationException
from app.domain.value_objects.enums import EstadoEvento
from app.infrastructure.db.repositories.evento_repository import SqlAlchemyEventoRepository
from app.infrastructure.db.session import get_session
from app.infrastructure.storage.local import LocalStorageService
from app.infrastructure.websockets.manager import event_manager
from app.presentation.api.v1.dependencies.auth import require_admin

router = APIRouter(prefix="/eventos", tags=["Eventos"])


def _parse_dt(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationException("Fecha en formato ISO-8601 inválido") from exc


async def _foto(file: UploadFile | None) -> tuple[str, bytes, str] | None:
    if file is None:
        return None
    content = await file.read()
    if not content:
        return None
    return file.filename or "foto.jpg", content, file.content_type or "image/jpeg"


@router.post("", response_model=EventoDTO, status_code=201, summary="Crear evento (admin)")
async def crear_evento(
    nombre_evento: str = Form(..., min_length=3, max_length=200),
    descripcion: str = Form(..., min_length=10),
    fecha_inicio: str = Form(..., description="ISO-8601"),
    fecha_fin: str = Form(..., description="ISO-8601"),
    foto: UploadFile | None = File(default=None),
    actor: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> EventoDTO:
    payload = CrearEventoRequest(
        nombre_evento=nombre_evento,
        descripcion=descripcion,
        fecha_inicio=_parse_dt(fecha_inicio),
        fecha_fin=_parse_dt(fecha_fin),
    )
    return await CrearEventoUseCase(
        SqlAlchemyEventoRepository(session), event_manager, LocalStorageService()
    ).execute(actor, payload, await _foto(foto))


@router.get("", response_model=list[EventoDTO], summary="Listar todos los eventos (admin)")
async def listar_eventos(
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> list[EventoDTO]:
    return await ListarEventosUseCase(SqlAlchemyEventoRepository(session)).execute(publicos=False)


@router.get("/{evento_id}", response_model=EventoDTO, summary="Obtener evento")
async def obtener_evento(
    evento_id: UUID,
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> EventoDTO:
    return await ObtenerEventoUseCase(SqlAlchemyEventoRepository(session)).execute(evento_id)


@router.patch("/{evento_id}", response_model=EventoDTO, summary="Actualizar o deshabilitar evento")
async def actualizar_evento(
    evento_id: UUID,
    nombre_evento: str | None = Form(default=None),
    descripcion: str | None = Form(default=None),
    fecha_inicio: str | None = Form(default=None),
    fecha_fin: str | None = Form(default=None),
    estado: EstadoEvento | None = Form(default=None),
    foto: UploadFile | None = File(default=None),
    _: Usuario = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> EventoDTO:
    payload = ActualizarEventoRequest(
        nombre_evento=nombre_evento,
        descripcion=descripcion,
        fecha_inicio=_parse_dt(fecha_inicio) if fecha_inicio else None,
        fecha_fin=_parse_dt(fecha_fin) if fecha_fin else None,
        estado=estado,
    )
    return await ActualizarEventoUseCase(
        SqlAlchemyEventoRepository(session), event_manager, LocalStorageService()
    ).execute(evento_id, payload, await _foto(foto))
