from argparse import ArgumentError
from .parsers import get_main_parser


def main():
    main_parser = get_main_parser()
    args = main_parser.parse_args()
    try:
        print(getattr(args, "handler").handle(args))
        return 0
    except ArgumentError as e:
        main_parser.error(e.message)
    # except Exception as e:
    # main_parser.error(f"Unexpected Error: {e}")


if __name__ == "__main__":
    main()
