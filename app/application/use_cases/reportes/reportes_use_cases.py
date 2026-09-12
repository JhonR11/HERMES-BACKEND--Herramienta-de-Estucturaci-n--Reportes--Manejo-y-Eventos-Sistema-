from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.application.dtos.catalogo import (
    ActualizarReporteRequest,
    ArchivoDTO,
    CrearReporteRequest,
    ReporteDTO,
)
from app.application.interfaces.storage import StorageService
from app.domain.entities.reporte import Reporte, ReporteArchivo
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ForbiddenException, NotFoundException, ValidationException
from app.domain.repositories.categoria_repository import CategoriaRepository
from app.domain.repositories.reporte_repository import ReporteRepository
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.domain.value_objects.enums import EstadoReporte, RolUsuario, TipoArchivo
from app.infrastructure.config.settings import get_settings


def _to_dto(reporte: Reporte) -> ReporteDTO:
    return ReporteDTO(
        id=reporte.id,
        nombre_reporte=reporte.nombre_reporte,
        descripcion_detallada=reporte.descripcion_detallada,
        categoria_id=reporte.categoria_id,
        categoria_nombre=reporte.categoria_nombre,
        creado_por=reporte.creado_por,
        estado=reporte.estado,
        docentes_ids=reporte.docentes_ids,
        archivos=[ArchivoDTO.model_validate(a) for a in reporte.archivos],
        creado_en=reporte.creado_en,
        actualizado_en=reporte.actualizado_en,
    )


class CrearReporteUseCase:
    def __init__(
        self,
        reportes: ReporteRepository,
        categorias: CategoriaRepository,
        usuarios: UsuarioRepository,
    ) -> None:
        self._reportes = reportes
        self._categorias = categorias
        self._usuarios = usuarios

    async def execute(self, actor: Usuario, payload: CrearReporteRequest) -> ReporteDTO:
        if await self._categorias.get_by_id(payload.categoria_id) is None:
            raise ValidationException("La categoría no existe")
        docentes_ids = list(dict.fromkeys([*payload.docentes_asociados, actor.id]))
        await self._assert_docentes(docentes_ids)
        now = datetime.now(timezone.utc)
        reporte = Reporte(
            id=uuid4(),
            nombre_reporte=payload.nombre_reporte,
            descripcion_detallada=payload.descripcion_detallada,
            categoria_id=payload.categoria_id,
            creado_por=actor.id,
            estado=EstadoReporte.ACTIVO,
            creado_en=now,
            actualizado_en=now,
            docentes_ids=docentes_ids,
        )
        return _to_dto(await self._reportes.add(reporte))

    async def _assert_docentes(self, ids: list[UUID]) -> None:
        for docente_id in ids:
            usuario = await self._usuarios.get_by_id(docente_id)
            if usuario is None or usuario.rol != RolUsuario.DOCENTE:
                raise ValidationException(f"El usuario {docente_id} no es un docente válido")


class ListarReportesUseCase:
    def __init__(self, reportes: ReporteRepository) -> None:
        self._reportes = reportes

    async def execute(self, actor: Usuario) -> list[ReporteDTO]:
        es_admin = actor.rol == RolUsuario.ADMINISTRADOR
        items = await self._reportes.list_for_usuario(actor.id, es_admin=es_admin)
        return [_to_dto(item) for item in items]


class ObtenerReporteUseCase:
    def __init__(self, reportes: ReporteRepository) -> None:
        self._reportes = reportes

    async def execute(self, actor: Usuario, reporte_id: UUID) -> ReporteDTO:
        reporte = await self._reportes.get_by_id(reporte_id)
        if reporte is None:
            raise NotFoundException("Reporte no encontrado")
        if actor.rol != RolUsuario.ADMINISTRADOR and actor.id not in {*reporte.docentes_ids, reporte.creado_por}:
            raise ForbiddenException("No tiene acceso a este reporte")
        return _to_dto(reporte)


class ActualizarReporteUseCase:
    def __init__(
        self,
        reportes: ReporteRepository,
        categorias: CategoriaRepository,
        usuarios: UsuarioRepository,
    ) -> None:
        self._reportes = reportes
        self._categorias = categorias
        self._usuarios = usuarios

    async def execute(self, actor: Usuario, reporte_id: UUID, payload: ActualizarReporteRequest) -> ReporteDTO:
        reporte = await self._reportes.get_by_id(reporte_id)
        if reporte is None:
            raise NotFoundException("Reporte no encontrado")
        es_admin = actor.rol == RolUsuario.ADMINISTRADOR
        if not es_admin and reporte.creado_por != actor.id:
            raise ForbiddenException("Solo el creador o un administrador pueden editar el reporte")
        if payload.nombre_reporte:
            reporte.nombre_reporte = payload.nombre_reporte
        if payload.descripcion_detallada:
            reporte.descripcion_detallada = payload.descripcion_detallada
        if payload.categoria_id:
            if await self._categorias.get_by_id(payload.categoria_id) is None:
                raise ValidationException("La categoría no existe")
            reporte.categoria_id = payload.categoria_id
        if payload.docentes_asociados is not None:
            docentes_ids = list(dict.fromkeys([*payload.docentes_asociados, reporte.creado_por]))
            for docente_id in docentes_ids:
                usuario = await self._usuarios.get_by_id(docente_id)
                if usuario is None or usuario.rol != RolUsuario.DOCENTE:
                    raise ValidationException(f"El usuario {docente_id} no es un docente válido")
            reporte.docentes_ids = docentes_ids
        reporte.actualizado_en = datetime.now(timezone.utc)
        return _to_dto(await self._reportes.update(reporte))


