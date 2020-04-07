"""Test_sysbasetype module."""

import unittest

from pineboolib import application

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.core import settings

orm_enabled: bool
orm_parser_disabled: bool
orm_load_disabled: bool


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        global orm_enabled, orm_parser_disabled, orm_load_disabled

        orm_enabled = settings.CONFIG.value("ebcomportamiento/orm_enabled", False)
        orm_parser_disabled = settings.CONFIG.value("ebcomportamiento/orm_parser_disabled", False)
        orm_load_disabled = settings.CONFIG.value("ebcomportamiento/orm_load_disabled", False)

        settings.CONFIG.set_value("ebcomportamiento/orm_enabled", True)
        settings.CONFIG.set_value("ebcomportamiento/orm_parser_disabled", False)
        settings.CONFIG.set_value("ebcomportamiento/orm_load_disabled", False)
        init_testing()

    def test_basic_1(self) -> None:
        """Test basic functions."""
        from pineboolib.application.parsers.mtdparser import pnormmodelsfactory, pnmtdparser
        from pineboolib.core.utils.utils_base import filedir
        from pineboolib.qsa import qsa
        import os

        file = filedir(
            "%s/cache/temp_db/sys/file.mtd/flmodules_model.py"
            % settings.CONFIG.value("ebcomportamiento/temp_dir")
        )

        if os.path.exists(file):
            os.remove(file)

        action_xml = application.PROJECT.actions["flmodules"]
        self.assertTrue(action_xml)
        pnmtdparser.mtd_parse(action_xml)
        self.assertTrue(os.path.exists(file))

    def test_basic_2(self) -> None:
        """Test ORM parser."""

        from pineboolib.application.parsers.mtdparser import pnmtdparser, pnormmodelsfactory
        from pineboolib.qsa import qsa
        import os

        for action_name in application.PROJECT.actions:
            file_path = pnmtdparser.mtd_parse(application.PROJECT.actions[action_name])
            if file_path:
                self.assertTrue(os.path.exists(file_path))

        pnormmodelsfactory.load_models()

    def test_basic_3(self) -> None:
        """Test create table."""

        from sqlalchemy import MetaData

        meta = MetaData()
        meta.create_all(application.PROJECT.conn_manager.mainConn().engine())

    def test_basic_4(self) -> None:
        """Test load model."""
        from pineboolib.qsa import qsa

        flareas_orm = qsa.orm_("flmodules")
        self.assertTrue(flareas_orm)
        session = flareas_orm.__session__
        self.assertEqual(session, application.PROJECT.conn_manager.mainConn().session())
        # self.assertEqual(session.query(flareas_orm).count(), 0)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        global orm_enabled, orm_parser_disabled, orm_load_disabled

        settings.CONFIG.set_value("ebcomportamiento/orm_enabled", orm_enabled)
        settings.CONFIG.set_value("ebcomportamiento/orm_parser_disabled", orm_parser_disabled)
        settings.CONFIG.set_value("ebcomportamiento/orm_load_disabled", orm_load_disabled)

        # finish_testing()
