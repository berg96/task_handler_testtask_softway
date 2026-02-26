from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.domain.enums import TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., description="Название задачи")


class TaskFromDB(TaskCreate):
    id: int = Field(..., description="Идентификатор записи в БД")
    status: TaskStatus = Field(..., description="Статус задачи")
    result: Optional[str] = Field(None, description="Результат выполнения задачи")
    created_at: datetime = Field(..., description="Время создания записи")
    updated_at: datetime = Field(..., description="Время обновления записи")

    model_config = ConfigDict(from_attributes=True)


class TaskList(BaseModel):
    items: list[TaskFromDB] = Field(..., description="Список заказов")
    count: int = Field(..., ge=0, description="Количество заказов")
