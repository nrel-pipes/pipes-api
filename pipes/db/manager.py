from __future__ import annotations

from abc import ABC

from pipes.db.document import DocumentDB
from pipes.db.dynamo import DynamoDB
from pipes.db.neptune import NeptuneDB


class AbstractObjectManager(ABC):

    def __init__(self) -> None:
        self.docdb = DocumentDB()
        self.neptune = NeptuneDB()
        self.dynamo = DynamoDB()
