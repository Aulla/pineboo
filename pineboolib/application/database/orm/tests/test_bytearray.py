"""Test bytearray module."""

import unittest

from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.qsa import qsa
from . import fixture_path
from datetime import datetime


class TestByteArray(unittest.TestCase):
    """TestByteArray Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test basic."""

        image_path = fixture_path("tux.png")
        session = qsa.thread_session_new()
        session.begin()
        obj = qsa.orm.flupdates()
        obj.auxbin = open(image_path, "rb").read()
        obj.fecha = datetime.now().date()
        obj.hora = datetime.now().time()
        obj.nombre = "prueba"
        obj.modulesdef = ""
        obj.filesdef = ""

        obj.shaglobal = ""
        obj.save()
        session.commit()
        qsa.thread_session_free()

    def test_basic2(self) -> None:
        """Test basic 2."""

        util = qsa.FLUtil()
        session = qsa.session()
        session.begin()
        image_path = fixture_path("tux.png")

        self.assertTrue(
            util.sqlInsert(
                "flupdates",
                ["fecha", "hora", "nombre", "modulesdef", "filesdef", "shaglobal", "auxbin"],
                [
                    datetime.now().date(),
                    datetime.now().time(),
                    "prueba2",
                    "",
                    "",
                    "",
                    open(image_path, "rb").read(),
                ],
            )
        )
        session.rollback()
        session.close()

    def test_basic3(self) -> None:
        """Test basic 3."""

        util = qsa.FLUtil()
        session = qsa.session()
        session.begin()
        sql = "INSERT INTO flupdates(id, fecha, hora , nombre, modulesdef, filesdef, shaglobal, actual, auxbin, auxtxt)"
        sql += " VALUES (666,'%s','%s','prueba3','x','y','z', False,'aa:123', 'tt')" % (
            datetime.now().date(),
            datetime.now().time(),
        )
        result = util.execSql(sql)
        self.assertTrue(result is not False)
        session.rollback()
        session.close()

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()
