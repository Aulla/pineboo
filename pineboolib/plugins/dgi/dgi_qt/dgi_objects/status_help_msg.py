"""StatusHelpMsg module."""

from pineboolib.core.utils import logging
from pineboolib.core import settings


LOGGER = logging.get_logger(__name__)


class StatusHelpMsg(object):
    """StatusHelpMsg class."""

    def send(self, text_: str) -> None:
        """Send a text."""

        try:
            from pineboolib.fllegacy.flapplication import aqApp

            aqApp.statusHelpMsg(text_)

            if settings.CONFIG.value("ebcomportamiento/parser_qsa_gui", False):
                aqApp.popupWarn(text_)
        except RuntimeError as error:
            LOGGER.warning(str(error))
