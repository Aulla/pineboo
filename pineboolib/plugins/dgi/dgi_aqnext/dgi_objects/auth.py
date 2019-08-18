"""auth module."""
# -*- coding: utf-8 -*-
from pineboolib.core import decorators


class auth(object):
    """Auth class."""

    @decorators.NotImplementedWarn
    def authenticate(**kwargs) -> bool:
        """Return authenticaion results."""
        print("Autenticando", kwargs)
        return True
