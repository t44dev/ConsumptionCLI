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
        return f"{self.__class__.__name__} | {self.first_name} {self.last_name} with ID: {self.id}"

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
        # Insert
        if self.id is None:
            id = db.cursor().execute("""INSERT INTO authors(
                                id,
                                first_name,
                                last_name,
                                pseudonym)
                                VALUES(?,?,?,?)""", (None, self.first_name, self.last_name, self.pseudonym)).lastrowid
            self.id = id
        # Update
        else:
            db.cursor().execute("""UPDATE authors
                    SET first_name = ?, last_name = ?, pseudonym = ?
                    WHERE id = ?""", (self.first_name, self.last_name, self.pseudonym, self.id))
        db.commit()
        return self.id

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
        author_data = SQLiteDatabaseHandler.get_db().cursor().execute("""SELECT * FROM authors WHERE id = ?""", (id, )).fetchone()
        return Author(*author_data)
    
    @classmethod
    def delete(cls, id : int) -> None:
        cls._instantiate_table()
        db = SQLiteDatabaseHandler.get_db()
        db.cursor().execute("DELETE FROM authors WHERE id = ?", (id, ))
        db.commit()

    @classmethod
    def _instantiate_table(cls) -> None:
        SQLiteDatabaseHandler.get_db().cursor().execute("""CREATE TABLE IF NOT EXISTS authors(
                                                        id INTEGER PRIMARY KEY NOT NULL,
                                                        first_name TEXT,
                                                        last_name TEXT,
                                                        pseudonym TEXT)""")
    
    def __eq__(self, other: Author) -> bool:
        return super().__eq__(other) and self.pseudonym == other.pseudonym