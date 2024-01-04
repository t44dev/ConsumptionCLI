# General Imports
import argparse
from abc import ABC, abstractmethod

# Consumption Imports
from consumptionbackend.Consumable import Status
from .SubNamespaceAction import SubNamespaceAction
from .cli_handling import CLIHandler, PersonnelHandler, ConsumableHandler, SeriesHandler


class MainParser:
    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")

    @classmethod
    def get(cls):
        main_parser = argparse.ArgumentParser(
            prog="Consumption CLI",
            description="A CLI tool for tracking media consumption",
        )
        sub_parsers = main_parser.add_subparsers()
        main_parser.set_defaults(handler=CLIHandler, mode="none")
        # Consumable
        ConsumableParser.setup(sub_parsers)
        # Series
        SeriesParser.setup(sub_parsers)
        # Personnel
        PersonnelParser.setup(sub_parsers)
        return main_parser


# Child Parsers


class ChildParser(ABC):
    def __init__(self) -> None:
        raise RuntimeError("Class cannot be used outside of a static context.")

    @classmethod
    @abstractmethod
    def setup(cls, parent_sp) -> None:
        pass


# Consumable Parsing


class ConsumableParser(ChildParser):
    @classmethod
    def setup(cls, parent_sp) -> None:
        parser: argparse.ArgumentParser = parent_sp.add_parser(
            "consumable", aliases=["c"], help="action on consumable entities"
        )
        parser.set_defaults(handler=ConsumableHandler)
        parser.add_argument(
            "--df",
            "--dateformat",
            dest="date_format",
            default=r"%Y/%m/%d",
            metavar="FORMAT",
            help="date format string, e.g %%Y/%%m/%%d",
        )
        sp = parser.add_subparsers()
        # Add Parsers
        cls._setup_new(sp)
        cls._setup_list(sp)
        cls._setup_update(sp)
        cls._setup_delete(sp)
        cls._setup_tag(sp)
        cls._setup_untag(sp)
        cls._setup_series(sp)
        cls._setup_personnel(sp)

    @classmethod
    def _setup_new(cls, parent_sp) -> None:
        # New Consumable
        parser_new = parent_sp.add_parser(
            "new", aliases=["n"], help="create a new consumable"
        )
        parser_new.set_defaults(mode="new")
        cls.add_set_args(parser_new, "new")

    @classmethod
    def _setup_list(cls, parent_sp) -> None:
        # List Consumable
        parser_list = parent_sp.add_parser(
            "list", aliases=["l"], help="list consumables"
        )
        parser_list.set_defaults(mode="list")
        parser_list.add_argument(
            "-o",
            "--order",
            dest="order",
            choices=ConsumableHandler.ORDER_LIST,
            default="name",
            help="order by attribute",
        )
        parser_list.add_argument(
            "--rv",
            "--reverse",
            dest="reverse",
            action="store_true",
            help="reverse order of listing",
        )
        parser_list.add_argument(
            "--static",
            dest="static",
            action="store_true",
            help="use a static listing instead of interactive scrolling",
        )
        cls.add_where_args(parser_list)

    @classmethod
    def _setup_update(cls, parent_sp) -> None:
        # Update Consumable
        parser_update = parent_sp.add_parser(
            "update", aliases=["u"], help="update existing consumable"
        )
        parser_update.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_update.set_defaults(mode="update")
        cls.add_where_args(parser_update)
        parser_set = parser_update.add_subparsers().add_parser("set", aliases=["s"])
        cls.add_set_args(parser_set)

    @classmethod
    def _setup_delete(cls, parent_sp) -> None:
        # Delete Consumable
        parser_delete = parent_sp.add_parser(
            "delete", aliases=["d"], help="delete existing consumable"
        )
        parser_delete.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_delete.set_defaults(mode="delete")
        cls.add_where_args(parser_delete)

    @classmethod
    def _setup_tag(cls, parent_sp) -> None:
        # Tag Consumable
        parser_tag = parent_sp.add_parser(
            "tag", aliases=["t"], help="add tag to existing consumable"
        )
        parser_tag.set_defaults(mode="tag")
        parser_tag.add_argument(
            "--tag", dest="tag", default=argparse.SUPPRESS, help="tag to add"
        )
        parser_tag.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        cls.add_where_args(parser_tag)

    @classmethod
    def _setup_untag(cls, parent_sp) -> None:
        # Untag Consumable
        parser_untag = parent_sp.add_parser(
            "untag", aliases=["ut"], help="remove tag from existing consumable"
        )
        parser_untag.set_defaults(mode="untag")
        parser_untag.add_argument(
            "--tag", dest="tag", default=argparse.SUPPRESS, help="tag to remove"
        )
        parser_untag.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        cls.add_where_args(parser_untag)

    @classmethod
    def _setup_series(cls, parent_sp) -> None:
        # Set Series
        parser_series = parent_sp.add_parser(
            "series", aliases=["ss"], help="set series of existing consumable"
        )
        parser_series.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_series.set_defaults(mode="set_series")
        cls.add_where_args(parser_series)
        parser_set = parser_series.add_subparsers().add_parser("set", aliases=["s"])
        SeriesParser.add_where_args(parser_set, "series")

    @classmethod
    def _setup_personnel(cls, parent_sp) -> None:
        parser_personnel = parent_sp.add_parser(
            "personnel", aliases=["p"], help="manage personnel of existing consumable"
        )
        parser_personnel.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_personnel.set_defaults(mode="personnel")
        cls.add_where_args(parser_personnel)
        sp = parser_personnel.add_subparsers()
        # Add Personnel
        parser_add = sp.add_parser("add", aliases=["a"], help="add personnel")
        parser_add.set_defaults(mode="add_personnel")
        parser_add.add_argument(
            "-r",
            "--role",
            dest="role",
            default=argparse.SUPPRESS,
            help="role to associate with added personnel",
        )
        PersonnelParser.add_where_args(parser_add, "personnel")
        # Remove Personnel
        parser_remove = sp.add_parser("remove", aliases=["r"], help="remove personnel")
        parser_remove.set_defaults(mode="remove_personnel")
        parser_remove.add_argument(
            "-r",
            "--role",
            dest="role",
            default=argparse.SUPPRESS,
            help="personnel role for removal",
        )
        PersonnelParser.add_where_args(parser_remove, "personnel")

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser, dest: str) -> None:
        parser.add_argument(
            "--sid",
            "--seriesid",
            type=int,
            dest=f"{dest}.series_id",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="SERIES_ID",
            help="unique series id",
        )
        parser.add_argument(
            "-n",
            "--name",
            dest=f"{dest}.name",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="NAME",
            help="consumable name",
        )
        parser.add_argument(
            "-t",
            "--type",
            type=str.upper,
            dest=f"{dest}.type",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="TYPE",
            help="type of consumable, e.g. Novel, Movie",
        )
        parser.add_argument(
            "-s",
            "--status",
            dest=f"{dest}.status",
            choices=[e.name for e in Status],
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="STATUS",
            help="progress status",
        )
        parser.add_argument(
            "-p",
            "--parts",
            type=int,
            dest=f"{dest}.parts",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="PART",
            help="e.g. Chapter, Episode",
        )
        parser.add_argument(
            "--mp",
            "--maxparts",
            dest=f"{dest}.max_parts",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="MAX_PARTS",
            help="total number of parts on completion",
        )
        parser.add_argument(
            "-c",
            "--completions",
            type=int,
            dest=f"{dest}.completions",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="COMPLETIONS",
            help="times completed",
        )
        parser.add_argument(
            "-r",
            "--rating",
            type=float,
            dest=f"{dest}.rating",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="RATING",
            help="numerical score",
        )
        parser.add_argument(
            "--sd",
            "--startdate",
            dest=f"{dest}.start_date",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="DATE",
            help="date of initial start",
        )
        parser.add_argument(
            "--ed",
            "--enddate",
            dest=f"{dest}.end_date",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="DATE",
            help="date of first completion",
        )

    @classmethod
    def add_where_args(
        cls, parser: argparse.ArgumentParser, dest: str = "where"
    ) -> None:
        parser.add_argument(
            "-i",
            "--id",
            type=int,
            dest=f"{dest}.id",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="ID",
            help="unique consumable id",
        )
        parser.add_argument(
            "--tg",
            "--tags",
            dest=f"{dest}.tags",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="TAGS",
            help="comma separated tags e.g. --tags tag1,tag2,tag3",
        )
        cls.add_args(parser, dest)

    @classmethod
    def add_set_args(cls, parser: argparse.ArgumentParser, dest: str = "set") -> None:
        cls.add_args(parser, dest)


