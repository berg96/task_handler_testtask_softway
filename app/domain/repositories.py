from abc import ABC, abstractmethod
from typing import Optional

from .entities.task import TaskEntity
from .enums import TaskStatus


class TaskRepositoryInterface(ABC):
    @abstractmethod
    async def create(self, title: str) -> TaskEntity:
        """Создать новую задачу"""
        pass

    @abstractmethod
    async def get(self, task_id: int, return_none: bool = False) -> Optional[TaskEntity]:
        """Получить задачу по ID"""
        pass

    @abstractmethod
    async def update(self, task_id: int, **fields) -> TaskEntity:
        """Обновить статус задачи"""
        pass

    @abstractmethod
    async def get_many(
        self,
        status: Optional[TaskStatus] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[TaskEntity]:
        """Получить список задач с фильтром и пагинацией"""
        pass
