"""Test_acls module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.fllegacy import flapplication, systype
from pineboolib.application.acls import pnaccesscontrollists


class TestACLS(unittest.TestCase):
    """TestPNBuffer Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        # install acls
        from pineboolib.application.database import pnsqlcursor

        cursor_flgroups = pnsqlcursor.PNSqlCursor("flgroups")
        cursor_flgroups.setModeAccess(cursor_flgroups.Insert)
        cursor_flgroups.refreshBuffer()
        cursor_flgroups.setValueBuffer("idgroup", "usuarios")
        cursor_flgroups.setValueBuffer("descripcion", "Grupo usuarios")
        cursor_flgroups.commitBuffer()

        cursor_flusers = pnsqlcursor.PNSqlCursor("flusers")
        cursor_flusers.setModeAccess(cursor_flusers.Insert)
        cursor_flusers.refreshBuffer()
        cursor_flusers.setValueBuffer("iduser", "memory_user")
        cursor_flusers.setValueBuffer("idgroup", "usuarios")
        cursor_flusers.setValueBuffer("descripcion", "test user")
        cursor_flusers.commitBuffer()

        cursor_flacls = pnsqlcursor.PNSqlCursor("flacls")
        cursor_flacls.setModeAccess(cursor_flacls.Insert)
        cursor_flacls.setActivatedCheckIntegrity(False)
        cursor_flacls.refreshBuffer()
        cursor_flacls.setValueBuffer("idacl", "primera")
        cursor_flacls.setValueBuffer("descripcion", "firsrt acl")
        cursor_flacls.setValueBuffer("prioridadgrupointro", 2)
        cursor_flacls.setValueBuffer("prioridadusuariointro", 1)
        cursor_flacls.commitBuffer()

        cursor_flacs = pnsqlcursor.PNSqlCursor("flacs")
        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 1)
        cursor_flacs.setValueBuffer("tipo", "table")
        cursor_flacs.setValueBuffer("nombre", "flgroups")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "primera")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:table:Maestro:flgroup")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.commitBuffer()

        id_acs = cursor_flacs.valueBuffer("idac")

        cursor_flacos = pnsqlcursor.PNSqlCursor("flacos")
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "descripcion")  # field_name
        cursor_flacos.setValueBuffer("permiso", "--")  # No visible
        cursor_flacos.setValueBuffer("idac", id_acs)
        cursor_flacos.setValueBuffer("tipocontrol", "Tabla")
        cursor_flacos.commitBuffer()

    def test_tables(self) -> None:
        """Test table acls."""

        sys_type = systype.SysType()
        sys_type.installACL("primera")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        flapplication.aqApp.set_acl(acl)

        # clear metadata cache
        flapplication.aqApp.db().manager().cacheMetaDataSys_ = {}
        flapplication.aqApp.db().manager().cacheMetaData_ = {}

        mtd_flgroups = flapplication.aqApp.db().manager().metadata("flgroups")
        self.assertTrue(mtd_flgroups)
        field_descripcion = mtd_flgroups.field("descripcion")
        self.assertFalse(field_descripcion.visible())

    @classmethod
    def tearDown(cls) -> None:
        """Ensure test clear all data."""
        from pineboolib.application.database import utils

        utils.sqlDelete("flacls", "1=1")
        utils.sqlDelete("flacs", "1=1")
        utils.sqlDelete("flacos", "1=1")
        utils.sqlDelete("flusers", "1=1")
        utils.sqlDelete("flgroups", "1=1")
        utils.sqlDelete("flfiles", "nombre='acl.xml'")
        flapplication.aqApp.db().manager().cacheMetaDataSys_ = {}
        flapplication.aqApp.db().manager().cacheMetaData_ = {}
        flapplication.aqApp.acl_ = None
