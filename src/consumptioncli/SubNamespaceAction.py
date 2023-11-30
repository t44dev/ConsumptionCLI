from argparse import Action, ArgumentParser, FileType, Namespace
from collections.abc import Callable, Iterable, Sequence
from typing import Any

_T = Any

# Thanks to hpaulj for the main ideas around this implementation https://stackoverflow.com/a/18677482


class SubNamespaceAction(Action):
    def __init__(
        self,
        option_strings: Sequence[str],
        dest: str,
        nargs: int | str | None = None,
        const: _T | None = None,
        default: _T | str | None = None,
        type: Callable[[str], _T] | FileType | None = None,
        choices: Iterable[_T] | None = None,
        required: bool = False,
        help: str | None = None,
        metavar: str | tuple[str, ...] | None = None,
    ) -> None:
        super().__init__(
            option_strings,
            dest,
            nargs,
            const,
            default,
            type,
            choices,
            required,
            help,
            metavar,
        )

    def __call__(
        self,
        parser: ArgumentParser,
        namespace: Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        dests = self.dest.split(".")
        dest = dests.pop()
        current = namespace
        for name in dests:
            if name in current:
                current = getattr(current, name)
            else:
                setattr(current, name, Namespace())
                current = getattr(current, name)
        setattr(current, dest, values)
