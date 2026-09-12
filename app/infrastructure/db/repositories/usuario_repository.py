from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.usuario import Usuario
from app.domain.repositories.usuario_repository import UsuarioRepository
from app.domain.value_objects.enums import RolUsuario
from app.infrastructure.db.models.usuario import UsuarioModel


def to_entity(model: UsuarioModel) -> Usuario:
    return Usuario(
        id=model.id,
        nombre=model.nombre,
        correo_institucional=model.correo_institucional,
        cedula_ciudadania=model.cedula_ciudadania,
        password_hash=model.password_hash,
        rol=model.rol,
        activo=model.activo,
        creado_en=model.creado_en,
        actualizado_en=model.actualizado_en,
    )


class SqlAlchemyUsuarioRepository(UsuarioRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, usuario_id: UUID) -> Usuario | None:
        model = await self._session.get(UsuarioModel, usuario_id)
        return to_entity(model) if model else None

    async def get_by_correo(self, correo: str) -> Usuario | None:
        result = await self._session.execute(
            select(UsuarioModel).where(UsuarioModel.correo_institucional == correo)
        )
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def get_by_cedula(self, cedula: str) -> Usuario | None:
        result = await self._session.execute(
            select(UsuarioModel).where(UsuarioModel.cedula_ciudadania == cedula)
        )
        model = result.scalar_one_or_none()
        return to_entity(model) if model else None

    async def list_docentes(self) -> list[Usuario]:
        result = await self._session.execute(
            select(UsuarioModel)
            .where(UsuarioModel.rol == RolUsuario.DOCENTE)
            .order_by(UsuarioModel.nombre)
        )
        return [to_entity(m) for m in result.scalars().all()]

    async def add(self, usuario: Usuario) -> Usuario:
        model = UsuarioModel(
            id=usuario.id,
            nombre=usuario.nombre,
            correo_institucional=usuario.correo_institucional,
            cedula_ciudadania=usuario.cedula_ciudadania,
            password_hash=usuario.password_hash,
            rol=usuario.rol,
            activo=usuario.activo,
            creado_en=usuario.creado_en,
            actualizado_en=usuario.actualizado_en,
        )
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)

    async def update(self, usuario: Usuario) -> Usuario:
        model = await self._session.get(UsuarioModel, usuario.id)
        if model is None:
            raise ValueError("Usuario no encontrado")
        model.nombre = usuario.nombre
        model.correo_institucional = usuario.correo_institucional
        model.cedula_ciudadania = usuario.cedula_ciudadania
        model.password_hash = usuario.password_hash
        model.rol = usuario.rol
        model.activo = usuario.activo
        await self._session.flush()
        await self._session.refresh(model)
        return to_entity(model)
