"""QCombobox module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]


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

    def setReadOnly(self, data: bool) -> None:
        """Set read only."""

        super().setEditable(not data)

    def getCurrentItem(self) -> Any:
        """Return current item selected."""

        return super().currentIndex

    def setCurrentItem(self, new_item: Union[str, int]) -> None:
        """Set current item."""

        pos = -1
        if isinstance(new_item, str):
            pos = 0
            size_ = self.model().rowCount()
            for pos_item in range(size_):
                item = self.model().index(pos_item, 0)
                if item.data() == new_item:
                    pos = pos_item
                    break

        else:
            pos = new_item

        super().setCurrentIndex(pos)

    def getCurrentText(self) -> str:
        """Return current item text."""

        return super().currentText()

    def setCurrentText(self, value: str) -> None:
        """Set current item text."""

        super().setCurrentText(value)

    def setSizeLimit(self, size: int) -> None:
        """Set size limit."""

        super().setMaxCount(size)

    def getSizeLimit(self) -> int:
        """Return size limit."""

        return super().maxCount()

    sizeLimit = property(getSizeLimit, setSizeLimit, None, "get/set size allowed items limits")
    currentItem = property(getCurrentItem, setCurrentItem, None, "get/set current item index")
    currentText: str = property(  # type: ignore [assignment] # noqa F821
        getCurrentText, setCurrentText, None, "get/set current text"
    )
