# General Imports
import argparse

# Package Imports
from .SubdictAction import SubdictAction
from .consumable_funcs import novel
from .creator_funcs import author

main_parser = argparse.ArgumentParser(prog="Consumption CLI")
sub_parsers = main_parser.add_subparsers()

def main_parser_func(*args, **kwargs):
    raise NotImplementedError()

main_parser.set_defaults(_func=main_parser_func)
main_parser.add_argument("-c", "--create", action="store_true", dest="create") # This is the default but is added for consistency
main_parser.add_argument("-u", "--update", action="store_true", dest="update")
main_parser.add_argument("-d", "--delete", action="store_true", dest="delete")
main_parser.add_argument("-l", "--list", action="store_true", dest="list")

### Consumables
## Novel
novel_parser = sub_parsers.add_parser("novel")
novel_parser.set_defaults(_func = novel)
novel_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-n", "--name", dest="name", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-v", "--volume", type=int, dest="major_parts", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-c", "--chapter", type=int, dest="minor_parts", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--rate", "--rating", type=float, dest="rating", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--sd", "--startdate", dest="start_date", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("--ed", "--enddate", dest="end_date", action=SubdictAction, default=argparse.SUPPRESS)
novel_parser.add_argument("-a", "--authorid", dest="author_id", action=SubdictAction, default=argparse.SUPPRESS)
# Commands
novel_parser.add_argument("--order", choices=["id", "name", "rating", "completions", "start_date", "end_date"], default="rating")
novel_parser.add_argument("--reverse", action="store_true")
novel_parser.add_argument("-r", "--read", dest="read", action="store_true")
novel_parser.add_argument("-f", "--finish", dest="finish", action="store_true")

### Creators
## Author
author_parser = sub_parsers.add_parser("author")
author_parser.set_defaults(_func = author)
author_parser.add_argument("-i", "--id", type=int, dest="id", action=SubdictAction, default=argparse.SUPPRESS)
author_parser.add_argument("--fn", "--firstname", dest="first_name", action=SubdictAction, default=argparse.SUPPRESS)
author_parser.add_argument("--ln", "--lastname", dest="last_name", action=SubdictAction, default=argparse.SUPPRESS)
author_parser.add_argument("--ps", "--pseudonym", dest="pseudonym", action=SubdictAction, default=argparse.SUPPRESS)
# Commands
author_parser.add_argument("--order", choices=["id", "first_name", "last_name", "pseudonym"], default="id")
author_parser.add_argument("--reverse", action="store_true")