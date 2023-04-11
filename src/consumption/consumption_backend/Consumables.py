# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union
from datetime import datetime

# Package Imports
from .Database import DatabaseEntity, SQLiteDatabaseHandler
from .Creators import Author

class Consumable(DatabaseEntity):
    
    def __init__(self, \
                 id : Union[int, None] = None, \
                 name : str = "", \
                 major_parts : int = 0, \
                 minor_parts : int = 0, \
                 completions : int = 0, \
                 rating : Union[float, None] = None, \
                 start_date : float = datetime.utcnow().timestamp(), \
                 end_date : Union[float, None] = None) -> None:
        super().__init__(id)
        self.name = name
        self.major_parts = major_parts
        self.minor_parts = minor_parts
        self.completions = completions
        self.rating = rating
        # Using posix-timestamp
        self.start_date = datetime.fromtimestamp(start_date)
        self.end_date = datetime.fromtimestamp(end_date) if end_date else end_date
    
    def __eq__(self, other: Consumable) -> bool:
        return super().__eq__(other) \
            and self.name == other.name \
            and self.major_parts == other.major_parts \
            and self.minor_parts == other.minor_parts \
            and self.completions == other.completions \
            and self.rating == other.rating \
            and self.start_date == other.start_date \
            and self.end_date == other.end_date
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__} | {self.name} with ID: {self.id}"

class Novel(Consumable):

    MAJOR_PART_NAME = "Volume"
    MINOR_PART_NAME = "Chapter"

    def __init__(self, 
                 id : Union[int, None] = None, \
                 name : str = "", \
                 major_parts : int = 0, \
                 minor_parts : int = 0, \
                 completions : int = 0, \
                 rating : Union[float, None] = None, \
                 start_date : float = datetime.utcnow().timestamp(), \
                 end_date : Union[float, None] = None, \
                 author : Union[Author, None] = None) -> None:
        super().__init__(id, name, major_parts, minor_parts, completions, rating, start_date, end_date)
        self.author = author
    
    def save(self) -> int:
        self._instantiate_table()
        db = SQLiteDatabaseHandler.get_db()
        if self.id is None:
            # Insert
            id = db.cursor().execute("""INSERT INTO novels(
                                id,
                                name,
                                major_parts,
                                minor_parts,
                                completions,
                                rating,
                                start_date,
                                end_date,
                                author_id)
                                VALUES(?,?,?,?,?,?,?,?,?)""", 
                                (None, 
                                self.name, 
                                self.major_parts, 
                                self.minor_parts, 
                                self.completions, 
                                self.rating,
                                self.start_date.timestamp(),
                                self.end_date.timestamp() if self.end_date else self.end_date,
                                self.author.id if self.author else self.author)).lastrowid
            self.id = id
        # Update
        else:
            db.cursor().execute("""UPDATE novels
                                SET name = ?, major_parts = ?, minor_parts = ?, completions = ?, rating = ?, start_date = ?, end_date = ?, author_id = ?
                                WHERE id = ?""", 
                                (self.name, 
                                self.major_parts, 
                                self.minor_parts, 
                                self.completions, 
                                self.rating,
                                self.start_date.timestamp(),
                                self.end_date.timestamp() if self.end_date else self.end_date,
                                self.author.id if self.author else self.author,
                                self.id))
        db.commit()
        return self.id

    @classmethod
    def find(cls, *args, **kwargs) -> list[Novel]:
        cls._instantiate_table()
        params = tuple(kwargs[key] for key in kwargs.keys())
        keys = list(kwargs.keys())
        sql = "SELECT * FROM novels"
        if params:
            sql += f" WHERE {keys[0]} = ?"
            for i in range(1, len(params)):
                sql += f" AND {keys[i]} = ?"
        novels = SQLiteDatabaseHandler.get_db().cursor().execute(sql, params).fetchall()
        return [Novel(*novel_data) for novel_data in novels]

    @classmethod    
    def get(cls, id : int) -> Novel:
        cls._instantiate_table()
        novel_data = SQLiteDatabaseHandler.get_db().cursor().execute("""SELECT * FROM novels WHERE nov_id = ?""", (id, )).fetchone()
        return Novel(*novel_data)

    @classmethod
    def delete(cls, id : int) -> None:
        cls._instantiate_table()
        SQLiteDatabaseHandler.get_db().cursor().execute("DELETE FROM novels WHERE id = ?", (id, ))

    @classmethod
    def _instantiate_table(cls) -> None:
        cur = SQLiteDatabaseHandler.get_db().cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS novels(
                    id INTEGER PRIMARY KEY NOT NULL UNIQUE DEFAULT 0,
                    name TEXT NOT NULL,
                    major_parts INTEGER NOT NULL DEFAULT 0,
                    minor_parts INTEGER NOT NULL DEFAULT 0,
                    completions INTEGER NOT NULL DEFAULT 0,
                    rating REAL,
                    start_date REAL NOT NULL,
                    end_date REAL,
                    author_id INTEGER,
                    FOREIGN KEY (author_id)
                        REFERENCES authors (author_id)
                        ON DELETE SET NULL
                        ON UPDATE NO ACTION)""")
        
    def __eq__(self, other: Novel) -> bool:
        return super().__eq__(other) and self.author == other.author