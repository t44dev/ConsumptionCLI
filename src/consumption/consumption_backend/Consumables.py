# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union
from datetime import datetime

from consumption.consumption_backend.Database import DatabaseEntity

# Package Imports
from .Database import DatabaseEntity

class Consumable(DatabaseEntity):
    
    def __init__(self, \
                database : str, \
                id : Union[int, None] = None, \
                name : str = "", \
                major_parts : int = 0, \
                minor_parts : int = 0, \
                completions : int = 0, \
                rating : Union[float, None] = None, \
                start_date : float = datetime.utcnow().timestamp(), \
                end_date : Union[float, None] = None) -> None:
        super().__init__(database, id)
        self.name = name
        self.major_parts = major_parts
        self.minor_parts = minor_parts
        self.completions = completions
        self.rating = rating
        # Using posix-timestamp
        self.start_date = datetime.fromtimestamp(start_date)
        self.end_date = datetime.fromtimestamp(end_date) if end_date else end_date
    
    def save(self, **kwargs) -> int:
        start_date = self.start_date.timestamp()
        end_date = self.end_date.timestamp() if self.end_date else None
        return super().save(name=self.name, \
                            major_parts=self.major_parts, \
                            minor_parts=self.minor_parts, \
                            completions=self.completions, \
                            rating=self.rating, \
                            start_date=start_date, \
                            end_date=end_date, \
                            **kwargs)

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
    DATABASE_NAME = "novels"

    def __init__(self, 
                id : Union[int, None] = None, \
                name : str = "", \
                major_parts : int = 0, \
                minor_parts : int = 0, \
                completions : int = 0, \
                rating : Union[float, None] = None, \
                start_date : float = datetime.utcnow().timestamp(), \
                end_date : Union[float, None] = None) -> None:
        super().__init__(Novel.DATABASE_NAME, id, name, major_parts, minor_parts, completions, rating, start_date, end_date)

    @classmethod
    def find(cls, **kwargs) -> list[Novel]:
        novels = cls.db_handler.find_many(cls.DATABASE_NAME, **kwargs)
        return [Novel(*novel_data) for novel_data in novels]

    @classmethod    
    def get(cls, id : int) -> Novel:
        novel_data = cls.db_handler.find_one(cls.DATABASE_NAME, id=id)
        return Novel(*novel_data)

    @classmethod
    def delete(cls, id : int) -> None:
        super().delete("novels", id)