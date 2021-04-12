"""IMainWindow module."""

from PyQt6 import QtWidgets  # type: ignore[import]

from typing import List, TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    from pineboolib.fllegacy import flworkspace  # noqa: F401 # pragma: no cover


class IMainWindow(QtWidgets.QMainWindow):
    """IMainWindow class."""

    _p_work_space: Optional["flworkspace.FLWorkSpace"]
    initialized_mods_: List[str]
    _dict_main_widgets: Dict[str, "QtWidgets.QWidget"]
    tab_widget: "QtWidgets.QTabWidget"
    container_: Optional["QtWidgets.QMainWindow"]
    main_widget: "QtWidgets.QWidget"

    def __init__(self):
        """Initialize."""
        super().__init__()
        self._dict_main_widgets = {}

    def writeState(self) -> None:
        """Write settings back to disk."""
        pass  # pragma: no cover

    def readState(self) -> None:
        """Read settings."""

        pass  # pragma: no cover

    def createUi(self, ui_file: str) -> None:
        """Create UI from a file."""

        pass  # pragma: no cover

    def writeStateModule(self) -> None:
        """Write settings for modules."""

        pass  # pragma: no cover

    def readStateModule(self) -> None:
        """Read settings for module."""

        pass  # pragma: no cover

    def initScript(self) -> None:
        """Startup process."""

        pass  # pragma: no cover

    def reinitScript(self):
        """Reinit script."""

        pass  # pragma: no cover

    def loadTabs(self) -> None:
        """Load tabs."""

        pass  # pragma: no cover

    def initToolBar(self) -> None:
        """Initialize toolbar."""

        pass  # pragma: no cover

    def initMenuBar(self) -> None:
        """Initialize menus."""

        pass  # pragma: no cover

    def windowMenuAboutToShow(self) -> None:
        """Signal called before window menu is shown."""

        pass  # pragma: no cover

    def activateModule(self, idm=None) -> None:
        """Initialize module."""

        pass  # pragma: no cover

    def existFormInMDI(self, form_name: str) -> bool:
        """Return if named FLFormDB is open."""

        return True  # pragma: no cover

    def windowMenuActivated(self, id_window: int) -> None:
        """Signal called when user clicks on menu."""

        pass  # pragma: no cover

    def windowClose(self) -> None:
        """Signal called on close."""

        pass  # pragma: no cover

    def toggleToolBar(self, toggle: bool) -> None:
        """Show or hide toolbar."""

        pass  # pragma: no cover

    def toggleStatusBar(self, toggle: bool) -> None:
        """Toggle status bar."""

        pass  # pragma: no cover

    def initToolBox(self) -> None:
        """Initialize toolbox."""

        pass  # pragma: no cover

    def setCaptionMainWidget(self, value: str) -> None:
        """Set application title."""

        pass  # pragma: no cover

    def setMainWidget(self, widget: "QtWidgets.QWidget") -> None:
        """Set mainWidget."""

        pass  # pragma: no cover
