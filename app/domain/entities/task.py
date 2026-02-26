from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.domain.enums import TaskStatus
from app.infrastructure.db import Task


@dataclass
class TaskEntity:
    id: int
    title: str
    status: TaskStatus
    result: Optional[str]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, task: Task) -> "TaskEntity":
        return cls(
            id=task.id,
            title=task.title,
            status=task.status,
            result=task.result,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
