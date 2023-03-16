# General Imports
from __future__ import annotations # For self-referential type-hints
from abc import abstractmethod, ABC
from typing import Union
import json
import sqlite3

class DatabaseEntity(ABC):
    
    def __init__(self, id : Union[int, None]) -> None:
        super().__init__()
        self.id = id    # None if created by user and internal db id if get() used.
    
    @abstractmethod
    def save(self) -> int:
        pass

    @classmethod
    @abstractmethod
    def find(cls, *args, **kwargs) -> list[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def get(cls, id : int) -> DatabaseEntity:
        pass

    @classmethod
    @abstractmethod
    def _instantiate_table(cls) -> None:
        pass

class SQLiteDatabaseHandler():

    DB_CONNECTION : sqlite3.Connection = None

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be instantiated, run get_db() to access Connection instance.")
    
    @classmethod
    def get_db(cls) -> sqlite3.Connection:
        if not SQLiteDatabaseHandler.DB_CONNECTION:
            with open("settings.json", "r") as f:
                settings = json.load(f)
                f.close()
                cls.DB_CONNECTION = sqlite3.connect(settings["DB_PATH"])
        return cls.DB_CONNECTION