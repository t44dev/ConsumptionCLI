# General Imports
import argparse

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable, Status
from consumptionbackend.Staff import Staff
from .SubdictAction import SubdictAction
from .CLIHandling import CLIHandler, StaffHandler, ConsumableHandler

main_parser = argparse.ArgumentParser(prog="Consumption CLI", description="A CLI tool for tracking media consumption")
sub_parsers = main_parser.add_subparsers()

main_parser.set_defaults(_handler=CLIHandler, _ent=DatabaseEntity)
main_parser.add_argument("-c", "--create", action="store_true", dest="create", help="create a new entity")
main_parser.add_argument("-u", "--update", action="store_true", dest="update", help="update an existing entity by its id")
main_parser.add_argument("-d", "--delete", action="store_true", dest="delete", help="delete an entity by its id")
main_parser.add_argument("-l", "--list", action="store_true", dest="list", help="list entities with some search conditions")

## Staff
staff_parser = sub_parsers.add_parser("staff", aliases=["s"], help="action on staff entities")
staff_parser.set_defaults(_handler=StaffHandler, _ent=Staff)
staff_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS, help="unique staff id")
staff_parser.add_argument("--fn", "--firstname", dest="first_name", action=SubdictAction, default=argparse.SUPPRESS, help="staff first name")
staff_parser.add_argument("--ln", "--lastname", dest="last_name", action=SubdictAction, default=argparse.SUPPRESS, help="staff last name")
staff_parser.add_argument("--ps", "--pseudonym", dest="pseudonym", action=SubdictAction, default=argparse.SUPPRESS, help="staff pseudonym")
# Commands
staff_parser.add_argument("-o", "--order", choices=["id", "first_name", "last_name", "pseudonym"], default="first_name", help="order by attribute, used when listing")
staff_parser.add_argument("--reverse", action="store_true", help="reverse order of listing")

## Consumable
cons_parser = sub_parsers.add_parser("consumable", aliases=["c"], help="action on consumable entities")
cons_parser.set_defaults(_handler=ConsumableHandler, _ent=Consumable)
cons_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS, help="unique consumable id")
cons_parser.add_argument("-t", "--type", type=str.upper, dest="type", action=SubdictAction, default=argparse.SUPPRESS, help="type of consumable, e.g. Novel, Movie")
cons_parser.add_argument("-n", "--name", dest="name", action=SubdictAction, default=argparse.SUPPRESS, help="consumable name")
cons_parser.add_argument("-s", "--status", dest="status", choices=[e.name for e in Status], action=SubdictAction, default=argparse.SUPPRESS, help="progress status")
cons_parser.add_argument("-M", "--major", type=int, dest="major_parts", action=SubdictAction, default=argparse.SUPPRESS, metavar="MAJOR", help="e.g. Volume, Season")
cons_parser.add_argument("-m", "--minor", type=int, dest="minor_parts", action=SubdictAction, default=argparse.SUPPRESS, metavar="MINOR", help="e.g. Chapter, Episode")
cons_parser.add_argument("-r", "--rating", type=float, dest="rating", action=SubdictAction, default=argparse.SUPPRESS, help="numerical score")
cons_parser.add_argument("--completions", type=int, dest="completions", action=SubdictAction, default=argparse.SUPPRESS, help="times completed")
cons_parser.add_argument("--sd", "--startdate", dest="start_date", action=SubdictAction, default=argparse.SUPPRESS, metavar="DATE", help="date of initial start")
cons_parser.add_argument("--ed", "--enddate", dest="end_date", action=SubdictAction, default=argparse.SUPPRESS, metavar="DATE", help="date of first completion")
cons_parser.add_argument("--df", "--dateformat", dest="date_format", default=r"%Y/%m/%d", metavar="FORMAT", help="date format string, e.g %%Y/%%m/%%d")
cons_parser.add_argument("-S", "--staff", dest="staff", nargs='*', default=[], metavar="ID ROLE", help="list of staff id (corresponding to existing staff entities) and role name pairs, e.g. 123 Author 42 Illustrator")
# Commands
cons_parser.add_argument("-o", "--order", choices=["id", "type", "name", "rating", "completions", "start_date", "end_date"], default="name", help="order by attribute, used when listing")
cons_parser.add_argument("--reverse", action="store_true", help="reverse order of listing")
cons_parser.add_argument("-c", "--continue", dest="increment", action="store_true", help="increment provided major part and minor part values instead of setting on update")
cons_parser.add_argument("-f", "--finish", dest="finish", action="store_true", help="finish consuming, setting end date as present date on first completion and adding a completion")

