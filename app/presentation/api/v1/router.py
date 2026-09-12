from fastapi import APIRouter

from app.presentation.api.v1.routers import admin_reportes, auth, docentes, eventos, noticias, public, reportes, ws

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(docentes.router)
api_router.include_router(reportes.router)
api_router.include_router(admin_reportes.router)
api_router.include_router(eventos.router)
api_router.include_router(noticias.router)
api_router.include_router(public.router)
api_router.include_router(ws.router)
