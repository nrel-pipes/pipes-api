from __future__ import annotations

from abc import ABC, abstractmethod


class AbstractDatabase(ABC):

    def __init__(self):
        pass

    @property
    @abstractmethod
    def endpoint(self):
        """database url"""

    @abstractmethod
    def connect(self):
        """Connect to database"""

    @abstractmethod
    def close(self):
        """Close database connection"""
