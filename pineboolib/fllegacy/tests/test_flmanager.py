"""Test_flmanager module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from . import fixture_path

from pineboolib import application


class TestFLManager(unittest.TestCase):
    """TestFLManager Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_init_count(self) -> None:
        """InitCount test."""

        manager_ = application.PROJECT.conn_manager.manager()
        self.assertTrue(manager_.initCount() >= 2)

    def test_basic1(self) -> None:
        """Basic test."""
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.fllegacy import systype
        import os

        qsa_sys = systype.SysType()
        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa_sys.loadModules(path, False))
        application.PROJECT.actions["flareas"].load_master_widget()

        cursor = pnsqlcursor.PNSqlCursor("fltest2")
        manager_ = cursor.db().manager()
        field_mtd = cursor.metadata().field("string_field")

        if field_mtd is not None:

            self.assertEqual(
                manager_.formatAssignValue(field_mtd, "string", True),
                "upper(fltest2.string_field) = 'STRING'",
            )

            self.assertEqual(
                manager_.formatAssignValueLike(field_mtd, "value", True),
                "upper(fltest2.string_field) LIKE 'VALUE%%'",
            )

            self.assertEqual(manager_.formatValueLike(field_mtd, "value", True), "LIKE 'VALUE%%'")

        mtd_ = manager_.metadata("flvar")
        self.assertTrue(mtd_ is not None)
        if mtd_ is not None:
            self.assertFalse(manager_.checkMetaData(mtd_, cursor.metadata()))
            self.assertTrue(manager_.checkMetaData(mtd_, mtd_))

        self.assertEqual(
            manager_.formatAssignValue("nombre", "string", "prueba.qs", True),
            "upper(nombre) = 'PRUEBA.QS'",
        )

        # self.assertFalse(manager_.alterTable(mtd_, mtd_, "", False))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