# Series Parsing


class SeriesParser(ChildParser):
    @classmethod
    def setup(cls, parent_sp) -> None:
        parser: argparse.ArgumentParser = parent_sp.add_parser(
            "series", aliases=["s"], help="action on series entities"
        )
        parser.set_defaults(handler=SeriesHandler)
        sp = parser.add_subparsers()
        cls._setup_new(sp)
        cls._setup_list(sp)
        cls._setup_update(sp)
        cls._setup_delete(sp)

    @classmethod
    def _setup_new(cls, parent_sp) -> None:
        # New Series
        parser_new = parent_sp.add_parser(
            "new", aliases=["n"], help="create a new series"
        )
        parser_new.set_defaults(mode="new")
        cls.add_set_args(parser_new, "new")

    @classmethod
    def _setup_list(cls, parser_sp) -> None:
        # List Series
        parser_list = parser_sp.add_parser("list", aliases=["l"], help="list series")
        parser_list.set_defaults(mode="list")
        parser_list.add_argument(
            "-o",
            "--order",
            dest="order",
            choices=SeriesHandler.ORDER_LIST,
            default="name",
            help="order by attribute",
        )
        parser_list.add_argument(
            "--rv",
            "--reverse",
            dest="reverse",
            action="store_true",
            help="reverse order of listing",
        )
        parser_list.add_argument(
            "--static",
            dest="static",
            action="store_true",
            help="use a static listing instead of interactive scrolling",
        )
        cls.add_where_args(parser_list)

    @classmethod
    def _setup_update(cls, parent_sp) -> None:
        # Update Series
        parser_update = parent_sp.add_parser(
            "update", aliases=["u"], help="update existing series"
        )
        parser_update.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_update.set_defaults(mode="update")
        cls.add_where_args(parser_update)
        set_parser = parser_update.add_subparsers().add_parser("set", aliases=["s"])
        cls.add_set_args(set_parser)

    @classmethod
    def _setup_delete(cls, parent_sp) -> None:
        # Delete Series
        parser_delete = parent_sp.add_parser(
            "delete", aliases=["d"], help="delete existing series"
        )
        parser_delete.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_delete.set_defaults(mode="delete")
        cls.add_where_args(parser_delete)

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser, dest: str) -> None:
        parser.add_argument(
            "-n",
            "--name",
            dest=f"{dest}.name",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="NAME",
            help="series name",
        )

    @classmethod
    def add_where_args(
        cls, parser: argparse.ArgumentParser, dest: str = "where"
    ) -> None:
        parser.add_argument(
            "-i",
            "--id",
            type=int,
            dest=f"{dest}.id",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            help="unique series id",
        )
        cls.add_args(parser, dest)

    @classmethod
    def add_set_args(cls, parser: argparse.ArgumentParser, dest: str = "set") -> None:
        cls.add_args(parser, dest)


