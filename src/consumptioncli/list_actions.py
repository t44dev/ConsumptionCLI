# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence

from consumptioncli import list_handling

# Consumption Imports
from . import list_handling
from . import cli_handling


# General Actions


class ListAction(ABC):
    ACTION_NAME: str = ""

    def __init__(
        self, priority: int, keys: Sequence[str], key_alises: Sequence[str]
    ) -> None:
        self.priority = priority
        self.keys = [key.upper() for key in keys]
        self.key_aliases = key_alises

    @abstractmethod
    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        pass


class ListUp(ListAction):
    ACTION_NAME: str = "Up"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        state.current = max(state.current - 1, 0)
        return state


class ListDown(ListAction):
    ACTION_NAME: str = "Down"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        state.current = min(state.current + 1, len(state.instances) - 1)
        return state


class ListQuit(ListAction):
    ACTION_NAME: str = "Quit"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        state.active = False
        return state


class ListSelect(ListAction):
    ACTION_NAME: str = "Select"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        if state.instances[state.current] in state.selected:
            state.selected.remove(state.instances[state.current])
        else:
            state.selected.add(state.instances[state.current])
        return state


# Consumable Actions


class ListTagSelected(ListAction):
    ACTION_NAME: str = "Tag Selected"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        list_handling.BaseInstanceList._uninit_curses(state.window)
        cli_handling.ConsumableHandler.do_tag(state.selected)
        state.window = list_handling.BaseInstanceList._init_curses()
        return state
