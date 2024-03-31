from __future__ import annotations

from abc import ABC

from beanie import Document

from pipes.db.document import DocumentDB

# from pipes.db.dynamo import DynamoDB
from pipes.db.neptune import NeptuneDB


class AbstractObjectManager(ABC):

    def __init__(self, document: Document, neptune: NeptuneDB) -> None:
        """Initialize a new object manager

        Parameters
        ----------
        document : Document
            The document class
        neptune : NeptuneDB
            The neptune instance
        """
        self._document = document
        self._neptune = neptune

    @property
    def d(self):
        return DocumentDB(self._document)

    @property
    def g(self):
        return self._neptune
