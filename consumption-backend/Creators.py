# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union

# Package Imports
from Database import DatabaseEntity, SQLiteDatabaseHandler

class Creator(DatabaseEntity):

    def __init__(self, id : int, first_name : Union[str, None], last_name : Union[str, None]):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

class Author(Creator):

    def __init__(self, id: int, first_name: Union[str, None], last_name: Union[str, None], pseudonym : Union[str, None]):
        super().__init__(id, first_name, last_name)
        self.pseudonym = pseudonym

    def save(self) -> None:
        self._instantiate_table()

    @classmethod
    def find(cls, *args, **kwargs) -> list[Author]:
        cls._instantiate_table()

    @classmethod
    def get(cls, id : int) -> Author:
        cls._instantiate_table()

    @classmethod
    def _instantiate_table(cls) -> None:
        cur = SQLiteDatabaseHandler.get_db().cursor
        cur.execute("""CREATE TABLE IF NOT EXISTS authors(
                    author_id,
                    author_first_name TEXT,
                    author_last_name TEXT,
                    author_pseudonym TEXT,
                    PRIMARY KEY (author_id)
        )""")