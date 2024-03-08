from __future__ import annotations

from pipes.db.abstract import AbstractDatabase


class DocumentDB(AbstractDatabase):

    @property
    def endpoint(self):
        return ""

    def connect(self):
        return None

    def close(self):
        if self.connection:
            self.connection.close()
        self.connection = None
