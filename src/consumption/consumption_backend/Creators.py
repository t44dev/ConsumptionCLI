# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union

# Package Imports
from .Database import DatabaseEntity, SQLiteDatabaseHandler

class Creator(DatabaseEntity):

    def __init__(self, id : Union[int, None], first_name : Union[str, None], last_name : Union[str, None]):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

class Author(Creator):

    def __init__(self, id: Union[int, None], first_name: Union[str, None], last_name: Union[str, None], pseudonym : Union[str, None]):
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
        print(sql, params)
        authors = SQLiteDatabaseHandler.get_db().cursor().execute(sql, params).fetchall()
        return authors

    @classmethod
    def get(cls, id : int) -> Author:
        cls._instantiate_table()
        author = SQLiteDatabaseHandler.get_db().cursor().execute("""SELECT * FROM authors WHERE author_id = ?""", (id, )).fetchone()
        return author

    @classmethod
    def _instantiate_table(cls) -> None:
        SQLiteDatabaseHandler.get_db().cursor().execute("""CREATE TABLE IF NOT EXISTS authors(
                                                        author_id INTEGER PRIMARY KEY NOT NULL,
                                                        author_first_name TEXT,
                                                        author_last_name TEXT,
                                                        author_pseudonym TEXT)""")