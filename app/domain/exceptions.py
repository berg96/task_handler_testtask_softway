from app.domain.enums import TaskStatus


class NotFoundError(Exception):
    resource: str = "Resource"
    message_template: str = "{resource} not found"

    def __init__(self, *, resource: str | None = None, identifier: str | int | None = None):
        self.resource = resource or self.resource
        self.identifier = identifier
        message = self.message_template.format(resource=self.resource)
        if identifier is not None:
            message += f" id={identifier}"
        super().__init__(message)


class TaskNotFound(NotFoundError):
    resource = "Task"


class InvalidTaskStatusTransition(Exception):
    def __init__(self, from_status: TaskStatus, to_status: TaskStatus):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(f"Cannot change task status from {from_status} to {to_status}")
