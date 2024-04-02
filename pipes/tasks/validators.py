from __future__ import annotations

from pipes.common.validators import DomainValidator
from pipes.tasks.schemas import TaskCreate


class TaskDomainValidator(DomainValidator):

    def __init__(self, context) -> None:
        self.context = context

    # TODO: task domain validation
    async def validate_inputs(
        self,
        t_create: TaskCreate,
    ) -> TaskCreate:
        """Task scheduled checkin date validation."""
        return t_create
