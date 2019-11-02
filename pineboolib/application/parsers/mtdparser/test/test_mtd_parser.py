"""Test_sysbasetype module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.core.settings import config


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic(self) -> None:
        """Test basic functions."""
        from pineboolib.application.parsers.mtdparser import pnmtdparser
        from pineboolib.core.utils.utils_base import filedir
        import os

        file = filedir(
            "%s/cache/temp_db/sys/file.mtd/flmodules_model.py"
            % config.value("ebcomportamiento/temp_dir")
        )
        if os.path.exists(file):
            os.remove(file)
        pnmtdparser.mtd_parse("flmodules")
        self.assertTrue(os.path.exists(file))

    def test_orm_parser(self) -> None:
        """Test ORM parser."""
        from pineboolib.core.settings import config
        from pineboolib.application.parsers.mtdparser import pnmtdparser, pnormmodelsfactory
        from pineboolib import application
        import os

        for table in application.project.conn_manager.useConn("default").tables("Tables"):
            file_path = pnmtdparser.mtd_parse(table)
            self.assertTrue(os.path.exists(file_path))

        pnormmodelsfactory.load_models()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
