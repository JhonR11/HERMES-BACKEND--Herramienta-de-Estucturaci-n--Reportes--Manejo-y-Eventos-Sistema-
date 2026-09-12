import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.session import Base


class NoticiaModel(Base):
    __tablename__ = "noticias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    titular: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion_noticia: Mapped[str] = mapped_column(Text, nullable=False)
    link_opcional: Mapped[str | None] = mapped_column(String(500))
    foto_url: Mapped[str | None] = mapped_column(String(500))
    creado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    creador = relationship("UsuarioModel", back_populates="noticias")
