from __future__ import annotations

from abc import ABC

from pipes.db.document import DocumentDB
from pipes.db.neptune import NeptuneDB


class AbstractObjectManager(ABC):

    __label__: str | None = None

    @property
    def d(self):
        docdb = DocumentDB()
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
