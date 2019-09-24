"""Test_acls module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.fllegacy import flapplication, systype
from pineboolib.core.settings import config
from pineboolib.application.acls import pnaccesscontrollists


class TestACLS(unittest.TestCase):
    """TestPNBuffer Class."""

    db_admin: bool

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        # install acls
        from pineboolib.application.database import pnsqlcursor

        cls.db_admin = config.value("application/dbadmin_enabled", False)

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
        cursor_flacls.setValueBuffer("descripcion", "first acl")
        cursor_flacls.setValueBuffer("prioridadgrupointro", 2)
        cursor_flacls.setValueBuffer("prioridadusuariointro", 1)
        cursor_flacls.commitBuffer()
        cursor_flacls.setModeAccess(cursor_flacls.Insert)
        cursor_flacls.setActivatedCheckIntegrity(False)
        cursor_flacls.refreshBuffer()
        cursor_flacls.setValueBuffer("idacl", "segunda")
        cursor_flacls.setValueBuffer("descripcion", "second acl")
        cursor_flacls.setValueBuffer("prioridadgrupointro", 2)
        cursor_flacls.setValueBuffer("prioridadusuariointro", 1)
        cursor_flacls.commitBuffer()
        cursor_flacls.setModeAccess(cursor_flacls.Insert)
        cursor_flacls.setActivatedCheckIntegrity(False)
        cursor_flacls.refreshBuffer()
        cursor_flacls.setValueBuffer("idacl", "tercera")
        cursor_flacls.setValueBuffer("descripcion", "third acl")
        cursor_flacls.setValueBuffer("prioridadgrupointro", 2)
        cursor_flacls.setValueBuffer("prioridadusuariointro", 1)
        cursor_flacls.commitBuffer()
        cursor_flacls.setModeAccess(cursor_flacls.Insert)
        cursor_flacls.setActivatedCheckIntegrity(False)
        cursor_flacls.refreshBuffer()
        cursor_flacls.setValueBuffer("idacl", "cuarta")
        cursor_flacls.setValueBuffer("descripcion", "fourth acl")
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
        id_acs_1 = cursor_flacs.valueBuffer("idac")

        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 2)
        cursor_flacs.setValueBuffer("tipo", "table")
        cursor_flacs.setValueBuffer("nombre", "flmodules")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "primera")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:table:Maestro:flmodules")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.commitBuffer()
        id_acs_2 = cursor_flacs.valueBuffer("idac")

        # global tables '--'
        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 3)
        cursor_flacs.setValueBuffer("tipo", "table")
        cursor_flacs.setValueBuffer("nombre", "flareas")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "segunda")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:table:Maestro:flareas")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.setValueBuffer("permiso", "--")
        cursor_flacs.commitBuffer()

        # global tables 'r-'
        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 4)
        cursor_flacs.setValueBuffer("tipo", "table")
        cursor_flacs.setValueBuffer("nombre", "flusers")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "segunda")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:table:Maestro:flusers")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.setValueBuffer("permiso", "r-")
        cursor_flacs.commitBuffer()

        # global tables 'rw'
        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 5)
        cursor_flacs.setValueBuffer("tipo", "table")
        cursor_flacs.setValueBuffer("nombre", "fltest")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "segunda")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:table:Maestro:fltest")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.setValueBuffer("permiso", "rw")
        cursor_flacs.commitBuffer()

        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 6)
        cursor_flacs.setValueBuffer("tipo", "form")
        cursor_flacs.setValueBuffer("nombre", "formRecordflmodules")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "tercera")
        cursor_flacs.setValueBuffer(
            "descripcion", "Sistema:Administración:form:Edición:formRecordflmodules"
        )
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Edición")
        cursor_flacs.commitBuffer()

        id_acs_3 = cursor_flacs.valueBuffer("idac")

        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 7)
        cursor_flacs.setValueBuffer("tipo", "mainwindow")
        cursor_flacs.setValueBuffer("nombre", "sys")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("idacl", "cuarta")
        cursor_flacs.setValueBuffer("descripcion", "Sistema:Administración:mainwindow:Maestro:sys")
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")
        cursor_flacs.commitBuffer()

        id_acs_4 = cursor_flacs.valueBuffer("idac")

        # global form 'r-'
        cursor_flacs.setModeAccess(cursor_flacs.Insert)
        cursor_flacs.setActivatedCheckIntegrity(False)
        cursor_flacs.refreshBuffer()
        cursor_flacs.setValueBuffer("prioridad", 8)
        cursor_flacs.setValueBuffer("tipo", "form")
        cursor_flacs.setValueBuffer("nombre", "formflmodules")
        cursor_flacs.setValueBuffer("idgroup", "usuarios")
        cursor_flacs.setValueBuffer("permiso", "r-")
        cursor_flacs.setValueBuffer("idacl", "tercera")
        cursor_flacs.setValueBuffer(
            "descripcion", "Sistema:Administración:form:Maestro:formflmodules"
        )
        cursor_flacs.setValueBuffer("degrupo", True)
        cursor_flacs.setValueBuffer("idarea", "sys")
        cursor_flacs.setValueBuffer("idmodule", "sys")
        cursor_flacs.setValueBuffer("tipoform", "Maestro")

        cursor_flacs.commitBuffer()

        cursor_flacos = pnsqlcursor.PNSqlCursor("flacos")
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        # single table 'r-'
        cursor_flacos.setValueBuffer("nombre", "descripcion")
        cursor_flacos.setValueBuffer("permiso", "r-")
        cursor_flacos.setValueBuffer("idac", id_acs_1)
        cursor_flacos.setValueBuffer("tipocontrol", "Tabla")
        cursor_flacos.commitBuffer()
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        # single table '--'
        cursor_flacos.setValueBuffer("nombre", "idgroup")
        cursor_flacos.setValueBuffer("permiso", "--")
        cursor_flacos.setValueBuffer("idac", id_acs_1)
        cursor_flacos.setValueBuffer("tipocontrol", "Tabla")
        cursor_flacos.commitBuffer()
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        # single table 'rw'
        cursor_flacos.setValueBuffer("nombre", "descripcion")
        cursor_flacos.setValueBuffer("permiso", "rw")
        cursor_flacos.setValueBuffer("idac", id_acs_2)
        cursor_flacos.commitBuffer()

        # single form 'r-'
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "botonExportar")
        cursor_flacos.setValueBuffer("descripcion", "Botón:botonExportar")
        cursor_flacos.setValueBuffer("tipocontrol", "Botón")
        cursor_flacos.setValueBuffer("permiso", "r-")
        cursor_flacos.setValueBuffer("idac", id_acs_3)
        cursor_flacos.commitBuffer()

        # single form '--'
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "botonCargar")
        cursor_flacos.setValueBuffer("descripcion", "Botón:botonCargar")
        cursor_flacos.setValueBuffer("tipocontrol", "Botón")
        cursor_flacos.setValueBuffer("permiso", "--")
        cursor_flacos.setValueBuffer("idac", id_acs_3)
        cursor_flacos.commitBuffer()

        # single mainwindow '--'
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "ebcomportamiento")
        cursor_flacos.setValueBuffer("descripcion", "Todos:ebcomportamiento")
        cursor_flacos.setValueBuffer("tipocontrol", "Todos")
        cursor_flacos.setValueBuffer("permiso", "--")
        cursor_flacos.setValueBuffer("idac", id_acs_4)
        cursor_flacos.commitBuffer()

        # single mainwindow '-w'
        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "flgroups")
        cursor_flacos.setValueBuffer("descripcion", "Todos:flgroups")
        cursor_flacos.setValueBuffer("tipocontrol", "Todos")
        cursor_flacos.setValueBuffer("permiso", "-w")
        cursor_flacos.setValueBuffer("idac", id_acs_4)
        cursor_flacos.commitBuffer()

    def test_form_flacos(self) -> None:
        """Test form acls from flacos."""
        from pineboolib.qsa import qsa

        sys_type = systype.SysType()
        sys_type.installACL("tercera")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        flapplication.aqApp.set_acl(acl)
        button_1 = qsa.from_project("formRecordflmodules").child("botonExportar")  # r-
        button_2 = qsa.from_project("formRecordflmodules").child("botonCargar")  # --
        self.assertTrue(button_2.isHidden())  # not visible
        self.assertFalse(button_2.isEnabled())  # not enabled
        self.assertFalse(button_1.isHidden())  # visible
        self.assertFalse(button_1.isEnabled())  # not enabled

    def test_mainwindow_flacos(self) -> None:

        from PyQt5 import QtWidgets

        from pineboolib import application
        import importlib

        sys_type = systype.SysType()
        sys_type.installACL("cuarta")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        flapplication.aqApp.set_acl(acl)

        config.set_value("application/dbadmin_enabled", True)

        project = application.project
        project.main_form = importlib.import_module("pineboolib.plugins.mainform.eneboo.eneboo")
        project.main_window = getattr(project.main_form, "mainWindow", None)
        main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_)
        self.main_w = main_form_()
        self.main_w.initScript()
        self.main_w.show()
        self.assertTrue(self.main_w)

        action_1 = self.main_w.findChild(QtWidgets.QAction, "ebcomportamiento")
        self.assertTrue(action_1)
        self.assertFalse(action_1.isVisible())

        action_2 = self.main_w.findChild(QtWidgets.QAction, "flgroups")
        self.assertTrue(action_2)
        self.assertFalse(action_2.isVisible())

        action_3 = self.main_w.findChild(QtWidgets.QAction, "flareas")
        self.assertTrue(action_3)
        self.assertTrue(action_3.isVisible())

    def test_form_globals(self) -> None:
        """Test form acls globals."""
        from pineboolib.qsa import qsa
        from pineboolib import application
        import importlib

        sys_type = systype.SysType()
        sys_type.installACL("tercera")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        flapplication.aqApp.set_acl(acl)

        project = application.project
        project.main_form = importlib.import_module("pineboolib.plugins.mainform.eneboo.eneboo")
        project.main_window = getattr(project.main_form, "mainWindow", None)
        main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_)
        self.main_w = main_form_()
        self.main_w.initScript()
        self.main_w.show()
        self.assertTrue(self.main_w)

        form = qsa.from_project("formflmodules")
        control_1 = form.child("tableDBRecords")
        self.assertTrue(control_1)
        self.assertFalse(control_1.isEnabled())

    def test_tables_flacos(self) -> None:
        """Test table acls from flacos."""

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
        # descripcion = '--'
        field_descripcion = mtd_flgroups.field("descripcion")
        self.assertFalse(field_descripcion.editable())
        self.assertTrue(field_descripcion.visible())

        # idgroup = 'r-'
        field_idgroup = mtd_flgroups.field("idgroup")
        self.assertFalse(field_idgroup.visible())

        mtd_flmodules = flapplication.aqApp.db().manager().metadata("flmodules")
        field_descripcion = mtd_flmodules.field("descripcion")

        # descripcion = 'rw'
        self.assertTrue(field_descripcion.editable())
        self.assertTrue(field_descripcion.visible())

    def test_tables_globals(self) -> None:
        """Test table acls globals."""

        sys_type = systype.SysType()
        sys_type.installACL("segunda")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        flapplication.aqApp.set_acl(acl)

        # clear metadata cache
        flapplication.aqApp.db().manager().cacheMetaDataSys_ = {}
        flapplication.aqApp.db().manager().cacheMetaData_ = {}

        mtd_flareas = flapplication.aqApp.db().manager().metadata("flareas")
        self.assertTrue(mtd_flareas)
        # '--'
        field_descripcion = mtd_flareas.field("descripcion")
        self.assertFalse(field_descripcion.editable())
        self.assertFalse(field_descripcion.visible())

        mtd_flusers = flapplication.aqApp.db().manager().metadata("flusers")
        self.assertTrue(mtd_flusers)
        # 'r-'
        field_descripcion = mtd_flusers.field("descripcion")
        self.assertFalse(field_descripcion.editable())
        self.assertTrue(field_descripcion.visible())

        mtd_fltest = flapplication.aqApp.db().manager().metadata("fltest")
        self.assertTrue(mtd_fltest)
        # 'rw'
        field = mtd_fltest.field("date_field")
        self.assertTrue(field.editable())
        self.assertTrue(field.visible())

    @classmethod
    def tearDownClass(cls) -> None:
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

        config.set_value("application/dbadmin_enabled", cls.db_admin)
