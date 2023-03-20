# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union

# Package Imports
from .Database import DatabaseEntity, SQLiteDatabaseHandler

class Creator(DatabaseEntity):

    def __init__(self, \
                 id : Union[int, None] = None, \
                 first_name : Union[str, None] = None, \
                 last_name : Union[str, None] = None) -> None:
        super().__init__(id)
        self.first_name = first_name
        self.last_name = last_name
    
    def __eq__(self, other: Creator) -> bool:
        return super().__eq__(other) and self.first_name == other.first_name and self.last_name == other.last_name
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} | {self.first_name} {self.last_name} created with ID: {self.id}"

class Author(Creator):

    def __init__(self, \
                 id: Union[int, None] = None, \
                 first_name: Union[str, None] = None, \
                 last_name: Union[str, None] = None, \
                 pseudonym : Union[str, None] = None) -> None:
        super().__init__(id, first_name, last_name)
        self.pseudonym = pseudonym

    def save(self) -> int:
        self._instantiate_table()
        db = SQLiteDatabaseHandler.get_db()
        id = db.cursor().execute("""INSERT INTO authors(
                            author_id,
                            author_first_name,
                            author_last_name,
                            author_pseudonym)
                            VALUES(?,?,?,?)""", (None, self.first_name, self.last_name, self.pseudonym)).lastrowid
        db.commit()
        self.id = id
        return id

    @classmethod
    def find(cls, *args, **kwargs) -> list[Author]:
        cls._instantiate_table()
        params = tuple(kwargs[key] for key in kwargs.keys())
        keys = list(kwargs.keys())
        sql = "SELECT * FROM authors"
        if params:
            sql += f" WHERE {keys[0]} = ?"
            for i in range(1, len(params)):
                sql += f" AND {keys[i]} = ?"
        authors = SQLiteDatabaseHandler.get_db().cursor().execute(sql, params).fetchall()
        return [Author(*author_data) for author_data in authors]

    @classmethod
    def get(cls, id : int) -> Author:
        cls._instantiate_table()
        author_data = SQLiteDatabaseHandler.get_db().cursor().execute("""SELECT * FROM authors WHERE author_id = ?""", (id, )).fetchone()
        return Author(*author_data)

    @classmethod
    def _instantiate_table(cls) -> None:
        SQLiteDatabaseHandler.get_db().cursor().execute("""CREATE TABLE IF NOT EXISTS authors(
                                                        author_id INTEGER PRIMARY KEY NOT NULL,
                                                        author_first_name TEXT,
                                                        author_last_name TEXT,
                                                        author_pseudonym TEXT)""")
    
    def __eq__(self, other: Author) -> bool:
        return super().__eq__(other) and self.pseudonym == other.pseudonym