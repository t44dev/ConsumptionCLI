import argparse
from .consumable_funcs import novel
from .creator_funcs import author

main_parser = argparse.ArgumentParser(prog="Consumption CLI")
sub_parsers = main_parser.add_subparsers()

## Consumables
# Novel
novel_parser = sub_parsers.add_parser("novel")
novel_parser.set_defaults(_func = novel)

## Creators
author_parser = sub_parsers.add_parser("author")
author_parser.set_defaults(_func = author)