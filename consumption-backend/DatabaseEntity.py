# General Imports
from __future__ import annotations # For self-referential type-hints
from abc import abstractmethod, ABC

class DatabaseEntity(ABC):
    
    def __init__(self, id : int) -> None:
        super().__init__()
        self.id = id    # None if created by user and internal db id if get() used.
    
    @abstractmethod
    def save() -> None:
        pass

    @classmethod
    @abstractmethod
    def find(cls, *args, **kwargs) -> list[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def get(cls, id : int) -> DatabaseEntity:
        pass