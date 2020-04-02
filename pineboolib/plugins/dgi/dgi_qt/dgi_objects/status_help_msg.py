"""StatusHelpMsg module."""

from pineboolib.core.utils import logging
from pineboolib.core import settings
from pineboolib import application

LOGGER = logging.get_logger(__name__)


class StatusHelpMsg(object):
    """StatusHelpMsg class."""

    def send(self, text_: str) -> None:
        """Send a text."""

        try:
            application.PROJECT.aq_app.statusHelpMsg(text_)

            if settings.CONFIG.value("ebcomportamiento/parser_qsa_gui", False):
                application.PROJECT.aq_app.popupWarn(text_)
        except RuntimeError as error:
            LOGGER.warning(str(error))
