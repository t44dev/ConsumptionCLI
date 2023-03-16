# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union
from datetime import datetime

# Package Imports
from .Database import DatabaseEntity, SQLiteDatabaseHandler
from .Creators import Author

class Consumable(DatabaseEntity):
    
    def __init__(self, \
                 id : Union[int, None], \
                 name : str, \
                 major_parts : int, \
                 minor_parts : int, \
                 completions : int, \
                 rating : Union[float, None], \
                 start_date : int, \
                 end_date : Union[int, None]) -> None:
        super().__init__(id)
        self.name = name
        self.major_parts = major_parts
        self.minor_parts = minor_parts
        self.completions = completions
        self.rating = rating
        # Using unix-timestamp
        self.start_date = datetime.fromtimestamp(start_date)
        self.end_date = datetime.fromtimestamp(end_date) if end_date else end_date

class Novel(Consumable):

    MAJOR_PART_NAME = "Volume"
    MINOR_PART_NAME = "Chapter"

    def __init__(self, 
                 id : Union[int, None], \
                 name : str, \
                 major_parts : int, \
                 minor_parts : int, \
                 completions : int, \
                 rating : Union[float, None], \
                 start_date : int, \
                 end_date : Union[int, None], \
                 author : Union[Author, None]) -> None:
        super().__init__(id, name, major_parts, minor_parts, completions, rating, start_date, end_date)
        self.author = author
    
    def save(self) -> int:
        self._instantiate_table()

    @classmethod
    def find(cls, *args, **kwargs) -> list[Novel]:
        cls._instantiate_table()

    @classmethod    
    def get(cls, id : int) -> Novel:
        cls._instantiate_table()

    @classmethod
    def _instantiate_table(cls) -> None:
        cur = SQLiteDatabaseHandler.get_db().cursor
        cur.execute("""CREATE TABLE IF NOT EXISTS novels(
                    nov_id INTEGER PRIMARY KEY NOT NULL UNIQUE DEFAULT 0,
                    author_id INTEGER,
                    nov_name TEXT NOT NULL,
                    nov_major_parts INTEGER NOT NULL DEFAULT 0,
                    nov_minor_parts INTEGER NOT NULL DEFAULT 0,
                    nov_completions INTEGER NOT NULL DEFAULT 0,
                    nov_rating REAL NOT NULL DEFAULT 0.0,
                    nov_start_date INTEGER NOT NULL,
                    nov_end_date INTEGER,
                    FOREIGN KEY (author_id)
                        REFERENCES authors (author_id)
                        ON DELETE SET NULL
                        ON UPDATE NO ACTION)""")