import asyncio
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.infrastructure.config.settings import get_settings
from app.infrastructure.db.repositories.evento_repository import SqlAlchemyEventoRepository
from app.infrastructure.db.session import AsyncSessionLocal
from app.infrastructure.websockets.manager import event_manager
from app.presentation.api.v1.router import api_router
from app.presentation.middlewares.exception_handlers import register_exception_handlers


async def _deshabilitar_eventos_vencidos() -> None:
    settings = get_settings()
    while True:
        async with AsyncSessionLocal() as session:
            count = await SqlAlchemyEventoRepository(session).deshabilitar_vencidos()
            await session.commit()
            if count:
                await event_manager.publish(
                    "evento.deshabilitado",
                    {"motivo": "vencimiento", "cantidad": count},
                )
        await asyncio.sleep(settings.event_expiry_poll_seconds)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    task = asyncio.create_task(_deshabilitar_eventos_vencidos())
    yield
    task.cancel()


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title="API de Reportes Docentes, Eventos y Noticias",
        description=(
            "Backend en Clean Architecture para la gestión institucional de reportes docentes, "
            "eventos y noticias.\n\n"
            "**Eventos vencidos:** un worker en segundo plano marca `DESHABILITADO` cuando "
            "`fecha_fin` ya pasó (además el listado público filtra `fecha_fin > now()`).\n\n"
            "**Tiempo real:** WebSocket en `/api/v1/ws/eventos` (se eligió WS frente a SSE "
            "porque el prompt exige difusión bidireccional lista para la página principal)."
        ),
        version="1.0.0",
        lifespan=lifespan,
        contact={"name": "Administración institucional"},
    )
    origins = settings.cors_origin_list
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials="*" not in origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(application)
    application.include_router(api_router)

    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    application.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    @application.get("/health", tags=["Sistema"], summary="Healthcheck")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return application


app = create_app()
