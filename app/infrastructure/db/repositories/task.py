from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import settings
from app.domain.entities.task import TaskEntity
from app.domain.enums import TaskStatus
from app.domain.exceptions import TaskNotFound
from app.domain.repositories import TaskRepositoryInterface
from app.infrastructure.db import Task


class TaskRepository(TaskRepositoryInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        title: str,
        status: Optional[TaskStatus] = TaskStatus.NEW,
        result: Optional[str] = None,
    ) -> TaskEntity:
        task = Task(title=title, status=status, result=result)
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return TaskEntity.from_orm(task)

    async def get(self, task_id: int, return_none: bool = False) -> Optional[TaskEntity]:
        result = await self.session.execute(select(Task).where(Task.id == task_id))
        task = result.scalar_one_or_none()
        if task is None:
            if return_none:
                return None
            raise TaskNotFound(identifier=task_id)
        return TaskEntity.from_orm(task)

    async def update(self, task_id: int, **fields) -> TaskEntity:
        result = await self.session.execute(select(Task).where(Task.id == task_id).with_for_update())
        task = result.scalar_one_or_none()
        if task is None:
            raise TaskNotFound(identifier=task_id)

        for key, value in fields.items():
            setattr(task, key, value)

        await self.session.commit()
        await self.session.refresh(task)
        return TaskEntity.from_orm(task)

    async def get_many(
        self,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = settings.LIMIT_DEFAULT,
        offset: Optional[int] = settings.OFFSET_DEFAULT,
    ) -> list[TaskEntity]:
        stmt = select(Task)

        if status:
            stmt = stmt.where(Task.status == status)

        stmt = stmt.order_by(Task.created_at).limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return [TaskEntity.from_orm(task) for task in result.scalars().all()]
