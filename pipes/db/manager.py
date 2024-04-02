from __future__ import annotations

from abc import ABC

from beanie import Document

from pipes.db.document import DocumentDB

# from pipes.db.dynamo import DynamoDB
from pipes.db.neptune import NeptuneDB


class AbstractObjectManager(ABC):

    __label__: str | None = None

    def __init__(self, document: Document) -> None:
        """Initialize a new object manager

        Parameters
        ----------
        document : Document
            The document class
        neptune : NeptuneDB
            The neptune instance
        """
        self.document = document

    @property
    def d(self):
        docdb = DocumentDB(self.document)
        return docdb

    @property
    def n(self):
        neptune = NeptuneDB()
        neptune.connect()
        return neptune

    @property
    def label(self):
        return self.__label__

    def __delete__(self):
        self.d.close()
        self.n.close()
