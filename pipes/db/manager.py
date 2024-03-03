from __future__ import annotations

from typing import Any

from pipes.db.document import DocumentDB
from pipes.db.graph import GraphDB


class PipesObjectManager:

    def __init__(self):
        self.d = DocumentDB()
        self.g = GraphDB()
        self._current_user = None

    @property
    def current_user(self):
        return self._current_user

    def set_current_user(self, user: Any):
        self._current_user = user
