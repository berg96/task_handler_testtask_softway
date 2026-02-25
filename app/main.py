from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.exception_handlers import setup_exception_handlers
from .api.router import main_router
from .config.health import run_health_check
from .config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not await run_health_check():
        exit(1)
    yield


app = FastAPI(title=settings.APP_TITLE, description=settings.APP_DESCRIPTION, lifespan=lifespan)

app.include_router(main_router)
setup_exception_handlers(app)
