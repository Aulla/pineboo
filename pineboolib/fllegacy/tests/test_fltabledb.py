"""Test_fltabledb module."""

from pineboolib.fllegacy import fltabledb
from pineboolib import application

import unittest
from pineboolib.loader.main import init_testing, finish_testing


class TestFLTableDB(unittest.TestCase):
    """Test FLTableDB class."""

    @classmethod
    def setUpClass(cls) -> None:
        """Ensure pineboo is initialized for testing."""
        init_testing()

    def test_export_to_ods(self) -> None:
        """Test export to ods."""

        application.project.actions["flareas"].openDefaultForm()

        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget
        # form = flformdb.FLFormDB(None, action)
        # self.assertTrue(form)
        # form.load()
        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        self.assertTrue(fltable)
        fltable.exportToOds()
        # self.assertTrue(form._loaded)
        # form.close()
        # self.assertFalse(form._loaded)
        # form.close()
        # self.assertFalse(form._loaded)

    def test_order_cols(self) -> None:
        """Test order cols."""

        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        fltable.setOrderCols(["descripcion", "idarea", "bloqueo"])
        self.assertEqual(fltable.orderCols(), ["descripcion", "idarea", "bloqueo"])
        fltable.setOrderCols(["idarea"])
        self.assertEqual(fltable.orderCols(), ["idarea", "descripcion", "bloqueo"])

    def test_put_x_col(self) -> None:
        """Test put first and second col."""

        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        self.assertEqual(fltable.orderCols(), ["idarea", "descripcion", "bloqueo"])
        fltable.putFirstCol(1)
        self.assertEqual(fltable.orderCols(), ["descripcion", "idarea", "bloqueo"])
        fltable.putFirstCol(1)
        self.assertEqual(fltable.orderCols(), ["idarea", "descripcion", "bloqueo"])
        fltable.putFirstCol(2)
        self.assertEqual(fltable.orderCols(), ["bloqueo", "descripcion", "idarea"])
        fltable.putFirstCol("idarea")
        self.assertEqual(fltable.orderCols(), ["idarea", "descripcion", "bloqueo"])
        fltable.putFirstCol("idarea")
        self.assertEqual(fltable.orderCols(), ["idarea", "descripcion", "bloqueo"])
        fltable.putFirstCol("descripcion")
        self.assertEqual(fltable.orderCols(), ["descripcion", "idarea", "bloqueo"])
        fltable.putSecondCol(2)
        self.assertEqual(fltable.orderCols(), ["descripcion", "bloqueo", "idarea"])
        fltable.putSecondCol(0)
        self.assertEqual(fltable.orderCols(), ["bloqueo", "descripcion", "idarea"])
        fltable.putSecondCol("bloqueo")
        self.assertEqual(fltable.orderCols(), ["descripcion", "bloqueo", "idarea"])
        fltable.putSecondCol("bloqueo")
        self.assertEqual(fltable.orderCols(), ["descripcion", "bloqueo", "idarea"])

    def test_sort_order(self) -> None:
        """Test sort orders."""

        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        cursor = fltable.cursor()
        fltable.setSortOrder(0, 2)
        self.assertEqual(cursor.sort(), "idarea DESC")
        fltable.setSortOrder(False, 1)
        self.assertEqual(cursor.sort(), "bloqueo DESC")
        fltable.setSortOrder(False, 0)
        self.assertEqual(cursor.sort(), "descripcion DESC")
        self.assertFalse(fltable.isSortOrderAscending())
        fltable.setSortOrder(1, 0)
        self.assertEqual(cursor.sort(), "descripcion ASC")
        fltable.setSortOrder(True, 1)
        self.assertEqual(cursor.sort(), "bloqueo ASC")
        self.assertTrue(fltable.isSortOrderAscending())

    def test_filter_records(self) -> None:
        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        cursor = fltable.cursor()

        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("idarea", "A")
        cursor.setValueBuffer("descripcion", "AREA A")
        cursor.setValueBuffer("bloqueo", False)
        cursor.commitBuffer()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("idarea", "A1")
        cursor.setValueBuffer("descripcion", "AREA A1")
        cursor.setValueBuffer("bloqueo", False)
        cursor.commitBuffer()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("idarea", "B")
        cursor.setValueBuffer("descripcion", "AREA B")
        cursor.setValueBuffer("bloqueo", False)
        cursor.commitBuffer()
        cursor.setModeAccess(cursor.Insert)
        cursor.refreshBuffer()
        cursor.setValueBuffer("idarea", "C")
        cursor.setValueBuffer("descripcion", "AREA C")
        cursor.setValueBuffer("bloqueo", False)
        cursor.commitBuffer()

        self.assertEqual(fltable.cursor().size(), 4)
        self.assertEqual(fltable.orderCols(), ["bloqueo", "idarea", "descripcion"])
        fltable.setOrderCols(["idarea", "descripcion", "bloqueo"])
        fltable.filterRecords("X")
        fltable.refresh()  # Forzamos refresh para emular el refresh delayed
        self.assertEqual(fltable.cursor().size(), 0)
        fltable.filterRecords("A")
        fltable.refresh()
        self.assertEqual(fltable.cursor().size(), 2)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
