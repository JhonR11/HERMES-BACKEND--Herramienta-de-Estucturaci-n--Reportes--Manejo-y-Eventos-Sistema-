from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.application.dtos.catalogo import CrearEventoRequest
from app.domain.exceptions import ValidationException
from app.application.use_cases.eventos.eventos_use_cases import _assert_fechas


def test_fechas_evento_invalidas() -> None:
    inicio = datetime.now(timezone.utc)
    try:
        _assert_fechas(inicio, inicio)
        raise AssertionError("debía fallar")
    except ValidationException:
        pass


def test_payload_evento() -> None:
    inicio = datetime.now(timezone.utc)
    payload = CrearEventoRequest(
        nombre_evento="Semana cultural",
        descripcion="Actividades abiertas a toda la comunidad.",
        fecha_inicio=inicio,
        fecha_fin=inicio + timedelta(days=2),
    )
    assert payload.nombre_evento.startswith("Semana")
    _ = uuid4()
