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
        qsa_sys.loadModules(path, False)
        application.PROJECT.actions["flareas"].load()

        cursor = pnsqlcursor.PNSqlCursor("fltest2")
        manager_ = cursor.db().manager()

        self.assertEqual(
            manager_.formatAssignValue(cursor.metadata().field("string_field"), "string", True),
            "upper(fltest2.string_field) = 'STRING'",
        )

        self.assertEqual(
            manager_.formatAssignValueLike("string_field", "string", "value", True),
            "upper(string_field) LIKE 'VALUE%%'",
        )

        mtd_ = manager_.metadata("flvar")
        self.assertTrue(mtd_ is not None)
        if mtd_ is not None:
            self.assertFalse(manager_.checkMetaData(mtd_, cursor.metadata()))
            self.assertTrue(manager_.checkMetaData(mtd_, mtd_))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