# Personnel Parsing


class PersonnelParser(ChildParser):
    @classmethod
    def setup(cls, parent_sp) -> None:
        parser: argparse.ArgumentParser = parent_sp.add_parser(
            "personnel", aliases=["p"], help="action on personnel entities"
        )
        parser.set_defaults(handler=PersonnelHandler)
        sp = parser.add_subparsers()
        cls._setup_new(sp)
        cls._setup_list(sp)
        cls._setup_update(sp)
        cls._setup_delete(sp)

    @classmethod
    def _setup_new(cls, parent_sp) -> None:
        # New Personnel
        parser_new = parent_sp.add_parser(
            "new", aliases=["n"], help="create new personnel"
        )
        parser_new.set_defaults(mode="new")
        cls.add_set_args(parser_new, "new")

    @classmethod
    def _setup_list(cls, parent_sp) -> None:
        # List Personnel
        parser_list = parent_sp.add_parser("list", aliases=["l"], help="list personnel")
        parser_list.set_defaults(mode="list")
        parser_list.add_argument(
            "-o",
            "--order",
            dest="order",
            choices=PersonnelHandler.ORDER_LIST,
            default="first_name",
            help="order by attribute",
        )
        parser_list.add_argument(
            "--rv",
            "--reverse",
            dest="reverse",
            action="store_true",
            help="reverse order of listing",
        )
        parser_list.add_argument(
            "--static",
            dest="static",
            action="store_true",
            help="use a static listing instead of interactive scrolling",
        )
        cls.add_where_args(parser_list)

    @classmethod
    def _setup_update(cls, parent_sp) -> None:
        # Update Personnel
        parser_update = parent_sp.add_parser(
            "update", aliases=["u"], help="update existing personnel"
        )
        parser_update.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_update.set_defaults(mode="update")
        cls.add_set_args(parser_update)
        set_parser = parser_update.add_subparsers().add_parser("set", aliases=["s"])
        cls.add_set_args(set_parser)

    @classmethod
    def _setup_delete(cls, parent_sp) -> None:
        # Delete Series
        parser_delete = parent_sp.add_parser(
            "delete", aliases=["d"], help="delete existing personnel"
        )
        parser_delete.add_argument(
            "--force",
            dest=f"force",
            action="store_true",
            help="complete action without confirmation",
        )
        parser_delete.set_defaults(mode="delete")
        cls.add_where_args(parser_delete)

    @classmethod
    def add_args(cls, parser: argparse.ArgumentParser, dest: str) -> None:
        parser.add_argument(
            "-f",
            "--firstname",
            dest=f"{dest}.first_name",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="FIRST NAME",
            help="personnel first name",
        )
        parser.add_argument(
            "-l",
            "--lastname",
            dest=f"{dest}.last_name",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="LAST NAME",
            help="personnel last name",
        )
        parser.add_argument(
            "-p",
            "--pseudonym",
            dest=f"{dest}.pseudonym",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            metavar="PSEUDONYM",
            help="personnel pseudonym",
        )

    @classmethod
    def add_where_args(
        cls, parser: argparse.ArgumentParser, dest: str = "where"
    ) -> None:
        parser.add_argument(
            "-i",
            "--id",
            type=int,
            dest=f"{dest}.id",
            action=SubNamespaceAction,
            default=argparse.SUPPRESS,
            help="unique personnel id",
        )
        cls.add_args(parser, dest)

    @classmethod
    def add_set_args(cls, parser: argparse.ArgumentParser, dest: str = "set") -> None:
        cls.add_args(parser, dest)
