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

    @property
    def x_max(self):
        if self._x_max is None:
            curses.update_lines_cols()
            return curses.COLS
        else:
            return self._x_max

    @property
    def y_max(self):
        if self._y_max is None:
            curses.update_lines_cols()
            return curses.LINES
        else:
            return self._y_max


def init_curses():
    curses.initscr()
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)


def new_win(coords: CursesCoords):
    window = curses.newwin(coords.y_max, coords.x_max, coords.y_start, coords.x_start)
    window.keypad(True)
    return window


def uninit_curses():
    curses.echo()
    curses.nocbreak()
    curses.curs_set(True)
    curses.endwin()
