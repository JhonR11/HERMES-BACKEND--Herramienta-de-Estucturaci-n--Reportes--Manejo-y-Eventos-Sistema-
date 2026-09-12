from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.entities.reporte import Reporte, ReporteArchivo
from app.domain.value_objects.enums import EstadoReporte


class ReporteRepository(ABC):
    @abstractmethod
    async def add(self, reporte: Reporte) -> Reporte: ...

    @abstractmethod
    async def update(self, reporte: Reporte) -> Reporte: ...

    @abstractmethod
    async def get_by_id(self, reporte_id: UUID) -> Reporte | None: ...

    @abstractmethod
    async def list_for_usuario(
        self,
        usuario_id: UUID,
        *,
        es_admin: bool,
        estado: EstadoReporte | None = None,
    ) -> list[Reporte]: ...

    @abstractmethod
    async def list_publicos(self) -> list[Reporte]: ...

    @abstractmethod
    async def list_en_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> list[Reporte]: ...

    @abstractmethod
    async def add_archivo(self, archivo: ReporteArchivo) -> ReporteArchivo: ...

    @abstractmethod
    async def get_archivo(self, archivo_id: UUID) -> ReporteArchivo | None: ...

    @abstractmethod
    async def delete_archivo(self, archivo_id: UUID) -> None: ...

    @abstractmethod
    async def count_pdfs(self, reporte_id: UUID) -> int: ...
