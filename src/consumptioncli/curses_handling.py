# General Imports
import curses


class CursesCoords:
    def __init__(
        self, x_start: int = 0, y_start: int = 0, x_max: int = None, y_max: int = None
    ) -> None:
        self.x_start = x_start
        self.y_start = y_start
        self._x_max = x_max
        self._y_max = y_max
        self._x_max_delta = 0
        self._y_max_delta = 0

    def width(self):
        return self.x_max - self.x_start

    def height(self):
        return self.y_max - self.y_start

    def delta_x_start(self, amount: int):
        self.x_start += amount

    def delta_y_start(self, amount: int):
        self.y_start += amount

    def delta_x_max(self, amount: int):
        self._x_max_delta += amount

    def delta_y_max(self, amount: int):
        self._y_max_delta += amount

    @property
    def x_max(self):
        if self._x_max is None:
            curses.update_lines_cols()
            return curses.COLS + self._x_max_delta
        else:
            return self._x_max + self._x_max_delta

    @property
    def y_max(self):
        if self._y_max is None:
            curses.update_lines_cols()
            return curses.LINES + self._y_max_delta
        else:
            return self._y_max + self._y_max_delta


def init_curses():
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)


def new_win(coords: CursesCoords):
    window = curses.newwin(
        coords.height(),
        coords.width(),
        coords.y_start,
        coords.x_start,
    )
    window.keypad(True)
    return window


def uninit_curses():
    curses.echo()
    curses.nocbreak()
    curses.curs_set(True)
    curses.endwin()
