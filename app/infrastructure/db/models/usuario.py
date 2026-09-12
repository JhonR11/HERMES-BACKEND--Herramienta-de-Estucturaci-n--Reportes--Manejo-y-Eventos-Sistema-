import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.value_objects.enums import RolUsuario
from app.infrastructure.db.models.enums import rol_usuario_enum
from app.infrastructure.db.session import Base


class UsuarioModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    correo_institucional: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    cedula_ciudadania: Mapped[str | None] = mapped_column(String(20), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(rol_usuario_enum, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("TRUE"))
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reportes_creados = relationship("ReporteModel", back_populates="creador", foreign_keys="ReporteModel.creado_por")
    eventos = relationship("EventoModel", back_populates="creador")
    noticias = relationship("NoticiaModel", back_populates="creador")
    refresh_tokens = relationship("RefreshTokenModel", back_populates="usuario")
