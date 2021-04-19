"""Test_sysbasetype module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.qsatypes import sysbasetype
from pineboolib import application

from typing import Any


class TestSysBaseClassGeneral(unittest.TestCase):
    """TestSysBaseClassGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic functions."""
        import platform
        from pineboolib.core.utils.utils_base import filedir

        import os

        base_type = sysbasetype.SysBaseType()
        self.assertEqual(base_type.nameUser(), "memory_user")
        # self.assertEqual(base_type.interactiveGUI(), "Pineboo")
        self.assertEqual(base_type.isLoadedModule("sys"), True)
        os_name = "LINUX"
        if platform.system() == "Windows":
            os_name = "WIN32"
        elif platform.system() == "Darwin":
            os_name = "MACX"

        self.assertEqual(base_type.osName(), os_name)
        self.assertEqual(base_type.nameBD(), "temp_db")
        self.assertEqual(base_type.installPrefix(), filedir(".."))
        self.assertEqual(base_type.version(), str(application.PROJECT.load_version()))
        file_path = "%s/test_sysbasetype.txt" % application.PROJECT.tmpdir

        if os.path.exists(file_path):
            os.remove(file_path)

        base_type.write("ISO-8859-15", file_path, "avión, caña")
        self.assertEqual(os.path.exists(file_path), True)
        self.assertEqual(base_type.nameDriver(), "FLsqlite")
        self.assertEqual(base_type.nameHost(), "")

    def test_basic_2(self) -> None:
        """Test Basic functions."""
        base_type = sysbasetype.SysBaseType()
        self.assertFalse(base_type.isDeveloperBuild())
        self.assertFalse(base_type.isNebulaBuild())
        self.assertFalse(base_type.isCloudMode())

        base_type.Mr_Proper()
        base_type.cleanupMetaData()

    def test_basic_3(self) -> None:
        """Test basic functions."""
        base_type = sysbasetype.SysBaseType()
        report_changes = "Nombre: 1 \nEstado: 2 \nShaOldTxt: 3 \nShaNewTxt: 4 \n###########################################\n"
        self.assertEqual(base_type.reportChanges({"prueba": "1@2@3@4"}), report_changes)

    def test_objects(self) -> None:
        """Test objects functions."""
        from pineboolib.fllegacy import fltabledb

        application.PROJECT.actions["flareas"].openDefaultForm()

        form = application.PROJECT.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ]._master_widget
        # form = flformdb.FLFormDB(None, action)
        # self.assertTrue(form)
        # form.load()
        if form is None:
            self.assertTrue(form)  # type: ignore [unreachable] # noqa F821
            return

        fltable: Any = form.findChild(fltabledb.FLTableDB, "tableDBRecords")

        base_type = sysbasetype.SysBaseType()

        self.assertFalse(base_type.setObjText(fltable, "flfielddb_5", "Holas"))
        self.assertFalse(base_type.setObjText(fltable, "toolButtonInsert", "prueba"))

        base_type.disableObj(form, "tableDBRecords")
        base_type.enableObj(form, "tableDBRecords")

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

        base_type = sysbasetype.SysBaseType()

        prueba_conn_1 = application.PROJECT.conn_manager.useConn("prueba")
        self.assertEqual(prueba_conn_1.isOpen(), False)
        self.assertEqual(base_type.addDatabase("prueba"), True)
        self.assertEqual(prueba_conn_1.isOpen(), True)
        self.assertEqual(base_type.removeDatabase("prueba"), True)
        self.assertNotEqual(base_type.idSession(), None)
        self.assertEqual(prueba_conn_1.isOpen(), False)
        prueba_conn_2 = application.PROJECT.conn_manager.useConn("prueba")
        self.assertEqual(prueba_conn_2.isOpen(), False)
        self.assertEqual(base_type.addDatabase("prueba"), True)
        self.assertEqual(prueba_conn_2.isOpen(), True)
        self.assertEqual(base_type.removeDatabase("prueba"), True)
        self.assertEqual(prueba_conn_1.isOpen(), False)

        self.assertTrue(
            base_type.addDatabase(
                "FLsqlite",
                ":memory:",
                prueba_conn_1.user(),
                prueba_conn_1.returnword(),
                prueba_conn_1.host(),
                prueba_conn_1.port(),
                "extra",
            )
        )
        self.assertEqual(application.PROJECT.conn_manager.useConn("extra")._db_name, ":memory:")
        self.assertEqual(
            application.PROJECT.conn_manager.useConn("extra")._db_host, prueba_conn_1.host()
        )
        self.assertEqual(
            application.PROJECT.conn_manager.useConn("extra")._db_port, prueba_conn_1.port()
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
