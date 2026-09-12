import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.value_objects.enums import EstadoReporte, TipoArchivo
from app.infrastructure.db.models.enums import estado_reporte_enum, tipo_archivo_enum
from app.infrastructure.db.session import Base


class ReporteDocenteModel(Base):
    __tablename__ = "reporte_docentes"

    reporte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reportes.id", ondelete="CASCADE"), primary_key=True
    )
    docente_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True
    )
    asignado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class ReporteArchivoModel(Base):
    __tablename__ = "reporte_archivos"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    reporte_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("reportes.id", ondelete="CASCADE"), nullable=False
    )
    tipo_archivo: Mapped[TipoArchivo] = mapped_column(tipo_archivo_enum, nullable=False)
    nombre_original: Mapped[str] = mapped_column(String(255), nullable=False)
    ruta_almacenada: Mapped[str] = mapped_column(String(500), nullable=False)
    url_publica: Mapped[str | None] = mapped_column(String(500))
    tamano_bytes: Mapped[int | None] = mapped_column(Integer)
    subido_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    reporte = relationship("ReporteModel", back_populates="archivos")


class ReporteModel(Base):
    __tablename__ = "reportes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    nombre_reporte: Mapped[str] = mapped_column(String(200), nullable=False)
    descripcion_detallada: Mapped[str] = mapped_column(Text, nullable=False)
    categoria_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("categorias_reporte.id", ondelete="RESTRICT"), nullable=False
    )
    creado_por: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("usuarios.id", ondelete="RESTRICT"), nullable=False
    )
    estado: Mapped[EstadoReporte] = mapped_column(
        estado_reporte_enum, nullable=False, server_default=text("'ACTIVO'")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    categoria = relationship("CategoriaReporteModel", back_populates="reportes")
    creador = relationship("UsuarioModel", back_populates="reportes_creados", foreign_keys=[creado_por])
    docentes = relationship("UsuarioModel", secondary="reporte_docentes", lazy="selectin")
    archivos = relationship("ReporteArchivoModel", back_populates="reporte", cascade="all, delete-orphan")
