# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union

# Package Imports
from .Database import DatabaseEntity

class Staff(DatabaseEntity):

    DATABASE_NAME = "staff"

    def __init__(self, \
                id : Union[int, None] = None, \
                first_name : Union[str, None] = None, \
                last_name : Union[str, None] = None, \
                pseudonym : Union[str, None] = None, \
                role : Union[str, None] = None) -> None:
        super().__init__(Staff.DATABASE_NAME, id)
        self.first_name = first_name
        self.last_name = last_name
        self.pseudonym = pseudonym
        self.role = role
    
    def save(self) -> int:
        return super().save(first_name=self.first_name, \
                            last_name=self.last_name, \
                            pseudonym=self.pseudonym)
    
    @classmethod
    def find(cls, **kwargs) -> list[Staff]:
        staff = cls.db_handler.find_many(cls.DATABASE_NAME, **kwargs)
        return [Staff(*staff_data) for staff_data in staff]
    
    @classmethod
    def get(cls, id: int) -> Staff:
        staff_data = cls.db_handler.find_one(cls.DATABASE_NAME, id=id)
        return Staff(*staff_data)
    
    @classmethod
    def delete(cls, id: int) -> bool:
        return super().delete(cls.DATABASE_NAME, id)

    def __eq__(self, other: Staff) -> bool:
        return super().__eq__(other) and self.first_name == other.first_name and self.last_name == other.last_name and self.pseudonym == other.pseudonym
    
    def __str__(self) -> str:
        # TODO: Make this be in the format First "Pseudonym" Last, omitting NoneTypes
        return f"{self.__class__.__name__} | {self.first_name} {self.last_name} with ID: {self.id}"