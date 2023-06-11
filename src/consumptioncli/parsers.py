# General Imports
import argparse

# Package Imports
from consumption.consumption_backend.Database import DatabaseEntity, SQLiteTableInstantiator
from consumption.consumption_backend.Consumable import Consumable, Status
from consumption.consumption_backend.Staff import Staff
from .SubdictAction import SubdictAction
from .CLIHandling import CLIHandler, StaffHandler, ConsumableHandler

main_parser = argparse.ArgumentParser(prog="Consumption CLI")
sub_parsers = main_parser.add_subparsers()

main_parser.set_defaults(_handler=CLIHandler, _ent=DatabaseEntity)
main_parser.add_argument("-c", "--create", action="store_true", dest="create") # This is the default but is added for consistency
main_parser.add_argument("-u", "--update", action="store_true", dest="update")
main_parser.add_argument("-d", "--delete", action="store_true", dest="delete")
main_parser.add_argument("-l", "--list", action="store_true", dest="list")

## Staff
staff_parser = sub_parsers.add_parser("staff", aliases=["s"])
staff_parser.set_defaults(_handler=StaffHandler, _ent=Staff)
staff_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--fn", "--firstname", dest="first_name", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--ln", "--lastname", dest="last_name", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--ps", "--pseudonym", dest="pseudonym", action=SubdictAction, default=argparse.SUPPRESS)
# Commands
staff_parser.add_argument("--order", choices=["id", "first_name", "last_name", "pseudonym"], default="first_name")
staff_parser.add_argument("--reverse", action="store_true")

## Consumable
cons_parser = sub_parsers.add_parser("consumable", aliases=["cons", "c"])
cons_parser.set_defaults(_handler=ConsumableHandler, _ent=Consumable)
cons_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-n", "--name", dest="name", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-t", "--type", type=str.upper, dest="type", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-s", "--status", dest="status", choices=[e.name for e in Status], action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-M", "--major", type=int, dest="major_parts", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-m", "--minor", type=int, dest="minor_parts", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("-r", "--rating", type=float, dest="rating", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("--sd", "--startdate", dest="start_date", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("--ed", "--enddate", dest="end_date", action=SubdictAction, default=argparse.SUPPRESS)
cons_parser.add_argument("--df", "--dateformat", dest="date_format", default="%Y/%m/%d")
cons_parser.add_argument("-S", "--staff", dest="staff", nargs='*', default=[])
# Commands
cons_parser.add_argument("--order", choices=["id", "name", "rating", "completions", "start_date", "end_date"], default="name")
cons_parser.add_argument("--reverse", action="store_true")
cons_parser.add_argument("-c", "--continue", dest="increment", action="store_true")
cons_parser.add_argument("-f", "--finish", dest="finish", action="store_true")

