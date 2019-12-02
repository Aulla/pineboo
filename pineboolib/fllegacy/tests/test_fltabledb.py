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
        """Test filterRecords function."""

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

    def test_x_edition_flags(self) -> None:
        """Test edition flags."""

        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        cursor = fltable.cursor()

        self.assertFalse(fltable.readOnly())
        fltable.setReadOnly(True)
        self.assertTrue(fltable.readOnly())
        fltable.setReadOnly(False)
        self.assertFalse(fltable.readOnly())

        self.assertFalse(fltable.editOnly())
        fltable.setEditOnly(True)
        self.assertTrue(fltable.editOnly())
        fltable.setEditOnly(False)
        self.assertFalse(fltable.editOnly())

        self.assertFalse(fltable.insertOnly())
        fltable.setInsertOnly(True)
        self.assertTrue(fltable.insertOnly())
        fltable.setInsertOnly(False)
        self.assertFalse(fltable.insertOnly())

    def test_x_tab_filter(self) -> None:
        from PyQt5 import QtCore
        from pineboolib.fllegacy import flutil

        util = flutil.FLUtil()
        form = application.project.actions[  # type: ignore [attr-defined] # noqa F821
            "flareas"
        ].mainform_widget

        fltable = form.findChild(fltabledb.FLTableDB, "tableDBRecords")
        fltable.filter_ = None
        fltable.activeTabFilter(True)
        fltable.tdbFilterClear()
        widget_cb = fltable.tdbFilter.cellWidget(1, 1)
        widget_cb.setCurrentText(util.tr("Igual a Valor"))
        widget_le = fltable.tdbFilter.cellWidget(1, 2)
        widget_le.setText("A")
        fltable.activeTabData(True)
        fltable.refresh()
        cursor1 = fltable.cursor()
        self.assertEqual(cursor1.size(), 1)

        fltable.activeTabFilter(True)
        fltable.tdbFilterClear()
        widget_cb_2 = fltable.tdbFilter.cellWidget(1, 1)
        widget_cb_2.setCurrentText(util.tr("Contiene Valor"))
        widget_le_2 = fltable.tdbFilter.cellWidget(1, 2)
        widget_le_2.setText("A")
        fltable.activeTabData(True)
        fltable.refresh()
        cursor2 = fltable.cursor()
        self.assertEqual(cursor2.size(), 2)

        fltable.activeTabFilter(True)
        fltable.tdbFilterClear()
        widget_cb_3 = fltable.tdbFilter.cellWidget(1, 1)
        widget_cb_3.setCurrentText(util.tr("Distinto de Valor"))
        widget_le_3 = fltable.tdbFilter.cellWidget(1, 2)
        widget_le_3.setText("W")
        fltable.activeTabData(True)
        fltable.refresh()
        cursor3 = fltable.cursor()
        self.assertEqual(cursor3.size(), 4)

        fltable.activeTabFilter(True)
        fltable.tdbFilterClear()
        widget_cb_4 = fltable.tdbFilter.cellWidget(0, 1)
        widget_cb_4.setCurrentText(util.tr("Contiene Valor"))
        widget_chb_1 = fltable.tdbFilter.cellWidget(0, 2)
        widget_chb_1.setChecked(True)
        fltable.activeTabData(True)
        fltable.refresh()
        cursor4 = fltable.cursor()
        self.assertEqual(cursor4.size(), 0)

        # _label = fltable.cursor().model().headerData(0, QtCore.Qt.Horizontal, QtCore.Qt.DisplayRole)
        fltable.activeTabFilter(True)
        fltable.tdbFilterClear()
        widget_cb_5 = fltable.tdbFilter.cellWidget(0, 1)
        widget_cb_5.setCurrentText(util.tr("Contiene Valor"))
        widget_chb_2 = fltable.tdbFilter.cellWidget(0, 2)
        widget_chb_2.setChecked(False)
        fltable.activeTabData(True)
        fltable.refresh()
        cursor5 = fltable.cursor()
        self.assertEqual(cursor5.size(), 4)

    @classmethod
    def tearDownClass(cls) -> None:
        """Ensure test clear all data."""
        finish_testing()
