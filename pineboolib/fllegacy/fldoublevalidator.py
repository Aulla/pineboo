"""Fldoublevalidator module."""
# -*- coding: utf-8 -*-


from PyQt6 import QtGui  # type: ignore[import]

from pineboolib import application

from typing import Tuple, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtWidgets  # pragma: no cover


class FLDoubleValidator(QtGui.QDoubleValidator):
    """FLDoubleValiator class."""

    _formatting: bool

    def __init__(
        self,
        max_value: Union[int, float],
        min_value: Union[int, float],
        part_decimal: int,
        parent: "QtWidgets.QWidget",
    ) -> None:
        """Inicialize."""
        super().__init__(max_value, min_value, part_decimal, parent)
        # 1 inferior
        # 2 superior
        # 3 partDecimal
        # 4 editor
        self.setNotation(self.Notation.StandardNotation)
        self._formatting = False

    def validate(self, input_: str, pos_cursor: int) -> Tuple["QtGui.QValidator.State", str, int]:
        """Return if a value is valid."""
        value_in = input_

        if value_in is None or self._formatting:
            return (self.State.Acceptable, value_in, pos_cursor)

        # pos_cursor= len(value_in)
        state = super().validate(value_in, pos_cursor)
        # 0 Invalid
        # 1 Intermediate
        # 2 Acceptable
        ret_2 = state[2]

        if state[0] in (self.State.Invalid, self.State.Intermediate) and len(value_in) > 0:
            state_ = value_in[1:]
            if (
                value_in[0] == "-"
                and super().validate(state_, pos_cursor)[0] == self.State.Acceptable
                or state_ == ""
            ):
                ret_0 = self.State.Acceptable
            else:
                ret_0 = self.State.Invalid
        else:
            ret_0 = self.State.Acceptable

        ret_1 = state[1]

        if application.PROJECT.aq_app.commaSeparator() == "," and ret_1.endswith("."):
            ret_1 = ret_1[0 : len(ret_1) - 1] + ","

        if len(ret_1) == 1 and ret_1 not in (
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            ",",
            ".",
        ):
            ret_0 = self.State.Invalid
            ret_1 = ""
            ret_2 = 0

        return (ret_0, ret_1, ret_2)
