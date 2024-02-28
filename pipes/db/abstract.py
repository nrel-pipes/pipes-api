from abc import ABC, abstractmethod


class AbstractDatabase(ABC):

    @abstractmethod
    def get(self, query):
        pass

    @abstractmethod
    def create(self, query):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def delete(self):
        pass
