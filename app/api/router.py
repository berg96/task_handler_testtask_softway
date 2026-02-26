from fastapi import APIRouter

from .task.router import router as task_router

main_router = APIRouter(prefix="/api")
main_router.include_router(task_router)
