# General Imports
import argparse

# Consumption Imports
from consumptionbackend.Consumable import Status
from .SubNamespaceAction import SubNamespaceAction
from .cli_handling import CLIHandler, PersonnelHandler, ConsumableHandler, SeriesHandler


def get_main_parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(
        prog="Consumption CLI", description="A CLI tool for tracking media consumption"
    )
    sub_parsers = main_parser.add_subparsers()
    main_parser.set_defaults(handler=CLIHandler, mode="none")
    # Consumable
    add_consumable_parsers(sub_parsers)
    # Personnel
    add_personnel_parsers(sub_parsers)
    # Series
    add_series_parsers(sub_parsers)
    return main_parser


# Consumable Parsing


def add_consumable_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    cons_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "consumable", aliases=["c"], help="action on consumable entities"
    )
    cons_parser.set_defaults(handler=ConsumableHandler)
    cons_parser.add_argument(
        "--df",
        "--dateformat",
        dest="date_format",
        default=r"%Y/%m/%d",
        metavar="FORMAT",
        help="date format string, e.g %%Y/%%m/%%d",
    )
    sub_cons_parsers = cons_parser.add_subparsers()
    # New Consumable
    cons_parser_new = sub_cons_parsers.add_parser(
        "new", aliases=["n"], help="create a new consumable"
    )
    cons_parser_new.set_defaults(mode="new")
    set_args_consumable(cons_parser_new, "new")
    # List Consumable
    cons_parser_list = sub_cons_parsers.add_parser(
        "list", aliases=["l"], help="list consumables"
    )
    cons_parser_list.set_defaults(mode="list")
    cons_parser_list.add_argument(
        "-o",
        "--order",
        dest="order",
        choices=ConsumableHandler.ORDER_LIST,
        default="name",
        help="order by attribute",
    )
    cons_parser_list.add_argument(
        "--rv",
        "--reverse",
        dest="reverse",
        action="store_true",
        help="reverse order of listing",
    )
    cons_parser_list.add_argument(
        "--static",
        dest="static",
        action="store_true",
        help="use a static listing instead of interactive scrolling",
    )
    where_args_consumable(cons_parser_list)
    # Update Consumable
    cons_parser_update = sub_cons_parsers.add_parser(
        "update", aliases=["u"], help="update existing consumable"
    )
    cons_parser_update.set_defaults(mode="update")
    where_args_consumable(cons_parser_update)
    set_parser = cons_parser_update.add_subparsers().add_parser("set", aliases=["s"])
    set_args_consumable(set_parser)
    # Delete Consumable
    cons_parser_delete = sub_cons_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing consumable"
    )
    cons_parser_delete.set_defaults(mode="delete")
    where_args_consumable(cons_parser_delete)
    # Tag Consumable
    cons_parser_tag = sub_cons_parsers.add_parser(
        "tag", aliases=["t"], help="add tag to existing consumable"
    )
    cons_parser_tag.set_defaults(mode="tag")
    cons_parser_tag.add_argument(
        "--tag", dest="tag", default=argparse.SUPPRESS, help="tag to add"
    )
    where_args_consumable(cons_parser_tag)
    # Untag Consumable
    cons_parser_untag = sub_cons_parsers.add_parser(
        "untag", aliases=["ut"], help="remove tag from existing consumable"
    )
    cons_parser_untag.set_defaults(mode="untag")
    cons_parser_untag.add_argument(
        "--tag", dest="tag", default=argparse.SUPPRESS, help="tag to remove"
    )
    where_args_consumable(cons_parser_untag)
    # Set Series
    cons_parser_series = sub_cons_parsers.add_parser(
        "series", aliases=["ss"], help="set series of existing consumable"
    )
    cons_parser_series.set_defaults(mode="set_series")
    where_args_consumable(cons_parser_series)
    set_parser = cons_parser_series.add_subparsers().add_parser("set", aliases=["s"])
    where_args_series(set_parser, "series")
    # Add/Remove Personnel
    cons_parser_personnel = sub_cons_parsers.add_parser(
        "personnel", aliases=["p"], help="manage personnel of existing consumable"
    )
    cons_parser_personnel.set_defaults(mode="personnel")
    where_args_consumable(cons_parser_personnel)
    sub_cons_parsers_personnel = cons_parser_personnel.add_subparsers()
    add_parser = sub_cons_parsers_personnel.add_parser(
        "add", aliases=["a"], help="add personnel"
    )
    add_parser.set_defaults(mode="add_personnel")
    add_parser.add_argument(
        "-r",
        "--role",
        dest="role",
        default=argparse.SUPPRESS,
        help="role to associate with added personnel",
    )
    where_args_personnel(add_parser, "personnel")
    remove_parser = sub_cons_parsers_personnel.add_parser(
        "remove", aliases=["r"], help="remove personnel"
    )
    remove_parser.set_defaults(mode="remove_personnel")
    remove_parser.add_argument(
        "-r",
        "--role",
        dest="role",
        default=argparse.SUPPRESS,
        help="personnel role for removal",
    )
    where_args_personnel(remove_parser, "personnel")


