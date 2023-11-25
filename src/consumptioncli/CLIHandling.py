# General Imports
from argparse import ArgumentError, Namespace
from datetime import datetime
from collections.abc import Sequence
from abc import abstractmethod, ABC
from tabulate import tabulate
from sqlite3 import IntegrityError

# Consumption Imports
from consumptionbackend.Consumable import Consumable
from consumptionbackend.Status import Status
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
from .utils import sort_by, request_input, confirm_action


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


class ConsumableHandler(CLIHandler):

    ORDER_LIST = ["id", "type", "name", "parts", "rating",
                  "completions", "status", "start_date", "end_date"]

    @classmethod
    def handle(cls, args: Namespace) -> str:
        match getattr(args, "mode"):
            case "new":
                return cls.cli_new(args)
            case "list":
                return cls.cli_list(args)
            case "update":
                return cls.cli_update(args)
            case "delete":
                return cls.cli_delete(args)
            case "tag":
                return cls.cli_tag(args)
            case "untag":
                return cls.cli_untag(args)
            case "set_series":
                return cls.cli_series(args)
            case "personnel":
                raise ArgumentError(
                    None, "Must select an action. e.g. cons consumable personnel add --name John")
            case "add_personnel":
                return cls.cli_add_personnel(args)
            case "remove_personnel":
                return cls.cli_remove_personnel(args)
            case _:
                return cls.no_action(args)

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        new = getattr(args, "new", Namespace())
        # Get mandatory args
        mandatory_args = ["name", "type"]
        for arg in mandatory_args:
            if arg not in new:
                value = request_input(arg)
                setattr(new, arg, value)
        # Prepare Arguments and Create
        cls._prepare_args(args, new)
        consumable = Consumable.new(**vars(new))
        # Create String
        return cls._tabulate([consumable], getattr(args, "date_format"))

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Create String
        consumables = Consumable.find(**vars(where))
        # Ordering
        consumables = sort_by(consumables, getattr(
            args, "order"), getattr(args, "reverse"))
        results = len(consumables)
        if results > 0:
            return cls._tabulate(consumables, getattr(args, "date_format")) + f"\n{results} Result(s)..."
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None, "Values to set must be non-empty. e.g. cons consumable update set --name A")
        # Prepare Arguments
        cls._prepare_args(args, where_mapping)
        cls._prepare_args(args, set_mapping)
        # Find
        consumables = Consumable.find(**vars(where_mapping))
        # Update
        updated_consumables = []
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        elif len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"update of {str(consumable)}"):
                    updated_consumables.append(
                        consumable.update_self(vars(set_mapping)))
        else:
            updated_consumables.append(
                consumables[0].update_self(vars(set_mapping)))
        # Create String
        if len(updated_consumables) > 0:
            return cls._tabulate(updated_consumables, getattr(args, "date_format"))
        else:
            return "No Consumable(s) updated."

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Find
        consumables = Consumable.find(**vars(where))
        # Delete
        deleted = 0
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        elif len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"deletion of {str(consumable)}"):
                    consumable.delete_self()
                    deleted += 1
        else:
            consumables[0].delete_self()
            deleted += 1
        # Create String
        return f"{deleted} Consumables deleted."

    @classmethod
    def cli_start(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_continue(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_finish(cls, args: Namespace) -> str:
        pass

    @classmethod
    def cli_tag(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        if "tag" in args:
            tag = getattr(args, "tag")
        else:
            tag = request_input("tag")
        # Find
        consumables = Consumable.find(**vars(where))
        # Tag
        tagged = 0
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        elif len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"tagging of {str(consumable)} with '{tag}'"):
                    if consumable.add_tag(tag):
                        tagged += 1
        else:
            consumables[0].add_tag(tag)
            tagged += 1
        # Create string
        return f"{tagged} Consumable(s) tagged."

    @classmethod
    def cli_untag(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        if "tag" in args:
            tag = getattr(args, "tag")
        else:
            tag = request_input("tag")
        # Find
        consumables = Consumable.find(**vars(where))
        # Untag
        untagged = 0
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        elif len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"removal of tag '{tag}' from {str(consumable)}"):
                    if consumable.remove_tag(tag):
                        untagged += 1
        else:
            consumables[0].remove_tag(tag)
            untagged += 1
        # Create string
        return f"{untagged} Consumable(s) untagged."

    @classmethod
    def cli_series(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        series_where = getattr(args, "series", Namespace())
        if len(vars(series_where)) == 0:
            raise ArgumentError(
                None, "Series to set must be specified e.g. cons consumable series set --name S")
        # Get Series
        series = Series.find(**vars(series_where))
        set_series = None
        if len(series) == 0:
            return "No Series matching conditions."
        elif len(series) > 1:
            for ser in series:
                if confirm_action(f"usage of {str(ser)} as Series to set"):
                    set_series = ser
                    break
            if set_series is None:
                return "No Series selected."
        else:
            set_series = series[0]
        # Set Series
        consumables = Consumable.find(**vars(where))
        consumables_altered = 0
        if len(consumables) == 0:
            return "No Consumables matching conditions."
        elif len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"setting Series of {str(consumable)} to {str(set_series)}"):
                    consumable.set_series(set_series)
                    consumables_altered += 1
        else:
            consumables[0].set_series(set_series)
            consumables_altered += 1
        return f"Series for {consumables_altered} Consumables updated"

    @classmethod
    def cli_add_personnel(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        personnel_where = getattr(args, "personnel", Namespace())
        if "role" in args:
            role = getattr(args, "role")
        else:
            role = request_input("Personnel role")
        # Get Personnel/Consumables
        personnel = Personnel.find(**vars(personnel_where))
        selected_personnel = []
        consumables = Consumable.find(**vars(where))
        consumables_altered = 0
        if len(personnel) == 0:
            return "No Personnel matching conditions."
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        # Confirmations
        if len(personnel) > 1:
            for pers in personnel:
                if confirm_action(f"selection of {str(pers)}"):
                    pers.role = role
                    selected_personnel.append(pers)
        else:
            personnel[0].role = role
            selected_personnel = personnel
        # Add to Consumables
        if len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"adding selected Personnel to {str(consumable)} as '{role}'"):
                    for pers_add in selected_personnel:
                        if consumable.add_personnel(pers_add):
                            consumables_altered += 1
        else:
            for pers_add in selected_personnel:
                if consumables[0].add_personnel(pers_add):
                    consumables_altered += 1
        return f"{len(selected_personnel)} Personnel added to {consumables_altered} Consumable(s) as '{role}'."

    @classmethod
    def cli_remove_personnel(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        personnel_where = getattr(args, "personnel", Namespace())
        if "role" in args:
            role = getattr(args, "role")
        else:
            role = request_input("Personnel role")
        # Get Personnel/Consumables
        personnel = Personnel.find(**vars(personnel_where))
        selected_personnel = []
        consumables = Consumable.find(**vars(where))
        consumables_altered = 0
        if len(personnel) == 0:
            return "No Personnel matching conditions."
        if len(consumables) == 0:
            return "No Consumables matching where conditions."
        # Confirmations
        if len(personnel) > 1:
            for pers in personnel:
                if confirm_action(f"selection of {str(pers)}"):
                    pers.role = role
                    selected_personnel.append(pers)
        else:
            personnel[0].role = role
            selected_personnel = personnel
        # Add to Consumables
        if len(consumables) > 1:
            for consumable in consumables:
                if confirm_action(f"removal of selected Personnel from {str(consumable)}"):
                    for pers_remove in selected_personnel:
                        if consumable.remove_personnel(pers_remove):
                            consumables_altered += 1
        else:
            for pers_remove in selected_personnel:
                if consumables[0].remove_personnel(pers_remove):
                    consumables_altered += 1
        return f"{len(selected_personnel)} Personnel removed from {consumables_altered} Consumable(s)'."

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons consuamble new")

    @classmethod
    def _tabulate(cls, instances: Sequence[Consumable], date_format: str = r"%Y/%m/%d") -> str:
        instances = [[row+1, i.id, i.type, i.name, i.parts, i.rating, i.completions, i.status.name,
                      datetime.fromtimestamp(i.start_date).strftime(
                          date_format) if i.start_date else i.start_date,
                      datetime.fromtimestamp(i.end_date).strftime(date_format) if i.end_date else i.end_date] for row, i in enumerate(instances)]
        return tabulate(instances, headers=["#", "ID", "Type", "Name", "Parts", "Rating", "Completions", "Status", "Started", "Completed"])

    @classmethod
    def _prepare_args(cls, args: Namespace, values: Namespace) -> None:
        # Date
        date_format = getattr(args, "date_format")
        if "start_date" in values:
            if getattr(values, "start_date").lower() == "none":
                setattr(values, "start_date", None)
            else:
                setattr(values, "start_date", datetime.strptime(
                    getattr(values, "start_date"), date_format).timestamp())
        if "end_date" in values:
            if getattr(values, "end_date").lower() == "none":
                setattr(values, "end_date", None)
            else:
                setattr(values, "end_date", datetime.strptime(
                    getattr(values, "end_date"), date_format).timestamp())
        # Status
        if "status" in values:
            setattr(values, "status", Status[getattr(values, "status")])
        # Tags
        if "tags" in values:
            tags = (getattr(values, "tags")).split(",")
            setattr(values, "tags", tags)

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


class SeriesHandler(CLIHandler):

    ORDER_LIST = ["name"]

    @classmethod
    def handle(cls, args: Namespace) -> str:
        match getattr(args, "mode"):
            case "new":
                return cls.cli_new(args)
            case "list":
                return cls.cli_list(args)
            case "update":
                return cls.cli_update(args)
            case "delete":
                return cls.cli_delete(args)
            case _:
                return cls.no_action(args)

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        new = getattr(args, "new", Namespace())
        # Get mandatory args
        mandatory_args = ["name"]
        for arg in mandatory_args:
            if arg not in new:
                value = request_input(arg)
                setattr(new, arg, value)
        # Create
        series = Series.new(**vars(new))
        # Create String
        return cls._tabulate([series])

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Create String
        series = Series.find(**vars(where))
        # Ordering
        series = sort_by(series, getattr(
            args, "order"), getattr(args, "reverse"))
        results = len(series)
        if results > 0:
            return cls._tabulate(series) + f"\n{results} Result(s)..."
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None, "Values to set must be non-empty. e.g. cons series update set --name A")
        # Find
        series = Series.find(**vars(where_mapping))
        # Update
        updated_series = []
        if len(series) == 0:
            return "No Series matching where conditions."
        elif len(series) > 1:
            for ser in series:
                if confirm_action(f"update of {str(ser)}"):
                    updated_series.append(
                        ser.update_self(vars(set_mapping)))
        # Create String
        else:
            updated_series.append(
                series[0].update_self(vars(set_mapping)))
        if len(updated_series) > 0:
            return cls._tabulate(updated_series)
        else:
            return "No Series updated."

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Find
        series = Series.find(**vars(where))
        # Delete
        deleted = 0
        if len(series) == 0:
            return "No Series matching where conditions."
        elif len(series) > 1:
            for ser in series:
                if confirm_action(f"deletion of {str(ser)}"):
                    try:
                        ser.delete_self()
                        deleted += 1
                    except IntegrityError as e:
                        print(f"{deleted} Series deleted.")
                        raise ArgumentError(
                            None, "Cannot delete Series with -1 ID")
        # Create String
        else:
            try:
                series[0].delete_self()
                deleted += 1
            except IntegrityError as e:
                print(f"{deleted} Series deleted.")
                raise ArgumentError(None, "Cannot delete Series with -1 ID")
        return f"{deleted} Series deleted."

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons series new")

    @classmethod
    def _tabulate(cls, instances: Sequence[Series]) -> str:
        instances = [[row+1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(instances, headers=["#", "ID", "Name"])


class PersonnelHandler(CLIHandler):

    ORDER_LIST = ["first_name", "last_name", "pseudonym"]

    @classmethod
    def handle(cls, args: Namespace) -> str:
        match getattr(args, "mode"):
            case "new":
                return cls.cli_new(args)
            case "list":
                return cls.cli_list(args)
            case "update":
                return cls.cli_update(args)
            case "delete":
                return cls.cli_delete(args)
            case _:
                return cls.no_action(args)

    @classmethod
    def cli_new(cls, args: Namespace) -> str:
        new = getattr(args, "new", Namespace())
        if len(vars(new)) == 0:
            raise ArgumentError(
                None, "One of the valid values must be set. i.e. first_name, last_name or pseudonym.")
        # Create
        personnel = Personnel.new(**vars(new))
        # Create String
        return cls._tabulate([personnel])

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Create String
        personnel = Personnel.find(**vars(where))
        # Ordering
        personnel = sort_by(personnel, getattr(
            args, "order"), getattr(args, "reverse"))
        results = len(personnel)
        if results > 0:
            return cls._tabulate(personnel) + f"\n{results} Result(s)..."
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None, "Values to set must be non-empty. e.g. cons personnel update set --firstname A")
        # Find
        personnel = Personnel.find(**vars(where_mapping))
        # Update
        updated_series = []
        if len(personnel) == 0:
            return "No Personnel matching where conditions."
        elif len(personnel) > 1:
            for pers in personnel:
                if confirm_action(f"update of {str(pers)}"):
                    updated_series.append(
                        pers.update_self(vars(set_mapping)))
        # Create String
        else:
            updated_series.append(
                personnel[0].update_self(vars(set_mapping)))
        if len(updated_series) > 0:
            return cls._tabulate(updated_series)
        else:
            return "No Personnel updated."

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Find
        personnel = Personnel.find(**vars(where))
        # Delete
        deleted = 0
        if len(personnel) == 0:
            return "No Personnel matching where conditions."
        elif len(personnel) > 1:
            for pers in personnel:
                if confirm_action(f"deletion of {str(pers)}"):
                    pers.delete_self()
                    deleted += 1
        # Create String
        else:
            personnel[0].delete_self()
            deleted += 1
        return f"{deleted} Personnel deleted."

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons personnel new")

    @classmethod
    def _tabulate(cls, instances: Sequence[Personnel]) -> str:
        instances = [[row+1, i.id, i.first_name, i.pseudonym, i.last_name]
                     for row, i in enumerate(instances)]
        return tabulate(instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"])
