from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.enums import RolUsuario


@dataclass
class Usuario:
    id: UUID
    nombre: str
    correo_institucional: str
    cedula_ciudadania: str | None
    password_hash: str
    rol: RolUsuario
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
