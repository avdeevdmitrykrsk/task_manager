from fastapi import APIRouter

from app.api.endpoints.task_manager import router as task_manager_router
from app.api.endpoints.websocket import router as websocket_router

main_router = APIRouter(prefix='/api')
main_router.include_router(task_manager_router)
main_router.include_router(websocket_router)
