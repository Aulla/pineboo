# -*- coding: utf-8 -*-
"""emptyscript module."""

from . import formdbwidget


class interna(object):  # pylint: disable=invalid-name
    """Interna class."""

    ctx: "FormInternalObj"

    def __init__(self, context: "FormInternalObj") -> None:
        """Inicialize."""

        self.ctx = context

    def init(self) -> None:
        """Run optional inicialize script."""

        self.ctx.interna_init()


class oficial(interna):  # pylint: disable=invalid-name
    """Oficial class."""

    def __init__(self, context: "FormInternalObj") -> None:
        """Inicialize."""

        super().__init__(context)


class head(oficial):  # pylint: disable=invalid-name
    """Head class."""

    def __init__(self, context: "FormInternalObj") -> None:
        """Inicialize."""

        super().__init__(context)


class ifaceCtx(head):  # pylint: disable=invalid-name
    """IfaceCtx class."""

    def __init__(self, context: "FormInternalObj") -> None:
        """Inicialize."""

        super().__init__(context)


class FormInternalObj(formdbwidget.FormDBWidget):
    """FormInternalObj class."""

    def _class_init(self) -> None:
        """Inicialize ifaceCtx."""

        self.iface = ifaceCtx(self)

    def interna_init(self) -> None:
        """Run optional inicialize script."""
        pass
