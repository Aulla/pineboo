"""Test_sysbasetype module."""

import unittest

from pineboolib import application

from pineboolib.loader.main import init_testing, finish_testing


class TestMtdParserGeneral(unittest.TestCase):
    """TestMtdParserGeneral Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""

        init_testing()

    def test_basic_1(self) -> None:
        """Test ORM parser."""

        from .. import pnmtdparser, pnormmodelsfactory
        import os

        for mtd_name in application.PROJECT.files.keys():
            if mtd_name.endswith(".mtd"):
                file_path = pnmtdparser.mtd_parse(
                    mtd_name, application.PROJECT.files[mtd_name].path()
                )
                if file_path:

                    self.assertTrue(os.path.exists(file_path))
                else:
                    self.assertTrue(False)

        pnormmodelsfactory.load_models()

    def test_basic_3(self) -> None:
        """Test create table."""

        from sqlalchemy import MetaData  # type: ignore

        meta = MetaData()
        meta.create_all(application.PROJECT.conn_manager.mainConn().engine())

    def test_basic_4(self) -> None:
        """Test load model."""
        from pineboolib.qsa import qsa

        flareas_orm = qsa.orm_("flmodules")
        self.assertTrue(flareas_orm)
        # session = flareas_orm.__session__
        # self.assertEqual(session, application.PROJECT.conn_manager.mainConn().session())
        # self.assertEqual(session.query(flareas_orm).count(), 0)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
