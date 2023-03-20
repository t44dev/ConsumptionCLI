from .parsers import main_parser

def main():
    args = main_parser.parse_args()
    try:
        print(args._func(**vars(args)))
    except TypeError as e:
        print(e)

if __name__ == "__main__":
    main()