"""Test_pnconnection module."""

import unittest
from pineboolib.loader.main import init_testing, finish_testing
from pineboolib import application
from pineboolib.application.database import pnsqlcursor


class TestPNConnection(unittest.TestCase):
    """TestPNConnection Class."""

    @classmethod
    def setUp(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic1(self) -> None:
        """Basic test 1."""

        conn_manager = application.PROJECT.conn_manager

        self.assertEqual(conn_manager.mainConn().connectionName(), "main_conn")
        conn_default_ = conn_manager.useConn("default")
        conn_db_aux_ = conn_manager.useConn("dbAux")
        conn_aux = conn_manager.useConn("Aux")
        conn_ = conn_manager.useConn("conn_test")
        self.assertNotEqual(conn_, conn_db_aux_)
        self.assertNotEqual(conn_db_aux_, conn_aux)
        dict_databases_1 = conn_manager.enumerate()
        self.assertTrue(dict_databases_1)

        self.assertTrue(conn_default_.isOpen())
        self.assertTrue(conn_manager.mainConn().isOpen())
        self.assertTrue(conn_manager.useConn("dbAux").isOpen())
        self.assertTrue(conn_manager.useConn("Aux").isOpen())
        self.assertFalse(conn_manager.useConn("conn_test").isOpen())

        self.assertEqual([*dict_databases_1], ["default", "dbAux", "Aux", "conn_test"])
        self.assertTrue("flareas" in conn_aux.tables("Tables"))
        self.assertTrue(conn_manager.removeConn("conn_test"))
        dict_databases_2 = conn_manager.enumerate()
        self.assertEqual([*dict_databases_2], ["default", "dbAux", "Aux"])

    def test_basic2(self) -> None:
        """Basic test 2."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.default()
        self.assertTrue("flareas" in conn_.tables("Tables"))
        self.assertTrue("sqlite_master" in conn_.tables())
        self.assertEqual(conn_.tables("SystemTables"), ["sqlite_master"])
        self.assertEqual(conn_.tables("Views"), [])

        data_base = conn_.database()
        data_base_aux = conn_manager.database("dbAux")
        self.assertNotEqual(
            conn_manager.db(), conn_manager.mainConn()
        )  # Compares default Vs main_conn
        self.assertNotEqual(data_base, data_base_aux)
        self.assertEqual(conn_.DBName(), str(conn_))

    def test_basic3(self) -> None:
        """Basic test 3."""

        from pineboolib.fllegacy import systype

        conn_manager = application.PROJECT.conn_manager
        sys_type = systype.SysType()
        conn_ = conn_manager.mainConn()

        self.assertTrue(conn_.driver())
        self.assertTrue(conn_.driver().connection())
        sys_type.addDatabase("conn_test_2")
        self.assertTrue(conn_manager.useConn("conn_test_2").isOpen())
        self.assertTrue(sys_type.removeDatabase("conn_test_2"))
        self.assertEqual(conn_.driverName(), "FLsqlite")
        self.assertEqual(conn_.driver().alias_, conn_.driverAlias())
        self.assertEqual(conn_.driverNameToDriverAlias(conn_.driverName()), "SQLite3 (SQLITE3)")

    def test_basic4(self) -> None:
        """Basic test 4."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.default()
        self.assertTrue(conn_.interactiveGUI())
        conn_.setInteractiveGUI(False)
        self.assertFalse(conn_.interactiveGUI())
        # self.assertNotEqual(conn_, conn_manager.db())
        self.assertEqual(conn_manager.dbAux(), conn_manager.useConn("dbAux"))

        self.assertEqual(conn_.formatValue("string", "hola", True), "'HOLA'")
        self.assertEqual(conn_.formatValueLike("string", "hola", True), "LIKE 'HOLA%%'")
        # self.assertTrue(conn_.canSavePoint())
        # self.assertTrue(conn_.canTransaction())
        self.assertEqual(conn_.transactionLevel(), 0)
        self.assertTrue(conn_.canDetectLocks())
        self.assertTrue(conn_manager.manager())
        self.assertTrue(conn_manager.managerModules())
        self.assertTrue(conn_.canOverPartition())

        mtd_seqs = conn_manager.manager().metadata("flseqs")
        self.assertTrue(mtd_seqs is not None)
        if mtd_seqs is not None:
            self.assertFalse(conn_.existsTable("fltest"))
            self.assertTrue(conn_.existsTable("flseqs"))
            self.assertFalse(conn_.mismatchedTable("flseqs", mtd_seqs))
            self.assertEqual(conn_.normalizeValue("holá, 'avión'"), "holá, ''avión''")

    def test_basic5(self) -> None:
        """Basic test 5."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.useConn("default")
        cursor = pnsqlcursor.PNSqlCursor("flareas")
        conn_.doTransaction(cursor)
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("idarea", "test")
        cursor.setValueBuffer("bloqueo", "false")
        cursor.setValueBuffer("descripcion", "test area")
        self.assertTrue(cursor.commitBuffer())
        conn_.doRollback(cursor)
        conn_.doTransaction(cursor)
        cursor.setModeAccess(cursor.Insert)
        cursor.setValueBuffer("idarea", "test")
        cursor.setValueBuffer("bloqueo", "false")
        cursor.setValueBuffer("descripcion", "test area")
        cursor.commitBuffer()
        conn_.doCommit(cursor, False)
        conn_.canRegenTables()

        self.assertEqual(conn_.tables(1)[0:3], ["flareas", "flfiles", "flgroups"])

        self.assertEqual(conn_.tables(2), ["sqlite_master"])
        self.assertEqual(conn_.tables(3), [])

        self.assertTrue(conn_.session())
        self.assertTrue(conn_.engine())

        self.assertFalse(conn_.port())
        self.assertFalse(conn_.returnword())

        # self.assertFalse(conn_.lastActiveCursor())

        # conn_.Mr_Proper() #FIXME

    def test_basic6(self) -> None:
        """Test basic 6."""
        from pineboolib.application.database import pnsqlcursor

        conn_manager = application.PROJECT.conn_manager
        conn_default = conn_manager.useConn("default")
        conn_manager.useConn("test")
        cursor = pnsqlcursor.PNSqlCursor("flsettings")
        cursor.setAskForCancelChanges(False)
        conn_manager.mainConn().Mr_Proper()
        # self.assertEqual(
        #    conn_manager.mainConn().queryUpdate("test", "field1, 'val_1'", "1=1"),
        #    "UPDATE test SET field1, 'val_1' WHERE 1=1",
        # )
        self.assertTrue(conn_manager.removeConn("test"))
        self.assertTrue(conn_default.doTransaction(cursor))
        self.assertTrue(cursor.inTransaction())
        self.assertTrue(conn_default.doCommit(cursor, False))
        self.assertTrue(conn_default.doTransaction(cursor))
        self.assertTrue(conn_default.doRollback(cursor))

    def test_reinit_connections(self) -> None:
        """Test removing users connections."""

        application.PROJECT.conn_manager.reinit_user_connections()
        self.assertTrue(application.PROJECT.conn_manager.default().isOpen())

    def test_isolation_sessions(self) -> None:
        """Test isolated sessions."""

        conn_manager = application.PROJECT.conn_manager
        default = conn_manager.default()
        db_aux = conn_manager.dbAux()
        self.assertNotEqual(default.session(), db_aux.session())

    @classmethod
    def tearDown(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
