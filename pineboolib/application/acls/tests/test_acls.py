"""Test_acls module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib.fllegacy import systype
from pineboolib.core import settings
from pineboolib.core.utils import utils_base
from pineboolib.application.acls import pnaccesscontrollists
from pineboolib import application, qsa
from . import fixture_path


class TestACLS(unittest.TestCase):
    """TestPNBuffer Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()
        utils_base.FORCE_DESKTOP = True

        # Install package
        qsa_sys = qsa.qsa.sys
        path = fixture_path("controlacceso.eneboopkg")
        qsa_sys.loadModules(path, False)

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
        cursor_flacls.setModeAccess(cursor_flacls.Insert)
        cursor_flacls.setActivatedCheckIntegrity(False)
        cursor_flacls.refreshBuffer()
        cursor_flacls.setValueBuffer("idacl", "final")
        cursor_flacls.setValueBuffer("descripcion", "clear")
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
        cursor_flacs.setValueBuffer("permiso", "--")
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

        cursor_flacos.setModeAccess(cursor_flacos.Insert)
        cursor_flacos.refreshBuffer()
        cursor_flacos.setValueBuffer("nombre", "flareas")
        cursor_flacos.setValueBuffer("descripcion", "Todos:flareas")
        cursor_flacos.setValueBuffer("tipocontrol", "Todos")
        cursor_flacos.setValueBuffer("permiso", "rw")
        cursor_flacos.setValueBuffer("idac", id_acs_4)
        cursor_flacos.commitBuffer()

    def test_form_flacos(self) -> None:
        """Test form acls from flacos."""
        from pineboolib.qsa import qsa
        from pineboolib.plugins.mainform import eneboo

        application.ENABLE_ACLS = True

        main_form_class = getattr(eneboo, "MainForm", None)
        self.assertTrue(main_form_class)
        application.PROJECT.main_window = main_form_class()

        sys_type = systype.SysType()
        sys_type.installACL("tercera")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)
        button_1 = qsa.from_project("formRecordflmodules").child("botonExportar")  # r-
        button_2 = qsa.from_project("formRecordflmodules").child("botonCargar")  # --
        self.assertTrue(button_2.isHidden())  # not visible
        self.assertFalse(button_2.isEnabled())  # not enabled
        self.assertFalse(button_1.isHidden())  # visible
        self.assertFalse(button_1.isEnabled())  # not enabled

    def test_mainwindow_flacos(self) -> None:
        """Test mainwindow flacos."""
        from PyQt6 import QtGui  # type: ignore[import]
        from pineboolib.plugins.mainform.eneboo import eneboo
        from pineboolib import application

        sys_type = systype.SysType()
        sys_type.installACL("cuarta")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)

        settings.CONFIG.set_value("application/dbadmin_enabled", True)
        application.PROJECT._db_admin_mode = True
        project = application.PROJECT
        # project.main_form = eneboo
        main_form_class = getattr(eneboo, "MainForm", None)
        # main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_class)
        self.main_w = main_form_class()
        project.main_window = self.main_w
        self.main_w.initScript()
        self.main_w.show()
        self.assertTrue(self.main_w)

        action_1 = self.main_w.findChild(QtGui.QAction, "ebcomportamiento")
        self.assertTrue(action_1)
        self.assertFalse(action_1.isVisible())

        action_2 = self.main_w.findChild(QtGui.QAction, "flgroups")
        self.assertTrue(action_2)
        self.assertFalse(action_2.isVisible())

        action_3 = self.main_w.findChild(QtGui.QAction, "flareas")
        self.assertTrue(action_3)
        self.assertTrue(action_3.isVisible())

    def test_mainwindow_global(self) -> None:
        """Test mainwindow global."""

        from PyQt6 import QtGui
        from pineboolib.plugins.mainform.eneboo import eneboo
        from pineboolib import application

        settings.CONFIG.set_value("ebcomportamiento/main_form_name", "eneboo")

        sys_type = systype.SysType()
        sys_type.installACL("cuarta")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)

        project = application.PROJECT
        main_form_class = getattr(eneboo, "MainForm", None)
        # main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_class)
        self.main_w = main_form_class()
        project.main_window = self.main_w
        self.main_w.initScript()
        self.main_w.show()
        self.assertTrue(self.main_w)

        action_1 = self.main_w.findChild(QtGui.QAction, "flusers")
        self.assertTrue(action_1)
        self.assertFalse(action_1.isVisible())

    def test_form_globals(self) -> None:
        """Test form acls globals."""
        from pineboolib.qsa import qsa
        from pineboolib import application
        from pineboolib.plugins.mainform.eneboo import eneboo

        sys_type = systype.SysType()
        sys_type.installACL("tercera")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)

        project = application.PROJECT
        main_form_class = getattr(eneboo, "MainForm", None)
        # main_form_ = getattr(project.main_form, "MainForm", None)
        self.assertTrue(main_form_class)
        self.main_w = main_form_class()
        project.main_window = self.main_w
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
        application.PROJECT.aq_app.set_acl(acl)

        mtd_flgroups = application.PROJECT.conn_manager.manager().metadata("flgroups")

        self.assertTrue(mtd_flgroups is not None)
        # descripcion = '--'
        field_descripcion = mtd_flgroups.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )
        self.assertFalse(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

        # idgroup = 'r-'
        field_idgroup = mtd_flgroups.field("idgroup")  # type: ignore [union-attr] # noqa: F821
        self.assertFalse(field_idgroup.visible())  # type: ignore [union-attr] # noqa: F821

        mtd_flmodules = application.PROJECT.conn_manager.manager().metadata("flmodules")
        field_descripcion = mtd_flmodules.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )

        # descripcion = 'rw'

        self.assertTrue(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

    def test_tables_globals(self) -> None:
        """Test table acls globals."""

        sys_type = systype.SysType()
        sys_type.installACL("segunda")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)

        mtd_flareas = application.PROJECT.conn_manager.manager().metadata("flareas")
        self.assertTrue(mtd_flareas is not None)
        # '--'
        field_descripcion = mtd_flareas.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )
        self.assertFalse(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertFalse(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

        mtd_flusers = application.PROJECT.conn_manager.manager().metadata("flusers")
        self.assertTrue(mtd_flusers)
        # 'r-'
        field_descripcion = mtd_flusers.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )
        self.assertFalse(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

        mtd_fltest = application.PROJECT.conn_manager.manager().metadata("fltest")
        self.assertTrue(mtd_fltest)
        # 'rw'
        field = mtd_fltest.field("date_field")  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field.visible())  # type: ignore [union-attr] # noqa: F821

    def test_disable_acls(self) -> None:
        """Check if acls.xml load is disables"""

        application.ENABLE_ACLS = False
        sys_type = systype.SysType()
        sys_type.installACL("segunda")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.aq_app.set_acl(acl)

        mtd_flareas = application.PROJECT.conn_manager.manager().metadata("flareas")
        self.assertTrue(mtd_flareas is not None)
        # '--'
        field_descripcion = mtd_flareas.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )
        self.assertTrue(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

        mtd_flusers = application.PROJECT.conn_manager.manager().metadata("flusers")
        self.assertTrue(mtd_flusers)
        # 'r-'
        field_descripcion = mtd_flusers.field(  # type: ignore [union-attr] # noqa: F821
            "descripcion"
        )
        self.assertTrue(field_descripcion.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field_descripcion.visible())  # type: ignore [union-attr] # noqa: F821

        mtd_fltest = application.PROJECT.conn_manager.manager().metadata("fltest")
        self.assertTrue(mtd_fltest)
        # 'rw'
        field = mtd_fltest.field("date_field")  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field.editable())  # type: ignore [union-attr] # noqa: F821
        self.assertTrue(field.visible())  # type: ignore [union-attr] # noqa: F821

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""

        finish_testing()

        """
        from pineboolib.application.database import utils

        sys_type = systype.SysType()
        sys_type.installACL("final")
        acl = pnaccesscontrollists.PNAccessControlLists()
        acl.init()
        application.PROJECT.conn_manager.set_acl(acl)

        utils.sqlDelete("flacls", "1=1")
        utils.sqlDelete("flacs", "1=1")
        utils.sqlDelete("flacos", "1=1")
        utils.sqlDelete("flusers", "1=1")
        utils.sqlDelete("flgroups", "1=1")
        utils.sqlDelete("flfiles", "nombre='acl.xml'")
        application.PROJECT.conn_manager.manager().cacheMetaDataSys_ = {}
        application.PROJECT.conn_manager.manager().cacheMetaData_ = {}
        application.PROJECT.aq_app.acl_ = None

        settings.CONFIG.set_value("application/dbadmin_enabled", cls.db_admin)
        """
