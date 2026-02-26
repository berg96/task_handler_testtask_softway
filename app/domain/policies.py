from app.domain.enums import TaskStatus
from app.domain.exceptions import InvalidTaskStatusTransition


class TaskStatusPolicy:
    FLOW = (TaskStatus.NEW, TaskStatus.PROCESSING, TaskStatus.DONE, TaskStatus.FAILED)

    @classmethod
    def validate_transition(cls, current: TaskStatus, target: TaskStatus) -> None:
        if target not in cls.FLOW:
            raise InvalidTaskStatusTransition(current, target)
        if cls.FLOW.index(target) <= cls.FLOW.index(current):
            raise InvalidTaskStatusTransition(current, target)
