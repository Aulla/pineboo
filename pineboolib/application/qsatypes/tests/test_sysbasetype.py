"""Test_sysbasetype module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestSysBaseClassGeneral(unittest.TestCase):
    """TestSysBaseClassGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic functions."""
        import platform
        from pineboolib.application.qsatypes import sysbasetype
        from pineboolib.core.utils.utils_base import filedir
        from pineboolib import application
        import os

        base_type = sysbasetype.SysBaseType()

        self.assertEqual(base_type.nameUser(), "memory_user")
        self.assertEqual(base_type.interactiveGUI(), "Pineboo")
        self.assertEqual(base_type.isLoadedModule("sys"), True)
        os_name = "LINUX"
        if platform.system() == "Windows":
            os_name = "WIN32"
        elif platform.system() == "Darwin":
            os_name = "MACX"

        self.assertEqual(base_type.osName(), os_name)
        self.assertEqual(base_type.nameBD(), "temp_db")
        self.assertEqual(base_type.installPrefix(), filedir(".."))
        self.assertEqual(base_type.version(), str(application.project.version))
        file_path = "%s/test_sysbasetype.txt" % application.project.tmpdir

        if os.path.exists(file_path):
            os.remove(file_path)

        base_type.write("ISO-8859-15", file_path, "avión, caña")
        self.assertEqual(os.path.exists(file_path), True)
        self.assertEqual(base_type.nameDriver(), "FLsqlite")
        self.assertEqual(base_type.nameHost(), None)

    def test_objects(self) -> None:
        """Test objects functions."""

        from pineboolib.qsa import dictmodules
        from pineboolib.application.qsatypes import sysbasetype
        from pineboolib.application.database import pnsqlcursor

        cursor_1 = pnsqlcursor.PNSqlCursor("flmodules")
        cursor_1.select()
        cursor_1.setModeAccess(cursor_1.Insert)
        cursor_1.refreshBuffer()
        cursor_1.insertRecord(False)

        form = dictmodules.from_project("formRecordflmodules")
        self.assertTrue(form)

        field = form.child("flfielddb_5")

        base_type = sysbasetype.SysBaseType()

        self.assertTrue(base_type.setObjText(form, "flfielddb_5", "Holas"))
        self.assertTrue(base_type.setObjText(form, "toolButtonInsert", "prueba"))

        base_type.disableObj(form, "flfielddb_5")
        self.assertTrue(field.keepDisabled_)
        base_type.enableObj(form, "flfielddb_5")
        self.assertFalse(field.keepDisabled_)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


class TestSysBaseClassDataBase(unittest.TestCase):
    """TestSysBaseClassDataBase Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test addDatabase and removeDatabase functions."""
        from pineboolib.application.qsatypes import sysbasetype
        from pineboolib import application

        base_type = sysbasetype.SysBaseType()

        prueba_conn_1 = application.project.conn_manager.useConn("prueba")
        self.assertEqual(prueba_conn_1.isOpen(), False)
        self.assertEqual(base_type.addDatabase("prueba"), True)
        self.assertEqual(prueba_conn_1.isOpen(), True)
        self.assertEqual(base_type.removeDatabase("prueba"), True)
        self.assertNotEqual(base_type.idSession(), None)
        self.assertEqual(prueba_conn_1.isOpen(), False)
        prueba_conn_2 = application.project.conn_manager.useConn("prueba")
        self.assertEqual(prueba_conn_2.isOpen(), False)
        self.assertEqual(base_type.addDatabase("prueba"), True)
        self.assertEqual(prueba_conn_2.isOpen(), True)
        self.assertEqual(base_type.removeDatabase("prueba"), True)
        self.assertEqual(prueba_conn_1.isOpen(), False)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
