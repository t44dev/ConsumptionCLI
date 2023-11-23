# General Imports
import argparse

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable, Status
from consumptionbackend.Personnel import Personnel
from consumptionbackend.Series import Series
from .SubNamespaceAction import SubNamespaceAction
from .CLIHandling import CLIHandler, PersonnelHandler, ConsumableHandler, SeriesHandler

def get_main_parser() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(prog="Consumption CLI", description="A CLI tool for tracking media consumption")
    sub_parsers = main_parser.add_subparsers()
    main_parser.set_defaults(_handler=CLIHandler, mode="none")
    # Consumable
    add_consumable_parsers(sub_parsers)
    # Personnel
    add_personnel_parsers(sub_parsers)
    # Series
    add_series_parsers(sub_parsers)
    return main_parser

# main_parser.add_argument("-c", "--create", action="store_true", dest="create", help="create a new entity")
# main_parser.add_argument("-u", "--update", action="store_true", dest="update", help="update an existing entity by its id")
# main_parser.add_argument("-d", "--delete", action="store_true", dest="delete", help="delete an entity by its id")
# main_parser.add_argument("-l", "--list", action="store_true", dest="list", help="list entities with some search conditions")

# Consumable Parsing
def add_consumable_parsers(sub_parsers : argparse._SubParsersAction) -> None:
    cons_parser = sub_parsers.add_parser("consumable", aliases=["c"], help="action on consumable entities")
    cons_parser.set_defaults(_handler=ConsumableHandler)
    cons_parser.add_argument("--df", "--dateformat", dest="date_format", default=r"%Y/%m/%d", metavar="FORMAT", help="date format string, e.g %%Y/%%m/%%d")
    sub_cons_parsers = cons_parser.add_subparsers()
    ## New Consumable
    cons_parser_new = sub_cons_parsers.add_parser("new", aliases=["n"], help="create a new consumable")
    cons_parser_new.set_defaults(mode="new")
    add_consumable_arguments(cons_parser_new, "new")
    ## List Consumable
    cons_parser_list = sub_cons_parsers.add_parser("list", aliases=["l"], help="list consumables")
    ## Update Consumable
    cons_parser_update = sub_cons_parsers.add_parser("update", aliases=["u"], help="update existing consumable")
    ## Delete Consumable
    cons_parser_delete = sub_cons_parsers.add_parser("delete", aliases=["d"], help="delete existing consumable")

def add_consumable_id_arg(parser : argparse.ArgumentParser, dest : str) -> None:
    parser.add_argument("-i", "--id", type=int, dest=f"{dest}.id", action=SubNamespaceAction, default=argparse.SUPPRESS, help="unique consumable id")

def add_consumable_arguments(parser : argparse.ArgumentParser, dest : str) -> None:
    parser.add_argument("--sid", "--seriesid", type=int, dest=f"{dest}.series_id", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="SERIES_ID", help="unique series id")
    parser.add_argument("-n", "--name", dest=f"{dest}.name", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="NAME", help="consumable name")
    parser.add_argument("-t", "--type", type=str.upper, dest=f"{dest}.type", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="TYPE", help="type of consumable, e.g. Novel, Movie")
    parser.add_argument("-s", "--status", dest=f"{dest}.status", choices=[e.name for e in Status], action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="STATUS", help="progress status")
    parser.add_argument("-p", "--parts", type=int, dest=f"{dest}parts", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="PART", help="e.g. Chapter, Episode")
    parser.add_argument("-c", "--completions", type=int, dest=f"{dest}.completions", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="COMPLETIONS", help="times completed")
    parser.add_argument("-r", "--rating", type=float, dest=f"{dest}.rating", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="RATING", help="numerical score")
    parser.add_argument("--sd", "--startdate", dest=f"{dest}.start_date", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="DATE", help="date of initial start")
    parser.add_argument("--ed", "--enddate", dest=f"{dest}.end_date", action=SubNamespaceAction, default=argparse.SUPPRESS, metavar="DATE", help="date of first completion")

# cons_parser.add_argument("-o", "--order", choices=["id", "type", "name", "rating", "completions", "start_date", "end_date"], default="name", help="order by attribute, used when listing")
# parser.add_argument("-S", "--personnel", dest="personnel", nargs='*', default=[], metavar="ID ROLE", help="list of personnel id (corresponding to existing personnel entities) and role name pairs, e.g. 123 Author 42 Illustrator")
# cons_parser.add_argument("--reverse", action="store_true", help="reverse order of listing")
# cons_parser.add_argument("-c", "--continue", dest="increment", action="store_true", help="increment provided major part and minor part values instead of setting on update")
# cons_parser.add_argument("-f", "--finish", dest="finish", action="store_true", help="finish consuming, setting end date as present date on first completion and adding a completion")

# Personnel Parsing
def add_personnel_parsers(sub_parsers : argparse._SubParsersAction) -> None:
    personnel_parser = sub_parsers.add_parser("personnel", aliases=["p"], help="action on personnel entities")
    personnel_parser.set_defaults(_handler=PersonnelHandler)
    ## New Personnel 
    ## List Personnel 
    ## Update Personnel 
    ## Delete Personnel
    
# personnel_parser.add_argument("-i", "--id", type=int, dest="id", action=SubNamespaceAction, default=argparse.SUPPRESS, help="unique personnel id")
# personnel_parser.add_argument("--fn", "--firstname", dest="first_name", action=SubNamespaceAction, default=argparse.SUPPRESS, help="personnel first name")
# personnel_parser.add_argument("--ln", "--lastname", dest="last_name", action=SubNamespaceAction, default=argparse.SUPPRESS, help="personnel last name")
# personnel_parser.add_argument("--ps", "--pseudonym", dest="pseudonym", action=SubNamespaceAction, default=argparse.SUPPRESS, help="personnel pseudonym")
# # Commands
# personnel_parser.add_argument("-o", "--order", choices=["id", "first_name", "last_name", "pseudonym"], default="first_name", help="order by attribute, used when listing")
# personnel_parser.add_argument("--reverse", action="store_true", help="reverse order of listing")

# Series Parsing
def add_series_parsers(sub_parsers : argparse._SubParsersAction)-> None:
    series_parser = sub_parsers.add_parser("series", aliases=["s"], help="action on series entities")
    series_parser.set_defaults(_handler=SeriesHandler)
    ## New Series
    ## List Series
    ## Update Series
    ## Delete Series