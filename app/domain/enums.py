import enum


class TaskStatus(str, enum.Enum):
    NEW = "new"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"
