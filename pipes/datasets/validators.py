from __future__ import annotations


from pipes.common.validators import DomainValidator
from pipes.datasets.schemas import DatasetCreate


class DatasetDomainValidator(DomainValidator):

    def __init__(self, context) -> None:
        self.context = context

    # TODO: dataset domain validation
    async def validate_scheduled_checkin(
        self,
        d_create: DatasetCreate,
    ) -> DatasetCreate:
        """Dataset scheduled checkin date validation."""
        return d_create
