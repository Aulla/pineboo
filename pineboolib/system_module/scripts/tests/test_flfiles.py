"""Test flfiles module."""


import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import logging, application
from . import fixture_path
from pineboolib.core.utils import utils_base

import os

LOGGER = logging.get_logger("eneboo_%s" % __name__)


class TestFlFiles(unittest.TestCase):
    """TestFlfiles class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        utils_base.FORCE_DESKTOP = True
        init_testing()

    def test_basic(self) -> None:
        """Test load files into Database."""
        from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform import eneboo

        application.PROJECT.main_window = eneboo.MainForm()
        application.PROJECT.main_window.initScript()

        path = fixture_path("principal.eneboopkg")
        self.assertTrue(os.path.exists(path))
        self.assertTrue(qsa.sys.loadModules(path, False))
        qsa.sys.reinit()

        script = qsa.from_project("formRecordflfiles")
        self.assertTrue(script)
        script.cursor().first()
        func_ = script.init
        self.assertTrue(func_)
        func_()

    def test_basic2(self) -> None:
        """Test basic 2."""
        from pineboolib.qsa import qsa

        session = qsa.thread_session_new()
        session.begin()
        file_class = qsa.orm_("flfiles")
        self.assertTrue(file_class)
        obj_ = file_class()
        obj_.nombre = "prueba.txt"
        obj_.idmodulo = "flfactppal"
        obj_.sha = ""
        self.assertTrue(obj_.save())
        session.commit()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
