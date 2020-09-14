# -*- coding: utf-8 -*-
"""
AQUtil Module.

Use the resources of pineboolib.fllegacy.flutil.FLUtil.
"""

from pineboolib import logging
from pineboolib.fllegacy import flutil

LOGGER = logging.get_logger(__name__)


class AQUtil(flutil.FLUtil):
    """AQUtil Class."""

    def __init__(self) -> None:
        """Initialize a new instance."""
