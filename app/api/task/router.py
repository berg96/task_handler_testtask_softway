from typing import Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.schemas import ErrorResponse
from app.api.task.schemas import TaskCreate, TaskFromDB, TaskList
from app.domain.enums import TaskStatus
from app.infrastructure.db import get_async_session
from app.infrastructure.db.repositories.task import TaskRepository
from app.infrastructure.tasks.task import process_task
from app.services.task_service import TaskService

router = APIRouter(tags=["Task"], prefix="/tasks")


@router.post(
    "/",
    response_model=TaskFromDB,
    status_code=status.HTTP_201_CREATED,
    name="Создать задачу",
    description="Создание задачи с указанным названием",
    responses={
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def create_order(
    data: TaskCreate,
    session: AsyncSession = Depends(get_async_session),
) -> TaskFromDB:
    repo = TaskRepository(session)
    task = await TaskService(repo).create_task(data.title)
    process_task.delay(task.id)
    return TaskFromDB.model_validate(task)


@router.get(
    "/{task_id}/",
    response_model=TaskFromDB,
    status_code=status.HTTP_200_OK,
    name="Получить задачу",
    description="Получение задачи по его идентификатору",
    responses={
        404: {"model": ErrorResponse, "description": "Заказ не найден"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def get_order(
    task_id: int = Path(..., description="ID задачи"),
    session: AsyncSession = Depends(get_async_session),
) -> TaskFromDB:
    repo = TaskRepository(session)
    task = await TaskService(repo).get_task(task_id)
    return TaskFromDB.model_validate(task)


@router.get(
    "/",
    response_model=TaskList,
    status_code=status.HTTP_200_OK,
    name="Получить задачи",
    description="Получение задач с возможностью фильтрации по статусу и пагинации",
    responses={
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"},
    },
)
async def get_tasks(
    task_status: Optional[TaskStatus] = Query(None, description="Статус задачи для фильтрации"),
    limit: Optional[int] = Query(None, ge=0, description="Ограничение по количеству в выдаче"),
    offset: Optional[int] = Query(None, ge=0, description="Смещение списка выдачи"),
    session: AsyncSession = Depends(get_async_session),
) -> TaskList:
    repo = TaskRepository(session)
    tasks = await TaskService(repo).get_many(task_status, limit, offset)
    return TaskList(items=[TaskFromDB.model_validate(task) for task in tasks], count=len(tasks))
