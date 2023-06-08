# General Imports
import argparse

# Package Imports
from consumption.consumption_backend.Database import DatabaseEntity, SQLiteTableInstantiator
from consumption.consumption_backend.Consumables import Novel
from consumption.consumption_backend.Staff import Staff
from .SubdictAction import SubdictAction
from .CLIHandling import CLIHandler, StaffHandler, ConsumableHandler

main_parser = argparse.ArgumentParser(prog="Consumption CLI")
sub_parsers = main_parser.add_subparsers()

main_parser.set_defaults(_handler=CLIHandler, _ent=DatabaseEntity, _db_instantiator=lambda : None)
main_parser.add_argument("-c", "--create", action="store_true", dest="create") # This is the default but is added for consistency
main_parser.add_argument("-u", "--update", action="store_true", dest="update")
main_parser.add_argument("-d", "--delete", action="store_true", dest="delete")
main_parser.add_argument("-l", "--list", action="store_true", dest="list")

### Staff
staff_parser = sub_parsers.add_parser("staff")
staff_parser.set_defaults(_handler=StaffHandler, _ent=Staff, _db_instantiator=SQLiteTableInstantiator.staff_table)
staff_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--fn", "--firstname", dest="first_name", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--ln", "--lastname", dest="last_name", action=SubdictAction, default=argparse.SUPPRESS)
staff_parser.add_argument("--ps", "--pseudonym", dest="pseudonym", action=SubdictAction, default=argparse.SUPPRESS)
# Commands
staff_parser.add_argument("--order", choices=["id", "first_name", "last_name", "pseudonym"], default="id")
staff_parser.add_argument("--reverse", action="store_true")

### Consumables
## Novel
novel_parser = sub_parsers.add_parser("novel")
novel_parser.set_defaults(_handler=ConsumableHandler, _ent=Novel, _db_instantiator=SQLiteTableInstantiator.novel_table)
novel_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-n", "--name", dest="name", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-v", "--volume", type=int, dest="major_parts", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-c", "--chapter", type=int, dest="minor_parts", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--rate", "--rating", type=float, dest="rating", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--sd", "--startdate", dest="start_date", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--ed", "--enddate", dest="end_date", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-S", "-staff", dest="staff", nargs='*', default=[])
# Commands
novel_parser.add_argument("--order", choices=["id", "name", "rating", "completions", "start_date", "end_date"], default="rating")
novel_parser.add_argument("--reverse", action="store_true")
novel_parser.add_argument("-r", "--read", dest="increment", action="store_true")
novel_parser.add_argument("-f", "--finish", dest="finish", action="store_true")

