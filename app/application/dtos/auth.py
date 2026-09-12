from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.value_objects.enums import RolUsuario


class UsuarioPublicoDTO(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "nombre": "Ana Pérez",
                    "correo_institucional": "ana.perez@institucion.edu.co",
                    "cedula_ciudadania": "1234567890",
                    "rol": "DOCENTE",
                    "activo": True,
                    "creado_en": "2026-01-15T10:00:00Z",
                    "actualizado_en": "2026-01-15T10:00:00Z",
                }
            ]
        },
    )

    id: UUID
    nombre: str
    correo_institucional: EmailStr
    cedula_ciudadania: str | None
    rol: RolUsuario
    activo: bool
    creado_en: datetime
    actualizado_en: datetime


class LoginRequest(BaseModel):
    correo_institucional: EmailStr = Field(examples=["admin@institucion.edu.co"])
    password: str = Field(min_length=1, examples=["changeme"])


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class SolicitarCambioPasswordRequest(BaseModel):
    correo_institucional: EmailStr


class ConfirmarCambioPasswordRequest(BaseModel):
    token: str = Field(min_length=20)
    password_nueva: str = Field(min_length=8)


class EnviarVistaCorreoRequest(BaseModel):
    correo_destino: EmailStr


class CrearDocenteRequest(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    correo_institucional: EmailStr
    cedula_ciudadania: str = Field(min_length=5, max_length=20, pattern=r"^[0-9]+$")


class ActualizarPerfilRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=2, max_length=150)
    correo_institucional: EmailStr | None = None
    password_actual: str | None = None
    password_nueva: str | None = Field(default=None, min_length=8)
