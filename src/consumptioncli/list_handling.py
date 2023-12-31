# General Imports
from abc import ABC, abstractmethod
from datetime import datetime
import curses
from collections.abc import Sequence
from tabulate import tabulate
from .utils import truncate

# Consumption Imports
from .curses_handling import init_curses, uninit_curses, new_win, CursesCoords
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
from . import list_actions


class ListState:
    def __init__(self, instances: Sequence[DatabaseEntity]) -> None:
        self.instances = instances
        self.selected = set()
        self.current = 0
        self.window = None
        self.coords = CursesCoords()

    def order_by(self, key: str, reverse: bool = False) -> None:
        # Thanks to Andrew Clark for solution to sorting list with NoneTypes https://stackoverflow.com/a/18411610
        self.instances = sorted(
            self.instances,
            key=lambda a: (getattr(a, key) is not None, getattr(a, key)),
            reverse=reverse,
        )


class BaseInstanceList(ABC):
    def __init__(self, instances: Sequence[DatabaseEntity]) -> None:
        self.state = ListState(instances)

    @abstractmethod
    def tabulate(self) -> str:
        pass

    def init_run(self, actions : Sequence[list_actions.ListAction], coords : CursesCoords = None) -> None:
        init_curses()
        self.run(actions, coords)
        uninit_curses()

    def run(self, actions: Sequence[list_actions.ListAction], coords : CursesCoords = None) -> None:
        # Setup State
        self.state.coords = coords if coords is not None else CursesCoords()
        self.state.window = new_win(self.state.coords)
        actions = BaseInstanceList._setup_actions(actions)
        # Render/Action Loop
        self._handle(actions)

    def _handle(self, actions: Sequence[list_actions.ListAction]) -> None:
        cont = True
        while cont:
            # Render
            self._render(self.tabulate(), actions)
            # Action
            key = self.state.window.getkey().upper()
            for action in actions:
                if key in action.keys:
                    self.state, cont = action.run(self.state)
    
    def _render(self, table: str, actions: Sequence[list_actions.ListAction]) -> None:
        self.state.window.erase()
        # Render Actions
        action_string = "   ".join(
            [
                f"[{'/'.join(action.key_aliases)}] {action.ACTION_NAME}"
                for action in actions
            ]
        )
        action_y = self.state.coords.y_max - 1 - (len(action_string) // self.state.coords.x_max)
        self.state.window.addstr(action_y, 0, action_string)
        # Render Table
        table = table.split("\n")
        headers = table[:2]
        body = table[2:]
        # Header
        self.state.window.addstr(0, 2, truncate(headers[0], self.state.coords.x_max - 2), curses.A_BOLD)
        self.state.window.addstr(1, 2, truncate(headers[1], self.state.coords.x_max - 2), curses.A_BOLD)
        # Body
        lines_before_after = action_y - 4
        start_index = max(0, self.state.current - (lines_before_after // 2))
        difference = start_index - (self.state.current - (lines_before_after // 2))
        end_index = min(
            len(self.state.instances) - 1,
            self.state.current + (lines_before_after // 2) + difference,
        )
        displayed = body[start_index : end_index + 1]
        for i, line in enumerate(displayed):
            true_i = i + start_index
            y_pos = i + 2
            attr = (
                curses.A_STANDOUT
                if self.state.instances[true_i] in self.state.selected
                else curses.A_NORMAL
            )
            if true_i == self.state.current:
                self.state.window.addstr(y_pos, 0, f"> {truncate(line, self.state.coords.x_max - 4)} <", attr)
            else:
                self.state.window.addstr(y_pos, 2, truncate(line, self.state.coords.x_max - 2), attr)
        self.state.window.refresh()

    @classmethod
    def _select_actions(
        cls
    ) -> Sequence[list_actions.ListAction]:
        return [
            list_actions.ListSelect(9997, ["\n", "KEY_ENTER"], ["Enter"]),
            list_actions.ListDeselectAll(9996, ["A"])
        ]

    @classmethod
    def _move_actions(
        cls
    ) -> Sequence[list_actions.ListAction]:
        return [
            list_actions.ListUp(9999, ["K", "KEY_UP"], ["K", "↑"]),
            list_actions.ListDown(9998, ["J", "KEY_DOWN"], ["J", "↓"])
        ]
    
    @classmethod
    def _default_actions(cls):
        return [
            list_actions.ListEnd(-9999, ["Q"]),
            *BaseInstanceList._move_actions(),
            *BaseInstanceList._select_actions()
        ]

    @classmethod
    def _setup_actions(
        cls, actions: Sequence[list_actions.ListAction]
    ) -> Sequence[list_actions.ListAction]:
        actions = sorted(actions, key=lambda x: x.priority, reverse=True)
        return actions

    def order_by(self, key: str, reverse: bool = False) -> None:
        self.state.order_by(key, reverse)


class ConsumableList(BaseInstanceList):
    def __init__(
        self, instances: Sequence[Consumable], date_format: str = r"%Y/%m/%d"
    ) -> None:
        super().__init__(instances)
        self.date_format = date_format

    def init_run(self, actions : Sequence[list_actions.ListAction] = None, coords : CursesCoords = None) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListConsumableUpdate(999, ["U"]),
                list_actions.ListConsumableDelete(998, ["D"]),
                list_actions.ListIncrementCurrentRating(997, ["L", "KEY_RIGHT"], ["L", "→"]),
                list_actions.ListDecrementCurrentRating(997, ["H", "KEY_LEFT"], ["H", "←"]),
                list_actions.ListTagSelected(995, ["T"]),
                list_actions.ListUntagSelected(994, ["G"]),
                list_actions.ListSetConsumableSeriesSelected(993, ["S"]),
                list_actions.ListAddConsumablePersonnelSelected(992, ["P"]),
            ]
        super().init_run(actions, coords)

    def tabulate(self) -> str:
        instances: Sequence[Consumable] = self.state.instances
        table_instances = [
            [
                row + 1,
                i.id,
                i.type,
                truncate(i.name, 50),
                f"{i.parts}/{'?' if i.max_parts is None else i.max_parts}",
                i.rating,
                i.completions,
                i.status.name,
                datetime.fromtimestamp(i.start_date).strftime(self.date_format)
                if i.start_date
                else i.start_date,
                datetime.fromtimestamp(i.end_date).strftime(self.date_format)
                if i.end_date
                else i.end_date,
            ]
            for row, i in enumerate(instances)
        ]
        return tabulate(
            table_instances,
            headers=[
                "#",
                "ID",
                "Type",
                "Name",
                "Parts",
                "Rating",
                "Completions",
                "Status",
                "Started",
                "Completed",
            ],
        )


class SeriesList(BaseInstanceList):
    def __init__(self, instances: Sequence[Series]) -> None:
        super().__init__(instances)

    def init_run(self, actions : Sequence[list_actions.ListAction] = None, coords : CursesCoords = None) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListSeriesUpdate(999, ["U"]),
                list_actions.ListSeriesDelete(998, ["D"]),
                list_actions.ListSetSeriesConsumable(997, ["C"])
            ]
        super().init_run(actions, coords)

    def tabulate(self) -> str:
        instances: Sequence[Series] = self.state.instances
        table_instances = [[row + 1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(table_instances, headers=["#", "ID", "Name"])


class PersonnelList(BaseInstanceList):
    def __init__(self, instances: Sequence[Personnel]) -> None:
        super().__init__(instances)

    def init_run(self, actions : Sequence[list_actions.ListAction] = None, coords : CursesCoords = None) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListPersonnelUpdate(999, ["U"]),
                list_actions.ListPersonnelDelete(998, ["D"]),
                list_actions.ListAddPersonnelConsumableSelected(997, ["C"])
            ]
        super().init_run(actions, coords)

    def tabulate(self) -> str:
        instances: Sequence[Personnel] = self.state.instances
        table_instances = [
            [row + 1, i.id, i.first_name, i.pseudonym, i.last_name]
            for row, i in enumerate(instances)
        ]
        return tabulate(
            table_instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"]
        )
