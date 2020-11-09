"""Test DlgConnect module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.loader.dlgconnect import dlgconnect
from pineboolib.core import settings
from pineboolib.core.utils import utils_base
import os
from pathlib import Path

actual_dir_profile: str = ""


class TestDlgConnect(unittest.TestCase):
    """Tes DlgConnect class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic_1(self) -> None:
        """Test basic 1."""

        dialog = dlgconnect.DlgConnect()
        dialog.load()
        dialog.cleanProfileForm()

        # dialog._user_interface.cbDBType.
        dialog._user_interface.cbProfiles.setEditText("eoo")
        dialog.edit_mode = False
        dialog._user_interface.cbAutoLogin.setChecked(True)
        dialog._user_interface.leDescription.setText("pytest")
        dialog._user_interface.leDBPassword.setText("12345")
        dialog._user_interface.leDBPassword2.setText("12345")
        dialog._user_interface.leProfilePassword.setText("12345")
        dialog._user_interface.leProfilePassword2.setText("12345")
        dialog._user_interface.leDBName.setText("prueba_db")
        dialog._user_interface.leURL.setText("localhost")
        dialog._user_interface.lePort.setText("5432")
        dialog._user_interface.leDBUser.setText("usuario")
        dialog._user_interface.leProfilePassword.setText("12345")
        self.assertEqual(dialog._user_interface.leURL.text(), "localhost")
        self.assertEqual(dialog._user_interface.leDBUser.text(), "usuario")
        self.assertEqual(dialog._user_interface.leDBPassword.text(), "12345")
        self.assertEqual(dialog._user_interface.leDBName.text(), "prueba_db")
        self.assertEqual(dialog._user_interface.leProfilePassword.text(), "12345")
        profile_dir: str = utils_base.filedir(
            settings.CONFIG.value(
                "ebcomportamiento/profiles_folder", "%s/Pineboo/profiles" % Path.home()
            )
        )
        if os.path.exists("%s/pytest.xml" % profile_dir):
            os.remove("%s/pytest.xml" % profile_dir)
        dialog.saveProfile()
        dialog.showOptions(True)
        dialog.showOptions(False)
        self.assertTrue(dialog.getProjectConfig("pytest"))
        dialog.editProfileName("pytest")
        dialog.close()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure this class is finished correctly."""

        finish_testing()
