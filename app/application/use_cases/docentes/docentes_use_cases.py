from datetime import datetime, timezone
from uuid import UUID, uuid4

from app.application.dtos.auth import ActualizarPerfilRequest, CrearDocenteRequest, UsuarioPublicoDTO
from app.domain.entities.usuario import Usuario
from app.domain.exceptions import ConflictException, ForbiddenException, NotFoundException, ValidationException
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.domain.value_objects.enums import RolUsuario
from app.infrastructure.security.password import hash_password, verify_password


def _to_dto(usuario: Usuario) -> UsuarioPublicoDTO:
    return UsuarioPublicoDTO.model_validate(usuario)


class CrearDocenteUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(self, payload: CrearDocenteRequest) -> UsuarioPublicoDTO:
        if await self._usuarios.get_by_correo(payload.correo_institucional):
            raise ConflictException("El correo institucional ya está registrado")
        if await self._usuarios.get_by_cedula(payload.cedula_ciudadania):
            raise ConflictException("La cédula ya está registrada")
        now = datetime.now(timezone.utc)
        docente = Usuario(
            id=uuid4(),
            nombre=payload.nombre,
            correo_institucional=str(payload.correo_institucional),
            cedula_ciudadania=payload.cedula_ciudadania,
            password_hash=hash_password(payload.cedula_ciudadania),
            rol=RolUsuario.DOCENTE,
            activo=True,
            creado_en=now,
            actualizado_en=now,
        )
        creado = await self._usuarios.add(docente)
        return _to_dto(creado)


class ListarDocentesUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(self) -> list[UsuarioPublicoDTO]:
        return [_to_dto(u) for u in await self._usuarios.list_docentes()]


class ObtenerDocenteUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(self, docente_id: UUID) -> UsuarioPublicoDTO:
        usuario = await self._usuarios.get_by_id(docente_id)
        if usuario is None or usuario.rol != RolUsuario.DOCENTE:
            raise NotFoundException("Docente no encontrado")
        return _to_dto(usuario)


class ActualizarPerfilUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(
        self,
        actor: Usuario,
        docente_id: UUID,
        payload: ActualizarPerfilRequest,
    ) -> UsuarioPublicoDTO:
        usuario = await self._usuarios.get_by_id(docente_id)
        if usuario is None:
            raise NotFoundException("Usuario no encontrado")
        es_admin = actor.rol == RolUsuario.ADMINISTRADOR
        if not es_admin and actor.id != usuario.id:
            raise ForbiddenException("Solo puede editar su propio perfil")
        if payload.nombre:
            usuario.nombre = payload.nombre
        if payload.correo_institucional:
            existente = await self._usuarios.get_by_correo(str(payload.correo_institucional))
            if existente and existente.id != usuario.id:
                raise ConflictException("El correo institucional ya está registrado")
            usuario.correo_institucional = str(payload.correo_institucional)
        if payload.password_nueva:
            if not es_admin:
                if not payload.password_actual or not verify_password(payload.password_actual, usuario.password_hash):
                    raise ValidationException("La contraseña actual no es correcta")
            usuario.password_hash = hash_password(payload.password_nueva)
        usuario.actualizado_en = datetime.now(timezone.utc)
        return _to_dto(await self._usuarios.update(usuario))


class CambiarEstadoDocenteUseCase:
    def __init__(self, usuarios: UsuarioRepository) -> None:
        self._usuarios = usuarios

    async def execute(self, docente_id: UUID, activo: bool) -> UsuarioPublicoDTO:
        usuario = await self._usuarios.get_by_id(docente_id)
        if usuario is None or usuario.rol != RolUsuario.DOCENTE:
            raise NotFoundException("Docente no encontrado")
        usuario.activo = activo
        usuario.actualizado_en = datetime.now(timezone.utc)
        return _to_dto(await self._usuarios.update(usuario))
