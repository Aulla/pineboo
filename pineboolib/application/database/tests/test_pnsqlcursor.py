"""Test_pnsqlcursor module."""

import unittest
from pineboolib.loader.main import init_testing
from pineboolib.core.utils import logging

logger = logging.getLogger("test")


class TestInsertData(unittest.TestCase):
    """TestInsertData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Insert data into a database."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", True)
        cursor.setValueBuffer("idarea", "T")
        cursor.setValueBuffer("descripcion", "Área de prueba T")
        self.assertTrue(cursor.commitBuffer())
        mode_access = cursor.modeAccess()
        self.assertEqual(mode_access, cursor.Edit)


class TestEditData(unittest.TestCase):
    """TestEditData Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Edit data from a database."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas")
        cursor.select("idarea ='T'")
        first_result = cursor.first()
        self.assertEqual(first_result, True)
        cursor.setModeAccess(cursor.Edit)
        cursor.refreshBuffer()

        value_idarea = cursor.valueBuffer("idarea")
        self.assertEqual(value_idarea, "T")


class TestDeleteData(unittest.TestCase):
    """TestDeletedata Class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Delete data from a database."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas")
        cursor.select("idarea ='T'")
        first_result = cursor.first()
        self.assertEqual(first_result, True)
        size_1 = cursor.size()
        self.assertEqual(size_1, 1)
        cursor.setModeAccess(cursor.Del)
        cursor.refreshBuffer()

        value_idarea = cursor.valueBuffer("idarea")
        self.assertEqual(value_idarea, "T")
        cursor.commitBuffer()

        size_2 = cursor.size()
        self.assertEqual(size_2, 0)


class TestMove(unittest.TestCase):
    """Test Move class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:

        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", False)
        cursor.setValueBuffer("idarea", "A")
        cursor.setValueBuffer("descripcion", "Área de prueba A")
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", False)
        cursor.setValueBuffer("idarea", "B")
        cursor.setValueBuffer("descripcion", "Área de prueba B")
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", False)
        cursor.setValueBuffer("idarea", "C")
        cursor.setValueBuffer("descripcion", "Área de prueba C")
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", False)
        cursor.setValueBuffer("idarea", "D")
        cursor.setValueBuffer("descripcion", "Área de prueba D")
        self.assertTrue(cursor.commitBuffer())
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("bloqueo", False)
        cursor.setValueBuffer("idarea", "E")
        cursor.setValueBuffer("descripcion", "Área de prueba E")
        self.assertTrue(cursor.commitBuffer())

        cursor.first()
        self.assertEqual(cursor.valueBuffer("idarea"), "A")
        res_1 = cursor.prev()
        self.assertEqual(res_1, False)
        self.assertEqual(cursor.valueBuffer("idarea"), "A")
        res_2 = cursor.last()
        self.assertEqual(res_2, True)
        self.assertEqual(cursor.valueBuffer("idarea"), "E")
        res_3 = cursor.next()
        self.assertEqual(res_3, False)
        self.assertEqual(cursor.valueBuffer("idarea"), "E")
        res_4 = cursor.prev()
        self.assertEqual(res_4, True)
        self.assertEqual(cursor.valueBuffer("idarea"), "D")
        cursor.prev()
        self.assertEqual(cursor.valueBuffer("idarea"), "C")
        res_5 = cursor.first()
        self.assertEqual(res_5, True)
        self.assertEqual(cursor.valueBuffer("idarea"), "A")
        cursor.next()
        self.assertEqual(cursor.valueBuffer("idarea"), "B")
        res_6 = cursor.next()
        self.assertEqual(res_6, True)
        self.assertEqual(cursor.valueBuffer("idarea"), "C")
        self.assertEqual(cursor.size(), 5)


