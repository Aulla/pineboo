"""Test_process module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.application.packager import pnpackager
from . import fixture_path


class TestPNPAckager(unittest.TestCase):
    """TestUnpacker Class."""


class TestProcess(unittest.TestCase):
    """TestProcess Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_pnpackager(self) -> None:
        """Test eneboopkgs load."""
        from pineboolib import application
        from pineboolib.fllegacy import systype
        import os

        file_name = "%s/package.eneboopkg" % application.PROJECT.tmpdir
        packager = pnpackager.PNPackager(file_name)
        self.assertTrue(packager.pack(fixture_path("principal")))
        self.assertTrue(os.path.exists(file_name))
        self.assertTrue(os.path.exists("%s/modules.def" % os.path.dirname(file_name)))
        self.assertTrue(os.path.exists("%s/files.def" % os.path.dirname(file_name)))

        qsa_sys = systype.SysType()
        self.assertTrue(qsa_sys.loadModules(file_name, False))

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
