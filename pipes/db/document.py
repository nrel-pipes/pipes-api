from beanie import Document

from pipes.db.abstract import AbstractDatabase


class DocumentDB(AbstractDatabase):

    async def get(self, document) -> Document:
        document = await document.find_one()
        return document

    async def create(self, document: Document) -> Document:
        document = await document.insert()
        return document

    async def update(self):
        pass

    async def delete(self):
        pass
