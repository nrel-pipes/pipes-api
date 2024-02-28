from __future__ import annotations

from pipes.db.document import DocumentDB
from pipes.db.graph import GraphDB


class DocumentGrahpObjectManager:

    def __init__(self):
        self.d = DocumentDB()
        self.g = GraphDB()
