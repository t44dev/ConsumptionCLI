# General Imports
from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Sequence
import curses
from datetime import datetime

# Consumption Imports
from consumptionbackend.Database import DatabaseEntity
from consumptionbackend.Consumable import Consumable, average_rating
from consumptionbackend.Series import Series
from consumptionbackend.Personnel import Personnel
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
        to_date = (
            lambda x: "n.d"
            if x is None
            else datetime.fromtimestamp(x).strftime(self.date_format)
        )
        info_list = [
            (1, f'#{instance.id} "{instance.name}"'),
            (
                2,
                f"{instance.type} - "
                + (
                    "No Series"
                    if instance.get_series().id == -1
                    else str(instance.get_series())
                ),
            ),
            (
                4,
                f"{instance.parts}/{'?' if instance.max_parts is None else instance.max_parts} parts, {instance.completions} Completion(s)",
            ),
            (
                5,
                f"{instance.status.name}{', ' + to_date(instance.start_date) + ' - ' + to_date(instance.end_date) if instance.start_date is not None or instance.end_date is not None else ''}",
            ),
        ]
        for y_pos, info in info_list:
            if y_pos < coords.height():
                window.addstr(
                    y_pos, BORDER_SIZE, truncate(info, coords.width() - BORDER_SIZE * 2)
                )

        # Tags
        tag_y = 7
        window.addstr(tag_y, BORDER_SIZE, "Tag(s): " + " ".join(instance.get_tags()))

        window.refresh()


class SeriesDetailWindow(BaseDetailWindow):
    def run(self) -> None:
        instance: Series = self.instance
        actions = [
            *list_handling.BaseInstanceList._default_actions(),
            list_actions.ListRemoveSelectedSeriesConsumable(self.instance, 500, ["R"]),
        ]
        super().run(
            list_handling.MiniInstanceList(instance.get_consumables(), "Consumables"),
            actions,
        )

    def _render_info(self, window, coords: CursesCoords) -> None:
        window.erase()

        # Title and Border
        window.box(0, 0)
        window.addstr(0, 0, self.INFO_TITLE)
        BORDER_SIZE = 1

        # Add Info
        instance: Series = self.instance
        consumables = instance.get_consumables()
        info_list = [
            (1, f'#{instance.id} "{instance.name}"'),
            (
                3,
                f"{sum([c.parts for c in consumables])}/{sum([c.max_parts for c in consumables if c.max_parts is not None])}"
                + (
                    "+? parts"
                    if None in [c.max_parts for c in consumables]
                    else " parts"
                )
                + f", {sum([c.completions for c in consumables])} Total Completions",
            ),
            (4, f"{average_rating(consumables):.2f} Average Rating"),
        ]
        for y_pos, info in info_list:
            if y_pos < coords.height():
                window.addstr(
                    y_pos, BORDER_SIZE, truncate(info, coords.width() - BORDER_SIZE * 2)
                )

        window.refresh()


class PersonnelDetailWindow(BaseDetailWindow):
    def run(self) -> None:
        instance: Personnel = self.instance
        actions = [
            *list_handling.BaseInstanceList._default_actions(),
            list_actions.ListRemoveSelectedPersonnelConsumable(instance, 500, ["R"]),
        ]
        super().run(
            list_handling.MiniInstanceList(instance.get_consumables(), "Consumables"),
            actions,
        )

    def _render_info(self, window, coords: CursesCoords) -> None:
        window.erase()

        # Title and Border
        window.box(0, 0)
        window.addstr(0, 0, self.INFO_TITLE)
        BORDER_SIZE = 1

        # Add Info
        instance: Personnel = self.instance
        consumables = instance.get_consumables()
        info_list = [
            (1, f'#{instance.id} "{str(instance)}"'),
            (
                3,
                f"{sum([c.parts for c in consumables])}/{sum([c.max_parts for c in consumables if c.max_parts is not None])}"
                + (
                    "+? parts"
                    if None in [c.max_parts for c in consumables]
                    else " parts"
                )
                + f", {sum([c.completions for c in consumables])} Total Completions",
            ),
            (4, f"{average_rating(consumables):.2f} Average Rating"),
        ]
        for y_pos, info in info_list:
            if y_pos < coords.height():
                window.addstr(
                    y_pos, BORDER_SIZE, truncate(info, coords.width() - BORDER_SIZE * 2)
                )

        window.refresh()
