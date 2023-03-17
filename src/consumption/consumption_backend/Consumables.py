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
    
    def __eq__(self, other: Consumable) -> bool:
        return super().__eq__(other) \
            and self.name == other.name \
            and self.major_parts == other.major_parts \
            and self.minor_parts == other.minor_parts \
            and self.completions == other.completions \
            and self.rating == other.rating \
            and self.start_date == other.start_date \
            and self.end_date == other.end_date

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
        db = SQLiteDatabaseHandler.get_db()
        id = db.cursor().execute("""INSERT INTO novels(
                            nov_id,
                            author_id,
                            nov_name,
                            nov_major_parts,
                            nov_minor_parts,
                            nov_completions,
                            nov_rating,
                            nov_start_date,
                            nov_end_date)
                            VALUES(?,?,?,?,?,?,?,?,?)""", 
                            (None, 
                             self.author.id, 
                             self.name, 
                             self.major_parts, 
                             self.minor_parts, 
                             self.completions, 
                             self.rating, 
                             self.start_date.timestamp(),
                             self.end_date.timestamp())).lastrowid
        db.commit()
        return id

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
                    nov_start_date REAL NOT NULL,
                    nov_end_date REAL,
                    FOREIGN KEY (author_id)
                        REFERENCES authors (author_id)
                        ON DELETE SET NULL
                        ON UPDATE NO ACTION)""")
        
    def __eq__(self, other: Novel) -> bool:
        return super().__eq__(other) and self.author == other.author