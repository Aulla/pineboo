"""QCombobox module."""

# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets  # type: ignore


from typing import Optional, Any, List, Union


class QComboBox(QtWidgets.QComboBox):
    """QComboBox class."""

    def __init__(
        self, parent: Optional[QtWidgets.QWidget] = None, name: Optional[str] = None
    ) -> None:
        """Inicialize."""

        super().__init__(parent)
        if name is not None:
            self.setObjectName(name)

        self.setEditable(False)

    def insertStringList(self, strl: List[str]) -> None:
        """Set items from an string list."""

        self.insertItems(len(strl), strl)

    def setReadOnly(self, b: bool) -> None:
        """Set read only."""

        super().setEditable(not b)

    def getCurrentItem(self) -> Any:
        """Return current item selected."""

        return super().currentIndex

    def setCurrentItem(self, i: Union[str, int]) -> None:
        """Set current item."""

        pos = -1
        if isinstance(i, str):
            pos = 0
            size_ = self.model().rowCount()
            for n in range(size_):
                item = self.model().index(n, 0)
                if item.data() == i:
                    pos = n
                    break

        else:
            pos = i

        super().setCurrentIndex(pos)

    def getCurrentText(self) -> str:
        """Return current item text."""

        return super().currentText()

    def setCurrentText(self, value: str) -> None:
        """Set current item text."""

        super().setCurrentText(value)

    currentItem = property(getCurrentItem, setCurrentItem, None, "get/set current item index")
    currentText: str = property(  # type: ignore [assignment] # noqa F821
        getCurrentText, setCurrentText, None, "get/set current text"
    )
