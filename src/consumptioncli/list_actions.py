# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Tuple
from collections.abc import Sequence

from consumptioncli import list_handling

# Consumption Imports
from consumptionbackend.Consumable import Consumable
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
from . import list_handling
from . import cli_handling
from .utils import confirm_action, request_input
from .curses_handling import init_curses, uninit_curses
from . import details_handling


def reinit_decorator(f):
    def wrapper(*args, **kwargs):
        uninit_curses()
        result = f(*args, **kwargs)
        init_curses()
        return result

    return wrapper


def new_current(state: list_handling.ListState):
    return max(0, min(state.current, len(state.instances) - 1))


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
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        pass


class ListUp(ListAction):
    ACTION_NAME: str = "Up"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        state.current = max(state.current - 1, 0)
        return state, True


class ListDown(ListAction):
    ACTION_NAME: str = "Down"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        state.current = max(0, min(state.current + 1, len(state.instances) - 1))
        return state, True


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

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        return state, False


class ListSelect(ListAction):
    ACTION_NAME: str = "Select"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            if state.instances[state.current] in state.selected:
                state.selected.remove(state.instances[state.current])
            else:
                state.selected.add(state.instances[state.current])
        return state, True


class ListSelectEnd(ListSelect):
    ACTION_NAME: str = "Select and Confirm"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        return super().run(state)[0], False


class ListDeselectAll(ListAction):
    ACTION_NAME: str = "Deselect All"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        state.selected = set()
        return state, True


# Consumable Actions


class ListConsumableUpdate(ListAction):
    ACTION_NAME: str = "Update Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        updates = cli_handling.ConsumableHandler.update_fields(
            state.selected, force=True
        )
        for i, cons in enumerate(state.instances):
            for updated in updates:
                if cons == updated:
                    state.instances[i] = updated
                    break
        state.selected = set(updates)
        return state, True


class ListConsumableDelete(ListAction):
    ACTION_NAME: str = "Delete Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if confirm_action("deletion of selected Consumable(s)"):
            cli_handling.ConsumableHandler.do_delete(state.selected, force=True)
        state.instances = list(
            filter(lambda x: x not in state.selected, state.instances)
        )
        state.selected = set()
        state.current = new_current(state)
        return state, True


class ListIncrementCurrentRating(ListAction):
    ACTION_NAME: str = "Increment Rating"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            cons: Consumable = state.instances[state.current]
            new_rating = 0.1 if cons.rating is None else min(10, cons.rating + 0.1)
            if new_rating != cons.rating:
                new_cons = cons.update_self({"rating": new_rating})
                state.instances[state.current] = new_cons
        return state, True


class ListDecrementCurrentRating(ListAction):
    ACTION_NAME: str = "Decrement Rating"

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            cons: Consumable = state.instances[state.current]
            new_rating = (
                None
                if cons.rating is None or cons.rating <= 0.15
                else max(0, cons.rating - 0.1)
            )
            if new_rating != cons.rating:
                new_cons = cons.update_self({"rating": new_rating})
                state.instances[state.current] = new_cons
        return state, True


class ListTagSelected(ListAction):
    ACTION_NAME: str = "Tag Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        cli_handling.ConsumableHandler.do_tag(state.selected, force=True)
        return state, True


class ListUntagSelected(ListAction):
    ACTION_NAME: str = "Untag Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        cli_handling.ConsumableHandler.do_untag(state.selected, force=True)
        return state, True


class ListSetConsumableSeriesSelected(ListAction):
    ACTION_NAME: str = "Set Selected Series"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        # Get Series
        series_list = list_handling.SeriesList(Series.find())
        series_list.order_by("name")
        actions = [
            *series_list._move_actions(),
            ListSelectEnd(-998, ["\n", "KEY_ENTER"], ["Enter"]),
            ListEnd(-999, ["Q"]),
        ]
        series_list.init_run(actions)
        # Assign Series
        if len(series_list.state.selected) == 1:
            selected_consumables: Sequence[Consumable] = state.selected
            selected_series: Series = series_list.state.selected.pop()
            for consumable in selected_consumables:
                consumable.set_series(selected_series)
        return state, True


class ListAddConsumablePersonnelSelected(ListAction):
    ACTION_NAME: str = "Add Personnel to Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        # Get Personnel to add
        personnel_list = list_handling.PersonnelList(Personnel.find())
        personnel_list.order_by("first_name")
        actions = [
            *personnel_list._move_actions(),
            *personnel_list._select_actions(),
            ListEnd(-9999, keys=["C"], action_name="Confirm Selection"),
        ]
        personnel_list.init_run(actions)
        selected_personnel: Sequence[Personnel] = personnel_list.state.selected
        # Get roles and assign
        selected_consumables: Sequence[Consumable] = state.selected
        for personnel in selected_personnel:
            personnel.role = request_input(f"role of {personnel}")
            for consumable in selected_consumables:
                consumable.add_personnel(personnel)
        return state, True


class ListViewConsumable(ListAction):
    ACTION_NAME: str = "View Info"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            details_handling.ConsumableDetailWindow(
                state.instances[state.current]
            ).init_run()
        return state, True


