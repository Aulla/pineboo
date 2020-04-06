"""IMainWindow module."""

from PyQt5 import QtWidgets

from typing import List, TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from pineboolib.fllegacy import flworkspace  # noqa: F401


class IMainWindow(QtWidgets.QMainWindow):
    """IMainWindow class."""

    _p_work_space: Optional["flworkspace.FLWorkSpace"]
    initialized_mods_: List[str]
    _dict_main_widgets: Dict[str, QtWidgets.QWidget]
    tab_widget: "QtWidgets.QTabWidget"
    container_: Optional[QtWidgets.QMainWindow]
    main_widget: QtWidgets.QWidget

    def __init__(self):
        """Initialize."""
        super().__init__()
        self._dict_main_widgets = {}

    def writeState(self) -> None:
        """Write settings back to disk."""
        pass

    def readState(self) -> None:
        """Read settings."""

        pass

    def createUi(self, ui_file: str) -> None:
        """Create UI from a file."""

        pass

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        pass

    def readStateModule(self) -> None:
        """Read settings for module."""

        pass

    def initScript(self) -> None:
        """Startup process."""

        pass

    def reinitScript(self):
        """Reinit script."""

        pass

    def loadTabs(self) -> None:
        """Load tabs."""

        pass

    def initToolBar(self) -> None:
        """Initialize toolbar."""

        pass

    def initMenuBar(self) -> None:
        """Initialize menus."""

        pass

    def windowMenuAboutToShow(self) -> None:
        """Signal called before window menu is shown."""

        pass

    def activateModule(self, idm=None) -> None:
        """Initialize module."""

        pass

    def existFormInMDI(self, form_name: str) -> bool:
        """Return if named FLFormDB is open."""

        return True

    def windowMenuActivated(self, id) -> None:
        """Signal called when user clicks on menu."""

        pass

    def windowClose(self) -> None:
        """Signal called on close."""

        pass

    def toggleToolBar(self, toggle: bool) -> None:
        """Show or hide toolbar."""

        pass

    def toggleStatusBar(self, toggle: bool) -> None:
        """Toggle status bar."""

        pass

    def initToolBox(self) -> None:
        """Initialize toolbox."""

        pass

    def setCaptionMainWidget(self, value: str) -> None:
        """Set application title."""

        pass

    def setMainWidget(self, w) -> None:
        """Set mainWidget."""

        pass
