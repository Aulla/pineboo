"""Dgi_schema module."""
# -*- coding: utf-8 -*-
from importlib import import_module
from typing import cast, Optional, Any
from PyQt6 import QtCore, QtWidgets  # type: ignore[import]

from pineboolib.application.utils.mobilemode import is_mobile_mode
from pineboolib import logging

LOGGER = logging.get_logger(__name__)


class DgiSchema(object):
    """dgi_schema class."""

    _desktop_enabled: bool
    _ml_default: bool
    _name: str
    _alias: str
    _local_desktop: bool
    _mobile: bool
    _clean_no_python: bool
    # FIXME: Guess this is because there is conditional code we don't want to run on certain DGI
    # .... this is really obscure. Please avoid at all costs. Having __NO_PYTHON__ is bad enough.
    _alternative_content_cached: bool

    def __init__(self) -> None:
        """Inicialize."""

        # FIXME: This init is intended to be called only on certain conditions.
        # ... Worse than it seems: looks like this class is prepared to be constructed without
        # ... calling __init__, on purpose, to have different behavior than calling it.

        self._desktop_enabled = True  # Indica si se usa en formato escritorio con interface Qt
        self._ml_default = True
        self._local_desktop = True
        self._name = "dgi_shema"
        self._alias = "Default Schema"
        self._show_object_not_found_warnings = True
        self._mobile = is_mobile_mode()

    def name(self) -> str:
        """Return DGI name."""
        return self._name

    def alias(self) -> str:
        """Return DGI alias."""
        return self._alias

    def create_app(self) -> "QtWidgets.QApplication":
        """Create an alternative Core.Application."""
        from pineboolib import application

        return application.PROJECT.app

    # Establece un lanzador alternativo al de la aplicación
    def alternativeMain(self, options: Any) -> Any:
        """Return alternative main."""
        return None

    def accept_file(self, name: str) -> bool:
        """Return True if file is accepted .False elsewhere."""
        return True

    def useDesktop(self) -> bool:
        """Return if desktop UI is used."""
        return self._desktop_enabled

    def setUseDesktop(self, val: bool) -> None:
        """Set if desktop UI is used."""
        self._desktop_enabled = val

    def localDesktop(
        self,
    ) -> bool:  # Indica si son ventanas locales o remotas a traves de algún parser
        """Return if is local desktop."""
        return self._local_desktop

    def setLocalDesktop(self, val: bool) -> None:
        """Set local desktop variable."""
        self._local_desktop = val

    def setUseMLDefault(self, val: bool) -> None:
        """Set if defaul main loader is used."""
        self._ml_default = val

    def useMLDefault(self) -> bool:
        """Return if main loaded is used."""
        return self._ml_default

    def setParameter(self, param: str) -> None:  # Se puede pasar un parametro al dgi
        """Set parameters to DGI."""
        pass

    def extraProjectInit(self) -> None:
        """Launch extra project init."""
        pass

    def showInitBanner(self) -> None:
        """Show init banner string."""

        print("")
        print("=============================================")
        print("                GDI_%s MODE               " % self._alias)
        print("=============================================")
        print("")
        print("")

    def mainForm(self) -> Any:
        """Return mainForm."""
        return QtCore.QObject()

    def interactiveGUI(self) -> str:
        """Return interactiveGUI name."""
        return "Pineboo"

    def show_object_not_found_warnings(self) -> bool:
        """Return if show warnings when objects not found."""
        return self._show_object_not_found_warnings

    def mobilePlatform(self) -> bool:
        """Return if run into a mobile platform."""
        return self._mobile

    def icon_size(self) -> QtCore.QSize:
        """Return default icon size."""

        size = QtCore.QSize(22, 22)
        # if self.mobilePlatform():
        #    size = QtCore.QSize(60, 60)

        return size

    def __getattr__(self, name: str) -> Optional["QtCore.QObject"]:
        """Return and object specified by name."""
        return self.resolveObject(self._name, name)

    def resolveObject(self, module_name: str, name: str) -> Optional["QtCore.QObject"]:
        """Return a DGI specific object."""
        cls = None
        mod_name_full = "pineboolib.plugins.dgi.dgi_%s.dgi_objects.%s" % (module_name, name.lower())
        try:
            # FIXME: Please, no.
            mod_ = import_module(mod_name_full)
            cls = getattr(mod_, name, None)
            LOGGER.trace("resolveObject: Loaded module %s", mod_name_full)
        except ModuleNotFoundError:
            LOGGER.trace("resolveObject: Module not found %s", mod_name_full)
        except Exception:
            LOGGER.exception("resolveObject: Unable to load module %s", mod_name_full)
        return cast(Optional[QtCore.QObject], cls)

    def use_alternative_credentials(self) -> bool:
        """Return True if use alternative authentication , False elsewhere."""
        return False

    def get_nameuser(self) -> str:
        """Return alternative user name."""
        return ""

    def debug(self, txt: str):
        """Show debug message."""
        LOGGER.info("---> %s" % txt)

    def exec(self):
        """Return default exec."""

        return 0