class TestBuffer(unittest.TestCase):
    """Test buffer class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test buffers data."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas")
        self.assertEqual(cursor.size(), 5)
        cursor.select("1=1 ORDER BY idarea ASC")
        cursor.setModeAccess(cursor.Edit)
        self.assertEqual(cursor.size(), 5)
        self.assertEqual(cursor.first(), True)
        cursor.refreshBuffer()
        buffer_copy = cursor.bufferCopy()
        buffer = cursor.buffer()
        if not buffer:
            raise Exception("buffer is empty!")

        if not buffer_copy:
            raise Exception("buffer is empty!")

        self.assertNotEqual(buffer, None)
        self.assertEqual(cursor.valueBuffer("idarea"), "A")

        self.assertEqual(buffer.value("idarea"), "A")
        self.assertEqual(buffer_copy.value("idarea"), "A")
        cursor.next()
        buffer = cursor.buffer()
        if not buffer:
            raise Exception("buffer is empty!")
        self.assertEqual(buffer.value("idarea"), "B")
        self.assertEqual(buffer_copy.value("idarea"), "A")


class TestValues(unittest.TestCase):
    """Test Values class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic(self) -> None:
        """Test values."""
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.application.qsatypes import date

        cursor = pnsqlcursor.PNSqlCursor("flupdates")
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        date_ = date.Date()
        cursor.setValueBuffer("fecha", date_)
        cursor.setValueBuffer("hora", "00:00:01")
        cursor.setValueBuffer("nombre", "nombre de prueba")
        cursor.setValueBuffer("modulesdef", "module_1\nmodule_2\nmodule_3")
        cursor.setValueBuffer("filesdef", "file_1\nfile_2\nfile_3")
        cursor.setValueBuffer("shaglobal", "1234567890")
        cursor.setValueBuffer("auxtxt", "aux_1\naux_2\naux_3")
        self.assertEqual(cursor.commitBuffer(), True)
        self.assertEqual(str(cursor.valueBuffer("fecha"))[0:8], str(date_)[0:8])
        self.assertEqual(cursor.valueBuffer("hora"), "00:00:01")
        self.assertEqual(cursor.valueBuffer("nombre"), "nombre de prueba")

        cursor_2 = pnsqlcursor.PNSqlCursor("fltest3")
        cursor_2.setModeAccess(cursor_2.Insert)
        cursor_2.refreshBuffer()
        cursor_2.setValueBuffer("string_field", "Campo de prueba test_pnsqlcursor_test_basic")
        self.assertTrue(cursor_2.commitBuffer())
        cursor_2.select()
        self.assertTrue(cursor_2.first())
        self.assertTrue(cursor_2.valueBuffer("counter"), "000001")
        cursor_2.setModeAccess(cursor_2.Del)
        cursor_2.refreshBuffer()
        self.assertTrue(cursor_2.commitBuffer())


class Test_emits(unittest.TestCase):
    """Test Emits class."""

    _transaction_begin: bool
    _transaction_end: bool
    _transaction_roll_back: bool

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_full(self) -> None:
        """Test full."""
        self._transaction_begin = False
        self._transaction_end = False
        self._transaction_roll_back = False

        from pineboolib.application.database import pnsignals
        from pineboolib.application.database import pnsqlcursor

        signals = pnsignals.PNSignals()
        signals.notify_begin_transaction_ = True
        signals.notify_end_transaction_ = True
        signals.notify_roll_back_transaction_ = True

        cursor = pnsqlcursor.PNSqlCursor("test")

        cursor.transactionBegin.connect(self.mark_transaction_begin)
        cursor.transactionEnd.connect(self.mark_transaction_end)
        cursor.transactionRollBack.connect(self.mark_transaction_roll_back)

        signals.emitTransactionBegin(cursor)
        signals.emitTransactionEnd(cursor)
        signals.emitTransactionRollback(cursor)

        self.assertTrue(self._transaction_begin)
        self.assertTrue(self._transaction_end)
        self.assertTrue(self._transaction_roll_back)

    def mark_transaction_begin(self) -> None:
        """Mark transaction begin."""

        self._transaction_begin = True

    def mark_transaction_end(self) -> None:
        """Mark transaction end."""

        self._transaction_end = True

    def mark_transaction_roll_back(self) -> None:
        """Mark transaction roll back."""
        self._transaction_roll_back = True


