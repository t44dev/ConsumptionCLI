# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence

from consumptioncli import list_handling

# Consumption Imports
from consumptionbackend.Consumable import Consumable
from . import list_handling
from . import cli_handling
from .utils import confirm_action


# General Actions


class ListAction(ABC):
    ACTION_NAME: str = ""

    def __init__(
        self, priority: int, keys: Sequence[str], key_alises: Sequence[str] = None
    ) -> None:
        self.priority = priority
        self.keys = [key.upper() for key in keys]
        self.key_aliases = self.keys if key_alises is None else key_alises

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


class ListDeselectAll(ListAction):
    ACTION_NAME: str = "Deselect All"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        state.selected = set()
        return state


# Consumable Actions


class ListConsumableUpdate(ListAction):
    ACTION_NAME: str = "Update Selected"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        list_handling.BaseInstanceList._uninit_curses(state.window)
        updates = cli_handling.ConsumableHandler.update_fields(
            state.selected, force=True
        )
        for i, cons in enumerate(state.instances):
            for updated in updates:
                if cons == updated:
                    state.instances[i] = updated
                    break
        state.selected = set(updates)
        state.window = list_handling.BaseInstanceList._init_curses()
        return state


class ListConsumableDelete(ListAction):
    ACTION_NAME: str = "Delete Selected"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        list_handling.BaseInstanceList._uninit_curses(state.window)
        if confirm_action("deletion of selected Consumable(s)"):
            cli_handling.ConsumableHandler.do_delete(state.selected, force=True)
        state.instances = list(
            filter(lambda x: x not in state.selected, state.instances)
        )
        state.selected = set()
        state.current = min(len(state.instances) - 1, state.current)
        state.window = list_handling.BaseInstanceList._init_curses()
        return state


class ListIncrementCurrentRating(ListAction):
    ACTION_NAME: str = "Increment Rating"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        cons: Consumable = state.instances[state.current]
        new_rating = 0.1 if cons.rating is None else min(10, cons.rating + 0.1)
        if new_rating != cons.rating:
            new_cons = cons.update_self({"rating": new_rating})
            state.instances[state.current] = new_cons
        return state


class ListDecrementCurrentRating(ListAction):
    ACTION_NAME: str = "Decrement Rating"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        cons: Consumable = state.instances[state.current]
        new_rating = (
            None
            if cons.rating is None or cons.rating <= 0.15
            else max(0, cons.rating - 0.1)
        )
        if new_rating != cons.rating:
            new_cons = cons.update_self({"rating": new_rating})
            state.instances[state.current] = new_cons
        return state


class ListTagSelected(ListAction):
    ACTION_NAME: str = "Tag Selected"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        list_handling.BaseInstanceList._uninit_curses(state.window)
        cli_handling.ConsumableHandler.do_tag(state.selected, force=True)
        state.window = list_handling.BaseInstanceList._init_curses()
        return state


class ListUntagSelected(ListAction):
    ACTION_NAME: str = "Untag Selected"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        list_handling.BaseInstanceList._uninit_curses(state.window)
        cli_handling.ConsumableHandler.do_untag(state.selected, force=True)
        state.window = list_handling.BaseInstanceList._init_curses()
        return state
