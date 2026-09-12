from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.categoria import CategoriaReporte
from app.domain.repositories.categoria_repository import CategoriaRepository
from app.infrastructure.db.models.categoria import CategoriaReporteModel


def to_entity(model: CategoriaReporteModel) -> CategoriaReporte:
    return CategoriaReporte(id=model.id, nombre=model.nombre, descripcion=model.descripcion)


class SqlAlchemyCategoriaRepository(CategoriaRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> list[CategoriaReporte]:
        result = await self._session.execute(select(CategoriaReporteModel).order_by(CategoriaReporteModel.nombre))
        return [to_entity(m) for m in result.scalars().all()]

    async def get_by_id(self, categoria_id: UUID) -> CategoriaReporte | None:
        model = await self._session.get(CategoriaReporteModel, categoria_id)
        return to_entity(model) if model else None
