from __future__ import annotations

from beanie import Document

from pipes.db.abstract import AbstractDatabase


class DocumentDB(AbstractDatabase):

    def __init__(self, document: Document) -> None:
        self.document = document

    def connect(self):
        pass

    def close(self):
        pass

    async def insert(self, instance: Document) -> Document:
        return await instance.insert()

    async def find_one(self, query: dict) -> Document | None:
        return await self.document.find_one(query)

    async def exists(self, query: dict) -> bool:
        doc = await self.find_one(query)
        return True if doc else False
