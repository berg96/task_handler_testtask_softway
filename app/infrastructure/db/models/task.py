from sqlalchemy import Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.enums import TaskStatus
from app.infrastructure.db.base import Base, TimestampMixin


class Task(TimestampMixin, Base):
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.NEW,
        index=True,
    )
    result: Mapped[str] = mapped_column(Text, nullable=True)
