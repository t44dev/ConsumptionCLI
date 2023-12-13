# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence

from consumptioncli import list_handling

# Consumption Imports
from consumptionbackend.Consumable import Consumable
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
from . import list_handling
from . import cli_handling
from .utils import confirm_action, request_input


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


class ListEnd(ListAction):
    def __init__(
        self,
        priority: int,
        keys: Sequence[str],
        key_alises: Sequence[str] = None,
        *args,
        action_name: str = "Quit",
    ) -> None:
        super().__init__(priority, keys, key_alises)
        self.ACTION_NAME = action_name

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


class ListSelectEnd(ListSelect):
    ACTION_NAME: str = "Select and Confirm"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        state.active = False
        return super().run(state)


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


class ListSetSeriesSelected(ListAction):
    ACTION_NAME: str = "Set Selected Series"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        # Uninit current list
        list_handling.BaseInstanceList._uninit_curses(state.window)
        # Get Series
        series_list = list_handling.SeriesList(Series.find())
        series_list.state.order_by("name")
        actions = series_list._setup_actions(
            series_list._add_move_actions(
                [
                    ListSelectEnd(-998, ["\n", "KEY_ENTER"], ["Enter"]),
                    ListEnd(-999, ["Q"]),
                ]
            )
        )
        series_list.state.window = series_list._init_curses()
        series_list._run(actions)
        series_list._uninit_curses(series_list.state.window)
        # Assign Series
        if len(series_list.state.selected) == 1:
            selected_consumables: Sequence[Consumable] = state.selected
            selected_series: Series = series_list.state.selected.pop()
            for consumable in selected_consumables:
                consumable.set_series(selected_series)
        # Restore state and return
        state.window = list_handling.BaseInstanceList._init_curses()
        return state


class ListPersonnelSelected(ListAction):
    ACTION_NAME: str = "Add Selected Personnel"

    def run(self, state: list_handling.ListState) -> list_handling.ListState:
        # Uninit current list
        list_handling.BaseInstanceList._uninit_curses(state.window)
        # Get Personnel to add
        personnel_list = list_handling.PersonnelList(Personnel.find())
        personnel_list.state.order_by("first_name")
        actions = personnel_list._setup_actions(
            personnel_list._add_move_actions(
                personnel_list._add_select_actions(
                    [ListEnd(-9999, keys=["C"], action_name="Confirm Selection")]
                )
            )
        )
        personnel_list.state.window = personnel_list._init_curses()
        personnel_list._run(actions)
        selected_personnel: Sequence[Personnel] = personnel_list.state.selected
        personnel_list._uninit_curses(personnel_list.state.window)
        # Get roles and assign
        selected_consumables: Sequence[Consumable] = state.selected
        for personnel in selected_personnel:
            personnel.role = request_input(f"role of {personnel}")
            for consumable in selected_consumables:
                consumable.add_personnel(personnel)
        # Restore state and return
        state.window = list_handling.BaseInstanceList._init_curses()
        return state
