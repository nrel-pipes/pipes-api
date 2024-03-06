from __future__ import annotations

from abc import ABC, abstractmethod

from beanie import Document
from pydantic import BaseModel

from pipes.db.document import DocumentDB
from pipes.db.graph import GraphDB
from pipes.users.schemas import UserDocument


class AbstractObjectManager(ABC):

    def __init__(self, user: UserDocument) -> None:
        self.d = DocumentDB()
        self.g = GraphDB()
        self.user = user
        self.validated_context = (
            Document()
        )  # NOTE: re-assign this value after context valiation

    @abstractmethod
    async def validate_context(self, context: BaseModel) -> BaseModel:
        """
        Validate the context against two points:
        * the object exists in database
        * the user has access to the object
        """
