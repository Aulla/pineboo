"""Test_virtual_database module."""
import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application


class TestVirtualExists(unittest.TestCase):
    """TestVirtualExists Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        application.VIRTUAL_DB = False
        init_testing()

    def test_basic(self) -> None:
        """Test basic."""
        import os

        self.assertTrue(
            os.path.exists("%s/sqlite_databases/temp_db.sqlite3" % application.PROJECT.tmpdir)
        )

    def test_use_channel(self) -> None:
        """Test use channel."""

        self.assertFalse(application.USE_WEBSOCKET_CHANNEL)
        from pineboolib.qsa import qsa

        self.assertFalse(
            qsa.ws_channel_send({}, "nobody")  # type: ignore [func-returns-value] # noqa: F821
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        application.VIRTUAL_DB = True
        finish_testing()


class TestVirtualNotExists(unittest.TestCase):
    """TestVirtualNotExists Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic."""
        import os

        self.assertFalse(
            os.path.exists("%s/sqlite_databases/temp_db.sqlite3" % application.PROJECT.tmpdir)
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
