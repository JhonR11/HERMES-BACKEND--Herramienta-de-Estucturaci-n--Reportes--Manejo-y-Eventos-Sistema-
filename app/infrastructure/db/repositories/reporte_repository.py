from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.reporte import Reporte, ReporteArchivo
from app.domain.repositories.reporte_repository import ReporteRepository
from app.domain.value_objects.enums import EstadoReporte, TipoArchivo
from app.infrastructure.db.models.reporte import ReporteArchivoModel, ReporteDocenteModel, ReporteModel
from app.infrastructure.db.models.usuario import UsuarioModel


def archivo_to_entity(model: ReporteArchivoModel) -> ReporteArchivo:
    return ReporteArchivo(
        id=model.id,
        reporte_id=model.reporte_id,
        tipo_archivo=model.tipo_archivo,
        nombre_original=model.nombre_original,
        ruta_almacenada=model.ruta_almacenada,
        url_publica=model.url_publica,
        tamano_bytes=model.tamano_bytes,
        subido_en=model.subido_en,
    )


def reporte_to_entity(model: ReporteModel) -> Reporte:
    return Reporte(
        id=model.id,
        nombre_reporte=model.nombre_reporte,
        descripcion_detallada=model.descripcion_detallada,
        categoria_id=model.categoria_id,
        creado_por=model.creado_por,
        estado=model.estado,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
        docentes_ids=[d.id for d in model.docentes],
        archivos=[archivo_to_entity(a) for a in model.archivos],
        categoria_nombre=model.categoria.nombre if model.categoria else None,
    )


_LOAD = (
    selectinload(ReporteModel.docentes),
    selectinload(ReporteModel.archivos),
    selectinload(ReporteModel.categoria),
)


class SqlAlchemyReporteRepository(ReporteRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_model(self, reporte_id: UUID) -> ReporteModel | None:
        result = await self._session.execute(
            select(ReporteModel).options(*_LOAD).where(ReporteModel.id == reporte_id)
        )
        return result.scalar_one_or_none()

    async def add(self, reporte: Reporte) -> Reporte:
        model = ReporteModel(
            id=reporte.id,
            nombre_reporte=reporte.nombre_reporte,
            descripcion_detallada=reporte.descripcion_detallada,
            categoria_id=reporte.categoria_id,
            creado_por=reporte.creado_por,
            estado=reporte.estado,
        )
        if reporte.docentes_ids:
            result = await self._session.execute(
                select(UsuarioModel).where(UsuarioModel.id.in_(reporte.docentes_ids))
            )
            model.docentes = list(result.scalars().all())
        self._session.add(model)
        await self._session.flush()
        loaded = await self._get_model(model.id)
        assert loaded is not None
        return reporte_to_entity(loaded)

    async def update(self, reporte: Reporte) -> Reporte:
        model = await self._get_model(reporte.id)
        if model is None:
            raise ValueError("Reporte no encontrado")
        model.nombre_reporte = reporte.nombre_reporte
        model.descripcion_detallada = reporte.descripcion_detallada
        model.categoria_id = reporte.categoria_id
        model.estado = reporte.estado
        result = await self._session.execute(
            select(UsuarioModel).where(UsuarioModel.id.in_(reporte.docentes_ids))
        ) if reporte.docentes_ids else None
        model.docentes = list(result.scalars().all()) if result else []
        await self._session.flush()
        loaded = await self._get_model(reporte.id)
        assert loaded is not None
        return reporte_to_entity(loaded)

    async def get_by_id(self, reporte_id: UUID) -> Reporte | None:
        model = await self._get_model(reporte_id)
        return reporte_to_entity(model) if model else None

    async def list_for_usuario(
        self,
        usuario_id: UUID,
        *,
        es_admin: bool,
        estado: EstadoReporte | None = None,
    ) -> list[Reporte]:
        stmt = select(ReporteModel).options(*_LOAD)
        if not es_admin:
            stmt = stmt.outerjoin(ReporteDocenteModel).where(
                or_(ReporteModel.creado_por == usuario_id, ReporteDocenteModel.docente_id == usuario_id)
            ).distinct()
        if estado:
            stmt = stmt.where(ReporteModel.estado == estado)
        stmt = stmt.order_by(ReporteModel.creado_en.desc())
        result = await self._session.execute(stmt)
        return [reporte_to_entity(m) for m in result.scalars().unique().all()]

    async def list_publicos(self) -> list[Reporte]:
        result = await self._session.execute(
            select(ReporteModel)
            .options(*_LOAD)
            .where(ReporteModel.estado == EstadoReporte.ACTIVO)
            .order_by(ReporteModel.creado_en.desc())
        )
        return [reporte_to_entity(m) for m in result.scalars().unique().all()]

    async def list_en_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> list[Reporte]:
        result = await self._session.execute(
            select(ReporteModel)
            .options(*_LOAD)
            .where(and_(ReporteModel.creado_en >= fecha_inicio, ReporteModel.creado_en <= fecha_fin))
            .order_by(ReporteModel.creado_en.asc())
        )
        return [reporte_to_entity(m) for m in result.scalars().unique().all()]

    async def add_archivo(self, archivo: ReporteArchivo) -> ReporteArchivo:
        model = ReporteArchivoModel(
            id=archivo.id,
            reporte_id=archivo.reporte_id,
            tipo_archivo=archivo.tipo_archivo,
            nombre_original=archivo.nombre_original,
            ruta_almacenada=archivo.ruta_almacenada,
            url_publica=archivo.url_publica,
            tamano_bytes=archivo.tamano_bytes,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return archivo_to_entity(model)

    async def get_archivo(self, archivo_id: UUID) -> ReporteArchivo | None:
        model = await self._session.get(ReporteArchivoModel, archivo_id)
        return archivo_to_entity(model) if model else None

    async def delete_archivo(self, archivo_id: UUID) -> None:
        await self._session.execute(delete(ReporteArchivoModel).where(ReporteArchivoModel.id == archivo_id))

    async def count_pdfs(self, reporte_id: UUID) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(ReporteArchivoModel)
            .where(
                ReporteArchivoModel.reporte_id == reporte_id,
                ReporteArchivoModel.tipo_archivo == TipoArchivo.PDF,
            )
        )
        return int(result.scalar_one())
