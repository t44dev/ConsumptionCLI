# General Imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Tuple
from itertools import count
import curses
from collections.abc import Sequence
from consumptioncli.list_actions import ListAction
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
    LIST_TITLE: str = "List"

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
    def _action_strs(cls, actions: Sequence[list_actions.ListAction]) -> Sequence[str]:
        return [
            f"[{'/'.join(action.key_aliases)}] {action.ACTION_NAME}"
            for action in actions
        ]

    @classmethod
    def _action_str(cls, actions: Sequence[list_actions.ListAction]) -> str:
        return "   ".join(cls._action_strs(actions))

    @classmethod
    def _grouped_action_strs(
        cls, actions: Sequence[list_actions.ListAction], width: int, spacing: int = 3
    ) -> Sequence[Sequence[str]]:
        action_strs = cls._action_strs(actions)
        if len(action_strs) == 0:
            return [[]]

        current_group = 0
        groups = [[action_strs.pop(0)]]
        for action_str in action_strs:
            new_length = (
                sum(map(len, groups[current_group]))
                + len(action_str)
                + spacing * len(groups[current_group])
            )
            if new_length <= width:
                groups[current_group].append(action_str)
            else:
                groups.append([action_str])
                current_group += 1
        return groups

    def _render(
        self,
        headers: Sequence[str],
        body: Sequence[str],
        actions: Sequence[list_actions.ListAction],
    ) -> None:
        window = self.state.window
        instances = self.state.instances
        selected = self.state.selected
        current_index = self.state.current
        window.erase()

        # Title and border
        window.box(0, 0)
        window.addstr(0, 0, truncate(self.LIST_TITLE, self.state.coords.width()))
        BORDER_SIZE = 1
        ## Relative coordinates of inner box
        coords = CursesCoords(
            BORDER_SIZE,
            BORDER_SIZE,
            self.state.coords.width() - BORDER_SIZE,
            self.state.coords.height() - BORDER_SIZE,
        )

        # Render Actions
        action_groups = BaseInstanceList._grouped_action_strs(actions, coords.width())
        action_lines = len(action_groups)
        for line_number, group in enumerate(action_groups):
            action_y = max(coords.y_start, (coords.y_max - action_lines) + line_number)
            if action_y < coords.y_max:
                action_string = "   ".join(group)
                window.addstr(action_y, coords.x_start, action_string)
        coords.delta_y_max(-action_lines - 1)

        # Render Table
        INDENT = 2

        ## Header
        header_lines = 0
        for header_line in headers:
            if header_lines < coords.height():
                header_y = header_lines + coords.y_start
                window.addstr(
                    header_y,
                    INDENT + 1,
                    truncate(header_line, coords.width() - INDENT),
                    curses.A_BOLD,
                )
                header_lines += 1
        coords.delta_y_start(header_lines)

        ## Body
        start_index = max(0, current_index - (coords.height() // 2))
        end_index = min(len(body), start_index + coords.height())
        for i, y_pos in zip(range(start_index, end_index), count(coords.y_start)):
            line = body[i]
            style = curses.A_STANDOUT if instances[i] in selected else curses.A_NORMAL
            if i == self.state.current:
                window.addstr(
                    y_pos,
                    coords.x_start,
                    f"> {truncate(line, coords.width() - 2*INDENT)} <",
                    style,
                )
            else:
                window.addstr(
                    y_pos,
                    coords.x_start + INDENT,
                    truncate(line, coords.width() - INDENT),
                    style,
                )
        window.refresh()

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
    LIST_TITLE: str = "Consumable List"

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
                list_actions.ListViewConsumable(999, ["V"]),
                list_actions.ListConsumableUpdate(899, ["U"]),
                list_actions.ListConsumableDelete(898, ["D"]),
                list_actions.ListIncrementCurrentRating(
                    799, ["L", "KEY_RIGHT"], ["L", "→"]
                ),
                list_actions.ListDecrementCurrentRating(
                    798, ["H", "KEY_LEFT"], ["H", "←"]
                ),
                list_actions.ListTagSelected(699, ["T"]),
                list_actions.ListUntagSelected(698, ["G"]),
                list_actions.ListSetConsumableSeriesSelected(799, ["S"]),
                list_actions.ListAddConsumablePersonnelSelected(798, ["P"]),
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
    LIST_TITLE: str = "Series List"

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
                list_actions.ListViewSeries(999, ["V"]),
                list_actions.ListSeriesUpdate(899, ["U"]),
                list_actions.ListSeriesDelete(898, ["D"]),
                list_actions.ListSetSeriesConsumable(799, ["C"]),
            ]
        super().init_run(actions, coords)

    def tabulate_str(self) -> str:
        instances: Sequence[Series] = self.state.instances
        table_instances = [[row + 1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(table_instances, headers=["#", "ID", "Name"])


class PersonnelList(BaseInstanceList):
    LIST_TITLE: str = "Personnel List"

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
                list_actions.ListViewPersonnel(999, ["V"]),
                list_actions.ListPersonnelUpdate(899, ["U"]),
                list_actions.ListPersonnelDelete(898, ["D"]),
                list_actions.ListAddPersonnelConsumableSelected(799, ["C"]),
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
    def __init__(self, instances: Sequence[DatabaseEntity], header="List") -> None:
        self.LIST_TITLE = header
        super().__init__(instances)

    def tabulate_str(self) -> str:
        return "\n".join(map(str, self.state.instances))

    def tabulate(self) -> Tuple[Sequence[str], Sequence[str]]:
        return ([], [str(c) for c in self.state.instances])
