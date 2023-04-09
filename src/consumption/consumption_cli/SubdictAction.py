from argparse import Action, ArgumentParser, Namespace
from typing import Sequence, Any, TypeVar

_T = TypeVar("_T")

class SubdictAction(Action):

    SUBDICT_DEST = "subdict"

    def __call__(self, 
                 parser: ArgumentParser, \
                 namespace: Namespace, \
                 values: str | Sequence[Any] | None, \
                 option_string: str | None = None) -> None:
        if values:
            try:
                subdict = getattr(namespace, self.SUBDICT_DEST)
            except AttributeError:
                subdict = dict()
            subdict[self.dest] = values
            setattr(namespace, self.SUBDICT_DEST, subdict)
        else:
            setattr(namespace, self.SUBDICT_DEST, dict())