class CambiarEstadoReporteUseCase:
    def __init__(self, reportes: ReporteRepository) -> None:
        self._reportes = reportes

    async def execute(self, reporte_id: UUID, estado: EstadoReporte) -> ReporteDTO:
        reporte = await self._reportes.get_by_id(reporte_id)
        if reporte is None:
            raise NotFoundException("Reporte no encontrado")
        reporte.estado = estado
        reporte.actualizado_en = datetime.now(timezone.utc)
        return _to_dto(await self._reportes.update(reporte))


class ListarReportesPublicosUseCase:
    def __init__(self, reportes: ReporteRepository) -> None:
        self._reportes = reportes

    async def execute(self) -> list[ReporteDTO]:
        return [_to_dto(item) for item in await self._reportes.list_publicos()]


class SubirArchivoReporteUseCase:
    def __init__(self, reportes: ReporteRepository, storage: StorageService) -> None:
        self._reportes = reportes
        self._storage = storage

    async def execute(
        self,
        actor: Usuario,
        reporte_id: UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str,
    ) -> ArchivoDTO:
        reporte = await self._reportes.get_by_id(reporte_id)
        if reporte is None:
            raise NotFoundException("Reporte no encontrado")
        if actor.rol != RolUsuario.ADMINISTRADOR and reporte.creado_por != actor.id:
            raise ForbiddenException("No puede adjuntar archivos a este reporte")
        tipo, ext_ok = self._validate_file(filename, content, content_type)
        if tipo == TipoArchivo.PDF and await self._reportes.count_pdfs(reporte_id) >= 1:
            raise ValidationException("El reporte ya tiene un PDF adjunto")
        stored, public_url = await self._storage.save(folder=str(reporte_id), filename=filename, content=content)
        archivo = ReporteArchivo(
            id=uuid4(),
            reporte_id=reporte_id,
            tipo_archivo=tipo,
            nombre_original=filename,
            ruta_almacenada=stored,
            url_publica=public_url,
            tamano_bytes=len(content),
            subido_en=datetime.now(timezone.utc),
        )
        saved = await self._reportes.add_archivo(archivo)
        return ArchivoDTO.model_validate(saved)

    def _validate_file(self, filename: str, content: bytes, content_type: str) -> tuple[TipoArchivo, bool]:
        settings = get_settings()
        lower = filename.lower()
        if lower.endswith(".pdf") or content_type == "application/pdf":
            if len(content) > settings.max_pdf_bytes:
                raise ValidationException("El PDF supera el tamaño máximo permitido")
            if not content.startswith(b"%PDF"):
                raise ValidationException("El archivo no es un PDF válido")
            return TipoArchivo.PDF, True
        image_types = {"image/jpeg", "image/png", "image/webp"}
        if content_type not in image_types and not lower.endswith((".jpg", ".jpeg", ".png", ".webp")):
            raise ValidationException("Solo se permiten imágenes (JPEG, PNG, WEBP) o un PDF")
        if len(content) > settings.max_image_bytes:
            raise ValidationException("La imagen supera el tamaño máximo permitido")
        return TipoArchivo.IMAGEN, True


class EliminarArchivoReporteUseCase:
    def __init__(self, reportes: ReporteRepository, storage: StorageService) -> None:
        self._reportes = reportes
        self._storage = storage

    async def execute(self, actor: Usuario, archivo_id: UUID) -> None:
        archivo = await self._reportes.get_archivo(archivo_id)
        if archivo is None:
            raise NotFoundException("Archivo no encontrado")
        reporte = await self._reportes.get_by_id(archivo.reporte_id)
        if reporte is None:
            raise NotFoundException("Reporte no encontrado")
        if actor.rol != RolUsuario.ADMINISTRADOR and reporte.creado_por != actor.id:
            raise ForbiddenException("No puede eliminar este archivo")
        await self._storage.delete(archivo.ruta_almacenada)
        await self._reportes.delete_archivo(archivo_id)
