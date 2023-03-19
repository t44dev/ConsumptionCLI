from .parsers import main_parser

def main():
    args = main_parser.parse_args()
    args._func(*args)

if __name__ == "__main__":
    main()