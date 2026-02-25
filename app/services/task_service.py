from typing import Optional

from app.domain.entities.task import TaskEntity
from app.domain.enums import TaskStatus
from app.domain.exceptions import TaskNotFound
from app.domain.policies import TaskStatusPolicy
from app.domain.repositories import TaskRepositoryInterface


class TaskService:
    def __init__(self, repo: TaskRepositoryInterface):
        self.repo = repo

    async def create_task(self, title: str) -> TaskEntity:
        task = await self.repo.create(title=title)
        return task

    async def get_task(self, task_id: int) -> Optional[TaskEntity]:
        return await self.repo.get(task_id=task_id)

    async def update_order_status(self, task_id: int, new_status: TaskStatus) -> Optional[TaskEntity]:
        if not (task := await self.get_task(task_id)):
            raise TaskNotFound(identifier=task_id)
        TaskStatusPolicy.validate_transition(task.status, new_status)
        order = await self.repo.update_status(task_id, new_status)
        return order

    async def get_many(
        self, status: Optional[TaskStatus] = None, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[TaskEntity]:
        return await self.repo.get_many(status=status, limit=limit, offset=offset)
