"""AQSButtonGroup module."""

from pineboolib.core.utils import logging
from pineboolib.q3widgets import qbuttongroup

from typing import Any

LOGGER = logging.get_logger(__name__)


class AQSButtonGroup(qbuttongroup.QButtonGroup):
    """AQSButtonGroup class."""

    def __init__(self, parent: Any, name="", *args):
        """Initialize."""

        super().__init__(parent)
        if name:
            self.setObjectName(name)

        if args:
            LOGGER.warning("LOS ARGUMENTOS NO ESTAN SOPORTADOS FIXME")
