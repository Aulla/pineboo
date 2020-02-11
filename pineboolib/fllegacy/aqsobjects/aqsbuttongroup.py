"""AQSButtonGroup module."""

from PyQt5 import QtCore
from pineboolib.core.utils import logging
from pineboolib.q3widgets import qbuttongroup

LOGGER = logging.getLogger(__name__)


class AQSButtonGroup(qbuttongroup.QButtonGroup):
    """AQSButtonGroup class."""

    def __init__(self, parent: QtCore.QObject, name="", *args):
        super().__init__(parent)
        if name:
            self.setObjectName(name)

        if args:
            LOGGER.warning("LOS ARGUMENTOS NO ESTAN SOPORTADOS FIXME")
