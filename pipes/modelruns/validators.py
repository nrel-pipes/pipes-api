from __future__ import annotations

from pipes.common.exceptions import ContextValidationError
from pipes.common.validators import DomainValidator
from pipes.db.document import DocumentDB
from pipes.models.contexts import ModelDocumentContext
from pipes.models.validators import ModelContextValidator
from pipes.modelruns.contexts import ModelRunSimpleContext, ModelRunDocumentContext
from pipes.modelruns.schemas import ModelRunDocument


class ModelRunContextValidator(ModelContextValidator):
    """Model run context validator class"""

    async def validate_document(
        self,
        context: ModelRunSimpleContext,
    ) -> ModelRunDocumentContext:
        """Get model run document through validation"""
        m_context = await super().validate_document(context)
        p_doc = m_context.project
        pr_doc = m_context.projectrun
        m_doc = m_context.model

        mr_name = context.modelrun
        docdb = DocumentDB()
        mr_doc = await docdb.find_one(
            collection=ModelRunDocument,
            query={"name": mr_name},
        )

        if not m_doc:
            raise ContextValidationError(
                f"Invalid context, model run '{mr_name}' "
                f"does not exist under model '{m_doc.name}'"
                f"of project run '{pr_doc.name}'"
                f"in project '{p_doc.name}'",
            )

        validated_context = ModelRunDocumentContext(
            project=p_doc,
            projectrun=pr_doc,
            model=m_doc,
            modelrun=mr_doc,
        )
        self._validated_context = validated_context

        return validated_context


class ModelRunDomainValidator(DomainValidator):

    def __init__(self, context: ModelDocumentContext) -> None:
        self.context = context

    # TODO: model domain validation
