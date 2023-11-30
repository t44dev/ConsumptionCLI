from typing import TypeVar, Callable
from collections.abc import Sequence

T = TypeVar("T")


def sort_by(instances: Sequence[T], sort_key: str, reverse: bool = False) -> list[T]:
    # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
    return sorted(
        instances,
        key=lambda a: (getattr(a, sort_key) is not None, getattr(a, sort_key)),
        reverse=reverse,
    )


def request_input(name: str, default: T = None, validator: Callable = None) -> T:
    if default is not None:
        request_string = f"Provide a {name} (Default : {default}): "
    else:
        request_string = f"Provide a {name}: "
    value = input(request_string).strip()
    if default:
        value = value if len(value) else default
    if validator is not None:
        while not validator(value):
            value = input(request_string).strip()
            if default:
                value = value if len(value) else default
    return value


def confirm_action(action: str) -> bool:
    prompt = f"Confirm {action} [Y/n]: "
    response = input(prompt).strip().lower()
    while response not in ["y", "n"]:
        print("Invalid input.")
        response = input(prompt).strip().lower()
    return response == "y"


def truncate(string: str, amount: int = 20) -> str:
    if len(string) > amount:
        diff = min(3, len(string) - amount)
        return string[0:amount] + "." * diff
    else:
        return string
