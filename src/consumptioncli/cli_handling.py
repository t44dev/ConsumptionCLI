# General Imports
from argparse import ArgumentError, Namespace
from datetime import datetime
from collections.abc import Sequence, Mapping
from abc import abstractmethod, ABC
from sqlite3 import IntegrityError

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable
from consumptionbackend.Status import Status
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
from .list_handling import ConsumableList, SeriesList, PersonnelList
from .utils import request_input, confirm_action, UNCHANGED_SENTINEL


class CLIHandler(ABC):
    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")

    @classmethod
    def handle(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An entity type must be seleced. e.g. cons consumable"
        )

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
    def do_update(
        cls,
        instances: Sequence[DatabaseEntity],
        set_mapping: Mapping,
        force: bool = False,
    ) -> Sequence[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def update_fields(
        cls, instances: Sequence[DatabaseEntity], force: bool = False
    ) -> Sequence[DatabaseEntity]:
        pass

    @classmethod
    @abstractmethod
    def cli_delete(cls, args: Namespace) -> str:
        pass

    @classmethod
    @abstractmethod
    def do_delete(cls, instances: Sequence[DatabaseEntity], force: bool = False) -> int:
        pass

    @classmethod
    @abstractmethod
    def no_action(cls, args: Namespace) -> str:
        pass


class ConsumableHandler(CLIHandler):
    ORDER_LIST = [
        "id",
        "type",
        "name",
        "parts",
        "rating",
        "completions",
        "status",
        "start_date",
        "end_date",
    ]

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
                    None,
                    "Must select an action. e.g. cons consumable personnel add --name John",
                )
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
        return ConsumableList([consumable], getattr(args, "date_format")).tabulate_str()

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Get Consumables
        consumables = Consumable.find(**vars(where))
        results = len(consumables)
        # Static vs. Dynamic
        static = getattr(args, "static", False)
        if results > 0:
            consumable_list = ConsumableList(consumables, getattr(args, "date_format"))
            consumable_list.order_by(getattr(args, "order"), getattr(args, "reverse"))
            if static:
                return consumable_list.tabulate_str() + f"\n{results} Result(s)..."
            else:
                consumable_list.init_run()
                return ""
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None,
                "Values to set must be non-empty. e.g. cons consumable update set --name A",
            )
        # Prepare Arguments
        cls._prepare_args(args, where_mapping)
        cls._prepare_args(args, set_mapping)
        # Find
        consumables = Consumable.find(**vars(where_mapping))
        if len(consumables) == 0:
            return "No Consumables found."
        # Update
        force = getattr(args, "force")
        updated_consumables = cls.do_update(consumables, vars(set_mapping), force)
        # Create String
        if len(updated_consumables) > 0:
            return ConsumableList(
                updated_consumables, getattr(args, "date_format")
            ).tabulate_str()
        else:
            return "No Consumable(s) updated."

    @classmethod
    def do_update(
        cls,
        instances: Sequence[Consumable],
        set_mapping: Mapping,
        force: bool = False,
    ) -> Sequence[Consumable]:
        updated_consumables = []
        for consumable in instances:
            if (
                force
                or len(instances) == 1
                or confirm_action(f"update of {str(consumable)}")
            ):
                updated_consumables.append(consumable.update_self(set_mapping))
        return updated_consumables

    @classmethod
    def update_fields(
        cls, instances: Sequence[Consumable], force: bool = False
    ) -> Sequence[Consumable]:
        # Setup
        set_mapping = Namespace()

        def converts(type):
            def _converts(x):
                try:
                    type(x)
                    return True
                except ValueError:
                    return False

            return _converts

        # Get attrs
        name = request_input("name", UNCHANGED_SENTINEL, lambda x: len(x))
        if name != UNCHANGED_SENTINEL:
            setattr(set_mapping, "name", name)
        type = request_input("type", UNCHANGED_SENTINEL, lambda x: len(x))
        if name != UNCHANGED_SENTINEL:
            setattr(set_mapping, "type", type)
        status = request_input(
            f"status i.e. {[e.name for e in Status]}",
            UNCHANGED_SENTINEL,
            lambda x: x in [e.name for e in Status],
        )
        if status != UNCHANGED_SENTINEL:
            setattr(set_mapping, "status", status)
        parts = request_input(f"number of parts", UNCHANGED_SENTINEL, converts(int))
        if parts != UNCHANGED_SENTINEL:
            setattr(set_mapping, "parts", int(parts))
        max_parts = request_input(
            f"max number of parts",
            UNCHANGED_SENTINEL,
            lambda x: converts(int)(x) or x in ["None", "Null", "?"],
        )
        if max_parts != UNCHANGED_SENTINEL:
            setattr(set_mapping, "max_parts", max_parts)
        completions = request_input(
            f"number of completions", UNCHANGED_SENTINEL, converts(int)
        )
        if completions != UNCHANGED_SENTINEL:
            setattr(set_mapping, "completions", int(completions))
        rating = request_input(f"rating", UNCHANGED_SENTINEL, converts(float))
        if rating != UNCHANGED_SENTINEL:
            setattr(set_mapping, "rating", float(rating))
        cls._prepare_args(Namespace(date_format="%Y"), set_mapping)
        if len(vars(set_mapping)) > 0:
            return cls.do_update(instances, vars(set_mapping), force)
        else:
            return instances

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Find
        consumables = Consumable.find(**vars(where))
        if len(consumables) == 0:
            return "No Consumables found."
        # Delete
        force = getattr(args, "force")
        deleted = cls.do_delete(consumables, force)
        # Create String
        return f"{deleted} Consumable(s) deleted."

    @classmethod
    def do_delete(cls, instances: Sequence[Consumable], force: bool = False) -> int:
        deleted = 0
        for consumable in instances:
            if (
                force
                or len(instances) == 1
                or confirm_action(f"deletion of {str(consumable)}")
            ):
                consumable.delete_self()
                deleted += 1
        return deleted

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
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Find
        consumables = Consumable.find(**vars(where))
        if len(consumables) == 0:
            return "No Consumables found."
        # Tag
        force = getattr(args, "force")
        tagged = cls.do_tag(consumables, getattr(args, "tag", None), force)
        return f"{tagged} Consumable(s) tagged."

    @classmethod
    def do_tag(
        cls, consumables: Sequence[Consumable], tag: str = None, force: bool = False
    ) -> int:
        # Get tag
        if tag is None:
            tag = request_input("tag")
        # Tag
        tagged = 0
        for consumable in consumables:
            if (
                force
                or len(consumables) == 1
                or confirm_action(f"tagging of {str(consumable)} with '{tag}'")
            ):
                if consumable.add_tag(tag):
                    tagged += 1
        return tagged

    @classmethod
    def cli_untag(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        # Find
        consumables = Consumable.find(**vars(where))
        if len(consumables) == 0:
            return "No Consumables found."
        # Untag
        force = getattr(args, "force")
        untagged = cls.do_untag(consumables, getattr(args, "tag", None), force)
        # Create string
        return f"{untagged} Consumable(s) untagged."

    @classmethod
    def do_untag(
        cls, consumables: Sequence[Consumable], tag: str = None, force: bool = False
    ) -> int:
        # Get tag
        if tag is None:
            tag = request_input("tag")
        # Untag
        untagged = 0
        for consumable in consumables:
            if (
                force
                or len(consumables) == 1
                or confirm_action(f"removal of tag '{tag}' from {str(consumable)}")
            ):
                if consumable.remove_tag(tag):
                    untagged += 1
        return untagged

    @classmethod
    def cli_series(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        series_where = getattr(args, "series", Namespace())
        # Prepare Arguments
        cls._prepare_args(args, where)
        force = getattr(args, "force")
        if len(vars(series_where)) == 0:
            raise ArgumentError(
                None,
                "Series to set must be specified e.g. cons consumable series set --name S",
            )
        # Get Series
        series = Series.find(**vars(series_where))
        set_series = None
        if len(series) == 0:
            return "No Series found."
        elif len(series) > 1 and force:
            raise ArgumentError(
                None, "Multiple Series match conditions with --force set."
            )
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
            return "No Consumables found."
        elif len(consumables) > 1:
            for consumable in consumables:
                if force or confirm_action(
                    f"setting Series of {str(consumable)} to {str(set_series)}"
                ):
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
        # Prepare Arguments
        cls._prepare_args(args, where)
        force = getattr(args, "force")
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
            return "No Personnel found."
        if len(consumables) == 0:
            return "No Consumables found."
        # Confirmations
        if len(personnel) > 1:
            for pers in personnel:
                if force or confirm_action(f"selection of {str(pers)}"):
                    pers.role = role
                    selected_personnel.append(pers)
        else:
            personnel[0].role = role
            selected_personnel = personnel
        # Add to Consumables
        if len(consumables) > 1:
            for consumable in consumables:
                if force or confirm_action(
                    f"adding selected Personnel to {str(consumable)} as '{role}'"
                ):
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
        # Prepare Arguments
        cls._prepare_args(args, where)
        force = getattr(args, "force")
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
            return "No Personnel found."
        if len(consumables) == 0:
            return "No Consumables found."
        # Confirmations
        if len(personnel) > 1:
            for pers in personnel:
                if force or confirm_action(f"selection of {str(pers)}"):
                    pers.role = role
                    selected_personnel.append(pers)
        else:
            personnel[0].role = role
            selected_personnel = personnel
        # Add to Consumables
        if len(consumables) > 1:
            for consumable in consumables:
                if force or confirm_action(
                    f"removal of selected Personnel from {str(consumable)}"
                ):
                    for pers_remove in selected_personnel:
                        if consumable.remove_personnel(pers_remove):
                            consumables_altered += 1
        else:
            for pers_remove in selected_personnel:
                if consumables[0].remove_personnel(pers_remove):
                    consumables_altered += 1
        return f"{len(selected_personnel)} Personnel removed from {consumables_altered} Consumable(s)."

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons consuamble new"
        )

    @classmethod
    def _prepare_args(cls, args: Namespace, values: Namespace) -> None:
        # Date
        date_format = getattr(args, "date_format")
        if "start_date" in values:
            if getattr(values, "start_date").lower() == "none":
                setattr(values, "start_date", None)
            else:
                try:
                    setattr(
                        values,
                        "start_date",
                        datetime.strptime(
                            getattr(values, "start_date"), date_format
                        ).timestamp(),
                    )
                except ValueError:
                    raise ArgumentError(None, "Invalid date for format.")
        if "end_date" in values:
            if getattr(values, "end_date").lower() == "none":
                setattr(values, "end_date", None)
            else:
                try:
                    setattr(
                        values,
                        "end_date",
                        datetime.strptime(
                            getattr(values, "end_date"), date_format
                        ).timestamp(),
                    )
                except ValueError:
                    raise ArgumentError(None, "Invalid date for format.")
        # Status
        if "status" in values:
            setattr(values, "status", Status[getattr(values, "status")])
        # Tags
        if "tags" in values:
            tags = (getattr(values, "tags")).split(",")
            setattr(values, "tags", tags)
        # Max Parts
        max_parts_none = ["None", "Null", "?"]
        if "max_parts" in values:
            max_parts = getattr(values, "max_parts").strip().lower()
            if max_parts in max_parts_none:
                max_parts = None
            else:
                try:
                    max_parts = int(max_parts)
                except ValueError:
                    raise ArgumentError(
                        None,
                        "Invalid value for max_parts. Must be an integer or one of ",
                    )
            setattr(values, "max_parts", max_parts)


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
        return SeriesList([series]).tabulate_str()

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Get Series
        series = Series.find(**vars(where))
        results = len(series)
        # Static vs Dynamic
        static = getattr(args, "static", False)
        if results > 0:
            series_list = SeriesList(series)
            series_list.order_by(getattr(args, "order"), getattr(args, "reverse"))
            if static:
                return series_list.tabulate_str() + f"\n{results} Result(s)..."
            else:
                series_list.init_run()
                return ""
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None,
                "Values to set must be non-empty. e.g. cons series update set --name A",
            )
        # Find
        series = Series.find(**vars(where_mapping))
        if len(series) == 0:
            return "No Series found."
        # Update
        force = getattr(args, "force")
        updated_series = cls.do_update(series, vars(set_mapping), force)
        # Create String
        if len(updated_series) > 0:
            return SeriesList(updated_series).tabulate_str()
        else:
            return "No Series updated."

    @classmethod
    def do_update(
        cls, instances: Sequence[Series], set_mapping: Mapping, force: bool = False
    ) -> Sequence[Series]:
        updated_series = []
        for ser in instances:
            if force or len(instances) == 1 or confirm_action(f"update of {str(ser)}"):
                updated_series.append(ser.update_self(set_mapping))
        return updated_series

    @classmethod
    def update_fields(
        cls, instances: Sequence[Series], force: bool = False
    ) -> Sequence[Series]:
        # Setup
        set_mapping = Namespace()

        # Get attrs
        name = request_input("name", UNCHANGED_SENTINEL, lambda x: len(x))
        if name != UNCHANGED_SENTINEL:
            setattr(set_mapping, "name", name)

        if len(vars(set_mapping)) > 0:
            return cls.do_update(instances, vars(set_mapping), force)
        else:
            return instances

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Find
        series = Series.find(**vars(where))
        series = list(filter(lambda x: x.id != -1), series)
        # Delete
        if len(series) == 0:
            return "No Series found."
        force = getattr(args, "force")
        deleted = cls.do_delete(series, force)
        # Create String
        return f"{deleted} Series deleted."

    @classmethod
    def do_delete(cls, instances: Sequence[DatabaseEntity], force: bool = False) -> int:
        deleted = 0
        for ser in instances:
            if (
                force
                or len(instances) == 1
                or confirm_action(f"deletion of {str(ser)}")
            ):
                ser.delete_self()
                deleted += 1
        return deleted

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons series new"
        )


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
                None,
                "One of the valid values must be set. i.e. first_name, last_name or pseudonym.",
            )
        # Create
        personnel = Personnel.new(**vars(new))
        # Create String
        return PersonnelList([personnel]).tabulate_str()

    @classmethod
    def cli_list(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Get Personnel
        personnel = Personnel.find(**vars(where))
        results = len(personnel)
        # Static vs. Dynamic
        static = getattr(args, "static", False)
        if results > 0:
            personnel_list = PersonnelList(personnel)
            personnel_list.order_by(getattr(args, "order"), getattr(args, "reverse"))
            if static:
                return personnel_list.tabulate_str() + f"\n{results} Result(s)..."
            else:
                personnel_list.init_run()
                return ""
        else:
            return "0 Results..."

    @classmethod
    def cli_update(cls, args: Namespace) -> str:
        where_mapping = getattr(args, "where", Namespace())
        set_mapping = getattr(args, "set", Namespace())
        if len(vars(set_mapping)) == 0:
            raise ArgumentError(
                None,
                "Values to set must be non-empty. e.g. cons personnel update set --firstname A",
            )
        # Find
        personnel = Personnel.find(**vars(where_mapping))
        # Update
        if len(personnel) == 0:
            return "No Personnel found."
        force = getattr(args, "force")
        updated_personnel = cls.do_update(personnel, vars(set_mapping), force)
        # Create String
        if len(updated_personnel) > 0:
            return PersonnelList(updated_personnel).tabulate_str()
        else:
            return "No Personnel updated."

    @classmethod
    def do_update(
        cls, instances: Sequence[Personnel], set_mapping: Mapping, force: bool = False
    ) -> Sequence[Personnel]:
        updated_personnel = []
        for pers in instances:
            if force or len(instances) == 1 or confirm_action(f"update of {str(pers)}"):
                updated_personnel.append(pers.update_self(set_mapping))
        return updated_personnel

    @classmethod
    def update_fields(
        cls, instances: Sequence[DatabaseEntity], force: bool = False
    ) -> Sequence[DatabaseEntity]:
        # Setup
        set_mapping = Namespace()

        # Get attrs
        first_name = request_input("first name", UNCHANGED_SENTINEL, lambda x: len(x))
        if first_name != UNCHANGED_SENTINEL:
            setattr(set_mapping, "first_name", first_name)
        pseudonym = request_input("pseudonym", UNCHANGED_SENTINEL, lambda x: len(x))
        if pseudonym != UNCHANGED_SENTINEL:
            setattr(set_mapping, "pseudonym", pseudonym)
        last_name = request_input("last name", UNCHANGED_SENTINEL, lambda x: len(x))
        if last_name != UNCHANGED_SENTINEL:
            setattr(set_mapping, "last_name", last_name)

        if len(vars(set_mapping)) > 0:
            return cls.do_update(instances, vars(set_mapping), force)
        else:
            return instances

    @classmethod
    def cli_delete(cls, args: Namespace) -> str:
        where = getattr(args, "where", Namespace())
        # Find
        personnel = Personnel.find(**vars(where))
        # Delete
        if len(personnel) == 0:
            return "No Personnel found."
        force = getattr(args, "force")
        deleted = cls.do_delete(personnel, force)
        # Create String
        return f"{deleted} Personnel deleted."

    @classmethod
    def do_delete(cls, instances: Sequence[Personnel], force: bool = False) -> int:
        deleted = 0
        for pers in instances:
            if (
                force
                or len(instances) == 1
                or confirm_action(f"deletion of {str(pers)}")
            ):
                pers.delete_self()
                deleted += 1
        return deleted

    @classmethod
    def no_action(cls, args: Namespace) -> str:
        raise ArgumentError(
            None, "An action action must be selected e.g. cons personnel new"
        )
