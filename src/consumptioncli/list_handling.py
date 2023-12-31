# General Imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple
from itertools import count
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
    def tabulate_str(self) -> str:
        pass

    def tabulate(self) -> Tuple[Sequence[str], Sequence[str]]:
        table = self.tabulate_str().split("\n")
        return (table[:2], table[2:])

    def init_run(
        self, actions: Sequence[list_actions.ListAction], coords: CursesCoords = None
    ) -> None:
        init_curses()
        self.run(actions, coords)
        uninit_curses()

    def run(
        self, actions: Sequence[list_actions.ListAction], coords: CursesCoords = None
    ) -> None:
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
            headers, body = self.tabulate()
            self._render(headers, body, actions)
            # Action
            key = self.state.window.getkey().upper()
            for action in actions:
                if key in action.keys:
                    self.state, cont = action.run(self.state)

    @classmethod
    def _action_str(cls, actions: Sequence[list_actions.ListAction]) -> str:
        return "   ".join(
            [
                f"[{'/'.join(action.key_aliases)}] {action.ACTION_NAME}"
                for action in actions
            ]
        )

    def _render(
        self,
        headers: Sequence[str],
        body: Sequence[str],
        actions: Sequence[list_actions.ListAction],
    ) -> None:
        window = self.state.window
        x_max, y_max = self.state.coords.x_max, self.state.coords.y_max
        window.erase()

        # Render Actions
        action_string = BaseInstanceList._action_str(actions)
        action_lines = len(action_string) // x_max
        action_y = y_max - 1 - action_lines
        window.addstr(action_y, 0, action_string)

        # Render Table
        header_lines = 0
        INDENT = 2
        ## Header
        for header_line in headers:
            window.addstr(
                header_lines,
                INDENT,
                truncate(header_line, x_max - INDENT),
                curses.A_BOLD,
            )
            header_lines += 1

        ## Body
        remaining_lines = y_max - header_lines - action_lines - 2
        start_index = max(0, self.state.current - (remaining_lines // 2))
        for i, y_pos in zip(
            range(start_index, start_index + remaining_lines), count(header_lines)
        ):
            line = body[i]
            style = (
                curses.A_STANDOUT
                if self.state.instances[i] in self.state.selected
                else curses.A_NORMAL
            )
            if i == self.state.current:
                self.state.window.addstr(
                    y_pos,
                    0,
                    f"> {truncate(line, self.state.coords.x_max - 2*INDENT)} <",
                    style,
                )
            else:
                self.state.window.addstr(
                    y_pos,
                    INDENT,
                    truncate(line, self.state.coords.x_max - INDENT),
                    style,
                )
        self.state.window.refresh()

    @classmethod
    def _select_actions(cls) -> Sequence[list_actions.ListAction]:
        return [
            list_actions.ListSelect(9997, ["\n", "KEY_ENTER"], ["Enter"]),
            list_actions.ListDeselectAll(9996, ["A"]),
        ]

    @classmethod
    def _move_actions(cls) -> Sequence[list_actions.ListAction]:
        return [
            list_actions.ListUp(9999, ["K", "KEY_UP"], ["K", "↑"]),
            list_actions.ListDown(9998, ["J", "KEY_DOWN"], ["J", "↓"]),
        ]

    @classmethod
    def _default_actions(cls):
        return [
            list_actions.ListEnd(-9999, ["Q"]),
            *BaseInstanceList._move_actions(),
            *BaseInstanceList._select_actions(),
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

    def init_run(
        self,
        actions: Sequence[list_actions.ListAction] = None,
        coords: CursesCoords = None,
    ) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListConsumableUpdate(999, ["U"]),
                list_actions.ListConsumableDelete(998, ["D"]),
                list_actions.ListIncrementCurrentRating(
                    997, ["L", "KEY_RIGHT"], ["L", "→"]
                ),
                list_actions.ListDecrementCurrentRating(
                    997, ["H", "KEY_LEFT"], ["H", "←"]
                ),
                list_actions.ListTagSelected(995, ["T"]),
                list_actions.ListUntagSelected(994, ["G"]),
                list_actions.ListSetConsumableSeriesSelected(993, ["S"]),
                list_actions.ListAddConsumablePersonnelSelected(992, ["P"]),
            ]
        super().init_run(actions, coords)

    def tabulate_str(self) -> str:
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

    def init_run(
        self,
        actions: Sequence[list_actions.ListAction] = None,
        coords: CursesCoords = None,
    ) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListSeriesUpdate(999, ["U"]),
                list_actions.ListSeriesDelete(998, ["D"]),
                list_actions.ListSetSeriesConsumable(997, ["C"]),
            ]
        super().init_run(actions, coords)

    def tabulate_str(self) -> str:
        instances: Sequence[Series] = self.state.instances
        table_instances = [[row + 1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(table_instances, headers=["#", "ID", "Name"])


class PersonnelList(BaseInstanceList):
    def __init__(self, instances: Sequence[Personnel]) -> None:
        super().__init__(instances)

    def init_run(
        self,
        actions: Sequence[list_actions.ListAction] = None,
        coords: CursesCoords = None,
    ) -> None:
        if actions is None:
            actions = [
                *BaseInstanceList._default_actions(),
                list_actions.ListPersonnelUpdate(999, ["U"]),
                list_actions.ListPersonnelDelete(998, ["D"]),
                list_actions.ListAddPersonnelConsumableSelected(997, ["C"]),
            ]
        super().init_run(actions, coords)

    def tabulate_str(self) -> str:
        instances: Sequence[Personnel] = self.state.instances
        table_instances = [
            [row + 1, i.id, i.first_name, i.pseudonym, i.last_name]
            for row, i in enumerate(instances)
        ]
        return tabulate(
            table_instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"]
        )


class MiniInstanceList(BaseInstanceList):
    def tabulate_str(self) -> str:
        return "\n".join(map(str, self.state.instances))

    def tabulate(self) -> Tuple[Sequence[str], Sequence[str]]:
        return ([], [str(c for c in self.state.instances)])
