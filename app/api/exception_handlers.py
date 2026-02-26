from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.domain.exceptions import (
    InvalidTaskStatusTransition,
    NotFoundError,
)

from .schemas import ErrorResponse


def _build_detail(message: str, exc: BaseException) -> str:
    """Безопасно формирует detail для ответа."""
    error_type = exc.__class__.__name__
    reason = str(exc)
    safe_reason = reason[:300] if reason else ""
    if safe_reason:
        return f"{message} ({error_type}): {safe_reason}"
    return f"{message} ({error_type})"


def setup_exception_handlers(app):
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(detail=_build_detail("Resource not found", exc)).model_dump(),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(detail=_build_detail("Database error", exc)).model_dump(),
        )

    @app.exception_handler(InvalidTaskStatusTransition)
    async def invalid_task_status_transition_handler(request: Request, exc: InvalidTaskStatusTransition):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(detail=_build_detail("Invalid task status transition", exc)).model_dump(),
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=ErrorResponse(detail=_build_detail("Invalid task title", exc)).model_dump(),
        )