def where_args_consumable(parser: argparse.ArgumentParser, dest: str = "where") -> None:
    parser.add_argument(
        "-i",
        "--id",
        type=int,
        dest=f"{dest}.id",
        action=SubNamespaceAction,
        default=argparse.SUPPRESS,
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
    _consumable_args(parser, dest)


def set_args_consumable(parser: argparse.ArgumentParser, dest: str = "set") -> None:
    _consumable_args(parser, dest)


def _consumable_args(parser: argparse.ArgumentParser, dest: str) -> None:
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
        type=int,
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


# Series Parsing


def add_series_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    series_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "series", aliases=["s"], help="action on series entities"
    )
    series_parser.set_defaults(handler=SeriesHandler)
    sub_series_parsers = series_parser.add_subparsers()
    # New Series
    series_parser_new = sub_series_parsers.add_parser(
        "new", aliases=["n"], help="create a new series"
    )
    series_parser_new.set_defaults(mode="new")
    set_args_series(series_parser_new, "new")
    # List Series
    series_parser_list = sub_series_parsers.add_parser(
        "list", aliases=["l"], help="list series"
    )
    series_parser_list.set_defaults(mode="list")
    series_parser_list.add_argument(
        "-o",
        "--order",
        dest="order",
        choices=SeriesHandler.ORDER_LIST,
        default="name",
        help="order by attribute",
    )
    series_parser_list.add_argument(
        "--rv",
        "--reverse",
        dest="reverse",
        action="store_true",
        help="reverse order of listing",
    )
    series_parser_list.add_argument(
        "--static",
        dest="static",
        action="store_true",
        help="use a static listing instead of interactive scrolling",
    )
    where_args_series(series_parser_list)
    # Update Series
    series_parser_update = sub_series_parsers.add_parser(
        "update", aliases=["u"], help="update existing series"
    )
    series_parser_update.set_defaults(mode="update")
    where_args_series(series_parser_update)
    set_parser = series_parser_update.add_subparsers().add_parser("set", aliases=["s"])
    set_args_series(set_parser)
    # Delete Series
    series_parser_delete = sub_series_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing series"
    )
    series_parser_delete.set_defaults(mode="delete")
    where_args_series(series_parser_delete)


def where_args_series(parser: argparse.ArgumentParser, dest: str = "where") -> None:
    parser.add_argument(
        "-i",
        "--id",
        type=int,
        dest=f"{dest}.id",
        action=SubNamespaceAction,
        default=argparse.SUPPRESS,
        help="unique series id",
    )
    _series_args(parser, dest)


def set_args_series(parser: argparse.ArgumentParser, dest: str = "set") -> None:
    _series_args(parser, dest)


def _series_args(parser: argparse.ArgumentParser, dest: str) -> None:
    parser.add_argument(
        "-n",
        "--name",
        dest=f"{dest}.name",
        action=SubNamespaceAction,
        default=argparse.SUPPRESS,
        metavar="NAME",
        help="series name",
    )


# Personnel Parsing


def add_personnel_parsers(sub_parsers: argparse._SubParsersAction) -> None:
    personnel_parser: argparse.ArgumentParser = sub_parsers.add_parser(
        "personnel", aliases=["p"], help="action on personnel entities"
    )
    personnel_parser.set_defaults(handler=PersonnelHandler)
    sub_personnel_parsers = personnel_parser.add_subparsers()
    # New Series
    personnel_parser_new = sub_personnel_parsers.add_parser(
        "new", aliases=["n"], help="create new personnel"
    )
    personnel_parser_new.set_defaults(mode="new")
    set_args_personnel(personnel_parser_new, "new")
    # List Series
    personnel_parser_list = sub_personnel_parsers.add_parser(
        "list", aliases=["l"], help="list personnel"
    )
    personnel_parser_list.set_defaults(mode="list")
    personnel_parser_list.add_argument(
        "-o",
        "--order",
        dest="order",
        choices=PersonnelHandler.ORDER_LIST,
        default="first_name",
        help="order by attribute",
    )
    personnel_parser_list.add_argument(
        "--rv",
        "--reverse",
        dest="reverse",
        action="store_true",
        help="reverse order of listing",
    )
    personnel_parser_list.add_argument(
        "--static",
        dest="static",
        action="store_true",
        help="use a static listing instead of interactive scrolling",
    )
    where_args_personnel(personnel_parser_list, "where")
    # Update Series
    personnel_parser_update = sub_personnel_parsers.add_parser(
        "update", aliases=["u"], help="update existing personnel"
    )
    personnel_parser_update.set_defaults(mode="update")
    set_args_personnel(personnel_parser_update)
    set_parser = personnel_parser_update.add_subparsers().add_parser(
        "set", aliases=["s"]
    )
    set_args_personnel(set_parser)
    # Delete Series
    personnel_parser_delete = sub_personnel_parsers.add_parser(
        "delete", aliases=["d"], help="delete existing personnel"
    )
    personnel_parser_delete.set_defaults(mode="delete")
    where_args_personnel(personnel_parser_delete)


def where_args_personnel(parser: argparse.ArgumentParser, dest: str = "where") -> None:
    parser.add_argument(
        "-i",
        "--id",
        type=int,
        dest=f"{dest}.id",
        action=SubNamespaceAction,
        default=argparse.SUPPRESS,
        help="unique personnel id",
    )
    _personnel_args(parser, dest)


def set_args_personnel(parser: argparse.ArgumentParser, dest: str = "set") -> None:
    _personnel_args(parser, dest)


def _personnel_args(parser: argparse.ArgumentParser, dest: str) -> None:
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
