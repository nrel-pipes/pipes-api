from __future__ import annotations

from pipes.db.abstract import AbstractDatabase


class DynamoDB(AbstractDatabase):

    def __init__(self):
        self.connection = None

    @property
    def endpoint(self) -> str:
        return ""

    def connect(self):
        return None

    def close(self) -> None:
        if self.connection:
            self.connection.close()
        self.connection = None
