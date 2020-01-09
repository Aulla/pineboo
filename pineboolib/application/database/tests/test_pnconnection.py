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
        conn_aux_ = conn_manager.useConn("dbAux")
        conn_ = conn_manager.useConn("conn_test")
        self.assertNotEqual(conn_, conn_aux_)
        dict_databases_1 = conn_manager.dictDatabases()
        self.assertTrue(dict_databases_1)

        self.assertTrue(conn_default_.isOpen())
        self.assertTrue(conn_manager.mainConn().isOpen())
        self.assertTrue(conn_manager.useConn("dbAux").isOpen())
        self.assertFalse(conn_manager.useConn("conn_test").isOpen())

        self.assertEqual([*dict_databases_1], ["dbAux", "default", "conn_test"])
        self.assertTrue(conn_manager.removeConn("conn_test"))
        dict_databases_2 = conn_manager.dictDatabases()
        self.assertEqual([*dict_databases_2], ["dbAux", "default"])

    def test_basic2(self) -> None:
        """Basic test 2."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.mainConn()
        self.assertTrue("flareas" in conn_.tables("Tables"))
        self.assertTrue("sqlite_master" in conn_.tables())
        self.assertEqual(conn_.tables("SystemTables"), ["sqlite_master"])
        self.assertEqual(conn_.tables("Views"), [])

        db = conn_.database()
        db_db_aux = conn_manager.database("dbAux")
        self.assertNotEqual(conn_manager.db(), conn_)  # Compares default Vs main_conn
        self.assertNotEqual(db, db_db_aux)
        self.assertEqual(conn_.DBName(), str(conn_))

    def test_basic3(self) -> None:
        """Basic test 3."""

        from pineboolib.fllegacy import systype

        conn_manager = application.PROJECT.conn_manager
        sys_type = systype.SysType()
        conn_ = conn_manager.mainConn()

        self.assertTrue(conn_.driver())
        self.assertTrue(conn_.cursor())
        sys_type.addDatabase("conn_test_2")
        self.assertTrue(conn_manager.useConn("conn_test_2").isOpen())
        self.assertTrue(sys_type.removeDatabase("conn_test_2"))
        self.assertEqual(conn_.driverName(), "FLsqlite")
        self.assertEqual(conn_.driver().alias_, conn_.driverAlias())
        self.assertEqual(conn_.driverNameToDriverAlias(conn_.driverName()), "SQLite3 (SQLITE3)")

    def test_basic4(self) -> None:
        """Basic test 4."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.mainConn()
        self.assertTrue(conn_.interactiveGUI_)
        conn_.setInteractiveGUI(False)
        self.assertFalse(conn_.interactiveGUI())
        # self.assertNotEqual(conn_, conn_manager.db())
        self.assertEqual(conn_manager.dbAux(), conn_manager.useConn("dbAux"))

        self.assertEqual(conn_.formatValue("string", "hola", True), "'HOLA'")
        self.assertEqual(conn_.formatValueLike("string", "hola", True), "LIKE 'HOLA%%'")
        self.assertTrue(conn_.canSavePoint())
        self.assertTrue(conn_.canTransaction())
        self.assertEqual(conn_.transactionLevel(), 0)
        self.assertTrue(conn_.canDetectLocks())
        self.assertTrue(conn_manager.manager())
        self.assertTrue(conn_manager.managerModules())
        self.assertTrue(conn_.canOverPartition())

        mtd_seqs = conn_manager.manager().metadata("flseqs")

        if mtd_seqs is None:
            raise Exception("mtd_seqs is empty!.")

        self.assertFalse(conn_.existsTable("fltest"))
        self.assertTrue(conn_.existsTable("flseqs"))
        self.assertFalse(conn_.mismatchedTable("flseqs", mtd_seqs))
        self.assertEqual(conn_.normalizeValue("holá, 'avión'"), "holá, ''avión''")

    def test_basic5(self) -> None:
        """Basic test 5."""

        conn_manager = application.PROJECT.conn_manager
        conn_ = conn_manager.mainConn()
        cursor = pnsqlcursor.PNSqlCursor("flareas")
        conn_.doTransaction(cursor)
        cursor.setModeAccess(cursor.Insert)
        cursor.setValueBuffer("idarea", "test")
        cursor.setValueBuffer("bloqueo", "false")
        cursor.setValueBuffer("descripcion", "test area")
        cursor.commitBuffer()
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
        self.assertTrue(conn_.declarative_base())
        self.assertFalse(conn_.port())
        self.assertFalse(conn_.password())

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
        self.assertEqual(
            conn_manager.mainConn().queryUpdate("test", "field1, 'val_1'", "1=1"),
            "UPDATE test SET field1, 'val_1' WHERE 1=1",
        )
        self.assertTrue(conn_manager.removeConn("test"))
        self.assertTrue(conn_default.doTransaction(cursor))
        self.assertTrue(cursor.inTransaction())
        self.assertTrue(conn_default.doCommit(cursor, False))
        self.assertTrue(conn_default.doTransaction(cursor))
        self.assertTrue(conn_default.doRollback(cursor))

    @classmethod
    def tearDown(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()


if __name__ == "__main__":
    unittest.main()
