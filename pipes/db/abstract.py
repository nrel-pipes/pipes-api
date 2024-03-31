from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractDatabase(ABC):

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    def __delete__(self):
        self.close()
