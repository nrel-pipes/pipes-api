from __future__ import annotations

from abc import ABC, abstractmethod

from beanie import Document

from pipes.db.document import DocumentDB
from pipes.db.graph import GraphDB
from pipes.common.contexts import UserContext


class AbstractObjectManager(ABC):

    def __init__(self, context: UserContext):
        self.d = DocumentDB()
        self.g = GraphDB()
        self.context = context

    @property
    def user(self) -> Document:
        return self.context.get("user", None)

    @abstractmethod
    async def validate_context(self, context):
        """Validate the context with the user"""
