"""Spinbox module."""

from PyQt6 import QtWidgets  # type: ignore[import]


class SpinBox(QtWidgets.QWidget):
    """SpinBox class."""

    _label: "QtWidgets.QLabel"
    _spin_box: "QtWidgets.QSpinBox"
    _lay: "QtWidgets.QHBoxLayout"

    def __init__(self, parent=None):
        """Initialize."""

        super().__init__(parent)

        self._lay = QtWidgets.QHBoxLayout(self)
        self._label = QtWidgets.QLabel()
        self._spin_box = QtWidgets.QSpinBox()

        self._lay.addWidget(self._label)
        self._lay.addWidget(self._spin_box)

    def getMax(self) -> int:
        """Return Maximum."""
        return self._spin_box.maximum()

    def setMax(self, max: int) -> None:
        """Set Maximum."""
        self._spin_box.setMaximum(max)

    def getMin(self) -> int:
        """Return Minimum."""
        return self._spin_box.minimum()

    def setMin(self, min: int) -> None:
        """Set Minimum."""
        self._spin_box.setMinimum(min)

    def getValue(self) -> int:
        """Return value."""
        return self._spin_box.value()

    def setValue(self, value: int) -> None:
        """Set Minimum."""
        self._spin_box.setValue(value)

    def getLabel(self) -> str:
        """Return label."""

        return self._label.text()

    def setLabel(self, label: str) -> None:
        """Set label."""

        self._label.setText(label)

    maximum: int = property(getMax, setMax)  # type: ignore [assignment] # noqa: F821
    minimum: int = property(getMin, setMin)  # type: ignore [assignment] # noqa: F821
    value: int = property(getValue, setValue)  # type: ignore [assignment] # noqa: F821
    label: str = property(getLabel, setLabel)  # type: ignore [assignment] # noqa: F821
