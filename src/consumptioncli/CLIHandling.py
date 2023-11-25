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
                None, "Values to set must be non-empty. e.g. cons consumable update where set --name A")
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
                        tagged +=1
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
                        untagged +=1
        else:
            consumables[0].remove_tag(tag)
            untagged += 1
        # Create string 
        return f"{untagged} Consumable(s) untagged."

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
                        raise ArgumentError(None, "Cannot delete Series with -1 ID") 
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
    def _tabulate(cls, instances : Sequence[Series]) -> str:
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
            raise ArgumentError(None, "One of the valid values must be set. i.e. first_name, last_name or pseudonym.")
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
                None, "Values to set must be non-empty. e.g. cons personnel update where set --firstname A")
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
    def _tabulate(cls, instances : Sequence[Personnel]) -> str:
        instances = [[row+1, i.id, i.first_name, i.pseudonym, i.last_name] for row, i in enumerate(instances)]
        return tabulate(instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"])

    # @classmethod
    # def cli_list(cls, ent: Type[Staff], subdict: dict, **kwargs) -> str:
        # instances = cls.get_list_ents(ent, subdict, **kwargs)
        # return cls._cli_tabulate(instances) + f"\n{len(instances)} Results..."

    # @classmethod
    # def _cli_tabulate(cls, instances : list[Staff]):
        # instances = [[row+1, i.id, i.pseudonym, i.first_name, i.last_name] for row, i in enumerate(instances)]
        # return tabulate(instances, headers=["#", "ID", "Pseudonym", "First Name", "Last Name"])
