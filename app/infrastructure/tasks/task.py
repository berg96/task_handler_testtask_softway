import asyncio

from app.domain.enums import TaskStatus
from app.infrastructure.db import async_session_maker
from app.infrastructure.db.repositories.task import TaskRepository
from app.services.task_service import TaskService

from .celery_app import celery_app


@celery_app.task(name="process_task")
def process_task(task_id: int):
    asyncio.run(_process(task_id))


async def _process(task_id: int):
    async with async_session_maker() as session:
        repo = TaskRepository(session)
        service = TaskService(repo)

        task = await service.update_task_status(task_id, TaskStatus.PROCESSING)

        await asyncio.sleep(3)

        if len(task.title) % 2 == 0:
            new_status = TaskStatus.DONE
            result = "success"
        else:
            new_status = TaskStatus.FAILED
            result = "error"

        await service.update_task_status(task_id, new_status)
        await service.update_result(task_id, result)
