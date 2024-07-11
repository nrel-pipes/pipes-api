from __future__ import annotations

from pydantic import BaseModel

from pipes.common.exceptions import UserPermissionDenied
from pipes.users.schemas import UserDocument


class ContextValidator:
    """PIPES context validator class"""

    def __init__(self) -> None:
        self._validated_context: BaseModel | None = None

    async def validate(self, user: UserDocument, context: BaseModel) -> BaseModel:
        """Validate context existence and user permissions"""
        # Object existence
        validated_context = await self.validate_document(context)
        self._validated_context = validated_context

        # User permission
        await self.validate_permission(user)

        return validated_context

    async def validate_document(self, context: BaseModel) -> BaseModel:
        """Implement concrete validation method"""
        # TODO: subclass validate and return validated context
        return context

    async def validate_permission(self, user: UserDocument) -> bool:
        """Implement concrete validation method"""
        if not user.is_active:
            raise UserPermissionDenied("Inactive user is not allowed.")

        if user.is_superuser:
            return True

        raise UserPermissionDenied("No permission to retrieve this project.")


class DomainValidator:
    """PIPES domain validator class"""

    async def validate(self, instance: BaseModel) -> BaseModel:
        """Call validation methods with names starting with validate_"""
        for attr_name in dir(self):
            if not attr_name.startswith("validate_"):
                continue

            validate_method = getattr(self, attr_name)
            instance = await validate_method(instance)

        return instance
