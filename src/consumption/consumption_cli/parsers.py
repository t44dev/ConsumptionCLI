import argparse
from .consumable_funcs import novel
from .creator_funcs import author

main_parser = argparse.ArgumentParser(prog="Consumption CLI")
sub_parsers = main_parser.add_subparsers()

# Need to specify _func for main parser otherwise errors on no type specification
# >>consumption // improper usage
# >>consumption {create, update, delete, list} {novel, author, movie...} // proper usage
def main_parser_func(*args, _message : str, **kwargs):
    raise TypeError(_message)
main_parser.set_defaults(_message="No type specified.", _func=main_parser_func)

### Consumables
## Novel
novel_parser = sub_parsers.add_parser("novel")
novel_parser.set_defaults(_func = novel)

### Creators
## Author
author_parser = sub_parsers.add_parser("author")
author_parser.set_defaults(_func = author)
