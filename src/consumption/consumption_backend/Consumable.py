# General Imports
from __future__ import annotations # For self-referential type-hints
from typing import Union
from datetime import datetime
from enum import Enum

# Package Imports
from .Database import DatabaseEntity
from .Staff import Staff

class Status(Enum):
    PLANNING = 0
    IN_PROGRESS = 1
    ON_HOLD = 2
    DROPPED = 3
    COMPLETED = 4

class Consumable(DatabaseEntity):
    
    MAJOR_PART_NAME = "Major"
    MINOR_PART_NAME = "Minor"
    DB_NAME = "consumables"
    DB_STAFF_MAPPING_NAME = "consumable_staff"

    def __init__(self, \
                id : Union[int, None] = None, \
                name : str = "", \
                type : str = "", \
                status : Union[Status, int] = Status.IN_PROGRESS, \
                major_parts : int = 0, \
                minor_parts : int = 0, \
                completions : int = 0, \
                rating : Union[float, None] = None, \
                start_date : float = None, \
                end_date : Union[float, None] = None, \
                staff : list[Staff] = None) -> None:
        super().__init__(self.DB_NAME, id)
        self.name = name
        self.type = type
        self.status = status if isinstance(status, Status) else Status(status)
        self.major_parts = major_parts
        self.minor_parts = minor_parts
        self.completions = completions
        self.rating = rating
        self.staff = [] if staff is None else staff
        # Using posix-timestamp
        self.start_date = start_date if start_date else datetime.utcnow().timestamp()
        self.end_date = end_date
        if self.id is not None:
            self.populate_staff()
    
    def populate_staff(self, **kwargs) -> None:
        mappings = self.db_handler.find_many(self.DB_STAFF_MAPPING_NAME, **kwargs)
        for staff_id, _, role in mappings:
            staff = Staff.get(staff_id)
            staff.role = role
            self.staff.append(staff)

    def toggle_staff(self, id : int, role : str) -> None:
        for i, staff in enumerate(self.staff):
            if staff.id == id and staff.role == role:
                # Remove Staff
                self.staff.pop(i)
                self.db_handler.delete(self.DB_STAFF_MAPPING_NAME, consumable_id=self.id, staff_id=id, role=role)
                return
        # Else Add Staff
        staff = Staff.get(id)
        staff.role = role
        self.staff.append(staff)
        self.db_handler.insert(self.DB_STAFF_MAPPING_NAME, consumable_id=self.id, staff_id=id, role=role)

    @classmethod
    def find(cls, **kwargs) -> list[Consumable]:
        consumables = cls.db_handler.find_many(cls.DB_NAME, **kwargs)
        return [Consumable(*data) for data in consumables]

    @classmethod    
    def get(cls, id : int) -> Consumable:
        data = cls.db_handler.find_one(cls.DB_NAME, id=id)
        return Consumable(*data)

    @classmethod
    def delete(cls, id : int) -> None:
        super().delete(cls.DB_NAME, id)

    def save(self, **kwargs) -> int:
        return super().save(name=self.name, \
                            type=self.type, \
                            status=self.status.value, \
                            major_parts=self.major_parts, \
                            minor_parts=self.minor_parts, \
                            completions=self.completions, \
                            rating=self.rating, \
                            start_date=self.start_date, \
                            end_date=self.end_date, \
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