class TestGeneral(unittest.TestCase):
    """Test General class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_1(self) -> None:
        """Basic tests 1."""
        from pineboolib import application
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest", "default")
        cursor2 = pnsqlcursor.PNSqlCursor("flareas", True, application.project.conn)
        self.assertEqual(cursor.table(), "fltest")
        action = cursor.action()
        action2 = cursor2.action()
        self.assertTrue(action)
        if action is None:
            raise Exception("action is None!")

        if action2 is None:
            raise Exception("action2 is None!")

        self.assertEqual(cursor.actionName(), "fltest")
        self.assertTrue(cursor.setAction(action))
        self.assertTrue(cursor.setAction(action2))

        cursor3 = pnsqlcursor.PNSqlCursor("fltest")
        cursor3.setMainFilter("id > 1")
        cursor3.select()
        cursor3.refresh()
        self.assertEqual(cursor3.mainFilter(), "id > 1")
        cursor3.refreshBuffer()
        self.assertEqual(cursor3.valueBuffer("id"), cursor3.valueBufferCopy("id"))
        self.assertEqual(cursor3.baseFilter(), "id > 1")

        self.assertFalse(cursor3.meta_model())
        self.assertFalse(cursor3.inTransaction())
        self.assertTrue(cursor3.commit())

        cursor3.refreshBuffer()

        cursor4 = pnsqlcursor.PNSqlCursor("flareas", "default")
        cursor4.select()
        cursor4.first()
        cursor4.setModeAccess(cursor4.Edit)
        cursor4.refreshBuffer()
        self.assertFalse(cursor4.isNull("idarea"))
        self.assertFalse(cursor4.isCopyNull("idarea"))

    def test_basic_2(self) -> None:
        """Basic tests 2."""
        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("flareas", "default")
        cursor.select()
        cursor.first()
        cursor.setModeAccess(cursor.Edit)

        self.assertFalse(cursor.isModifiedBuffer())
        cursor.setValueBuffer("descripcion", "Descripcion de prueba para a")
        self.assertTrue(cursor.isModifiedBuffer())

        cursor2 = pnsqlcursor.PNSqlCursor("flmodules", "default")
        cursor2.setAskForCancelChanges(False)
        cursor2.setActivatedCheckIntegrity(False)
        cursor2.setActivatedCommitActions(False)

        self.assertFalse(cursor2.activatedCommitActions())
        cursor2.setModeAccess(cursor2.Insert)
        cursor2.refreshBuffer()
        cursor2.setValueBuffer("idmodulo", "Z")
        cursor2.setValueBuffer("descripcion", "Esta es la descripción")
        cursor2.setValueBuffer("version", "0.0")
        cursor2.commitBuffer()

        cursor2.select('idmodulo = "Z"')
        cursor2.first()
        cursor2.setModeAccess(cursor2.Del)
        cursor2.refreshBuffer()
        cursor2.commitBuffer()

    def test_basic_3(self) -> None:
        """Basic tests 3."""

        from pineboolib.application.database import pnsqlcursor

        cursor = pnsqlcursor.PNSqlCursor("fltest", "default")

        self.assertEqual(cursor.msgCheckIntegrity(), "\nBuffer vacío o no hay metadatos")
        self.assertFalse(cursor.checkIntegrity(False))
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        self.assertEqual(cursor.msgCheckIntegrity(), "")
        self.assertTrue(cursor.checkIntegrity(False))

        self.assertFalse(cursor.cursorRelation())

        cursor2 = pnsqlcursor.PNSqlCursor("flareas")
        cursor2.select()
        self.assertTrue(cursor2.first())
        cursor2.setUnLock("bloqueo", True)
        self.assertFalse(cursor2.isLocked())
        cursor2.setUnLock("bloqueo", False)
        self.assertFalse(cursor2.isLocked())
        cursor2.setModeAccess(cursor2.Del)
        cursor2.refreshBuffer()
        self.assertTrue(cursor2.commitBuffer())

        self.assertEqual(cursor2.curFilter(), "")
        cursor2.setFilter("bloqueo = true")
        self.assertEqual(cursor2.curFilter(), "bloqueo = true")

        cursor2.setSort("bloqueo ASC")

    def test_basic_4(self) -> None:
        """Basic tests 4."""
        from pineboolib.application.database import pnsqlcursor

        cursor_fake = pnsqlcursor.PNSqlCursor("fake")
        self.assertFalse(cursor_fake._valid)
        self.assertFalse(cursor_fake.isModifiedBuffer())
        self.assertTrue(cursor_fake.activatedCheckIntegrity())
        self.assertEqual(cursor_fake.checkIntegrity(False), False)
        self.assertEqual(cursor_fake.table(), "")
        self.assertEqual(cursor_fake.mainFilter(), "")
        cursor_fake.setValueBuffer("no_field", "XXX")
        self.assertFalse(cursor_fake.valueBuffer("no_field"))
        cursor = pnsqlcursor.PNSqlCursor("fltest")
        self.assertTrue(cursor._valid)
        cursor_2 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_2.select()
        cursor_2.first()
        cursor_2.setModeAccess(cursor_2.Insert)
        self.assertFalse(cursor_2.fieldDisabled("descripcion"))
        cursor_2.refreshBuffer()
        self.assertEqual(
            cursor_2.msgCheckIntegrity(),
            "\nflareas:Área : No puede ser nulo\nflareas:Descripción : No puede ser nulo",
        )
        self.assertEqual(
            cursor_2.valueBuffer("descripcion"), cursor_2.valueBufferCopy("descripcion")
        )

        self.assertTrue(cursor_2.field("idarea"))
        buffer = cursor_2.buffer()
        if buffer:
            self.assertTrue(buffer.isGenerated("idarea"))
        cursor_2.setEdition(True, "prueba")
        self.assertTrue(cursor_2.d.edition_states_)
        cursor_2.restoreEditionFlag("prueba")
        cursor_2.setBrowse(True, "prueba2")
        self.assertTrue(cursor_2.d.browse_states_)
        cursor_2.restoreBrowseFlag("prueba2")

    def test_basic_5(self) -> None:
        """Basic tests 5."""
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.qsa import qsa

        cursor_qry = pnsqlcursor.PNSqlCursor("fltest2")
        self.assertTrue(cursor_qry)
        self.assertFalse(cursor_qry.d.needUpdate())
        cursor = pnsqlcursor.PNSqlCursor("fltest")
        self.assertFalse(cursor.d.needUpdate())
        self.assertEqual(cursor.primaryKey(), "id")
        self.assertEqual(cursor.fieldType("id"), 100)
        cursor_qry.setNotGenerateds()
        cursor.sort()

        self.assertFalse(cursor.fieldType("id2"))
        for f in cursor:
            self.assertTrue(f)

        cursor_2 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_2.update(False)

        cursor.changeConnection("dbAux")
        self.assertEqual(cursor.transactionsOpened(), [])
        cursor.db().doTransaction(cursor)
        self.assertEqual(cursor.transactionsOpened(), ["1"])
        cursor.db().doRollback(cursor)
        cursor.setForwardOnly(True)

        cursor_3 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_3.select()
        self.assertTrue(cursor_3.first())
        cursor_3.chooseRecord(False)
        qsa.from_project("formRecordflareas").form.reject()
        cursor_3.select()
        cursor_3.first()
        cursor_3.browseRecord(False)
        qsa.from_project("formRecordflareas").form.reject()
        cursor_3.select()
        cursor_3.first()
        cursor_3.editRecord(False)
        qsa.from_project("formRecordflareas").form.reject()

        cursor_4 = pnsqlcursor.PNSqlCursor("flareas")
        cursor_4.select()
        cursor_4.first()
        self.assertTrue(cursor_4.selection_pk("B"))
        cursor_4.last()
        self.assertTrue(cursor_4.selection_pk("B"))
        cursor_4.last()
        self.assertFalse(cursor_4.selection_pk("J"))
        cursor_4.setNull("idarea")
        cursor_4.setModeAccess(cursor_4.Insert)
        cursor_4.refreshBuffer()
        self.assertFalse(cursor_4.checkIntegrity())


class TestRelations(unittest.TestCase):
    """Test Relations class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_basic_relations_1(self) -> None:
        """Test basic relations 1."""
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.application.metadata import pnrelationmetadata

        cur_areas = pnsqlcursor.PNSqlCursor("flareas")
        rel = pnrelationmetadata.PNRelationMetaData(
            "flareas", "idarea", pnrelationmetadata.PNRelationMetaData.RELATION_1M
        )
        rel.setField("idarea")
        cur_areas.select()
        cur_areas.first()
        self.assertEqual(cur_areas.valueBuffer("idarea"), "B")
        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.refreshBuffer()
        cur_modulos = pnsqlcursor.PNSqlCursor("flmodules", True, "default", cur_areas, rel)
        cur_modulos.select()
        cur_modulos.refreshBuffer()
        cur_rel = cur_modulos.cursorRelation()
        if cur_rel:
            self.assertEqual(cur_rel.valueBuffer("idarea"), "B")
        self.assertTrue(cur_areas.isLocked())
        self.assertFalse(cur_modulos.fieldDisabled("icono"))
        self.assertEqual(cur_modulos.msgCheckIntegrity(), "\nBuffer vacío o no hay metadatos")
        self.assertTrue(cur_modulos.isLocked())
        cur_modulos.bufferSetNull("icono")
        cur_modulos.bufferCopySetNull("icono")
        self.assertTrue(cur_modulos.bufferCopyIsNull("icono"))
        cur_modulos.setModeAccess(cur_modulos.Insert)
        cur_modulos.refreshBuffer()
        cur_modulos.setValueBuffer("idmodulo", "TM")
        cur_modulos.setValueBuffer("descripcion", "Desc")
        self.assertEqual(cur_modulos.checkIntegrity(False), True)
        self.assertTrue(cur_modulos.commitBuffer())
        self.assertTrue(cur_areas.rollback())

    def test_basic_relations_2(self) -> None:
        """Test basic relations 2."""
        from pineboolib.application.database import pnsqlcursor
        from pineboolib.application.metadata import pnrelationmetadata

        cur_areas = pnsqlcursor.PNSqlCursor("flareas")
        rel = pnrelationmetadata.PNRelationMetaData(
            "flareas", "idarea", pnrelationmetadata.PNRelationMetaData.RELATION_1M
        )
        rel.setField("idarea")
        cur_areas.select()
        cur_areas.first()
        self.assertEqual(cur_areas.valueBuffer("idarea"), "B")
        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.refreshBuffer()
        cur_areas.transaction()
        cur_modulos = pnsqlcursor.PNSqlCursor("flmodules", True, "default", cur_areas, rel)
        cur_modulos.setModeAccess(cur_modulos.Insert)
        self.assertEqual(cur_areas.transactionsOpened(), ["1"])
        cur_modulos.refreshBuffer()
        cur_modulos.transaction()
        cur_modulos.rollbackOpened(-1, "Mensage de prueba 1º")

        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.refreshBuffer()
        cur_areas.transaction()
        cur_modulos = pnsqlcursor.PNSqlCursor("flmodules", True, "default", cur_areas, rel)
        cur_modulos.setModeAccess(cur_modulos.Insert)
        self.assertEqual(cur_areas.transactionsOpened(), ["2", "1"])
        cur_modulos.refreshBuffer()
        cur_modulos.transaction()
        cur_modulos.commitOpened(-1, "Mensage de prueba 2º")

        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.refreshBuffer()
        cur_areas.transaction()
        cur_modulos = pnsqlcursor.PNSqlCursor("flmodules", True, "default", cur_areas, rel)
        cur_modulos.setModeAccess(cur_modulos.Insert)
        self.assertEqual(cur_areas.transactionsOpened(), ["3", "2", "1"])
        cur_modulos.refreshBuffer()
        cur_modulos.transaction()
        self.assertTrue(cur_modulos.commitBufferCursorRelation())

        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.refreshBuffer()
        cur_areas.transaction()
        self.assertTrue(cur_areas.commitBuffer())
        cur_areas.setEditMode()
        cur_areas.setModeAccess(cur_areas.Edit)
        cur_areas.setEditMode()
        cur_areas.primeInsert()
        cur_modulos.setModeAccess(cur_modulos.Insert)
        cur_modulos.refreshDelayed()
        self.assertTrue(cur_modulos.fieldDisabled("idarea"))
        self.assertFalse(cur_modulos.commitBuffer())
        self.assertEqual(cur_modulos.transactionsOpened(), ["4"])
        self.assertTrue(cur_modulos.rollback())
        self.assertEqual(cur_modulos.transactionsOpened(), [])
        self.assertTrue(cur_areas.rollback())


if __name__ == "__main__":
    unittest.main()
