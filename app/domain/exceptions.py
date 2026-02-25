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
