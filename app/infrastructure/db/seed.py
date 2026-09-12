"""Seed de administrador inicial. Las categorías se insertan en la migración Alembic."""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select

from app.domain.value_objects.enums import RolUsuario
from app.infrastructure.config.settings import get_settings
from app.infrastructure.db.models.usuario import UsuarioModel
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.security.password import hash_password


async def seed_admin() -> None:
    settings = get_settings()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(UsuarioModel).where(UsuarioModel.correo_institucional == settings.admin_email)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return
        now = datetime.now(timezone.utc)
        session.add(
            UsuarioModel(
                id=uuid4(),
                nombre="Administrador General",
                correo_institucional=settings.admin_email,
                cedula_ciudadania=None,
                password_hash=hash_password(settings.admin_password),
                rol=RolUsuario.ADMINISTRADOR,
                activo=True,
                creado_en=now,
                actualizado_en=now,
            )
        )
        await session.commit()


if __name__ == "__main__":
    asyncio.run(seed_admin())
