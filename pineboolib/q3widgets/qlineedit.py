"""Qlineedit module."""

# -*- coding: utf-8 -*-
from PyQt6 import QtWidgets  # type: ignore[import]
from pineboolib.core import decorators


from typing import Optional, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from . import qframe  # noqa: F401 # pragma: no cover
    from . import qgroupbox  # noqa: F401 # pragma: no cover
    from . import qwidget  # noqa: F401 # pragma: no cover
    from . import qlineedit  # noqa: F401 # pragma: no cover


class QLineEdit(QtWidgets.QLineEdit):
    """QLineEdit class."""

    _parent = None
    WindowOrigin = 0
    autoSelect: bool = False

    def __init__(self, parent: Optional[Any] = None, name: Optional[str] = None) -> None:
        """Inicialize."""

        super(QLineEdit, self).__init__(parent)
        self._parent = parent

        if name:
            self.setObjectName(name)

        self.setMaximumHeight(22)

    def getText(self) -> str:
        """Return the text of the field."""

        return super().text()

    def setText(self, text: Any) -> None:
        """Set the text of the field."""

        super().setText(str(text))

    text: str = property(getText, setText)  # type: ignore [assignment] # noqa F821

    @decorators.not_implemented_warn
    def setBackgroundOrigin(self, bgo: Any):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def setLineWidth(self, width: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def setFrameShape(self, frame_shape: int):
        """Not implemented."""
        pass

    @decorators.not_implemented_warn
    def setFrameShadow(self, frame_shadow: int):
        """Not implemented."""
        pass
