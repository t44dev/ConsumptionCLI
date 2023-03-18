# General Imports
from __future__ import annotations # For self-referential type-hints
from pathlib import Path
import os
from abc import abstractmethod, ABC
from typing import Union
import json
import sqlite3

# Package Imports
from .PathHandling import CONFIG_PATH

class DatabaseEntity(ABC):
    
    def __init__(self, id : Union[int, None] = None) -> None:
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

    def __eq__(self, other : DatabaseEntity) -> bool:
        return self.id == other.id

class SQLiteDatabaseHandler():

    DB_CONNECTION : sqlite3.Connection = None

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be instantiated, run get_db() to access Connection instance.")
    
    @classmethod
    def get_db(cls) -> sqlite3.Connection:
        if not SQLiteDatabaseHandler.DB_CONNECTION:
            with open(CONFIG_PATH, "r") as f:
                cfg = json.load(f)
                DB_PATH = Path(os.path.expanduser(cfg["DB_PATH"]))
                print(str(DB_PATH))
                cls.DB_CONNECTION = sqlite3.connect(DB_PATH)
        return cls.DB_CONNECTION