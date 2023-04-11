from .parsers import main_parser

def main():
    args = main_parser.parse_args()
    if "subdict" not in args:   # Default value is empty dict, see SubdictAction.py
        setattr(args, "subdict", dict())
    print(args._func(main_parser, **vars(args)))

if __name__ == "__main__":
    main()