class ListRemoveSelectedPersonnel(ListAction):
    ACTION_NAME: str = "Remove Selected"

    def __init__(
        self,
        instance: Consumable,
        priority: int,
        keys: Sequence[str],
        key_alises: Sequence[str] = None,
    ) -> None:
        self.instance = instance
        super().__init__(priority, keys, key_alises)

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        for personnel in state.selected:
            self.instance.remove_personnel(personnel)
            for i, other_personnel in enumerate(state.instances):
                if (
                    personnel == other_personnel
                    and personnel.role == other_personnel.role
                ):
                    state.instances.pop(i)
        state.selected = set()
        state.current = new_current(state)
        return state, True


# Series Actions


class ListSeriesUpdate(ListAction):
    ACTION_NAME: str = "Update Current"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            current_instance = state.instances[state.current]
            updated_instance = cli_handling.SeriesHandler.update_fields(
                [current_instance], force=True
            )[0]
            state.instances[state.current] = updated_instance
            if current_instance in state.selected:
                state.selected.remove(current_instance)
                state.selected.add(updated_instance)
        return state, True


class ListSeriesDelete(ListAction):
    ACTION_NAME: str = "Delete Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if confirm_action("deletion of selected Series"):
            cli_handling.SeriesHandler.do_delete(state.selected, force=True)
        state.instances = list(
            filter(lambda x: x not in state.selected, state.instances)
        )
        state.selected = set()
        state.current = new_current(state)
        return state, True


class ListSetSeriesConsumable(ListAction):
    ACTION_NAME: str = "Add Consumables"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            # Get Consumables
            consumable_list = list_handling.ConsumableList(Consumable.find())
            consumable_list.order_by("name")
            actions = [
                *consumable_list._move_actions(),
                *consumable_list._select_actions(),
                ListEnd(-999, ["C"], action_name="Confirm Selection"),
            ]
            consumable_list.init_run(actions)
            selected_consumables: Sequence[Consumable] = consumable_list.state.selected
            # Assign Series
            selected_series: Series = state.instances[state.current]
            for consumable in selected_consumables:
                consumable.set_series(selected_series)
        return state, True


class ListViewSeries(ListAction):
    ACTION_NAME: str = "View Info"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            details_handling.SeriesDetailWindow(
                state.instances[state.current]
            ).init_run()
        return state, True


class ListRemoveSelectedSeriesConsumable(ListAction):
    ACTION_NAME: str = "Remove Selected"

    def __init__(
        self,
        instance: Series,
        priority: int,
        keys: Sequence[str],
        key_alises: Sequence[str] = None,
    ) -> None:
        self.instance = instance
        super().__init__(priority, keys, key_alises)

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        for consumable in state.selected:
            consumable.set_series(Series.find(id=-1)[0])
            state.instances.remove(consumable)

        state.selected = set()
        state.current = new_current(state)
        return state, True


# Personnel Actions


class ListPersonnelUpdate(ListAction):
    ACTION_NAME: str = "Update Current"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            current_instance = state.instances[state.current]
            updated_instance = cli_handling.PersonnelHandler.update_fields(
                [current_instance], force=True
            )[0]
            state.instances[state.current] = updated_instance
            if current_instance in state.selected:
                state.selected.remove(current_instance)
                state.selected.add(updated_instance)
        return state, True


class ListPersonnelDelete(ListAction):
    ACTION_NAME: str = "Delete Selected"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if confirm_action("deletion of selected Personnel"):
            cli_handling.PersonnelHandler.do_delete(state.selected, force=True)
        state.instances = list(
            filter(lambda x: x not in state.selected, state.instances)
        )
        state.selected = set()
        state.current = new_current(state)
        return state, True


class ListAddPersonnelConsumableSelected(ListAction):
    ACTION_NAME: str = "Add Selected to Consumables"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        # Get Consumables to add
        consumable_list = list_handling.ConsumableList(Consumable.find())
        consumable_list.state.order_by("name")
        actions = [
            *consumable_list._move_actions(),
            *consumable_list._select_actions(),
            ListEnd(-9999, keys=["C"], action_name="Confirm Selection"),
        ]
        consumable_list.init_run(actions)
        selected_consumables: Sequence[Consumable] = consumable_list.state.selected
        # Get roles and assign
        selected_personnel: Sequence[Personnel] = state.selected
        for personnel in selected_personnel:
            personnel.role = request_input(f"role of {personnel}")
            for consumable in selected_consumables:
                consumable.add_personnel(personnel)
        return state, True


class ListViewPersonnel(ListAction):
    ACTION_NAME: str = "View Info"

    @reinit_decorator
    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if len(state.instances) > 0:
            details_handling.PersonnelDetailWindow(
                state.instances[state.current]
            ).init_run()
        return state, True


class ListRemoveSelectedPersonnelConsumable(ListAction):
    ACTION_NAME: str = "Remove Selected"

    def __init__(
        self,
        instance: Personnel,
        priority: int,
        keys: Sequence[str],
        key_alises: Sequence[str] = None,
    ) -> None:
        self.instance = instance
        super().__init__(priority, keys, key_alises)

    def run(
        self, state: list_handling.ListState
    ) -> Tuple[list_handling.ListState, bool]:
        if self.instance.role is not None:
            for consumable in state.selected:
                consumable.remove_personnel(self.instance)
                state.instances.remove(consumable)

            state.selected = set()
            state.current = new_current(state)
        return state, True
