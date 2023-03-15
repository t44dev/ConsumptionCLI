# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union
from datetime import datetime

# Package Imports
from DatabaseEntity import DatabaseEntity
from Creators import Author

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
    
    def save() -> None:
        pass

    def find(cls, *args, **kwargs) -> list[Novel]:
        pass

    def get(cls, id : int) -> Novel:
        pass

if __name__ == "__main__":
    c = Novel(123, "!233", 5, 0, 23, 2.5, 17828123, 1298123, None)
    print(c)