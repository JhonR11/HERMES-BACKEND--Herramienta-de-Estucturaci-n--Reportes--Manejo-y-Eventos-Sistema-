from app.application.dtos.catalogo import CategoriaDTO
from app.domain.repositories.categoria_repository import CategoriaRepository


class ListarCategoriasUseCase:
    def __init__(self, categorias: CategoriaRepository) -> None:
        self._categorias = categorias

    async def execute(self) -> list[CategoriaDTO]:
        return [CategoriaDTO.model_validate(item) for item in await self._categorias.list_all()]
