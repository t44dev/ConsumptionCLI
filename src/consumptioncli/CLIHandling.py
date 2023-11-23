# General Imports
from argparse import ArgumentError, Namespace
from datetime import datetime
from typing import Type, TypeVar, Callable
from abc import abstractmethod, ABC
from tabulate import tabulate

# Consumption Imports
from consumptionbackend.Consumable import Consumable, Status

T = TypeVar("T")


def request_input(name: str, default: T = None, validator: Callable = None) -> T:
    if default is not None:
        request_string = f"Provide a {name} (Default : {default}): "
    else:
        request_string = f"Provide a {name}: "
    value = input(request_string).strip()
    if default:
        value = value if len(value) else default
    if validator is not None:
        while not validator(value):
            value = input(request_string).strip()
            if default:
                value = value if len(value) else default
    return value


class CLIHandler(ABC):

    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")

    @classmethod
    def handle(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An entity type must be seleced. e.g. cons consumable")

    @classmethod
    @abstractmethod
    def cli_new(cls, args: Namespace) -> str:
        pass

    @classmethod
    @abstractmethod
    def cli_list(cls, args: Namespace) -> str:
        pass

    @classmethod
    @abstractmethod
    def cli_update(cls, args: Namespace) -> str:
        pass

    @classmethod
    @abstractmethod
    def cli_delete(cls, args: Namespace) -> str:
        pass

    @classmethod
    @abstractmethod
    def no_action(cls, args: Namespace) -> str:
        pass

    # @classmethod
    # def get_list_ents(cls, ent : Type[T], subdict : dict, **kwargs) -> list[T]:
        # sortkey = kwargs["order"]
        # # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
        # return sorted(ent.find(**subdict), key = lambda a : (getattr(a, sortkey) is not None, getattr(a, sortkey)), reverse=kwargs["reverse"])

    # @classmethod
    # def get_ent(cls, ent : Type[T], subdict : dict) -> T:
        # if "id" not in subdict:
        # raise ArgumentError(None, f"No {ent.__name__} ID specified.")
        # try:
        # instance = ent.get(subdict["id"])
        # except TypeError:
        # raise ArgumentError(None, f"Author with ID {subdict['id']} not found.")
        # return instance

    # @classmethod
    # @abstractmethod
    # def cli_list(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        # raise ArgumentError(None, "Please specify an entity to list.")

    # @classmethod
    # @abstractmethod
    # def _cli_tabulate(cls, instances : list[DatabaseEntity]) -> str:
        # pass

    # @classmethod
    # def cli_update(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        # instance = cls.get_ent(ent, subdict)
        # for key, value in subdict.items():
        # setattr(instance, key, value)
        # instance.save()
        # return cls._cli_tabulate([instance])

    # @classmethod
    # def cli_delete(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        # if "id" not in subdict:
        # raise ArgumentError(None, f"No {ent.__name__} ID specified.")
        # ent.delete(subdict["id"])
        # return f"{ent.__name__} deleted."

    # @classmethod
    # def cli_create(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs) -> str:
        # try:
        # instance = ent(**subdict)
        # except ValueError as e:
        # raise ArgumentError(None, str(e))
        # except TypeError:
        # raise ArgumentError(None, "Could not instanitate specified entity.")
        # instance.save()
        # return cls._cli_tabulate([instance])

    # @classmethod
    # def cli_noaction(cls, ent : Type[DatabaseEntity], subdict : dict, **kwargs):
        # raise ArgumentError(None, "No action specified.")


class ConsumableHandler(CLIHandler):

    @classmethod
    def handle(cls, args: Namespace) -> str:
        match args.mode:
            case "new":
                return cls.cli_new(args)
            case _:
                return cls.no_action(args)

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        new = getattr(args, "new", Namespace())
        # Prepare Arguments and Create
        mandatory_args = ["name", "type"]
        for arg in mandatory_args:
            if arg not in new:
                value = request_input(arg)
                setattr(new, arg, value)
        cls._prepare_args(args, new)
        # Get necessary args
        consumable = Consumable.new(**vars(new))
        # Create String
        return cls._tabulate_consumable([consumable], args.date_format)

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        pass

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons consuamble new")

    @classmethod
    def _tabulate_consumable(cls, instances: list[Consumable], date_format: str = r"%Y/%m/%d") -> str:
        instances = [[row+1, i.id, i.type, i.name, i.parts, i.rating, i.completions, i.status.name,
                      datetime.fromtimestamp(i.start_date).strftime(
                          date_format) if i.start_date else i.start_date,
                      datetime.fromtimestamp(i.end_date).strftime(date_format) if i.end_date else i.end_date] for row, i in enumerate(instances)]
        return tabulate(instances, headers=["#", "ID", "Type", "Name", "Parts", "Rating", "Completions", "Status", "Started", "Completed"])

    @classmethod
    def _prepare_args(cls, args: Namespace, values: Namespace) -> None:
        # Date
        date_format = args.date_format
        if "start_date" in values:
            values.start_date = datetime.strptime(
                values.start_date, date_format).timestamp()
        if "end_date" in values:
            values.end_date = datetime.strptime(
                values.end_date, date_format).timestamp()
        # Status
        if "status" in values:
            values.status = Status[values.status]

    # @classmethod
    # def add_staff(cls, ent : Consumable, staff_list : list[str]):
        # if len(staff_list) % 2 != 0:
            # raise ArgumentError(None, "Staff arguments must be passed in id, Role pairs. e.g. -S 2 Author 3 Illustrator.")
        # try:
            # staff_list = [(int(staff_list[i]), staff_list[i+1]) for i in range(0, len(staff_list), 2)]
            # for staff in staff_list:
            # ent.toggle_staff(staff[0], staff[1])
        # except ValueError:
            # raise ArgumentError(None, "Staff arguments must be passed in id, Role pairs. e.g. -S 2 Author 3 Illustrator.")
        # except TypeError:
            # raise ArgumentError(None, "Staff id must exist within the database.")

    # @classmethod
    # def _handle_type_conversion(cls, subdict : dict, date_format : str) -> None:
        # if "start_date" in subdict:
            # if subdict["start_date"] == "None":
            # subdict["start_date"] = None
            # else:
            # subdict["start_date"] = datetime.strptime(subdict["start_date"], date_format).timestamp()
        # if "end_date" in subdict:
            # if subdict["end_date"] == "None":
            # subdict["end_date"] = None
            # else:
            # subdict["end_date"] = datetime.strptime(subdict["end_date"], date_format).timestamp()
        # if "status" in subdict:
            # subdict["status"] = Status[subdict["status"]]

    # @classmethod
    # def cli_list(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        # try:
            # cls._handle_type_conversion(subdict, kwargs["date_format"])
        # except ValueError as e:
            # raise ArgumentError(None, str(e))
        # instances = cls.get_list_ents(ent, subdict, **kwargs)
        # return cls._cli_tabulate(instances, kwargs["date_format"]) + f"\n{len(instances)} Results..."

    # @classmethod
    # def cli_update(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        # instance = cls.get_ent(ent, subdict)
        # # Handle increment
        # if kwargs["increment"]:
            # instance.status = Status.IN_PROGRESS
            # inc_major_parts = subdict.pop("major_parts") if "major_parts" in subdict else 0
            # inc_minor_parts = subdict.pop("minor_parts") if "minor_parts" in subdict else 0
            # # Only increment parts on first completion
            # if instance.completions == 0:
            # subdict["major_parts"] = instance.major_parts + inc_major_parts
            # subdict["minor_parts"] = instance.minor_parts + inc_minor_parts
        # # Handle finish
        # if kwargs["finish"]:
            # instance.status = Status.COMPLETED
            # if instance.completions == 0:
            # instance.end_date = datetime.utcnow().timestamp()
            # instance.completions = instance.completions + 1
        # # Convert dates to float and other type conversions
        # try:
            # cls._handle_type_conversion(subdict, kwargs["date_format"])
        # except ValueError as e:
            # raise ArgumentError(None, str(e))
        # # Update other values
        # for key, value in subdict.items():
            # setattr(instance, key, value)
        # instance.save()
        # cls.add_staff(instance, kwargs["staff"])
        # return cls._cli_tabulate([instance], kwargs["date_format"])

    # @classmethod
    # def cli_delete(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        # try:
            # cls._handle_type_conversion(subdict, kwargs["date_format"])
        # except ValueError as e:
            # raise ArgumentError(None, str(e))
        # return super().cli_delete(ent, subdict, **kwargs)

    # @classmethod
    # def cli_create(cls, ent: Type[Consumable], subdict: dict, **kwargs) -> str:
        # try:
            # cls._handle_type_conversion(subdict, kwargs["date_format"])
        # except ValueError as e:
            # raise ArgumentError(None, str(e))
        # try:
            # instance = ent(**subdict)
        # except ValueError as e:
            # raise ArgumentError(None, str(e))
        # except TypeError as e:
            # raise ArgumentError(None, "Could not instanitate specified entity.")
        # instance.save()
        # cls.add_staff(instance, kwargs["staff"])
        # return cls._cli_tabulate([instance], kwargs["date_format"])


class SeriesHandler(CLIHandler):

    @classmethod
    def handle(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        pass

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        pass


class PersonnelHandler(CLIHandler):

    @classmethod
    def handle(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        pass

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        pass

    # @classmethod
    # def cli_list(cls, ent: Type[Staff], subdict: dict, **kwargs) -> str:
        # instances = cls.get_list_ents(ent, subdict, **kwargs)
        # return cls._cli_tabulate(instances) + f"\n{len(instances)} Results..."

    # @classmethod
    # def _cli_tabulate(cls, instances : list[Staff]):
        # instances = [[row+1, i.id, i.pseudonym, i.first_name, i.last_name] for row, i in enumerate(instances)]
        # return tabulate(instances, headers=["#", "ID", "Pseudonym", "First Name", "Last Name"])
