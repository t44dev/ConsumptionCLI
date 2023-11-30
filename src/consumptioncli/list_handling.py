# General Imports
from abc import ABC, abstractmethod
from datetime import datetime
import curses
from collections.abc import Sequence, Mapping
from typing import Callable, Tuple, TypeAlias
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


Action: TypeAlias = Tuple[str, Callable[[ListState], ListState], str, int]
# Dictionary that maps key names (as in keyboard) to a tuple of an action name,
# a callable that updates some ListState, a key name alias and a priority for display
Actions: TypeAlias = Mapping[str, Action]


class BaseInstanceList(ABC):
    def __init__(self, instances: Sequence[DatabaseEntity]) -> None:
        self.state = ListState(instances)

    @abstractmethod
    def run(self) -> None:
        pass

    @abstractmethod
    def tabulate(self) -> str:
        pass

    def _run(self, actions: Actions) -> None:
        # Setup State
        actions = BaseInstanceList._setup_actions(actions)
        window = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(False)
        window.keypad(True)
        # Render/Action Loop
        while self.state.active:
            self._render(self.tabulate(), actions, window)
            key = window.getkey().upper()
            if key in actions:
                self.state = actions[key][1](self.state)
        # Reset State
        curses.echo()
        curses.nocbreak()
        curses.curs_set(True)
        window.keypad(False)
        curses.endwin()

    def _render(self, table: str, actions: Actions, window) -> None:
        window.erase()
        table = table.split("\n")
        # Render Table
        headers = table[:2]
        body = table[2:]
        # Header
        window.addstr(0, 2, headers[0], curses.A_BOLD)
        window.addstr(1, 2, headers[1], curses.A_BOLD)
        # Body
        lines_before_after = curses.LINES - 5
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
                window.addstr(y_pos, 0, f"> {line} <", attr)
            else:
                window.addstr(y_pos, 2, line, attr)
        # Render Actions
        processed_actions = dict()
        for key, (name, _, alias, priority) in sorted(
            actions.items(), key=lambda x: x[1][3], reverse=True
        ):
            if name in processed_actions:
                if alias not in processed_actions.get(name)[0]:
                    processed_actions.get(name)[0].append(alias)
            else:
                processed_actions[name] = [[alias], priority]
        processed_actions = sorted(
            processed_actions.items(), key=lambda x: x[1][1], reverse=True
        )
        action_strings = []
        for name, (aliases, _) in processed_actions:
            action_strings.append(f"[{'/'.join(aliases)}] {name}")
        window.addstr(curses.LINES - 1, 0, "   ".join(action_strings))
        window.refresh()

    @classmethod
    def _setup_actions(cls, actions: Actions) -> Actions:
        actions["K"] = ("Up", list_actions.move_up, "K", 9999)
        actions["KEY_UP"] = ("Up", list_actions.move_up, "↑", 9998)
        actions["J"] = ("Down", list_actions.move_down, "J", 9997)
        actions["KEY_DOWN"] = ("Down", list_actions.move_down, "↓", 9996)
        actions["\n"] = ("Select", list_actions.select_current, "Enter", 9995)
        actions["KEY_ENTER"] = ("Select", list_actions.select_current, "Enter", 9994)
        actions["Q"] = ("Quit", list_actions.quit, "Q", -9999)
        return actions


class ConsumableList(BaseInstanceList):
    def __init__(
        self, instances: Sequence[Consumable], date_format: str = r"%Y/%m/%d"
    ) -> None:
        super().__init__(instances)
        self.date_format = date_format

    def run(self) -> None:
        super()._run(dict())

    def tabulate(self) -> str:
        instances: Sequence[Consumable] = self.state.instances
        table_instances = [
            [
                row + 1,
                i.id,
                i.type,
                truncate(i.name),
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
        super()._run(dict())

    def tabulate(self) -> str:
        instances: Sequence[Series] = self.state.instances
        table_instances = [[row + 1, i.id, i.name] for row, i in enumerate(instances)]
        return tabulate(table_instances, headers=["#", "ID", "Name"])


class PersonnelList(BaseInstanceList):
    def __init__(self, instances: Sequence[Personnel]) -> None:
        super().__init__(instances)

    def run(self) -> None:
        super()._run(dict())

    def tabulate(self) -> str:
        instances: Sequence[Personnel] = self.state.instances
        table_instances = [
            [row + 1, i.id, i.first_name, i.pseudonym, i.last_name]
            for row, i in enumerate(instances)
        ]
        return tabulate(
            table_instances, headers=["#", "ID", "First Name", "Pseudonym", "Last Name"]
        )
