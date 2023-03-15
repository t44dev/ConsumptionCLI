# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union

# Package Imports
from .DatabaseEntity import DatabaseEntity

class Creator(DatabaseEntity):

    def __init__(self, id : int, first_name : Union[str, None], last_name : Union[str, None]):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name

class Author(Creator):

    def __init__(self, id: int, first_name: Union[str, None], last_name: Union[str, None], pseudonym : Union[str, None]):
        super().__init__(id, first_name, last_name)
        self.pseudonym = pseudonym

    def save() -> None:
        pass

    def find(cls, *args, **kwargs) -> list[Author]:
        pass

    def get(cls, id : int) -> Author:
        pass