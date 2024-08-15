from __future__ import annotations

from beanie import Document
from pymongo.results import UpdateResult

from pipes.db.abstract import AbstractDatabase


class DocumentDB(AbstractDatabase):

    def connect(self):
        pass

    def close(self):
        pass

    async def get(self, collection: Document, id: str) -> Document:
        return await collection.get(id)

    async def insert(self, instance: Document) -> Document:
        return await instance.insert()

    async def find_one(self, collection: Document, query: dict) -> Document | None:
        return await collection.find_one(query)

    async def exists(self, collection: Document, query: dict) -> bool:
        doc = await collection.find_one(query)
        return True if doc else False

    async def find_all(
        self,
        collection: Document,
        query: dict | None = None,
    ) -> list[Document]:
        if query:
            return await collection.find(query).to_list()

        return await collection.find().to_list()

    async def update_one(
        self,
        collection: Document,
        find: dict,
        update: dict,
    ) -> UpdateResult:
        return await collection.find_one(find).update(update)
