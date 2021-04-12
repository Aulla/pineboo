"""Input module."""

from PyQt6 import QtWidgets  # type: ignore[import]
from typing import Any, Optional, Union, Iterable


class Input(object):
    """
    Data entry dialog.
    """

    @classmethod
    def getText(cls, question: str, prevtxt: str = "", title: str = "Pineboo") -> Optional[str]:
        """
        Return Text.

        @param question. Label of the dialogue.
        @param prevtxt. Initial value to specify in the field.
        @param title. Title of the dialogue.
        @return string of collected text.
        """
        parent = QtWidgets.QApplication.activeWindow()
        text, result = QtWidgets.QInputDialog.getText(
            parent, title, question, QtWidgets.QLineEdit.EchoMode.Normal, prevtxt
        )
        if not result:
            return None
        return text

    @classmethod
    def getNumber(
        cls, question: str, value: Union[str, float], part_decimal: int = 0, title: str = "Pineboo"
    ) -> float:
        """Return number."""

        parent = QtWidgets.QApplication.activeWindow()
        text, result = QtWidgets.QInputDialog.getText(
            parent,
            title,
            question,
            QtWidgets.QLineEdit.EchoMode.Normal,
            str(round(float(value), part_decimal)),
        )
        ret: float = 0.00
        if result:
            ret = float(text)

        return ret

    @classmethod
    def getItem(
        cls, question: str, items_list: Iterable = [], editable: bool = True, title: str = "Pineboo"
    ) -> Any:
        """
        Return Item.

        @param question. Label of the dialogue.
        @param item_list. Items List.
        @param title. Title of the dialogue.
        @return item, Selected item.
        """
        parent = QtWidgets.QApplication.activeWindow()
        items = []
        for i in items_list:
            items.append(i)

        text, result = QtWidgets.QInputDialog.getItem(parent, title, question, items, 0, editable)
        if not result:
            return None
        return text
