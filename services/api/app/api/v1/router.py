from fastapi import APIRouter

from app.api.v1.routes.admin import router as admin_router
from app.api.v1.routes.admin_chat import router as admin_chat_router
from app.api.v1.routes.auth import router as auth_router
from app.api.v1.routes.chat import router as chat_router
from app.api.v1.routes.cms import router as cms_router
from app.api.v1.routes.projects import router as projects_router
from app.api.v1.routes.runs import router as runs_router
from app.api.v1.routes.scenarios import router as scenarios_router
from app.api.v1.routes.soil_samples import router as soil_samples_router
from app.api.v1.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(admin_router)
api_router.include_router(admin_chat_router)
api_router.include_router(auth_router)
api_router.include_router(chat_router)
api_router.include_router(cms_router)
api_router.include_router(projects_router)
api_router.include_router(soil_samples_router)
api_router.include_router(scenarios_router)
api_router.include_router(runs_router)
api_router.include_router(system_router)
