from argparse import ArgumentError
from .parsers import main_parser
from consumptionbackend.Database import SQLiteTableInstantiator

def main():
    args = vars(main_parser.parse_args())
    subdict = args.pop("subdict") if "subdict" in args else dict() # Default value is empty dict, see SubdictAction.py
    try:
        SQLiteTableInstantiator.run()
        print(args["_handler"].handle(args["_ent"], subdict, **args))
    except ArgumentError as e:
        main_parser.error(e.message)

if __name__ == "__main__":
    main()