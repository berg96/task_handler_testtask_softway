from datetime import UTC, datetime
from typing import Optional

from app.domain.entities.task import TaskEntity
from app.domain.enums import TaskStatus
from app.domain.exceptions import TaskNotFound
from app.domain.repositories import TaskRepositoryInterface


class FakeTaskRepository(TaskRepositoryInterface):
    def __init__(self) -> None:
        self._store: dict[int, TaskEntity] = {}
        self._id_seq = 1

    async def create(self, title: str, status: TaskStatus = TaskStatus.NEW, result: Optional[str] = None) -> TaskEntity:
        now = datetime.now(UTC)

        task = TaskEntity(
            id=self._id_seq,
            title=title,
            status=status,
            result=result,
            created_at=now,
            updated_at=now,
        )

        self._store[self._id_seq] = task
        self._id_seq += 1

        return task

    async def get(self, task_id: int, return_none: bool = False):
        task = self._store.get(task_id)

        if task is None and not return_none:
            raise TaskNotFound(identifier=task_id)

        return task

    async def update_status(self, task_id: int, new_status: TaskStatus):
        task = self._store.get(task_id)

        if task is None:
            raise TaskNotFound(identifier=task_id)

        task.status = new_status
        task.updated_at = datetime.now(UTC)

        return task

    async def get_many(
        self,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ):
        items = list(self._store.values())

        if status:
            items = [t for t in items if t.status == status]

        items.sort(key=lambda t: t.created_at)

        offset = offset or 0
        limit = limit or len(items)

        return items[offset : offset + limit]
