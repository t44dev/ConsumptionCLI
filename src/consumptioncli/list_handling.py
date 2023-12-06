# General Imports
from abc import ABC, abstractmethod
from datetime import datetime
import curses
from collections.abc import Sequence
from tabulate import tabulate
from .utils import truncate

# Consumption Imports
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
        self.active = True
        self.window = None


class BaseInstanceList(ABC):
    def __init__(self, instances: Sequence[DatabaseEntity]) -> None:
        self.state = ListState(instances)

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def tabulate(self) -> str:
        pass

    @classmethod
    def _init_curses(self):
        window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        window.keypad(True)
        return window

    @classmethod
    def _uninit_curses(self, window):
        curses.echo()
        curses.nocbreak()
        curses.curs_set(True)
        window.keypad(False)
        curses.endwin()

    def _init_run(self, actions: Sequence[list_actions.ListAction]) -> None:
        # Setup State
        actions = BaseInstanceList._setup_actions(actions)
        self.state.window = BaseInstanceList._init_curses()
        # Render/Action Loop
        self._run(actions)
        # Reset State
        BaseInstanceList._uninit_curses(self.state.window)

    def _run(self, actions: Sequence[list_actions.ListAction]) -> None:
        while self.state.active:
            # Render
            self._render(self.tabulate(), actions)
            # Action
            key = self.state.window.getkey().upper()
            for action in actions:
                for action_key in action.keys:
                    if key == action_key:
                        self.state = action.run(self.state)

    def _render(self, table: str, actions: Sequence[list_actions.ListAction]) -> None:
        self.state.window.erase()
        # Render Actions
        action_string = "   ".join(
            [
                f"[{'/'.join(action.key_aliases)}] {action.ACTION_NAME}"
                for action in actions
            ]
        )
        action_y = curses.LINES - 1 - (len(action_string) // curses.COLS)
        self.state.window.addstr(action_y, 0, action_string)
        # Render Table
        table = table.split("\n")
        headers = table[:2]
        body = table[2:]
        # Header
        self.state.window.addstr(0, 2, headers[0], curses.A_BOLD)
        self.state.window.addstr(1, 2, headers[1], curses.A_BOLD)
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
                self.state.window.addstr(y_pos, 0, f"> {line} <", attr)
            else:
                self.state.window.addstr(y_pos, 2, line, attr)
        self.state.window.refresh()

    @classmethod
    def _setup_actions(
        cls, actions: Sequence[list_actions.ListAction]
    ) -> Sequence[list_actions.ListAction]:
        actions.append(list_actions.ListUp(9999, ["K", "KEY_UP"], ["K", "↑"]))
        actions.append(list_actions.ListDown(9998, ["J", "KEY_DOWN"], ["J", "↓"]))
        actions.append(list_actions.ListSelect(9997, ["\n", "KEY_ENTER"], ["Enter"]))
        actions.append(list_actions.ListDeselectAll(9996, ["A"]))
        actions.append(list_actions.ListQuit(-9999, ["Q"]))
        actions = sorted(actions, key=lambda x: x.priority, reverse=True)
        return actions


class ConsumableList(BaseInstanceList):
    def __init__(
        self, instances: Sequence[Consumable], date_format: str = r"%Y/%m/%d"
    ) -> None:
        super().__init__(instances)
        self.date_format = date_format

    def run(self) -> None:
        actions = []
        actions.append(list_actions.ListConsumableUpdate(999, ["U"]))
        actions.append(list_actions.ListConsumableDelete(998, ["D"]))
        actions.append(
            list_actions.ListIncrementCurrentRating(997, ["KEY_RIGHT"], ["→"])
        )
        actions.append(
            list_actions.ListDecrementCurrentRating(997, ["KEY_LEFT"], ["←"])
        )
        actions.append(list_actions.ListTagSelected(995, ["T"]))
        actions.append(list_actions.ListUntagSelected(994, ["G"]))
        super()._init_run(actions)

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

    def run(self) -> None:
        super()._init_run([])

    def tabulate(self) -> str:
        instances: Sequence[Series] = self.state.instances
        table_instances = [[row + 1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(table_instances, headers=["#", "ID", "Name"])


class PersonnelList(BaseInstanceList):
    def __init__(self, instances: Sequence[Personnel]) -> None:
        super().__init__(instances)

    def run(self) -> None:
        super()._init_run([])

    def tabulate(self) -> str:
        instances: Sequence[Personnel] = self.state.instances
        table_instances = [
            [row + 1, i.id, i.first_name, i.pseudonym, i.last_name]
            for row, i in enumerate(instances)
        ]
        return tabulate(
            table_instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"]
        )
