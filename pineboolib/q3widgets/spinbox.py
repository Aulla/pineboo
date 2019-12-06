"""Spinbox module."""
from . import qspinbox


class SpinBox(qspinbox.QSpinBox):
    """SpinBox class."""

    def getMax(self) -> int:
        """Return Maximum."""
        return super().maximum()

    def setMax(self, max: int) -> None:
        """Set Maximum."""
        super().setMaximum(max)

    def getMin(self) -> int:
        """Return Minimum."""
        return super().minimum()

    def setMin(self, min: int) -> None:
        """Set Minimum."""
        super().setMinimum(min)

    def getValue(self) -> int:
        """Return value."""
        return super().value()

    def setValue(self, value: int) -> None:
        """Set Minimum."""
        super().setValue(value)

    maximum: int = property(getMax, setMax)  # type: ignore [assignment] # noqa: F821
    minimum: int = property(getMin, setMin)  # type: ignore [assignment] # noqa: F821
    value: int = property(getValue, setValue)  # type: ignore [assignment] # noqa: F821
