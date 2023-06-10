# General Imports
from argparse import ArgumentError
from datetime import datetime
from typing import Type, TypeVar
from abc import abstractmethod, ABC
from tabulate import tabulate

# Package Imports
from consumption.consumption_backend.Database import DatabaseEntity
from consumption.consumption_backend.Consumable import Consumable, Status
from consumption.consumption_backend.Staff import Staff

T = TypeVar("T", DatabaseEntity, Consumable, Staff)

class CLIHandler(ABC):
    
    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")
    
    @classmethod
    def handle(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        match kwargs:
            case {"list" : True}:
                return cls.cli_list(ent, subdict, **kwargs)
            case {"update" : True}:
                return cls.cli_update(ent, subdict, **kwargs)
            case {"delete" : True}:
                return cls.cli_delete(ent, subdict, **kwargs)
            case {"create" : True}:
                return cls.cli_create(ent, subdict, **kwargs)
            case _:
                return cls.cli_noaction(ent, subdict, **kwargs)

    @classmethod
    def get_list_ents(cls, ent : Type[T], subdict : dict, **kwargs) -> list[T]:
        sortkey =  kwargs["order"]
        # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
        return sorted(ent.find(**subdict), key = lambda a : (getattr(a, sortkey) is not None, getattr(a, sortkey)), reverse=kwargs["reverse"])

    @classmethod
    def get_ent(cls, ent : Type[T], subdict : dict) -> T:
        if "id" not in subdict:
            raise ArgumentError(None, f"No {ent.__name__} ID specified.")
        try:
            instance = ent.get(subdict["id"])
        except TypeError:
            raise ArgumentError(None, f"Author with ID {subdict['id']} not found.")
        return instance

    @classmethod
    @abstractmethod
    def cli_list(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        raise ArgumentError(None, "Please specify an entity to list.")

    @classmethod
    def cli_update(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        instance = cls.get_ent(ent, subdict)
        for key, value in subdict.items():
            setattr(instance, key, value)
        instance.save()
        return str(instance)

    @classmethod
    def cli_delete(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        if "id" not in subdict:
            raise ArgumentError(None, f"No {ent.__name__} ID specified.")
        ent.delete(subdict["id"])
        return f"{ent.__name__} deleted."

    @classmethod
    def cli_create(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        try:
            instance = ent(**subdict)
        except TypeError:
            raise ArgumentError(None, "Could not instanitate specified entity.")
        instance.save()
        return str(instance)
    
    @classmethod
    def cli_noaction(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs):
        raise ArgumentError(None, "No action specified.")

class ConsumableHandler(CLIHandler):
    
    @classmethod
    def add_staff(cls, ent : Consumable, staff_list : list[str]):
        if len(staff_list) % 2 != 0:
            raise ArgumentError(None, "Staff arguments must be passed in id, Role pairs. e.g. -S 2 Author 3 Illustrator.")
        try:
            staff_list = [(int(staff_list[i]), staff_list[i+1]) for i in range(0, len(staff_list), 2)]
            for staff in staff_list:
                ent.toggle_staff(staff[0], staff[1])
        except ValueError:
            raise ArgumentError(None, "Staff arguments must be passed in id, Role pairs. e.g. -S 2 Author 3 Illustrator.")
        except TypeError:
            raise ArgumentError(None, "Staff id must exist within the database.")
        
    @classmethod
    def _handle_type_conversion(cls, subdict : dict, date_format : str) -> None:
        if "start_date" in subdict:
            subdict["start_date"] = datetime.strptime(subdict["start_date"], date_format).timestamp()
        if "end_date" in subdict:
            subdict["end_date"] = datetime.strptime(subdict["end_date"], date_format).timestamp()
        if "status" in subdict:
            subdict["status"] = Status[subdict["status"]]

    @classmethod
    def cli_list(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        try:
            cls._handle_type_conversion(subdict, kwargs["date_format"])
        except ValueError as e:
            raise ArgumentError(None, str(e))
        instances = cls.get_list_ents(ent, subdict, **kwargs)
        date_format = kwargs["date_format"]
        instances = [[i.id, i.name, i.major_parts, i.minor_parts, i.rating, i.completions, i.status.name,
                      datetime.fromtimestamp(i.start_date).strftime(date_format) if i.start_date else i.start_date, 
                      datetime.fromtimestamp(i.end_date).strftime(date_format) if i.end_date else i.end_date] for i in instances]
        return str(tabulate(instances, headers=["#", "Name", ent.MAJOR_PART_NAME, ent.MINOR_PART_NAME, "Rating", "Completions", "Status", "Started", "Completed"]))

    @classmethod
    def cli_update(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        instance = cls.get_ent(ent, subdict)
        # Add Volumes, Chapters, set End Date
        inc_major_parts = subdict.pop("major_parts") if "major_parts" in subdict else 0
        inc_minor_parts = subdict.pop("minor_parts") if "minor_parts" in subdict else 0
        # Only update if first completion
        if instance.completions == 0:
            if kwargs["finish"]:
                instance.end_date = datetime.utcnow().timestamp()
                instance.completions = instance.completions + 1
            subdict["major_parts"] = instance.major_parts + inc_major_parts
            subdict["minor_parts"] = instance.minor_parts + inc_minor_parts
        # Otherwise only update completions on finish flag
        else:
            if kwargs["finish"]:
                instance.completions = instance.completions + 1
        # Convert dates to float and other type conversions
        try:
            cls._handle_type_conversion(subdict, kwargs["date_format"])
        except ValueError as e:
            raise ArgumentError(None, str(e))
        # Update other values
        for key, value in subdict.items():
            setattr(instance, key, value)
        instance.save()
        cls.add_staff(instance, kwargs["staff"])
        return str(instance)
    
    @classmethod
    def cli_delete(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        try:
            cls._handle_type_conversion(subdict, kwargs["date_format"])
        except ValueError as e:
            raise ArgumentError(None, str(e)) 
        return super().cli_delete(ent, subdict, **kwargs)

    @classmethod
    def cli_create(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        try:
            cls._handle_type_conversion(subdict, kwargs["date_format"])
        except ValueError as e:
            raise ArgumentError(None, str(e))
        try:
            instance = ent(**subdict)
        except TypeError:
            raise ArgumentError(None, "Could not instanitate specified entity.")
        instance.save()
        cls.add_staff(instance, kwargs["staff"])
        return str(instance)

class StaffHandler(CLIHandler):

    @classmethod
    def cli_list(cls, ent: Type[Staff], subdict: dict, **kwargs) -> str:
        staff = cls.get_list_ents(ent, subdict, **kwargs)
        staff = [[i.id, i.pseudonym, i.first_name, i.last_name] for i in staff]
        return str(tabulate(staff, headers=["#", "Pseudonym", "First Name", "Last Name"]))