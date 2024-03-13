from __future__ import annotations


from pipes.common.validators import DomainValidator
from pipes.models.schemas import ModelDocument
from pipes.modelruns.schemas import ModelRunDocument
from pipes.datasets.schemas import DatasetDocument


class DatasetDomainValidator(DomainValidator):

    def __init__(self) -> None:
        self._cached_mr_doc = None

    async def _get_parent(self, d_doc: DatasetDocument) -> ModelRunDocument:
        """Get the parent document, here is model doc"""
        mr_doc = self._cached_mr_doc

        if mr_doc is None:
            mr_id = d_doc.context.modelrun
            mr_doc = await ModelDocument.get(mr_id)
            self._cached_mr_doc = mr_doc

        return mr_doc

    # TODO: dataset domain validation

    async def validate_scheduled_checkin(
        self,
        d_doc: DatasetDocument,
    ) -> DatasetDocument:
        """Dataset scheduled checkin date validation."""

        return d_doc
