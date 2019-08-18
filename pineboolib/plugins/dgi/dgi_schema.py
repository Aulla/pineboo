"""Dgi_schema module."""
# -*- coding: utf-8 -*-
from importlib import import_module
from typing import List, cast, Optional, Any
from PyQt5 import QtCore

from pineboolib.application.utils.mobilemode import is_mobile_mode
from pineboolib import logging

logger = logging.getLogger(__name__)


class dgi_schema(object):
    """dgi_schema class."""

    _desktopEnabled: bool
    _mLDefault: bool
    _name: str
    _alias: str
    _localDesktop: bool
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

        self._desktopEnabled = True  # Indica si se usa en formato escritorio con interface Qt
        self.setUseMLDefault(
            True
        )  # FIXME: Setters are wrong. Inside private context, even wronger.
        self.setLocalDesktop(True)
        self._name = "dgi_shema"
        self._alias = "Default Schema"
        self._show_object_not_found_warnings = True
        self.loadReferences()
        self._mobile = is_mobile_mode()

    def name(self) -> str:
        """Return DGI name."""
        return self._name

    def alias(self) -> str:
        """Return DGI alias."""
        return self._alias

    def create_app(self) -> QtCore.QCoreApplication:
        """Create an alternative Core.Application."""
        from pineboolib.application import project

        return project.app

    # Establece un lanzador alternativo al de la aplicación
    def alternativeMain(self, options: Any) -> Any:
        """Return alternative main."""
        return None

    def accept_file(self, name: str) -> bool:
        """Return True if file is accepted .False elsewhere."""
        return True

    def useDesktop(self) -> bool:
        """Return if desktop UI is used."""
        return self._desktopEnabled

    def setUseDesktop(self, val: bool) -> None:
        """Set if desktop UI is used."""
        self._desktopEnabled = val

    def localDesktop(
        self
    ) -> bool:  # Indica si son ventanas locales o remotas a traves de algún parser
        """Return if is local desktop."""
        return self._localDesktop

    def setLocalDesktop(self, val: bool) -> None:
        """Set local desktop variable."""
        self._localDesktop = val

    def setUseMLDefault(self, val: bool) -> None:
        """Set if defaul main loader is used."""
        self._mLDefault = val

    def useMLDefault(self) -> bool:
        """Return if main loaded is used."""
        return self._mLDefault

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

    def processEvents(self) -> None:
        """Run Process events."""
        from PyQt5 import QtWidgets  # type: ignore

        QtWidgets.qApp.processEvents()

    def show_object_not_found_warnings(self) -> bool:
        """Return if show warnings when objects not found."""
        return self._show_object_not_found_warnings

    def loadReferences(self) -> None:
        """Load specific DGI references."""
        return

    def mobilePlatform(self) -> bool:
        """Return if run into a mobile platform."""
        return self._mobile

    def isDeployed(self) -> bool:
        """Return True only if the code is running inside a PyInstaller bundle."""
        # FIXME: Delete me. This functionality DOES NOT DEPEND on which interface is being used.
        # .... a bundle is a bundle regardless of wether is running as jsonrpc or Qt.
        # .... A copy of this function has been moved to pineboolib.core.utils.utils_base.is_deployed() for convenience
        raise Exception("Please DELETE ME. DEPRECATED")

    def iconSize(self) -> QtCore.QSize:
        """Return default icon size."""
        from PyQt5 import QtCore  # type: ignore

        size = QtCore.QSize(22, 22)
        # if self.mobilePlatform():
        #    size = QtCore.QSize(60, 60)

        return size

    def alternative_content_cached(self) -> bool:
        """Return alternative content cached."""
        # FIXME: This is not needed. Use "content_cached" to return an exception or None, to signal
        # ... the module is unaware on how to perform the task
        # ... also the naming is bad. It conveys having done a cache in the past.
        return self._alternative_content_cached

    def alternative_script_path(self, script_name: str) -> Optional[str]:
        """Return alternative script path."""
        # FIXME: Probably the same. Not needed.
        return None

    def use_model(self):
        """Return if this DGI use models."""
        return False

    def __getattr__(self, name: str) -> Optional[QtCore.QObject]:
        """Return and object specified by name."""
        return self.resolveObject(self._name, name)

    def resolveObject(self, module_name: str, name: str) -> Optional[QtCore.QObject]:
        """Return a DGI specific object."""
        cls = None
        mod_name_full = "pineboolib.plugins.dgi.dgi_%s.dgi_objects.%s" % (module_name, name.lower())
        try:
            # FIXME: Please, no.
            mod_ = import_module(mod_name_full)
            cls = getattr(mod_, name, None)
            logger.trace("resolveObject: Loaded module %s", mod_name_full)
        except ModuleNotFoundError:
            logger.trace("resolveObject: Module not found %s", mod_name_full)
        except Exception:
            logger.exception("resolveObject: Unable to load module %s", mod_name_full)
        return cast(Optional[QtCore.QObject], cls)

    def sys_mtds(self) -> List[str]:
        """Return optional system mtds tables list."""
        return []

    def use_alternative_credentials(self) -> bool:
        """Return True if use alternative authentication , False elsewhere."""
        return False

    def get_nameuser(self) -> str:
        """Return alternative user name."""
        return ""

    def debug(self, txt: str):
        """Show debug message."""
        logger.warning("---> %s" % txt)

    def content_cached(
        self,
        tmp_folder: str,
        db_name: str,
        module_id: str,
        file_ext: str,
        file_name: str,
        sha_key: str,
    ) -> Optional[str]:
        """Return content cahced from a specific file."""

        return ""

    def load_meta_model(self, module_nae: str) -> Any:
        """Load meta model process."""
        return ""
