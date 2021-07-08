# -*- coding: utf-8 -*-
"""dlgconnect module."""

import os
from PyQt6 import QtWidgets, QtGui, QtCore  # type: ignore[import]


from pineboolib import logging
from pineboolib.core import decorators, settings
from pineboolib.loader import projectconfig

from typing import Optional, cast, Dict, Any

LOGGER = logging.get_logger(__name__)


class DlgConnect(QtWidgets.QWidget):
    """
    DlgConnect Class.

    This class shows manages the Login dialog.
    """

    _options_showed: bool
    _min_size: "QtCore.QSize"
    _max_size: "QtCore.QSize"
    edit_mode: bool

    profiles: Dict[
        str, "projectconfig.ProjectConfig"
    ]  #: Index of loaded profiles. Keyed by description.
    selected_project_config: Optional[
        "projectconfig.ProjectConfig"
    ]  #: Contains the selected item to load.

    def __init__(self) -> None:
        """
        Initialize.
        """
        from pineboolib.application.database import pnsqldriversmanager

        super().__init__()
        self._options_showed = False
        self._min_size = QtCore.QSize(350, 140)
        self._max_size = QtCore.QSize(350, 495)
        self.profile_dir: str = projectconfig.ProjectConfig.profile_dir
        self.sql_drivers = pnsqldriversmanager.PNSqlDriversManager()
        self.edit_mode = False
        self.profiles = {}
        self.selected_project_config = None

    def load(self) -> None:
        """
        Load the dlgconnect form.
        """
        from pineboolib.fllegacy import flmanagermodules
        from pineboolib.core.utils import utils_base

        dlg_ = utils_base.filedir("loader/dlgconnect/dlgconnect.ui")

        self._user_interface: Any = flmanagermodules.FLManagerModules.createUI(dlg_, None, self)
        if not self._user_interface:
            raise Exception("Error creating dlgConnect")

        frame_geo = self.frameGeometry()
        primary_screen = QtGui.QGuiApplication.primaryScreen()
        frame_geo.moveCenter(primary_screen.geometry().center())
        self.move(frame_geo.topLeft())

        self._user_interface.pbLogin.clicked.connect(self.open)
        self._user_interface.tbOptions.clicked.connect(self.toggleOptions)
        self._user_interface.pbSaveConnection.clicked.connect(self.saveProfile)
        self._user_interface.tbDeleteProfile.clicked.connect(self.deleteProfile)
        self._user_interface.tbEditProfile.clicked.connect(self.editProfile)
        self.cleanProfileForm()
        self._user_interface.cbDBType.currentIndexChanged.connect(self.updatePort)
        self._user_interface.cbProfiles.currentIndexChanged.connect(self.enablePassword)
        self._user_interface.cbAutoLogin.stateChanged.connect(self.cbAutoLogin_checked)
        self._user_interface.le_profiles.setText(self.profile_dir)
        self._user_interface.tb_profiles.clicked.connect(self.change_profile_dir)
        self.showOptions(False)
        self.loadProfiles()
        self._user_interface.leDescription.textChanged.connect(self.updateDBName)
        self._user_interface.installEventFilter(self)

    def cleanProfileForm(self) -> None:
        """
        Clean the profiles creation tab, and fill in the basic data of the default SQL driver.
        """
        self._user_interface.leDescription.setText("")
        driver_list = self.sql_drivers.aliasList()
        self._user_interface.cbDBType.clear()
        self._user_interface.cbDBType.addItems(driver_list)
        self._user_interface.cbDBType.setCurrentText(self.sql_drivers.defaultDriverName())
        self._user_interface.leURL.setText("localhost")
        self._user_interface.leDBUser.setText("")
        self._user_interface.leDBPassword.setText("")
        self._user_interface.leDBName.setText("")
        self._user_interface.leProfilePassword.setText("")
        self._user_interface.leProfilePassword2.setText("")
        self._user_interface.cbAutoLogin.setChecked(False)
        self.updatePort()

    def loadProfiles(self) -> None:
        """
        Update ComboBox of profiles.
        """
        if not os.path.exists(self.profile_dir):
            return

        self._user_interface.cbProfiles.clear()
        self.profiles.clear()

        with os.scandir(self.profile_dir) as profile:
            for entry in profile:
                if entry.name.startswith("."):
                    continue
                if not entry.name.endswith(".xml"):
                    continue
                if not entry.is_file():
                    continue

                pconf = projectconfig.ProjectConfig(
                    filename=os.path.join(self.profile_dir, entry.name),
                    database="unset",
                    type="unset",
                )
                try:
                    pconf.load_projectxml()
                except projectconfig.PasswordMismatchError:
                    LOGGER.trace(
                        "Profile %r [%r] requires a password", pconf.description, entry.name
                    )
                except Exception:
                    LOGGER.exception("Unexpected error trying to read profile %r", entry.name)
                    continue
                self.profiles[pconf.description] = pconf

        for name in sorted(self.profiles.keys()):
            self._user_interface.cbProfiles.addItem(name)

        last_profile = settings.SETTINGS.value("DBA/last_profile", None)

        if last_profile:
            self._user_interface.cbProfiles.setCurrentText(last_profile)

    @decorators.pyqt_slot()
    def toggleOptions(self) -> None:
        """Show/Hide Options."""
        self.showOptions(not self._options_showed)

    def showOptions(self, show_options: bool) -> None:
        """
        Show the frame options.
        """
        if show_options:
            self._user_interface.frmOptions.show()
            self._user_interface.tbDeleteProfile.show()
            self._user_interface.tbEditProfile.show()
            self._user_interface.setMinimumSize(self._max_size)
            self._user_interface.setMaximumSize(self._max_size)
            self._user_interface.resize(self._max_size)
        else:
            self._user_interface.frmOptions.hide()
            self._user_interface.tbDeleteProfile.hide()
            self._user_interface.tbEditProfile.hide()
            self._user_interface.setMinimumSize(self._min_size)
            self._user_interface.setMaximumSize(self._min_size)
            self._user_interface.resize(self._min_size)

        self._options_showed = show_options

    @decorators.pyqt_slot()
    def open(self) -> None:
        """
        Open the selected connection.
        """
        current_profile = self._user_interface.cbProfiles.currentText()
        pconf = self.getProjectConfig(current_profile)
        if pconf is None:
            return
        self.selected_project_config = pconf
        settings.SETTINGS.set_value("DBA/last_profile", current_profile)
        self.close()

    @decorators.pyqt_slot()
    def saveProfile(self) -> None:
        """
        Save the connection.
        """
        if self._user_interface.leDescription.text() == "":
            QtWidgets.QMessageBox.information(
                self._user_interface, "Pineboo", "La descripción no se puede dejar en blanco"
            )
            self._user_interface.leDescription.setFocus()
            return

        if self._user_interface.leDBPassword.text() != self._user_interface.leDBPassword2.text():
            QtWidgets.QMessageBox.information(
                self._user_interface, "Pineboo", "La contraseña de la BD no coincide"
            )
            self._user_interface.leDBPassword.setText("")
            self._user_interface.leDBPassword2.setText("")
            return

        if (
            self._user_interface.leProfilePassword.text()
            != self._user_interface.leProfilePassword2.text()
        ):

            QtWidgets.QMessageBox.information(
                self._user_interface, "Pineboo", "La contraseña del perfil no coincide"
            )
            self._user_interface.leProfilePassword.setText("")
            self._user_interface.leProfilePassword2.setText("")
            return

        if self.edit_mode:
            pconf = self.getProjectConfig(self._user_interface.cbProfiles.currentText())
            if pconf is None:
                return
            pconf.description = self._user_interface.leDescription.text()
        else:
            pconf = projectconfig.ProjectConfig(
                description=self._user_interface.leDescription.text(),
                database="unset",
                type="unset",
            )

        if not os.path.exists(self.profile_dir):
            import pathlib

            pathlib.Path(self.profile_dir).mkdir(parents=True, exist_ok=True)

        if os.path.exists(pconf.filename) and not self.edit_mode:
            QtWidgets.QMessageBox.information(
                self._user_interface, "Pineboo", "El perfil ya existe"
            )
            return

        pconf.type = self._user_interface.cbDBType.currentText()
        pconf.host = self._user_interface.leURL.text()
        pconf.port = int(self._user_interface.lePort.text())
        pconf.username = self._user_interface.leDBUser.text()
        pconf.password = self._user_interface.leDBPassword.text()
        pconf.database = self._user_interface.leDBName.text()

        pass_profile_text = ""
        if not self._user_interface.cbAutoLogin.isChecked():
            pass_profile_text = self._user_interface.leProfilePassword.text()
        pconf.project_password = pass_profile_text
        pconf.save_projectxml(overwrite_existing=self.edit_mode)
        # self.cleanProfileForm()
        self.loadProfiles()
        self._user_interface.cbProfiles.setCurrentText(pconf.description)

    @decorators.pyqt_slot()
    def deleteProfile(self) -> None:
        """
        Delete the selected connection.
        """
        if self._user_interface.cbProfiles.count() > 0:
            res = QtWidgets.QMessageBox.warning(
                self._user_interface,
                "Pineboo",
                "¿Desea borrar el perfil %s?" % self._user_interface.cbProfiles.currentText(),
                cast(
                    QtWidgets.QMessageBox.StandardButton,
                    QtWidgets.QMessageBox.StandardButton.Ok
                    | QtWidgets.QMessageBox.StandardButton.No,
                ),
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if res == QtWidgets.QMessageBox.StandardButton.No:
                return

            pconf: "projectconfig.ProjectConfig" = self.profiles[
                self._user_interface.cbProfiles.currentText()
            ]
            os.remove(pconf.filename)
            self.loadProfiles()

    def getProjectConfig(self, name: str) -> Optional["projectconfig.ProjectConfig"]:
        """
        Get a profile by name and ensure its fully loaded.
        """
        if name not in self.profiles.keys():
            return None

        pconf: "projectconfig.ProjectConfig" = self.profiles[name]

        if pconf.password_required:
            # As it failed to load earlier, it needs a password.
            # Copy the current password and test again...
            pconf.project_password = self._user_interface.lePassword.text()
            try:
                pconf.load_projectxml()
            except projectconfig.PasswordMismatchError:
                QtWidgets.QMessageBox.information(
                    self._user_interface, "Pineboo", "Contraseña Incorrecta"
                )
                return None
        return pconf

    @decorators.pyqt_slot()
    def editProfile(self) -> None:
        """
        Edit the selected connection.
        """
        # Cogemos el perfil y lo abrimos
        self.editProfileName(self._user_interface.cbProfiles.currentText())

    def editProfileName(self, name: str) -> None:
        """
        Edit profile from name. Must have been loaded earlier on loadProfiles.
        """
        pconf = self.getProjectConfig(name)
        if pconf is None:
            return

        self._user_interface.leProfilePassword.setText(pconf.project_password)
        self._user_interface.leProfilePassword2.setText(pconf.project_password)

        self._user_interface.cbAutoLogin.setChecked(pconf.project_password == "")

        self._user_interface.leDescription.setText(pconf.description)
        self._user_interface.leDBName.setText(pconf.database)

        self._user_interface.leURL.setText(pconf.host)
        self._user_interface.lePort.setText(str(pconf.port))
        self._user_interface.cbDBType.setCurrentText(pconf.type)

        self._user_interface.leDBUser.setText(pconf.username)

        self._user_interface.leDBPassword.setText(pconf.password)
        self._user_interface.leDBPassword2.setText(pconf.password)

        self.edit_mode = True

    @decorators.pyqt_slot(int)
    def updatePort(self) -> None:
        """
        Update to the driver default port.
        """
        self._user_interface.lePort.setText(
            self.sql_drivers.port(self._user_interface.cbDBType.currentText())
        )

    @decorators.pyqt_slot(int)
    def enablePassword(self, enable: Optional[int] = None) -> None:
        """
        Check if the profile requires password to login or not.
        """
        if self._user_interface.cbProfiles.count() == 0:
            return
        pconf: "projectconfig.ProjectConfig" = self.profiles[
            self._user_interface.cbProfiles.currentText()
        ]
        # NOTE: This disables the password entry once the password has been processed for
        # .. the profile once. So the user does not need to retype it.
        self._user_interface.lePassword.setEnabled(pconf.password_required)
        self._user_interface.lePassword.setText("")

    def updateDBName(self) -> None:
        """
        Update the name of the database with the description name.
        """
        self._user_interface.leDBName.setText(
            self._user_interface.leDescription.text().replace(" ", "_").lower()
        )

    @decorators.pyqt_slot(int)
    def cbAutoLogin_checked(self) -> None:
        """
        Process checked event from AutoLogin checkbox.
        """

        if self._user_interface.cbAutoLogin.isChecked():
            self._user_interface.leProfilePassword.setEnabled(False)
            self._user_interface.leProfilePassword2.setEnabled(False)
        else:
            self._user_interface.leProfilePassword.setEnabled(True)
            self._user_interface.leProfilePassword2.setEnabled(True)

    def change_profile_dir(self) -> None:
        """
        Change the path where profiles are saved.
        """

        new_dir = QtWidgets.QFileDialog.getExistingDirectory(
            self._user_interface,
            self.tr("Carpeta profiles"),
            self.profile_dir,
            QtWidgets.QFileDialog.Option.ShowDirsOnly,
        )

        if new_dir and new_dir is not self.profile_dir:
            settings.CONFIG.set_value("ebcomportamiento/profiles_folder", new_dir)
            self.profile_dir = new_dir
            projectconfig.ProjectConfig.profile_dir = new_dir
            self.loadProfiles()

    def eventFilter(self, object: "QtCore.QObject", event: "QtCore.QEvent") -> bool:
        """Event Filter."""

        if isinstance(event, QtGui.QKeyEvent):
            if event.key() in (
                cast(int, QtCore.Qt.Key.Key_Return),
                cast(int, QtCore.Qt.Key.Key_Enter),
            ):
                self.open()
                return True

            elif event.key() == cast(int, QtCore.Qt.Key.Key_Escape):
                self.close()
                return True

        return super().eventFilter(object, event)
