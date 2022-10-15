"""Fltabledb module."""

# -*- coding: utf-8 -*-

from PyQt6 import QtCore, QtGui, QtWidgets  # type: ignore[import]

from pineboolib.application.database import pnsqlcursor
from pineboolib.application.metadata import pnfieldmetadata, pnrelationmetadata
from pineboolib.application.qsatypes import sysbasetype
from pineboolib.application import qsadictmodules
from pineboolib.q3widgets import qtable

from pineboolib.core.utils import utils_base
from pineboolib.core import decorators, settings

from pineboolib import application

from pineboolib import logging

from . import (
    fldatatable,
    flformsearchdb,
    flutil,
    flformrecorddb,
    fldoublevalidator,
    fluintvalidator,
    flintvalidator,
    flcheckbox,
    fltimeedit,
    fldateedit,
    flspinbox,
)

from pineboolib.fllegacy.aqsobjects import aqods

from typing import Any, Optional, List, Union, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from pineboolib.interfaces import isqlcursor  # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # pragma: no cover


LOGGER = logging.get_logger(__name__)
DEBUG = False


class FLTableDB(QtWidgets.QWidget):
    """
    PLUGIN that contains a database table.

    This object contains everything needed to handle
    the data in a table. In addition to the functionality of
    Search the table by a field, using filters.

    This plugin to be functional must have as one
    from your parents or predecessor to an FLFormDB object.

    @author InfoSiAL S.L.
    """

    """
    Tipos de condiciones para el filtro
    """
    _all: int = 0
    _contains: int = 1
    _starts: int = 2
    _end: int = 3
    _equal: int = 4
    _dist: int = 5
    _greater: int = 6
    _less: int = 7
    _from_to: int = 8
    _null: int = 9
    _not_null: int = 10

    _parent: "QtWidgets.QWidget"
    _name: str

    _tdb_filter: Optional[Any]

    _pb_data: "QtWidgets.QPushButton"
    _pb_filter: "QtWidgets.QPushButton"
    _pb_odf: "QtWidgets.QPushButton"

    _combo_box_field_to_search_1: "QtWidgets.QComboBox"
    _combo_box_field_to_search_2: "QtWidgets.QComboBox"
    _line_edit_search: "QtWidgets.QLineEdit"

    _tab_data_layout: "QtWidgets.QVBoxLayout"
    _tab_control_layout: "QtWidgets.QHBoxLayout"

    _data_layout: "QtWidgets.QHBoxLayout"
    _tab_data: "QtWidgets.QFrame"
    _tab_filter: "QtWidgets.QFrame"
    _buttons_layout: "QtWidgets.QVBoxLayout"
    _master_layout: "QtWidgets.QVBoxLayout"
    _tab_filter_loader: bool

    _loaded: bool
    """
    Tamaño de icono por defecto
    """
    _icon_size: Optional[Any]

    """
    Componente para visualizar los registros
    """
    _table_records: Optional["fldatatable.FLDataTable"]

    """
    Nombre de la tabla a la que esta asociado este componente.
    """
    _table_name: Optional[str]

    """
    Nombre del campo foráneo
    """
    _foreign_field: Optional[str]

    """
    Nombre del campo de la relación
    """
    _field_relation: Optional[str]

    """
    Cursor con los datos de origen para el componente
    """
    cursor_: "isqlcursor.ISqlCursor"

    """
    Cursor auxiliar de uso interno para almacenar los registros de la tabla
    relacionada con la de origen
    """
    _cursor_aux: Optional["isqlcursor.ISqlCursor"]

    """
    Matiene la ventana padre
    """
    _top_widget: Optional["QtWidgets.QWidget"]

    """
    Indica que la ventana ya ha sido mostrada una vez
    """
    _showed: bool

    """
    Mantiene el filtro de la tabla
    """

    """
    Almacena si el componente está en modo sólo lectura
    """
    _read_only: bool
    _req_read_only: bool

    """
    Almacena si el componente está en modo sólo edición
    """
    _edit_only: bool
    _req_edit_only: bool

    """
    Indica si el componente está en modo sólo permitir añadir registros
    """
    _insert_only: bool
    _req_insert_only: bool

    """
    Indica que no se realicen operaciones con la base de datos (abrir formularios). Modo "sólo tabla".
    """
    _only_table: bool
    _req_only_table: bool

    """
    Almacena los metadatos del campo por el que está actualmente ordenada la tabla
    """
    _sort_field_1: Optional["pnfieldmetadata.PNFieldMetaData"]

    """
    Almacena los metadatos del campo por el que está actualmente ordenada la tabla en segunda instancia

    @author Silix - dpinelo
    """
    _sort_field_2: Optional["pnfieldmetadata.PNFieldMetaData"]

    """
    Crónometro interno
    """
    _timer: Optional["QtCore.QTimer"]

    """
    Filtro inicial de búsqueda
    """
    _init_search: Optional[str]

    """
    Indica que la columna de seleción está activada
    """
    _check_column_enabled: bool

    """
    Indica el texto de la etiqueta de encabezado para la columna de selección
    """
    _alias_check_column: str

    """
    Indica el nombre para crear un pseudocampo en el cursor para la columna de selección
    """
    _field_name_check_column: str

    """
    Indica que la columna de selección está visible
    """
    _check_column_visible: bool

    """
    Indica el número de columna por la que ordenar los registros
    """
    _sort_column_1: int

    """
    Indica el número de columna por la que ordenar los registros

    @author Silix - dpinelo
    """
    _sort_column_2: int

    """
    Indica el número de columna por la que ordenar los registros

    @author Silix
    """
    _sort_column_3: int

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros
    """
    _order_asc_1: bool

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros

    @author Silix - dpinelo
    """
    _order_asc_2: bool

    """
    Indica el sentido ascendente o descendente del la ordenacion actual de los registros

    @author Silix
    """
    _order_asc_3: bool

    """
    Indica si se debe establecer automáticamente la primera columna como de ordenación
    """
    _auto_sort_column: bool

    """
    Almacena la última claúsula de filtro aplicada en el refresco
    """
    _tdb_filter_last_where: str

    """
    Diccionario que relaciona literales descriptivos de una condición de filtro
    con su enumeración
    """
    _map_cond_type: List[str]

    """
    Indica si el marco de búsqueda está oculto
    """
    _find_hidden: bool

    """
    Indica si el marco para conmutar entre datos y filtro está oculto
    """
    _filter_hidden: bool

    """
    Indica si se deben mostrar los campos tipo pixmap en todas las filas
    """
    _show_all_pixmaps: bool

    """
    Nombre de la función de script a invocar para obtener el color y estilo de las filas y celdas

    El nombre de la función debe tener la forma 'objeto.nombre_funcion' o 'nombre_funcion',
    en el segundo caso donde no se especifica 'objeto' automáticamente se añadirá como
    prefijo el nombre del formulario donde se inicializa el componente FLTableDB seguido de un punto.
    De esta forma si utilizamos un mismo formulario para varias acciones, p.e. master.ui, podemos controlar
    si usamos distintas funciones de obtener color para cada acción (distintos nombres de formularios) o
    una única función común para todas las acciones.

    Ej. Estableciendo 'tdbGetColor' si el componente se inicializa en el formulario maestro de clientes,
    se utilizará 'formclientes.tdbGetColor', si se inicializa en el fomulario maestro de proveedores, se
    utilizará 'formproveedores.tdbGetColor', etc... Si establecemos 'flfactppal.tdbGetColor' siempre se llama a
    esa función independientemente del formulario en el que se inicialize el componente.

    Cuando se está pintando una celda se llamará a esa función pasándole cinco parámentros:
    - Nombre del campo correspondiente a la celda
    - Valor del campo de la celda
    - Cursor de la tabla posicionado en el registro correspondiente a la fila que
      está pintando. AVISO: En este punto los valores del buffer son indefinidos, no se hace refreshBuffer
      por motivos de eficiencia
    - Tipo del campo, ver flutil.FLUtilInterface::Type en FLObjectFactory.h
    - Seleccionado. Si es TRUE indica que la celda a pintar está en la fila resaltada/seleccionada.
      Generalmente las celdas en la fila seleccionada se colorean de forma distinta al resto.

    La función debe devolver una array con cuatro cadenas de caracteres;

    [ "color_de_fondo", "color_lapiz", "estilo_fondo", "estilo_lapiz" ]

    En los dos primeros, el color, se puede utilizar cualquier valor aceptado por QColor::setNamedColor, ejemplos;

    "green"
    "#44ADDB"

    En los dos últimos, el estilo, se pueden utilizar los valores aceptados por QBrush::setStyle y QPen::setStyle,
    ver en fldatatable.FLDataTable.cpp las funciones nametoBrushStyle y nametoPenStyle, ejemplos;

    "SolidPattern"
    "DiagCrossPattern"
    "DotLine"
    "SolidLine"

    Si alguno de los valores del array es vacio "", entonces se utilizarán los colores o estilos establecidos por defecto.
    """
    _function_get_color: Optional[str]

    """
    Editor falso
    """
    _fake_editor: Optional[Any] = None

    _tabledb_filter_records_function_name: Optional[str]

    def __init__(self, parent: Optional["QtWidgets.QWidget"] = None, name: str = "") -> None:
        """
        Inicialize.
        """
        if parent is None:
            return
        super().__init__(parent)

        self._top_widget = parent
        self._table_records = None
        self._table_name = None
        self._foreign_field = None
        self._field_relation = None
        self._cursor_aux = None
        self._show_all_pixmaps = True
        self._showed = False
        self._filter = ""
        self._sort_column_1 = 0
        self._sort_column_2 = 1
        self._sort_column_3 = 2
        self._sort_field_1 = None
        self._init_search = None
        self._auto_sort_column = True
        self._order_asc_1 = True
        self._order_asc_2 = True
        self._order_asc_3 = True
        self._read_only = False
        self._edit_only = False
        self._only_table = False
        self._insert_only = False
        self._req_read_only = False
        self._req_edit_only = False
        self._req_insert_only = False
        self._req_only_table = False
        self._tab_filter_loader = False
        self._field_name_check_column = ""
        self._alias_check_column = ""
        self._timer_1 = QtCore.QTimer(self)
        if name:
            self.setObjectName(name)
        self._check_column_visible = False
        self._check_column_enabled = False
        self._tdb_filter_last_where = ""

        self._icon_size = []

        self._icon_size = application.PROJECT.DGI.icon_size()

        self._tab_control_layout = QtWidgets.QHBoxLayout()
        self._tab_filter = QtWidgets.QFrame()  # contiene filtros
        self._tab_filter.setObjectName("tdbFilter")
        self._tab_data = QtWidgets.QFrame()  # contiene data
        self._tab_data.setObjectName("tabTable")
        self._function_get_color = None

        from . import flformdb

        while not isinstance(self._top_widget, flformdb.FLFormDB):
            self._top_widget = self._top_widget.parentWidget()
            if not self._top_widget:
                break

        self._loaded = False
        self.createFLTableDBWidget()

    # def __getattr__(self, name):
    #    return DefFun(self, name)

    def load(self) -> None:
        """Initialize the cursor and controls."""

        # Es necesario pasar a modo interactivo lo antes posible
        # Sino, creamos un bug en el cierre de ventana: se recarga toda la tabla para saber el tamaño
        # print("FLTableDB(%s): setting columns in interactive mode" % self._tableName))
        if self.loaded():
            return

        if self._top_widget is not None:
            if not self._top_widget.cursor():
                LOGGER.warning(
                    "FLTableDB : Uno de los padres o antecesores de FLTableDB deber ser de la clase FLFormDB o heredar de ella"
                )
                return

            self.cursor_ = cast(pnsqlcursor.PNSqlCursor, self._top_widget.cursor())

        self.initCursor()
        # self.setFont(QtWidgets.QApplication.font())

        if not self.objectName():
            self.setObjectName("FLTableDB")

        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.refreshDelayed)  # type: ignore [attr-defined] # noqa: F821

        # FIXME: El problema de que aparezca al editar un registro que no es, es por carga doble de initCursor()
        # ...... Cuando se lanza showWidget, y tiene _initCursorWhenLoad, lanza initCursor y luego otra vez.
        # ...... esta doble carga provoca el error y deja en el formulario el cursor original.

        self._map_cond_type = []

        self._loaded = True
        self.showWidget()

        if DEBUG:
            LOGGER.warning(
                "**FLTableDB::name: %r cursor: %r", self.objectName(), self.cursor().curName()
            )

    def loaded(self) -> bool:
        """Return if the control is inicilized."""

        return self._loaded

    def initCursor(self) -> None:
        """
        Start the cursor according to this field either from the source table or from a related table.
        """
        if not self._top_widget or not hasattr(self, "cursor_"):
            return

        if not self.cursor().private_cursor.metadata_:
            return

        self._top_widget.formClosed.connect(self.closeCursor)  # type: ignore [attr-defined]

        table_metadata: Optional["pntablemetadata.PNTableMetaData"] = self.cursor().metadata()
        if self._sort_field_1 is None:
            if table_metadata is not None:
                self._sort_field_1 = table_metadata.field(table_metadata.primaryKey())

        own_table_metadata = None
        if self._table_name:
            if DEBUG:
                LOGGER.warning(
                    "**FLTableDB::name: %r tableName: %r", self.objectName(), self._table_name
                )

            if not self.cursor().db().connManager().manager().existsTable(self._table_name):
                own_table_metadata = True
                table_metadata = (
                    self.cursor().db().connManager().manager().createTable(self._table_name)
                )
            else:
                own_table_metadata = True
                manager_tmd = self.cursor().db().connManager().manager().metadata(self._table_name)

                if not manager_tmd or isinstance(manager_tmd, bool):
                    return

                table_metadata = manager_tmd

            # if table_metadata is None:
            #    return

            if not self._foreign_field or not self._field_relation:
                if not self.cursor().metadata():
                    if (
                        own_table_metadata
                        and table_metadata is not None
                        and not table_metadata.inCache()
                    ):
                        del table_metadata
                    return

                if not self.cursor().metadata().name() == self._table_name:
                    ctxt = self.cursor().context()
                    self.cursor_ = pnsqlcursor.PNSqlCursor(
                        self._table_name,
                        True,
                        self.cursor().db().connectionName(),
                        None,
                        None,
                        self,
                    )

                    if self.cursor():
                        self.cursor().setContext(ctxt)
                        self._cursor_aux = None

                    if own_table_metadata and table_metadata and not table_metadata.inCache():
                        del table_metadata

                    return

            else:
                cursor_top_widget = cast(pnsqlcursor.PNSqlCursor, self._top_widget.cursor())
                if cursor_top_widget and cursor_top_widget.metadata().name() != self._table_name:
                    self.cursor_ = cursor_top_widget

        if (
            not self._table_name
            or not self._foreign_field
            or not self._field_relation
            or self._cursor_aux
        ):
            if own_table_metadata and table_metadata and not table_metadata.inCache():
                del table_metadata

            return

        self._cursor_aux = self.cursor()
        cursor_name = self.cursor().metadata().name()
        relation_metadata = (
            self.cursor()
            .metadata()
            .relation(self._foreign_field, self._field_relation, self._table_name)
        )
        test_m1 = (
            table_metadata.relation(self._field_relation, self._foreign_field, cursor_name)
            if table_metadata is not None
            else None
        )
        check_integrity = False
        if not relation_metadata:
            if test_m1:
                if test_m1.cardinality() == pnrelationmetadata.PNRelationMetaData.RELATION_M1:
                    check_integrity = True
            field_metadata = self.cursor().metadata().field(self._foreign_field)
            if field_metadata is not None:
                tmd_aux_ = self.cursor().db().connManager().manager().metadata(self._table_name)
                if not tmd_aux_ or tmd_aux_.isQuery():
                    check_integrity = False
                if tmd_aux_ and not tmd_aux_.inCache():
                    del tmd_aux_

                relation_metadata = pnrelationmetadata.PNRelationMetaData(
                    self._table_name,
                    self._field_relation,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    check_integrity,
                )
                field_metadata.addRelationMD(relation_metadata)
                LOGGER.warning(
                    "FLTableDB : La relación entre la tabla del formulario %s y esta tabla %s de este campo no existe, "
                    "pero sin embargo se han indicado los campos de relación( %s, %s )",
                    cursor_name,
                    self._table_name,
                    self._field_relation,
                    self._foreign_field,
                )
                LOGGER.trace(
                    "FLTableDB : Creando automáticamente %s.%s --1M--> %s.%s",
                    cursor_name,
                    self._foreign_field,
                    self._table_name,
                    self._field_relation,
                )
            else:
                LOGGER.warning(
                    "FLTableDB : El campo ( %s ) indicado en la propiedad foreignField no se encuentra en la tabla ( %s )",
                    self._foreign_field,
                    cursor_name,
                )
                pass

        relation_metadata = test_m1
        if not relation_metadata and table_metadata is not None:
            field_metadata = table_metadata.field(self._field_relation)
            if field_metadata is not None:
                relation_metadata = pnrelationmetadata.PNRelationMetaData(
                    cursor_name,
                    self._foreign_field,
                    pnrelationmetadata.PNRelationMetaData.RELATION_1M,
                    False,
                    False,
                    False,
                )
                field_metadata.addRelationMD(relation_metadata)
                if DEBUG:
                    LOGGER.trace(
                        "FLTableDB : Creando automáticamente %s.%s --1M--> %s.%s",
                        self._table_name,
                        self._field_relation,
                        cursor_name,
                        self._foreign_field,
                    )

            else:
                if DEBUG:
                    LOGGER.warning(
                        "FLTableDB : El campo ( %s ) indicado en la propiedad fieldRelation no se encuentra en la tabla ( %s )",
                        self._field_relation,
                        self._table_name,
                    )

        self.cursor_ = pnsqlcursor.PNSqlCursor(
            self._table_name,
            True,
            self.cursor().db().connectionName(),
            self._cursor_aux,
            relation_metadata,
            self,
        )
        if not self.cursor():
            self.cursor_ = self._cursor_aux
            self._cursor_aux = None

        else:
            self.cursor().setContext(self._cursor_aux.context())
            if self._showed:
                try:
                    self._cursor_aux.newBuffer.disconnect(self.refresh)
                except Exception:
                    pass

            self._cursor_aux.newBuffer.connect(self.refresh)

        # Si hay cursor_top_widget no machaco el cursor de _top_widget
        if (
            self._cursor_aux
            and isinstance(self._top_widget, flformsearchdb.FLFormSearchDB)
            and not cursor_top_widget
        ):
            self._top_widget.setWindowTitle(self.cursor().metadata().alias())
            self._top_widget.setCursor(self.cursor())

        if own_table_metadata or table_metadata and not table_metadata.inCache():
            del table_metadata

    def closeCursor(self):
        """Close cursor."""

        if self.cursor_:
            try:
                self.cursor_.newBuffer.disconnect(self.refresh)
            except Exception:
                pass
        if self._cursor_aux:
            try:
                self._cursor_aux.newBuffer.disconnect(self.refresh)
            except Exception:
                pass
        cursor_rel = self.cursor_.cursorRelation()
        if cursor_rel:
            try:
                cursor_rel.newBuffer.disconnect(self.cursor_.refresh)
            except Exception:
                pass

        self._cursor_aux = None
        self.cursor_ = None  # type: ignore [assignment]

    def cursor(self) -> "isqlcursor.ISqlCursor":  # type: ignore [override] # noqa F821
        """
        Return the cursor used by the component.

        return pnsqlcursor.PNSqlCursor object with the cursor containing the records to be used in the form
        """
        # if not self.cursor().buffer():
        #    self.cursor().refreshBuffer()
        return self.cursor_

    def tableName(self) -> str:
        """
        Return the name of the associated table.

        @return Name of the associated table
        """
        if not self._table_name:
            raise Exception("_table_name is empty!")
        return self._table_name

    def setTableName(self, table_name: str) -> None:
        """
        Set the name of the associated table.

        @param table_name Name of the table
        """
        self._table_name = table_name
        if self._top_widget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def foreignField(self) -> Optional[str]:
        """
        Return the name of the foreign field.

        @return Field Name
        """
        return self._foreign_field

    def setForeignField(self, foreign_field: str) -> None:
        """
        Set the name of the foreign field.

        @param foreign_field Name of the associated field.
        """
        self._foreign_field = foreign_field
        if self._top_widget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def fieldRelation(self) -> Optional[str]:
        """
        Return the name of the related field.

        @return Field Name
        """
        return self._field_relation

    def setFieldRelation(self, field_name: str) -> None:
        """
        To set the name of the related field.

        @param field_name Field name
        """
        self._field_relation = field_name
        if self._top_widget:
            self.initCursor()
        else:
            self.initFakeEditor()

    def setReadOnly(self, mode: bool) -> None:
        """
        Set if the component is in read-only mode or not.
        """

        if self._table_records:
            self._read_only = mode
            self._table_records.setFLReadOnly(mode)
            self.readOnlyChanged.emit(mode)

        self._req_read_only = mode

    def readOnly(self) -> bool:
        """Return if the control is in read only mode."""

        return self._req_read_only

    def setEditOnly(self, mode: bool) -> None:
        """
        Set if the component is in edit only mode or not.
        """
        if self._table_records:
            self._edit_only = mode
            self._table_records.setEditOnly(mode)
            self.editOnlyChanged.emit(mode)

        self._req_edit_only = mode

    def editOnly(self) -> bool:
        """Return if the control is in edit only mode."""
        return self._req_edit_only

    def setInsertOnly(self, mode: bool) -> None:
        """
        Set the component to insert only or not.
        """
        if self._table_records:
            self._insert_only = mode
            self._table_records.setInsertOnly(mode)
            self.insertOnlyChanged.emit(mode)

        self._req_insert_only = mode

    def insertOnly(self) -> bool:
        """Return if the control is in insert only mode."""
        return self._req_insert_only

    def setInitSearch(self, init_search: str) -> None:
        """
        Set the initial search filter.
        """
        self._init_search = init_search

    def setOrderCols(self, fields: List[str]):
        """
        Set the order of the columns in the table.

        @param fields List of the names of the fields sorted as you wish them to appear in the table from left to right
        """
        if not self.cursor() or not self._table_records:
            return
        table_metadata = self.cursor().metadata()
        if not table_metadata:
            return

        if not self._showed:
            self.showWidget()

        fields_list: List[str] = []

        for num, field_name in enumerate(fields):
            field_metadata = table_metadata.field(field_name)
            if field_metadata is not None:
                if field_metadata.visibleGrid():
                    fields_list.append(field_name)

            if len(fields_list) > self.cursor().model().columnCount():
                return

            _index = self._table_records.logical_index_to_visual_index(
                self._table_records.column_name_to_column_index(field_name)
            )
            self.moveCol(_index, num)

        if not self._line_edit_search:
            raise Exception("_line_edit_search is not defined!")

        self.setSortOrder(True)
        text_search = self._line_edit_search.text()
        self.refresh(True)

        if text_search:
            self.refresh(False, True)

            try:
                self._line_edit_search.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.filterRecords
                )
            except Exception:
                pass
            self._line_edit_search.setText(text_search)
            self._line_edit_search.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.filterRecords
            )
            self._line_edit_search.selectAll()
            # self.seekCursor()
            QtCore.QTimer.singleShot(0, self._table_records.ensureRowSelectedVisible)
        else:
            self.refreshDelayed()

    def orderCols(self) -> List[str]:
        """
        Return the list of fields sorted by their columns in the table from left to right.
        """
        list_: List[str] = []

        if not self.cursor():
            return list_

        table_metadata = self.cursor().metadata()
        if not table_metadata:
            return list_

        if not self._showed:
            self.showWidget()

        model = self.cursor().model()

        if model:
            if not self._table_records:
                raise Exception("_table_records is not defined!")

            for column in range(model.columnCount()):
                alias_ = self._table_records.model().headerData(
                    self._table_records.visual_index_to_metadata_index(column),
                    QtCore.Qt.Orientation.Horizontal,
                    QtCore.Qt.ItemDataRole.DisplayRole,
                )
                list_.append(table_metadata.fieldAliasToName(alias_) or "")

        return list_

    def setFilter(self, filter: str) -> None:
        """
        Set the table filter.

        @param filter Where statement setting the filter
        """
        self._filter = filter

    def filter(self) -> str:
        """
        Return the table filter.

        @return Filter
        """
        return self._filter

    def findFilter(self) -> Optional[str]:
        """
        Return the filter of the table imposed in the Find.

        @return Filter
        """
        return self._tdb_filter_last_where

    def checkColumnEnabled(self) -> bool:
        """
        Return if the selection column is activated.
        """
        return self._check_column_enabled

    def setCheckColumnEnabled(self, value: bool) -> None:
        """
        Set the activation status of the selection column.

        The change of status will not be effective until the next refresh.
        """
        self._check_column_enabled = value

    def aliasCheckColumn(self) -> Optional[str]:
        """
        Obtain the header label text for the selection column.
        """
        if not self._table_records:
            raise Exception("_table_records is not defined!")

        return self._table_records.model().headerData(
            # self._table_records.selectionModel().selectedColumns(),
            self._table_records.currentColumn(),
            QtCore.Qt.Orientation.Horizontal,
            QtCore.Qt.ItemDataRole.DisplayRole,
        )

    def setAliasCheckColumn(self, alias: str) -> None:
        """
        Set the text of the header tag for the selection column.

        The change of the label text will not be effective until the next refresh
        """
        self._alias_check_column = alias

    def findHidden(self) -> bool:
        """
        Get if the search frame is hidden.
        """
        return self._find_hidden

    @decorators.deprecated
    def setFindHidden(self, value: bool) -> None:
        """
        Hide or show the search frame.

        @param h TRUE hides it, FALSE shows it.
        """
        # if self._find_hidden is not h:
        #    self._find_hidden = h
        #    if h:
        #        self._tab_control_layout.hide()
        #    else:
        #        self._tab_control_layout.show()
        pass

    def filterHidden(self) -> bool:
        """
        Return if the frame for switching between data and filter is hidden.
        """
        return self._filter_hidden

    @decorators.deprecated
    def setFilterHidden(self, value: bool) -> None:
        """
        Hide or show the frame to switch between data and filter.

        @param value TRUE hides it, FALSE shows it
        """
        # if self._filter_hidden is not h:
        #    self._filter_hidden = h
        #    if h:
        #        self._tab_filter.hide()
        #    else:
        #        self._tab_filter.show()
        pass

    def showAllPixmaps(self) -> bool:
        """
        Return if images of unselected lines are displayed.
        """
        return self._show_all_pixmaps

    def setShowAllPixmaps(self, value: bool) -> None:
        """
        Set if images of unselected lines are displayed.
        """
        self._show_all_pixmaps = value

    def functionGetColor(self) -> Optional[str]:
        """
        Return the function that calculates the color of the cell.
        """
        return self._function_get_color

    def setFunctionGetColor(self, function_get_color: str) -> None:
        """
        Set the function that calculates the color of the cell.
        """
        self._function_get_color = function_get_color

        # if self._table_records is not None:
        #    self.tableRecords().setFunctionGetColor("%s.%s" % (self._top_widget.name(), f))

    def setFilterRecordsFunction(self, function_filter_record: str) -> None:
        """
        Assign the function name to call when the filter changes.
        """
        self._tabledb_filter_records_function_name = function_filter_record

    def setOnlyTable(self, value: bool = True) -> None:
        """
        Enable table only mode.
        """
        if self._table_records:
            self._only_table = value
            self._table_records.setOnlyTable(value)

        self._req_only_table = value

    def onlyTable(self) -> bool:
        """
        Return if the control is in table only mode.
        """
        return self._req_only_table

    @decorators.not_implemented_warn
    def setAutoSortColumn(self, value: bool = True):
        """
        Set auto sort mode.
        """
        self._auto_sort_column = value

    def autoSortColumn(self) -> bool:
        """Return if auto sort mode is enabled."""

        return self._auto_sort_column

    def eventFilter(self, obj_: "QtCore.QObject", event: "QtCore.QEvent") -> bool:
        """
        Process user events.
        """
        if (
            not self._table_records
            or not self._line_edit_search
            or not self._combo_box_field_to_search_1
            or not self._combo_box_field_to_search_2
            or not self.cursor()
        ):
            return super().eventFilter(obj_, event)

        if event.type() == QtCore.QEvent.Type.KeyPress:
            key = cast(QtGui.QKeyEvent, event)

            if isinstance(obj_, fldatatable.FLDataTable):

                if key.key() == cast(int, QtCore.Qt.Key.Key_F2):
                    self._combo_box_field_to_search_1.showPopup()
                    return True

            # if event.type() == QtCore.QEvent.WindowUnblocked and isinstance(obj_, fldatatable.FLDataTable):
            #    self.refreshDelayed()
            #    return True

            elif isinstance(obj_, QtWidgets.QLineEdit):

                if key.key() in (
                    cast(int, QtCore.Qt.Key.Key_Enter),
                    cast(int, QtCore.Qt.Key.Key_Return),
                ):
                    self._table_records.setFocus()
                    return True

                elif key.key() == cast(int, QtCore.Qt.Key.Key_Up):
                    self._combo_box_field_to_search_1.setFocus()
                    return True

                elif key.key() == cast(int, QtCore.Qt.Key.Key_Down):
                    self._table_records.setFocus()
                    return True

                elif key.key() == cast(int, QtCore.Qt.Key.Key_F2):
                    self._combo_box_field_to_search_1.showPopup()
                    return True

                elif key.text() in ["'", "\\"]:
                    return True

        if obj_ in (self._table_records, self._line_edit_search):
            return False
        else:
            return super().eventFilter(obj_, event)

    def showEvent(self, event: "QtGui.QShowEvent") -> None:
        """
        Proccess show event.
        """
        super().showEvent(event)
        self.load()
        if not self.loaded():
            self.showWidget()

    def showWidget(self) -> None:
        """
        Show the widget.
        """
        if self._showed:
            return

        if not self._top_widget:
            self.initFakeEditor()
            self._showed = True
            return

        if not self.cursor():
            return

        self._showed = True

        # own_tmd = bool(self._table_name)
        if self._table_name:
            if not self.cursor().db().connManager().manager().existsTable(self._table_name):
                table_metadata = (
                    self.cursor().db().connManager().manager().createTable(self._table_name)
                )
            else:
                table_metadata = (
                    self.cursor().db().connManager().manager().metadata(self._table_name)
                )

            if not table_metadata:
                return

        self.tableRecords()

        if not self._cursor_aux:
            if not self._init_search:
                self.refresh(True, True)
                # if self._table_records:
                #    QtCore.QTimer.singleShot(0, self._table_records.ensureRowSelectedVisible)
            else:
                self.refresh(True)
                if self._table_records and self._table_records.numRows() <= 0:

                    self.refresh(False, True)
                else:
                    self.refreshDelayed()

            if (
                not isinstance(self._top_widget, flformrecorddb.FLFormRecordDB)
                and self._line_edit_search is not None
            ):
                self._line_edit_search.setFocus()

        if self._cursor_aux:
            if (
                isinstance(self._top_widget, flformrecorddb.FLFormRecordDB)
                and self._cursor_aux.modeAccess() == pnsqlcursor.PNSqlCursor.Browse
            ):
                self.cursor().setEdition(False)
                self.setReadOnly(True)

            if self._init_search:
                self.refresh(True, True)
                if self._table_records:
                    QtCore.QTimer.singleShot(0, self._table_records.ensureRowSelectedVisible)
            else:
                # self.refresh(True)
                # if self._table_records and self._table_records.numRows() <= 0:
                #    self.refresh(False, True)
                # else:

                self.refreshDelayed()

        elif (
            isinstance(self._top_widget, flformrecorddb.FLFormRecordDB)
            and self.cursor().modeAccess() == pnsqlcursor.PNSqlCursor.Browse
            and table_metadata
            and not table_metadata.isQuery()
        ):
            self.cursor().setEdition(False)
            self.setReadOnly(True)

        # if own_table_metadata and table_metadata and not table_metadata.inCache():
        #    del table_metadata

    def createFLTableDBWidget(self) -> None:
        """Create all controls."""

        size_policy = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum
        )
        size_policy.setHeightForWidth(True)

        size_policy_clean = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed
        )
        size_policy_clean.setHeightForWidth(True)

        size_policy_group_box = QtWidgets.QSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
        )

        self._data_layout = QtWidgets.QHBoxLayout()  # Contiene _tab_data y _tab_filters
        # self._data_layout.setContentsMargins(0, 0, 0, 0)
        # self._data_layout.setSizeConstraint(0)

        self._tab_data_layout = QtWidgets.QVBoxLayout()
        filter_layout = QtWidgets.QVBoxLayout()
        filter_layout.setSpacing(2)
        filter_layout.setContentsMargins(1, 2, 1, 2)
        if self._tab_data:
            self._tab_data.setSizePolicy(size_policy_group_box)
            self._tab_data.setLayout(self._tab_data_layout)

        if self._tab_filter:
            self._tab_filter.setSizePolicy(size_policy_group_box)
            self._tab_filter.setLayout(filter_layout)

        # Fix para acercar el lineEdit con el fltable
        # self._tab_data.setContentsMargins(0, 0, 0, 0)
        # self._tab_filter.setContentsMargins(0, 0, 0, 0)
        self._tab_data_layout.setContentsMargins(0, 0, 0, 0)
        # filter_layout.setContentsMargins(0, 0, 0, 0)

        # Contiene botones lateral (datos, filtros, odf)
        self._buttons_layout = QtWidgets.QVBoxLayout()
        self._master_layout = QtWidgets.QVBoxLayout()  # Contiene todos los layouts

        self._pb_data = QtWidgets.QPushButton(self)
        self._pb_data.setSizePolicy(size_policy)
        if self._icon_size is not None:
            self._pb_data.setMinimumSize(self._icon_size)
        self._pb_data.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._pb_data.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-data.png"))
        )
        self._pb_data.setText("")
        self._pb_data.setToolTip("Mostrar registros")
        self._pb_data.setWhatsThis("Mostrar registros")
        self._buttons_layout.addWidget(self._pb_data)
        self._pb_data.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
            self.activeTabData
        )

        self._pb_filter = QtWidgets.QPushButton(self)
        self._pb_filter.setSizePolicy(size_policy)
        if self._icon_size is not None:
            self._pb_filter.setMinimumSize(self._icon_size)
        self._pb_filter.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._pb_filter.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-filter.png"))
        )
        self._pb_filter.setText("")
        self._pb_filter.setToolTip("Mostrar filtros")
        self._pb_filter.setWhatsThis("Mostrar filtros")
        self._buttons_layout.addWidget(self._pb_filter)
        self._pb_filter.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
            self.activeTabFilter
        )

        self._pb_odf = QtWidgets.QPushButton(self)
        self._pb_odf.setSizePolicy(size_policy)
        if self._icon_size is not None:
            self._pb_odf.setMinimumSize(self._icon_size)
        self._pb_odf.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self._pb_odf.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-odf.png"))
        )
        self._pb_odf.setText("")
        self._pb_odf.setToolTip("Exportar a hoja de cálculo")
        self._pb_odf.setWhatsThis("Exportar a hoja de cálculo")
        self._buttons_layout.addWidget(self._pb_odf)
        self._pb_odf.clicked.connect(self.exportToOds)  # type: ignore [attr-defined] # noqa: F821
        if settings.CONFIG.value("ebcomportamiento/FLTableExport2Calc", "false") == "true":
            self._pb_odf.setDisabled(True)

        self.pb_clean = QtWidgets.QPushButton(self)
        self.pb_clean.setSizePolicy(size_policy_clean)
        if self._icon_size is not None:
            self.pb_clean.setMinimumSize(self._icon_size)
        self.pb_clean.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.pb_clean.setIcon(
            QtGui.QIcon(utils_base.filedir("./core/images/icons", "fltable-clean.png"))
        )
        self.pb_clean.setText("")
        self.pb_clean.setToolTip("Limpiar filtros")
        self.pb_clean.setWhatsThis("Limpiar filtros")
        filter_layout.addWidget(self.pb_clean)
        self.pb_clean.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
            self.tdbFilterClear
        )

        spacer = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
        )
        self._buttons_layout.addItem(spacer)

        self._combo_box_field_to_search_1 = QtWidgets.QComboBox()
        self._combo_box_field_to_search_2 = QtWidgets.QComboBox()
        # self._combo_box_field_to_search_1.addItem("*")
        # self._combo_box_field_to_search_2.addItem("*")
        self._line_edit_search = QtWidgets.QLineEdit()
        self._line_edit_search.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
            self.filterRecords
        )
        label1 = QtWidgets.QLabel()
        label2 = QtWidgets.QLabel()
        label1.setStyleSheet("border: 0px")
        label2.setStyleSheet("border: 0px")

        label1.setText("Buscar")
        label2.setText("en")

        if self._tab_control_layout is not None:
            control_frame = QtWidgets.QFrame()
            lay = QtWidgets.QHBoxLayout()
            control_frame.setFrameStyle(cast(int, QtWidgets.QFrame.Shadow.Raised.value))
            control_frame.setStyleSheet("QFrame { border: 1px solid black; }")
            lay.setContentsMargins(2, 2, 2, 2)
            lay.setSpacing(2)
            lay.addWidget(label1)
            lay.addWidget(self._line_edit_search)
            lay.addWidget(label2)
            lay.addWidget(self._combo_box_field_to_search_1)
            lay.addWidget(self._combo_box_field_to_search_2)
            control_frame.setLayout(lay)

            self._tab_control_layout.addWidget(control_frame)
            self._master_layout.addLayout(self._tab_control_layout)

        self._master_layout.addLayout(self._data_layout)
        self._master_layout.setSpacing(2)
        self._master_layout.setContentsMargins(1, 2, 1, 2)
        self.setLayout(self._master_layout)

        # Se añade data, filtros y botonera
        if self._tab_data is not None:
            self._data_layout.addWidget(self._tab_data)
        if self._tab_filter is not None:
            self._data_layout.addWidget(self._tab_filter)
            self._tab_filter.hide()

        self._data_layout.addLayout(self._buttons_layout)
        self._combo_box_field_to_search_1.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
            self.putFirstCol
        )
        self._combo_box_field_to_search_2.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
            self.putSecondCol
        )

        self._tdb_filter = qtable.QTable()

        filter_layout.addWidget(self._tdb_filter)

    def tableRecords(self) -> "fldatatable.FLDataTable":
        """
        Obtiene el componente tabla de registros.
        """
        if self._table_records is None:
            self._table_records = fldatatable.FLDataTable(self._tab_data, "tableRecords")
            if self._table_records is not None:
                self._table_records.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                self.setFocusProxy(self._table_records)
                if self._tab_data_layout is not None:
                    self._tab_data_layout.addWidget(self._table_records)
                self.setTabOrder(self._table_records, self._line_edit_search)
                self.setTabOrder(self._line_edit_search, self._combo_box_field_to_search_1)
                self.setTabOrder(
                    self._combo_box_field_to_search_1, self._combo_box_field_to_search_2
                )
                if self._line_edit_search is not None:
                    self._line_edit_search.installEventFilter(self)
                self._table_records.installEventFilter(self)

                if self._auto_sort_column:
                    self._table_records.header().sectionClicked.connect(self.switchSortOrder)

        t_cursor = self._table_records.cursor_
        if (
            self.cursor()
            and self.cursor() is not t_cursor
            and self.cursor().private_cursor.metadata_ is not None
            and (
                not t_cursor
                or (
                    t_cursor
                    and t_cursor.metadata()
                    and t_cursor.metadata().name() != self.cursor().metadata().name()
                )
            )
        ):
            self.setTableRecordsCursor()

        return self._table_records

    def setTableRecordsCursor(self) -> None:
        """
        Assign the current cursor of the component to the record table.
        """

        if self._table_records is None:
            self._table_records = fldatatable.FLDataTable(self._tab_data, "tableRecords")
            if self._table_records is not None:
                self._table_records.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
                self.setFocusProxy(self._table_records)
                if self._tab_data_layout is not None:
                    self._tab_data_layout.addWidget(self._table_records)
                self.setTabOrder(self._table_records, self._line_edit_search)
                self.setTabOrder(self._line_edit_search, self._combo_box_field_to_search_1)
                self.setTabOrder(
                    self._combo_box_field_to_search_1, self._combo_box_field_to_search_2
                )
                self._table_records.installEventFilter(self)

                if self._line_edit_search is not None:
                    self._line_edit_search.installEventFilter(self)

        if self._check_column_enabled:
            try:
                self._table_records.clicked.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self._table_records.setChecked
                )
            except Exception:
                LOGGER.warning("setTableRecordsCursor: Error disconnecting setChecked signal")
            self._table_records.clicked.connect(  # type: ignore [attr-defined] # noqa: F821
                self._table_records.setChecked
            )

        t_cursor = self._table_records.cursor_
        if t_cursor is not self.cursor():
            self._table_records.setFLSqlCursor(self.cursor())
            if t_cursor:
                self._table_records.recordChoosed.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.recordChoosedSlot
                )
                t_cursor.newBuffer.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.currentChangedSlot
                )

            self._table_records.recordChoosed.connect(  # type: ignore [attr-defined] # noqa: F821
                self.recordChoosedSlot
            )
            self.cursor().newBuffer.connect(  # type: ignore [attr-defined] # noqa: F821
                self.currentChangedSlot
            )

    @decorators.pyqt_slot()
    def recordChoosedSlot(self) -> None:
        """Perform operations when selecting a record."""
        if (
            isinstance(self._top_widget, flformsearchdb.FLFormSearchDB)
            and self._top_widget._in_exec
        ):
            self._top_widget.accept()
        else:
            self.cursor().chooseRecord()

    @decorators.pyqt_slot()
    def currentChangedSlot(self) -> None:
        """Emit current changed signal."""
        self.currentChanged.emit()

    def currentRow(self) -> int:
        """Return current row index."""

        return self.cursor().at()

    def refreshTabData(self) -> None:
        """
        Refresh the data tab by applying the filter.
        """
        if self._filter and self._tdb_filter_last_where:
            self._filter = self._filter.replace(self._tdb_filter_last_where, "")

        self._tdb_filter_last_where = self.tdbFilterBuildWhere()
        self.refresh(False, True)

    def refreshTabFilter(self) -> None:
        """
        Refresh the filter tab.
        """
        if self._tab_filter_loader:
            return

        hori_header = self.tableRecords().horizontalHeader()
        if not hori_header:
            return

        hori_count = hori_header.count() - self._sort_column_1
        if self._tdb_filter and self.cursor():
            table_metadata = self.cursor().metadata()
            if table_metadata is None:
                return

            field = None
            # type = None
            # len = None
            part_integer = None
            part_decimal = None
            rx_ = None

            self._tdb_filter.setSelectionMode(QtWidgets.QTableWidget.SelectionMode.NoSelection)
            self._tdb_filter.setNumCols(5)

            not_visibles = 0
            for field in table_metadata.fieldList():
                if not field.visibleGrid():
                    not_visibles += 1

            self._tdb_filter.setNumRows(hori_count - not_visibles)
            self._tdb_filter.setColumnReadOnly(0, True)
            util = flutil.FLUtil()
            self._tdb_filter.setColumnLabels(",", self.tr("Campo,Condición,Valor,Desde,Hasta"))

            self._map_cond_type.insert(self._all, self.tr("Todos"))
            self._map_cond_type.insert(self._contains, self.tr("Contiene Valor"))
            self._map_cond_type.insert(self._starts, self.tr("Empieza por Valor"))
            self._map_cond_type.insert(self._end, self.tr("Acaba por Valor"))
            self._map_cond_type.insert(self._equal, self.tr("Igual a Valor"))
            self._map_cond_type.insert(self._dist, self.tr("Distinto de Valor"))
            self._map_cond_type.insert(self._greater, self.tr("Mayor que Valor"))
            self._map_cond_type.insert(self._less, self.tr("Menor que Valor"))
            self._map_cond_type.insert(self._from_to, self.tr("Desde - Hasta"))
            self._map_cond_type.insert(self._null, self.tr("Vacío"))
            self._map_cond_type.insert(self._not_null, self.tr("No Vacío"))
            idx_i = 0
            # for headT in hori_count:
            _linea = 0

            while idx_i < hori_count:
                _label = (
                    self.cursor()
                    .model()
                    .headerData(
                        idx_i + self._sort_column_1,
                        QtCore.Qt.Orientation.Horizontal,
                        QtCore.Qt.ItemDataRole.DisplayRole,
                    )
                )
                _alias = table_metadata.fieldAliasToName(_label)
                if _alias is None:
                    idx_i += 1
                    continue

                field = table_metadata.field(_alias)

                if field is None:
                    idx_i += 1
                    continue

                if not field.visibleGrid():
                    idx_i += 1
                    continue

                self._tdb_filter.setText(_linea, 0, _label)

                type_ = field.type()
                len_ = field.length()
                part_integer = field.partInteger()
                part_decimal = field.partDecimal()
                rx_ = field.regExpValidator()
                has_option_list = field.hasOptionsList()

                cond = QtWidgets.QComboBox(self)
                if not type_ == "pixmap":
                    cond_list = [
                        self.tr("Todos"),
                        self.tr("Igual a Valor"),
                        self.tr("Distinto de Valor"),
                        self.tr("Vacío"),
                        self.tr("No Vacío"),
                    ]
                    if not type_ == "bool":
                        cond_list = [
                            self.tr("Todos"),
                            self.tr("Igual a Valor"),
                            self.tr("Distinto de Valor"),
                            self.tr("Vacío"),
                            self.tr("No Vacío"),
                            self.tr("Contiene Valor"),
                            self.tr("Empieza por Valor"),
                            self.tr("Acaba por Valor"),
                            self.tr("Mayor que Valor"),
                            self.tr("Menor que Valor"),
                            self.tr("Desde - Hasta"),
                        ]
                    cond.insertItems(len(cond_list), cond_list)
                    self._tdb_filter.setCellWidget(_linea, 1, cond)

                idx_j = 2
                while idx_j < 5:
                    if type_ in (
                        "uint",
                        "int",
                        "double",
                        "string",
                        "stringlist",
                        "timestamp",
                        "json",
                    ):
                        if has_option_list:
                            editor_qcb = QtWidgets.QComboBox(self)
                            option_list_translated = []
                            option_list_not_transalated = field.optionsList()
                            for item in option_list_not_transalated:
                                option_list_translated.append(util.translate("Metadata", item))

                            editor_qcb.insertItems(
                                len(option_list_translated), option_list_translated
                            )

                            self._tdb_filter.setCellWidget(_linea, idx_j, editor_qcb)
                        else:

                            editor_le = QtWidgets.QLineEdit(self)
                            if type_ == "double":

                                editor_le.setValidator(
                                    fldoublevalidator.FLDoubleValidator(
                                        0, pow(10, part_integer) - 1, part_decimal, editor_le
                                    )
                                )
                                editor_le.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                            elif type_ in ("uint", "int"):
                                if type_ == "uint":

                                    editor_le.setValidator(
                                        fluintvalidator.FLUIntValidator(
                                            0, pow(10, part_integer) - 1, editor_le
                                        )
                                    )
                                else:

                                    editor_le.setValidator(
                                        flintvalidator.FLIntValidator(
                                            pow(10, part_integer) - 1 * (-1),
                                            pow(10, part_integer) - 1,
                                            editor_le,
                                        )
                                    )

                                editor_le.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                            else:  # string, stringlist, timestamp
                                if len_ > 0:
                                    editor_le.setMaxLength(len_)
                                    if rx_:
                                        editor_le.setValidator(
                                            QtGui.QRegularExpressionValidator(
                                                QtCore.QRegularExpression(rx_), editor_le
                                            )
                                        )

                                editor_le.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

                            self._tdb_filter.setCellWidget(_linea, idx_j, editor_le)

                    elif type_ == "serial":

                        editor_se = flspinbox.FLSpinBox()
                        editor_se.setMaxValue(pow(10, part_integer) - 1)
                        self._tdb_filter.setCellWidget(_linea, idx_j, editor_se)

                    elif type_ == "pixmap":

                        editor_px = QtWidgets.QLineEdit(self)
                        self._tdb_filter.setRowReadOnly(idx_i, True)
                        self._tdb_filter.setCellWidget(_linea, idx_j, editor_px)

                    elif type_ == "date":

                        editor_de = fldateedit.FLDateEdit(self, _label)
                        editor_de.setOrder(fldateedit.FLDateEdit.DMY)
                        editor_de.setAutoAdvance(True)
                        editor_de.setCalendarPopup(True)
                        editor_de.setSeparator("-")
                        editor_de.setDate(QtCore.QDate().currentDate())
                        self._tdb_filter.setCellWidget(_linea, idx_j, editor_de)

                    elif type_ == "time":

                        editor_te = fltimeedit.FLTimeEdit(self)
                        time_now = QtCore.QTime.currentTime()
                        editor_te.setTime(time_now)
                        self._tdb_filter.setCellWidget(_linea, idx_j, editor_te)

                    elif type_ in (pnfieldmetadata.PNFieldMetaData.Unlock, "bool"):

                        editor_cb = flcheckbox.FLCheckBox(self)
                        self._tdb_filter.setCellWidget(_linea, idx_j, editor_cb)

                    idx_j += 1

                idx_i += 1
                _linea += 1

        idx_k = 0

        while idx_k < 5:
            if self._tdb_filter:
                self._tdb_filter.adjustColumn(idx_k)
            idx_k += 1

        self._tab_filter_loader = True  # Con esto no volvemos a cargar y reescribir el filtro

    def decodeCondType(self, cond_type: str) -> int:
        """
        Obtain the enumeration corresponding to a condition for the filter from its literal.
        """

        for num, value in enumerate(self._map_cond_type):
            if cond_type == value:
                return num

        return self._all

    def tdbFilterBuildWhere(self) -> str:
        """
        Build the filter clause in SQL from the contents of the values defined in the filter tab.
        """
        if not self._top_widget:
            return ""

        if self._tdb_filter is None:
            return ""

        rows_count = self._tdb_filter.numRows()
        # rows_count = self.cursor().model.columnCount()
        if not rows_count or not self.cursor():
            return ""

        table_metadata = self.cursor().metadata()
        if not table_metadata:
            return ""

        where = ""

        for idx in range(rows_count):
            if self._tdb_filter is None:
                break
            field_name = table_metadata.fieldAliasToName(self._tdb_filter.text(idx, 0))
            if field_name is None:
                raise Exception("field_name could not be resolved!")

            field = table_metadata.field(field_name)
            if field is None:
                continue

            cond = self._tdb_filter.cellWidget(idx, 1)
            if cond is None:
                continue

            cond_type = self.decodeCondType(cond.currentText())
            if cond_type == self._all:
                continue

            if table_metadata.isQuery():
                qry = (
                    self.cursor()
                    .db()
                    .connManager()
                    .manager()
                    .query(self.cursor().metadata().query())
                )

                if qry is not None:
                    for qry_field in qry.fieldList():
                        if qry_field.endswith(".%s" % field_name):
                            break

                    field_name = qry_field
            else:
                field_name = table_metadata.name() + "." + field_name

            _field_arg = field_name or ""
            arg2 = ""
            arg4 = ""
            type_ = field.type()
            has_option_list = field.hasOptionsList()

            if type_ in ("string", "stringlist", "timestamp"):
                _field_arg = "UPPER(%s)" % field_name

            if type_ in ("uint", "int", "double", "string", "stringlist", "timestamp", "json"):
                if has_option_list:
                    if cond_type == self._from_to:
                        editor_op_1 = self._tdb_filter.cellWidget(idx, 3)
                        editor_op_2 = self._tdb_filter.cellWidget(idx, 4)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_1.currentText, True)
                        )
                        arg4 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_2.currentText, True)
                        )
                    else:
                        editor_op_1 = self._tdb_filter.cellWidget(idx, 2)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_1.currentText, True)
                        )
                else:
                    if cond_type == self._from_to:
                        editor_op_1 = self._tdb_filter.cellWidget(idx, 3)
                        editor_op_2 = self._tdb_filter.cellWidget(idx, 4)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_1.text(), True)
                        )
                        arg4 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_2.text(), True)
                        )
                    else:
                        editor_op_1 = self._tdb_filter.cellWidget(idx, 2)
                        arg2 = (
                            self.cursor()
                            .db()
                            .connManager()
                            .manager()
                            .formatValue(type_, editor_op_1.text(), True)
                        )

            if type_ == "serial":
                if cond_type == self._from_to:
                    editor_op_1 = self._tdb_filter.cellWidget(idx, 3)
                    editor_op_2 = self._tdb_filter.cellWidget(idx, 4)
                    arg2 = editor_op_1.value()
                    arg4 = editor_op_2.value()
                else:

                    editor_op_1 = flspinbox.FLSpinBox(self._tdb_filter.cellWidget(idx, 2))
                    arg2 = editor_op_1.value()

            if type_ == "date":
                util = flutil.FLUtil()
                if cond_type == self._from_to:
                    editor_op_1 = self._tdb_filter.cellWidget(idx, 3)
                    editor_op_2 = self._tdb_filter.cellWidget(idx, 4)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type_, util.dateDMAtoAMD(str(editor_op_1.text())))
                    )
                    arg4 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type_, util.dateDMAtoAMD(str(editor_op_2.text())))
                    )
                else:
                    editor_op_1 = self._tdb_filter.cellWidget(idx, 2)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(type_, util.dateDMAtoAMD(str(editor_op_1.text())))
                    )

            if type_ == "time":
                if cond_type == self._from_to:
                    editor_op_1 = self._tdb_filter.cellWidget(idx, 3)
                    editor_op_2 = self._tdb_filter.cellWidget(idx, 4)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(
                            type_, editor_op_1.time().toString(QtCore.Qt.DateFormat.ISODate)
                        )
                    )
                    arg4 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(
                            type_, editor_op_2.time().toString(QtCore.Qt.DateFormat.ISODate)
                        )
                    )
                else:
                    editor_op_1 = self._tdb_filter.cellWidget(idx, 2)
                    arg2 = (
                        self.cursor()
                        .db()
                        .connManager()
                        .manager()
                        .formatValue(
                            type_, editor_op_1.time().toString(QtCore.Qt.DateFormat.ISODate)
                        )
                    )

            if type_ in ("unlock", "bool"):
                editor_op_1 = self._tdb_filter.cellWidget(idx, 2)
                checked_ = False
                if editor_op_1.isChecked():
                    checked_ = True
                arg2 = self.cursor().db().connManager().manager().formatValue(type_, checked_)

            if where:
                where += " AND"

            cond_val = " " + _field_arg
            if arg2 is None:
                arg2 = ""
            if cond_type == self._contains:
                cond_val += " LIKE '%" + arg2.replace("'", "") + "%'"
            elif cond_type == self._starts:
                cond_val += " LIKE '" + arg2.replace("'", "") + "%'"
            elif cond_type == self._end:
                cond_val += " LIKE '%%" + arg2.replace("'", "") + "'"
            elif cond_type == self._equal:
                cond_val += " = " + str(arg2)
            elif cond_type == self._dist:
                cond_val += " <> " + str(arg2)
            elif cond_type == self._greater:
                cond_val += " > " + str(arg2)
            elif cond_type == self._less:
                cond_val += " < " + str(arg2)
            elif cond_type == self._from_to:
                cond_val += " >= " + str(arg2) + " AND " + _field_arg + " <= " + str(arg4)
            elif cond_type == self._null:
                cond_val += " IS NULL "
            elif cond_type == self._not_null:
                cond_val += " IS NOT NULL "

            where += cond_val

        return where

    def initFakeEditor(self) -> None:
        """
        Initialize a false and non-functional editor.

        This is used when the form is being edited with the designer and not
        You can display the actual editor for not having a connection to the database.
        Create a very schematic preview of the editor, but enough to
        See the position and approximate size of the actual editor.
        """
        if not self._fake_editor:
            self._fake_editor = QtWidgets.QTextEdit(self._tab_data)

            size_policy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding
            )
            size_policy.setHeightForWidth(True)

            self._fake_editor.setSizePolicy(size_policy)
            self._fake_editor.setTabChangesFocus(True)
            self._fake_editor.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            self.setFocusProxy(self._fake_editor)
            if not self._tab_data_layout:
                raise Exception("self._tab_data_layout is not defined!")
            self._tab_data_layout.addWidget(self._fake_editor)
            self.setTabOrder(self._fake_editor, self._line_edit_search)
            self.setTabOrder(self._fake_editor, self._combo_box_field_to_search_1)
            self._fake_editor.show()

            prty = ""
            if self._table_name:
                prty = prty + "tableName: %s\n" % self._table_name
            if self._foreign_field:
                prty = prty + "foreignField: %s\n" % self._foreign_field
            if self._field_relation:
                prty = prty + "fieldRelation: %s\n" % self._field_relation

            self._fake_editor.setText(prty)

    @decorators.pyqt_slot()
    @decorators.pyqt_slot(bool)
    @decorators.pyqt_slot(bool, bool)
    def refresh(self, *args) -> None:
        """
        Update the recordset.
        """
        refresh_head: bool = False
        refresh_data: bool = True

        if len(args) == 1:
            if isinstance(args[0], list):
                refresh_head = args[0][0]
                refresh_data = args[0][1]
            else:
                refresh_head = args[0]

        elif len(args) == 2:
            refresh_head = args[0]
            refresh_data = args[1]

        if not self.cursor() or not self._table_records:
            return

        table_metadata = self.cursor().private_cursor.metadata_
        if not table_metadata:
            return
        if not self._table_name:
            self._table_name = table_metadata.name()

        if self._check_column_enabled:
            if not self._check_column_visible:
                field_check = table_metadata.field(self._field_name_check_column)
                if field_check is None:
                    self._field_name_check_column = "%s_check_column" % table_metadata.name()

                    if self._field_name_check_column not in table_metadata.fieldNames():
                        field_check = pnfieldmetadata.PNFieldMetaData(
                            self._field_name_check_column,
                            self.tr(self._alias_check_column),
                            True,
                            False,
                            pnfieldmetadata.PNFieldMetaData.Check,
                            0,
                            False,
                            True,
                            True,
                            0,
                            0,
                            False,
                            False,
                            False,
                            None,
                            False,
                            None,
                            True,
                            False,
                            False,
                        )
                        table_metadata.addFieldMD(field_check)
                    else:
                        field_check = table_metadata.field(self._field_name_check_column)

                if field_check is None:
                    raise Exception("field_check is empty!")

                self.tableRecords().cur.model().updateColumnsCount()
                self.tableRecords().header().reset()
                self.tableRecords().header().swapSections(
                    self.tableRecords().column_name_to_column_index(field_check.name()),
                    self._sort_column_1,
                )
                self._check_column_visible = True
                self.setTableRecordsCursor()
                self._sort_column_1 = 1
                self._sort_column_2 = 2
                self._sort_column_3 = 3

                # for i in enumerate(buffer_.count()):
                #    buffer_.setGenerated(i, True)

        else:
            self.setTableRecordsCursor()
            self._sort_column_1 = 0
            self._sort_column_2 = 1
            self._sort_column_3 = 2
            self._check_column_visible = False

        if self._function_get_color:
            self._table_records.setFunctionGetColor(  # FIXME: no usar top_widget
                self._function_get_color, getattr(self._top_widget, "iface", None)
            )

        if refresh_head:
            if not self.tableRecords().header().isHidden():
                self.tableRecords().header().hide()

            model = self.cursor().model()
            for column in range(model.columnCount()):
                field = model.metadata().indexFieldObject(column)
                if not field.visibleGrid() or (
                    field.type() == "check" and not self._check_column_enabled
                ):
                    self._table_records.setColumnHidden(column, True)
                else:
                    self._table_records.setColumnHidden(column, False)

            if self._auto_sort_column:
                sort_list = []
                field_1 = self._table_records.visual_index_to_field(self._sort_column_1)
                field_2 = self._table_records.visual_index_to_field(self._sort_column_2)
                field_3 = self._table_records.visual_index_to_field(self._sort_column_3)

                if field_1 is not None:
                    sort_list.append(
                        "%s %s" % (field_1.name(), "ASC" if self._order_asc_1 else "DESC")
                    )
                if field_2 is not None:
                    sort_list.append(
                        "%s %s" % (field_2.name(), "ASC" if self._order_asc_2 else "DESC")
                    )
                if field_3 is not None:
                    sort_list.append(
                        "%s %s" % (field_3.name(), "ASC" if self._order_asc_3 else "DESC")
                    )

                id_mod = (
                    self.cursor()
                    .db()
                    .connManager()
                    .managerModules()
                    .idModuleOfFile("%s.mtd" % self.cursor().metadata().name())
                )
                function_qsa = "%s.tableDB_setSort_%s" % (id_mod, self.cursor().metadata().name())

                vars_: List[Any] = []
                vars_.append(sort_list)
                if field_1:
                    vars_.append(field_1.name())
                    vars_.append(self._order_asc_1)
                if field_2:
                    vars_.append(field_2.name())
                    vars_.append(self._order_asc_2)
                if field_3:
                    vars_.append(field_3.name())
                    vars_.append(self._order_asc_3)

                ret = application.PROJECT.call(function_qsa, vars_, None, False)
                LOGGER.debug("functionQsa: %s -> %r" % (function_qsa, ret))
                if ret and not isinstance(ret, bool):
                    if isinstance(ret, str):
                        ret = [ret]
                    if isinstance(ret, list):
                        sort_list = ret

                self._table_records.setSort(", ".join(sort_list))

            if model:
                if self._combo_box_field_to_search_1 is None:
                    raise Exception("comboBoxFieldSearch is not defined!")

                if self._combo_box_field_to_search_2 is None:
                    raise Exception("comboBoxFieldSearch2 is not defined!")

                try:
                    self._combo_box_field_to_search_1.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.putFirstCol
                    )
                    self._combo_box_field_to_search_2.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.putSecondCol
                    )
                except Exception:
                    LOGGER.error("Se ha producido un problema al desconectar")
                    return

                self._combo_box_field_to_search_1.clear()
                self._combo_box_field_to_search_2.clear()

                # cb1 = None
                # cb2 = None
                for column in range(model.columnCount()):
                    visual_column = self._table_records.header().logicalIndex(column)
                    if visual_column is not None:
                        field = model.metadata().indexFieldObject(visual_column)
                        if not field.visibleGrid():
                            continue
                        #    self._table_records.setColumnHidden(column, True)
                        # else:
                        self._combo_box_field_to_search_1.addItem(
                            model.headerData(
                                visual_column,
                                QtCore.Qt.Orientation.Horizontal,
                                QtCore.Qt.ItemDataRole.DisplayRole,
                            )
                        )
                        self._combo_box_field_to_search_2.addItem(
                            model.headerData(
                                visual_column,
                                QtCore.Qt.Orientation.Horizontal,
                                QtCore.Qt.ItemDataRole.DisplayRole,
                            )
                        )

                self._combo_box_field_to_search_1.addItem("*")
                self._combo_box_field_to_search_2.addItem("*")
                self._combo_box_field_to_search_1.setCurrentIndex(self._sort_column_1)
                self._combo_box_field_to_search_2.setCurrentIndex(self._sort_column_2)
                self._combo_box_field_to_search_1.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.putFirstCol
                )
                self._combo_box_field_to_search_2.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.putSecondCol
                )

            else:
                self._combo_box_field_to_search_1.addItem("*")
                self._combo_box_field_to_search_2.addItem("*")

            self._table_records.header().show()

        if refresh_data or self.sender():
            final_filter = self._filter
            if self._tdb_filter_last_where:
                if not final_filter:
                    final_filter = self._tdb_filter_last_where
                else:
                    final_filter = "%s AND %s" % (final_filter, self._tdb_filter_last_where)

            self._table_records.setPersistentFilter(final_filter)
            self._table_records.setShowAllPixmaps(self._show_all_pixmaps)
            self._table_records.refresh()

        if self._init_search:
            try:
                self._line_edit_search.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.filterRecords
                )
            except Exception:
                pass
            self._line_edit_search.setText(self._init_search)
            self._line_edit_search.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.filterRecords
            )
            self._line_edit_search.selectAll()
            self._init_search = None
            # self.seekCursor()

        if not self._read_only == self._req_read_only or (
            self._table_records and not self._read_only == self._table_records.flReadOnly()
        ):
            self.setReadOnly(self._req_read_only)

        if not self._edit_only == self._req_edit_only or (
            self._table_records and not self._edit_only == self._table_records.editOnly()
        ):
            self.setEditOnly(self._req_edit_only)

        if not self._insert_only == self._req_insert_only or (
            self._table_records and not self._insert_only == self._table_records.insertOnly()
        ):
            self.setInsertOnly(self._req_insert_only)

        if not self._only_table == self._req_only_table or (
            self._table_records and not self._only_table == self._table_records.onlyTable()
        ):
            self.setOnlyTable(self._req_only_table)

        if self._table_records and self._table_records.isHidden():
            self._table_records.show()

        # QtCore.QTimer.singleShot(50, self.setSortOrder)

    def refreshDelayed(self, msec: int = 5, refresh_data: bool = True) -> None:
        """
        Update the recordset with a delay.

        Accept a lapse of time in milliseconds, activating the internal _timer for
        to perform the final refresh upon completion of said lapse.

        @param msec Amount of lapsus time, in milliseconds.
        """

        self._refresh_data = refresh_data
        QtCore.QTimer.singleShot(msec, self.refreshDelayed2)
        # self.seekCursor()

    def refreshDelayed2(self) -> None:
        """Refresh the data when the time ends."""
        row = self.currentRow()
        self.refresh(True, self._refresh_data)
        self._refresh_data = False
        if row > -1:
            self.setCurrentRow(row)

    @decorators.pyqt_slot(bool)
    def insertRecord(self, wait: bool = True) -> None:
        """Call method FLSqlCursor.insertRecord."""

        widget = cast(QtWidgets.QWidget, self.sender())
        relation_lock = False
        cur_relation = self.cursor().cursorRelation()
        if cur_relation is not None:
            relation_lock = cur_relation.isLocked()

        if widget and (
            not self.cursor()
            or self._req_read_only
            or self._req_edit_only
            or self._req_only_table
            or relation_lock
        ):
            widget.setDisabled(True)
            return

        if self.cursor():
            self.cursor().insertRecord(wait)

    @decorators.pyqt_slot(bool)
    def editRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.editRecord.
        """
        widget = cast(QtWidgets.QWidget, self.sender())
        cur_relation = self.cursor().cursorRelation()

        if (
            widget
            and not isinstance(widget, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self._req_read_only
                or self._req_insert_only
                or self._req_only_table
                or (cur_relation is not None and cur_relation.isLocked())
            )
        ):
            widget.setDisabled(True)
            return

        if self.cursor():
            self.cursor().editRecord()

    @decorators.pyqt_slot(bool)
    def browseRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.browseRecord.
        """

        widget = cast(QtWidgets.QWidget, self.sender())

        if (
            widget
            and not isinstance(widget, fldatatable.FLDataTable)
            and (not self.cursor() or self._req_only_table)
        ):
            widget.setDisabled(True)
            return

        if self.cursor():
            self.cursor().browseRecord(wait)

    @decorators.pyqt_slot(bool)
    def deleteRecord(self, wait: bool = True) -> None:
        """
        Call method FLSqlCursor.deleteRecord.
        """
        widget = cast(QtWidgets.QWidget, self.sender())

        cur_relation = self.cursor().cursorRelation()

        if (
            widget
            and not isinstance(widget, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self._req_read_only
                or self._req_insert_only
                or self._req_edit_only
                or self._req_only_table
                or (cur_relation and cur_relation.isLocked())
            )
        ):
            widget.setDisabled(True)
            return

        if self.cursor():
            self.cursor().deleteRecord(wait)

    @decorators.pyqt_slot()
    def copyRecord(self) -> None:
        """
        Call method FLSqlCursor.copyRecord.
        """
        widget = cast(QtWidgets.QWidget, self.sender())

        cur_relation = self.cursor().cursorRelation()

        if (
            widget
            and not isinstance(widget, fldatatable.FLDataTable)
            and (
                not self.cursor()
                or self._req_read_only
                or self._req_edit_only
                or self._req_only_table
                or (cur_relation and cur_relation.isLocked())
            )
        ):
            widget.setDisabled(True)
            return

        if self.cursor():
            self.cursor().copyRecord()

    @decorators.pyqt_slot(int)
    @decorators.pyqt_slot(str)
    def putFirstCol(self, col: Union[int, str]) -> None:
        """
        Place the column first by passing the name of the field.

        This slot is connected to the search combo box
        of the component. When we select a field it is placed
        as the first column and the table is rearranged with this column.
        In this way we will always have the table sorted by
        the field in which we want to search.

        @param c Field name, this column exchanges its position with the first column
        @return False if the field does not exist
        @author Friday@xmarts.com.mx
        @author InfoSiAL, S.L.
        """
        if not self._table_records:
            raise Exception("_table_records is not defined!")

        col_index_: int
        if isinstance(col, str):
            col_index_ = self._table_records.logical_index_to_visual_index(
                self._table_records.column_name_to_column_index(col)
            )
        else:
            col_index_ = col

        _index = self._table_records.visual_index_to_column_index(col_index_)

        if _index is None or _index < 0:
            return
        self.moveCol(_index, self._sort_column_1)
        self._table_records.sortByColumn(
            self._sort_column_1,
            QtCore.Qt.SortOrder.AscendingOrder
            if self._order_asc_1
            else QtCore.Qt.SortOrder.DescendingOrder,
        )

    @decorators.pyqt_slot(int)
    @decorators.pyqt_slot(str)
    def putSecondCol(self, col: Union[int, str]) -> None:
        """
        Place the column as second by passing the name of the field.

        @author Silix - dpinelo
        """
        if not self._table_records:
            raise Exception("_table_records is not defined!")

        col_index_: int
        if isinstance(col, str):
            col_index_ = self._table_records.logical_index_to_visual_index(
                self._table_records.column_name_to_column_index(col)
            )
        else:
            col_index_ = col

        _index = self._table_records.visual_index_to_column_index(col_index_)

        if _index is None or _index < 0:
            return

        self.moveCol(_index, self._sort_column_2)

    def moveCol(self, from_: int, to_: int, first_search: bool = True) -> None:
        """
        Move a column from one source field to the column in another destination field.

        @param from Name of the source column field
        @param to_ Name of the destination column field
        @param first_search dpinelo: Indicates if columns are moved considering that this function
        called or not, from the main search and filtering combo
        """
        if from_ < 0 or to_ < 0:
            return

        table_metadata = self.cursor().metadata()
        if not table_metadata:
            return

        if not self._table_records:
            raise Exception("_table_records is not defined!")

        self._table_records.hide()

        text_search = self._line_edit_search.text()

        field = self.cursor().metadata().indexFieldObject(to_)

        if to_ == 0:  # Si ha cambiado la primera columna
            try:
                self._combo_box_field_to_search_1.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.putFirstCol
                )
            except Exception:
                LOGGER.error("Se ha producido un problema al desconectar")
                return

            self._combo_box_field_to_search_1.setCurrentIndex(from_)
            self._combo_box_field_to_search_1.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.putFirstCol
            )

            # Actializamos el segundo combo
            try:
                self._combo_box_field_to_search_2.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.putSecondCol
                )
            except Exception:
                pass
            # Falta mejorar
            if (
                self._combo_box_field_to_search_1.currentIndex()
                == self._combo_box_field_to_search_2.currentIndex()
            ):
                self._combo_box_field_to_search_2.setCurrentIndex(
                    self._table_records._h_header.logicalIndex(self._sort_column_1)
                )
            self._combo_box_field_to_search_2.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.putSecondCol
            )

        if to_ == 1:  # Si es la segunda columna ...
            try:
                self._combo_box_field_to_search_2.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.putSecondCol
                )
            except Exception:
                pass
            self._combo_box_field_to_search_2.setCurrentIndex(from_)
            self._combo_box_field_to_search_2.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.putSecondCol
            )

            if (
                self._combo_box_field_to_search_1.currentIndex()
                == self._combo_box_field_to_search_2.currentIndex()
            ):
                try:
                    self._combo_box_field_to_search_1.currentIndexChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                        self.putFirstCol
                    )
                except Exception:
                    pass
                if (
                    self._combo_box_field_to_search_1.currentIndex()
                    == self._combo_box_field_to_search_2.currentIndex()
                ):
                    self._combo_box_field_to_search_1.setCurrentIndex(
                        self._table_records._h_header.logicalIndex(self._sort_column_2)
                    )
                self._combo_box_field_to_search_1.currentIndexChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                    self.putFirstCol
                )

        if not text_search:
            text_search = self.cursor().valueBuffer(field.name())

        # self.refresh(True)

        if text_search:
            self.refresh(False, True)
            try:
                self._line_edit_search.textChanged.disconnect(  # type: ignore [attr-defined] # noqa: F821
                    self.filterRecords
                )
            except Exception:
                pass
            self._line_edit_search.setText(str(text_search))
            self._line_edit_search.textChanged.connect(  # type: ignore [attr-defined] # noqa: F821
                self.filterRecords
            )
            self._line_edit_search.selectAll()
            # self.seekCursor()
            QtCore.QTimer.singleShot(0, self._table_records.ensureRowSelectedVisible)
        else:
            self.refreshDelayed()

        self._table_records.header().swapSections(from_, to_)

        self.refresh(True, False)

    def setEnabled(self, enabled: bool) -> None:
        """
        Set read only True or False.
        """
        self.setReadOnly(not enabled)

    def setColumnWidth(self, field: str, weight: int) -> None:
        """
        Set the width of a column.

        @param field Name of the database field corresponding to the column
        @param w Column width
        """
        if self._table_records:
            self._table_records.setColWidth(field, weight)

    def setCurrentRow(self, row: int) -> None:
        """
        Select the indicated row.

        @param row Index of the row to select
        """
        if self._table_records:
            self._table_records.selectRow(row)
            self._table_records.scrollTo(self._table_records.cur.model().index(row, 0))

    @decorators.not_implemented_warn
    def columnWidth(self, col: int) -> None:
        """
        Return Column width.
        """
        pass

    @decorators.not_implemented_warn
    def setRowHeight(self, row: int, height: int) -> None:
        """
        Set the height of a row.

        @param row Row order number, starting at 0
        @param h High in the row
        """
        pass

    @decorators.not_implemented_warn
    def rowHeight(self, row: int) -> None:
        """
        Return height in the row.
        """
        pass

    def exportToOds(self) -> None:
        """
        Export to an ODS spreadsheet and view it.
        """
        if not self.cursor() or self.cursor().private_cursor.metadata_ is None:
            return

        cursor = pnsqlcursor.PNSqlCursor(self.cursor().curName())
        _filter = self.cursor().curFilter()
        if not _filter:
            _filter = "1 = 1"
        if self.cursor().sort():
            _filter += " ORDER BY %s" % self.cursor().sort()
        cursor.select(_filter)
        ods_enabled = True
        if settings.CONFIG.value("ebcomportamiento/FLTableExport2Calc", False):
            ods_enabled = False

        global_function_qsa = "flfactppal.exportFLTablesGranted"

        ret = application.PROJECT.call(global_function_qsa, [], None, False, None)
        if isinstance(ret, bool):
            ods_enabled = ret

        id_module = (
            self.cursor_.db()
            .managerModules()
            .idModuleOfFile("%s.mtd" % self.cursor_.metadata().name())
        )
        function_qsa = "%s.exportFLTableGranted_%s" % (id_module, self.cursor_.metadata().name())
        ret = application.PROJECT.call(function_qsa, [], None, False, None)
        if isinstance(ret, bool):
            ods_enabled = ret

        if not ods_enabled:
            QtWidgets.QMessageBox.information(
                QtWidgets.QApplication.activeModalWidget(),
                self.tr("Opción deshabilitada"),
                self.tr("Esta opción ha sido deshabilitada."),
                QtWidgets.QMessageBox.StandardButton.Ok,
            )
            return

        metadata = cursor.metadata()
        if not metadata:
            return

        table_records = self.tableRecords()
        if not hasattr(table_records, "cursor"):
            return

        # hor_header = table_records.horizontalHeader()
        title_style = [aqods.AQOdsStyle.Align_center, aqods.AQOdsStyle.Text_bold]
        border_bot = aqods.AQOdsStyle.Border_bottom
        border_right = aqods.AQOdsStyle.Border_right
        border_left = aqods.AQOdsStyle.Border_left
        italic = aqods.AQOdsStyle.Text_italic
        ods_gen = aqods.AQOdsGenerator()
        spread_sheet = aqods.AQOdsSpreadSheet(ods_gen)
        sheet = aqods.AQOdsSheet(spread_sheet, metadata.alias())
        tdb_num_rows = cursor.size()
        tdb_num_cols = len(metadata.fieldNames())

        util = flutil.FLUtil()
        id_pix = 0
        progress_dialog = util.createProgressDialog("Procesando", tdb_num_rows)
        util.setProgress(1)
        row = aqods.AQOdsRow(sheet)
        row.addBgColor(aqods.aq_ods_color(0xE7E7E7))
        for idx in range(tdb_num_cols):
            field = metadata.indexFieldObject(table_records.visual_index_to_metadata_index(idx))
            if field is not None and field.visibleGrid():
                row.opIn(title_style)
                row.opIn(border_bot)
                row.opIn(border_left)
                row.opIn(border_right)
                row.opIn(field.alias())

        row.close()

        # cur = table_records.cursor()
        # cur_row = table_records.currentRow()

        cursor.first()

        for idx_row in range(tdb_num_rows):
            if progress_dialog.wasCanceled():
                break

            row = aqods.AQOdsRow(sheet)
            for idx_col in range(tdb_num_cols):
                # idx = table_records.indexOf(c)  # Busca si la columna se ve
                # if idx == -1:
                #    continue

                field = metadata.indexFieldObject(
                    table_records.visual_index_to_metadata_index(idx_col)
                )
                if field is not None and field.visibleGrid():
                    val = cursor.valueBuffer(field.name())
                    if field.type() == "double":
                        row.setFixedPrecision(metadata.fieldPartDecimal(field.name()))
                        row.opIn(float(val))

                    elif field.type() == "date":
                        if val is not None:
                            val = str(val)
                            if val.find("T") > -1:
                                val = val[0 : val.find("T")]

                            row.opIn(val)
                        else:
                            row.coveredCell()

                    elif field.type() in ("bool", "unlock"):
                        str_ = self.tr("Sí") if val else self.tr("No")
                        row.opIn(italic)
                        row.opIn(str_)

                    elif field.type() == "pixmap":
                        if val:
                            if val.find("cacheXPM") > -1:
                                pix = QtGui.QPixmap(val)
                                if not pix.isNull():

                                    pix_name = "pix%s_" % id_pix
                                    id_pix += 1
                                    row.opIn(
                                        aqods.AQOdsImage(
                                            pix_name,
                                            round((pix.width() * 2.54) / 98, 2) * 20,
                                            round((pix.height() * 2.54) / 98, 2) * 20,
                                            0,
                                            0,
                                            val,
                                        )
                                    )
                                else:
                                    row.coveredCell()

                            else:
                                row.coveredCell()
                        else:
                            row.coveredCell()

                    else:
                        if isinstance(val, list):
                            val = ",".join(val)

                        if val:
                            row.opIn(str(val))
                        else:
                            row.coveredCell()
            row.close()
            if not idx_row % 4:
                util.setProgress(idx_row)

            cursor.next()

        # cur.seek(cur_row)
        sheet.close()
        spread_sheet.close()

        util.setProgress(tdb_num_rows)
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        file_name = "%s/%s%s.ods" % (
            application.PROJECT.tmpdir,
            metadata.name(),
            QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz"),
        )
        ods_gen.generateOds(file_name)
        if not application.PROJECT.debug_level == 1000:  # test
            sysbasetype.SysBaseType.openUrl(file_name)

        QtWidgets.QApplication.restoreOverrideCursor()
        util.destroyProgressDialog()

    def switchSortOrder(self, col: int = 0) -> None:
        """
        Switch the direction of the table records sorting, from ascending to descending and vice versa.

        Records are always sorted by the first column.
        If the autoSortColumn property is TRUE.
        """
        if not self._auto_sort_column:
            return
        if self._table_records:
            if self._table_records.logical_index_to_visual_index(
                col
            ) == self._table_records.visual_index_to_column_index(self._sort_column_1):

                self._order_asc_1 = not self._order_asc_1

            self.setSortOrder(self._order_asc_1, self._sort_column_1)

    @decorators.pyqt_slot(str)
    def filterRecords(self, chr_: str) -> None:
        """
        Filter the records in the table using the first field, according to the given pattern.

        This slot is connected to the component search text box,
        taking the content of this as a standard for filtering.

        @param chr_ Character string with filtering pattern
        """
        if not self.cursor().model:
            return
        base_filter: Any = None
        if not self._table_records:
            LOGGER.warning("FLTableDB %s has no tablerecords defined!", self.objectName())
            return

        refresh_data = False
        msec_refresh = 200

        valid_idx = self._table_records.visual_index_to_column_index(
            self._sort_column_1
        )  # corrige posición con ocultos.
        colidx = self._table_records.visual_index_to_metadata_index(
            valid_idx
        )  # posicion en metadata.

        if colidx is None:
            raise Exception("Unexpected: Column not found")
        field = self.cursor().model().metadata().indexFieldObject(colidx)
        base_filter = (
            (self.cursor().db().connManager().manager().formatAssignValueLike(field, chr_, True))
            if chr_
            else None
        )

        id_module = (
            self.cursor()
            .db()
            .connManager()
            .managerModules()
            .idModuleOfFile("%s.mtd" % self.cursor().metadata().name())
        )
        function_qsa = "tableDB_filterRecords_" + self.cursor().metadata().name()

        vargs = []
        vargs.append(self.cursor().metadata().name())
        vargs.append(chr_)
        vargs.append(field.name())
        vargs.append(base_filter)

        iface = qsadictmodules.from_project(id_module).iface
        func_ = getattr(iface, function_qsa, None)
        if func_:
            LOGGER.debug("function_qsa:%s.%s:", (id_module, function_qsa))
            ret = func_(*vargs)

            if ret is not isinstance(ret, bool):
                base_filter = ret

        self.refreshDelayed(msec_refresh, refresh_data)
        self._filter = base_filter or ""

    def setSortOrder(
        self, ascending: Union[bool, int] = True, col_order: Optional[int] = None
    ) -> None:
        """Set sort columns order."""
        if isinstance(ascending, int):
            ascending = ascending == 1

        order = (
            QtCore.Qt.SortOrder.AscendingOrder if ascending else QtCore.Qt.SortOrder.DescendingOrder
        )

        col = col_order if col_order is not None else self._sort_column_1

        if col == 0:
            self._order_asc_1 = ascending
        elif col == 1:
            self._order_asc_2 = ascending
        elif col == 2:
            self._order_asc_3 = ascending

        if self._table_records:
            while True:

                column = self._table_records.header().logicalIndex(col)
                if not self._table_records.isColumnHidden(column):
                    break
                col += 1

            self._table_records.sortByColumn(column, order)

    def isSortOrderAscending(self) -> bool:
        """Return if the order of the first column is ascending."""

        return self._order_asc_1

    def setActionName(self, name: str):
        """Set action Name to the cursor (deprecated)."""
        pass

    def activeTabData(self) -> None:
        """
        Activate the data table.
        """

        if self._tab_filter is not None:
            self._tab_filter.hide()
        if self._tab_data is not None:
            self._tab_data.show()
        self.refreshTabData()

    def activeTabFilter(self) -> None:
        """
        Activate the filter table.
        """

        if self._tab_data is not None:
            self._tab_data.hide()
        if self._tab_filter is not None:
            self._tab_filter.show()
        self.refreshTabFilter()

    def tdbFilterClear(self) -> None:
        """
        Clean and initialize the filter.
        """
        if not self._top_widget:
            return

        self._tab_filter_loader = False
        self.refreshTabFilter()

    """
    Señal emitida cuando se refresca por cambio de filtro
    """
    refreshed = QtCore.pyqtSignal()

    """
    Señal emitida cuando se establece si el componente es o no de solo lectura.
    """
    readOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece si el componente es o no de solo edición.
    """
    editOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece si el componente es o no de solo inserción.
    """
    insertOnlyChanged = QtCore.pyqtSignal(bool)

    """
    Señal emitida cuando se establece cambia el registro seleccionado.
    """
    currentChanged = QtCore.pyqtSignal()

    def primarysKeysChecked(self) -> List[Any]:
        """Return a list of the primary keys checked."""
        return self.tableRecords().primarysKeysChecked()

    def clearChecked(self) -> None:
        """Empty the list of primary keys checked."""

        self.tableRecords().clearChecked()

    def setPrimaryKeyChecked(self, name: str, checked: bool) -> None:
        """Set a primary key cheked and add to the cheked list."""

        self.tableRecords().setPrimaryKeyChecked(name, checked)
