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
        if not title or not title.strip():
            raise ValueError("Title cannot be empty")
        return await self.repo.create(title=title)

    async def get_task(self, task_id: int) -> Optional[TaskEntity]:
        return await self.repo.get(task_id=task_id)

    async def update_task_status(self, task_id: int, new_status: TaskStatus) -> TaskEntity:
        if not (task := await self.get_task(task_id)):
            raise TaskNotFound(identifier=task_id)
        TaskStatusPolicy.validate_transition(task.status, new_status)
        return await self.repo.update(task_id, status=new_status)

    async def update_result(self, task_id: int, result: str) -> TaskEntity:
        return await self.repo.update(task_id, result=result)

    async def get_many(
        self, status: Optional[TaskStatus] = None, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> list[TaskEntity]:
        return await self.repo.get_many(status=status, limit=limit, offset=offset)
