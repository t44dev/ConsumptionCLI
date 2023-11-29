# General Imports
from __future__ import annotations

# Consumption Imports
from . import list_handling


def move_up(state: list_handling.ListState) -> list_handling.ListState:
    state.current = max(state.current - 1, 0)
    return state


def move_down(state: list_handling.ListState) -> list_handling.ListState:
    state.current = min(state.current + 1, len(state.instances) - 1)
    return state


def quit(state: list_handling.ListState) -> list_handling.ListState:
    state.active = False
    return state


def select_current(state: list_handling.ListState) -> list_handling.ListState:
    if state.instances[state.current] in state.selected:
        state.selected.remove(state.instances[state.current])
    else:
        state.selected.add(state.instances[state.current])
    return state
