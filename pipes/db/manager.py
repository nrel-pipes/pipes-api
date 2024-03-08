from __future__ import annotations

from abc import ABC, abstractmethod

from pipes.db.document import DocumentDB
from pipes.db.dynamo import DynamoDB
from pipes.db.neptune import NeptuneDB
from pipes.users.schemas import UserDocument


class AbstractObjectManager(ABC):

    def __init__(self) -> None:
        self.docdb = DocumentDB()
        self.neptune = NeptuneDB()
        self.dynamo = DynamoDB()
        self._current_user: UserDocument | None = None
        self._validated_context: dict = {}

    @property
    def current_user(self) -> UserDocument | None:
        return self._current_user

    @property
    def validated_context(self) -> dict:
        return self._validated_context

    @abstractmethod
    async def validate_user_context(self, user: UserDocument, context: dict):
        """
        Validate the context against two points:
        * the object exists in database
        * the user has access to the object
        """
        self._current_user = user
        # Validate context based on user
        # validated_context = {...}
        # self._validated_context = validated_context
        # return validated_context
