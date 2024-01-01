# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence
import curses
from datetime import datetime

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable
from . import list_handling
from . import list_actions
from .curses_handling import init_curses, uninit_curses, new_win, CursesCoords
from .utils import truncate


class BaseDetailWindow(ABC):
    INFO_TITLE: str = "Info"

    def __init__(self, instance: DatabaseEntity) -> None:
        self.instance = instance

    def init_run(self) -> None:
        init_curses()
        self.run()
        uninit_curses()

    def run(
        self,
        list: list_handling.BaseInstanceList,
        actions: Sequence[list_actions.ListAction],
    ) -> None:
        # Static Info Window
        coords = CursesCoords(x_max=curses.COLS // 2)
        info_win = new_win(coords)
        self._render_info(info_win, coords)
        # Render Dynamic List
        list.run(actions, CursesCoords(x_start=curses.COLS // 2))

    @abstractmethod
    def _render_info(self, window, coords: CursesCoords) -> None:
        pass


class ConsumableDetailWindow(BaseDetailWindow):
    def run(self, date_format: str = r"%Y/%m/%d") -> None:
        instance: Consumable = self.instance
        self.date_format = date_format
        actions = [
            *list_handling.BaseInstanceList._default_actions(),
            list_actions.ListRemoveSelectedPersonnel(instance, 500, ["R"]),
        ]
        super().run(
            list_handling.MiniInstanceList(instance.get_personnel(), "Personnel"),
            actions,
        )

    def _render_info(self, window, coords: CursesCoords) -> None:
        window.erase()

        # Title and Border
        window.box(0, 0)
        window.addstr(0, 0, self.INFO_TITLE)
        BORDER_SIZE = 1

        # Add Info
        instance: Consumable = self.instance
        window.addstr(
            1,
            BORDER_SIZE,
            truncate(
                f'#{instance.id} "{instance.name}"', coords.width() - BORDER_SIZE * 2
            ),
        )
        window.addstr(
            2, BORDER_SIZE, truncate(instance.type, coords.width() - BORDER_SIZE * 2)
        )

        window.addstr(
            4,
            BORDER_SIZE,
            truncate(
                f"{instance.parts}/{'?' if instance.max_parts is None else instance.max_parts} parts, {instance.completions} Completion(s)",
                coords.width() - BORDER_SIZE * 2,
            ),
        )
        if instance.start_date is not None or instance.end_date is not None:
            start = (
                "n.d."
                if instance.start_date is None
                else datetime.fromtimestamp(instance.start_date).strftime(
                    self.date_format
                )
            )
            end = (
                "n.d."
                if instance.end_date is None
                else datetime.fromtimestamp(instance.end_date).strftime(
                    self.date_format
                )
            )
            window.addstr(
                5,
                BORDER_SIZE,
                truncate(
                    f"{instance.status.name}, {start} - {end}",
                    coords.width() - BORDER_SIZE * 2,
                ),
            )
        else:
            window.addstr(
                5,
                BORDER_SIZE,
                truncate(instance.status.name, coords.width() - BORDER_SIZE * 2),
            )

        window.refresh()
