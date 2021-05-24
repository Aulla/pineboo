"""Dummy signal module."""

from typing import List, Callable, TYPE_CHECKING
from pineboolib.application import connections

if TYPE_CHECKING:
    from . import basemodel


class FakeSignal(object):
    """FakeSignal class."""

    _remote_funcs: List[Callable]
    _parent_model: "basemodel.BaseModel"

    def __init__(self, parent_model: "basemodel.BaseModel"):
        """Initialice."""
        self._parent_model = parent_model
        self._remote_funcs = []

    def connect(self, func_: Callable) -> None:
        """Set a function to connect."""

        if func_ not in self._remote_funcs:
            self._remote_funcs.append(func_)

    def disconnect(self, func_: Callable) -> None:
        """Set a function to disconnect."""

        if func_ in self._remote_funcs:
            self._remote_funcs.remove(func_)

    def emit(self, text: str) -> None:
        """Call all conected functions."""
        for func_ in self._remote_funcs:
            func_(*[text, self._parent_model.cursor][: connections.get_expected_args_num(func_)])
