# -*- coding: utf-8 -*-
"""PNAction Module."""

from pineboolib.core.utils.struct import ActionStruct
from pineboolib import logging
from typing import Union, Any

LOGGER = logging.get_logger(__name__)


class PNAction(object):
    """
    PNAction Class.

    This class contains information on actions to open forms.

    It is used to automatically link forms with your script,
    interface and source table.

    @author InfoSiAL S.L.
    """

    """
    Nombre de la accion
    """
    _name: str

    """
    Nombre del script asociado al formulario de edición de registros
    """
    _script_form_record: str

    """
    Nombre del script asociado al formulario maestro
    """
    _script_form: str

    """
    Nombre de la tabla origen para el formulario maestro
    """
    _table: str

    """
    Nombre del formulario maestro
    """
    _form: str

    """
    Nombre del formulario de edición de registros
    """
    _form_record: str

    """
    Texto para la barra de título del formulario maestro
    """
    _caption: str

    """
    Descripción
    """
    _description: str

    """
    Class
    """
    _class: str

    def __init__(self, action: Union[str, ActionStruct]) -> None:
        """Initialize."""

        self._name = ""
        self._caption = ""
        self._description = ""
        self._form = ""
        self._form_record = ""
        self._script_form = ""
        self._script_form_record = ""
        self._table = ""
        self._class = ""

        if isinstance(action, str):
            self.setName(action)

        elif isinstance(action, ActionStruct):
            self.setName(action._name)
            self.setScriptForm(action._master_script)
            self.setScriptFormRecord(action._record_script)
            self.setForm(action._master_form)
            self.setFormRecord(action._record_form)
            self.setCaption(action._alias)
            self.setTable(action._table)
        else:
            raise Exception("Unsupported action %r" % action)

    def __repr__(self):
        """Return the values ​​in a text string."""

        return self._name

    def __str__(self):
        """Return the values ​​in a text string."""

        return self._name

    def __eq__(self, other: Any) -> bool:
        """Return compare result."""

        if isinstance(other, str):
            return self._name == other
        else:
            return self is other

    def setName(self, name: str) -> None:
        """Set the name of the action."""

        self._name = name

    def setScriptFormRecord(self, script_form_record: str) -> None:
        """Set the name of the script associated with the record editing form."""

        self._script_form_record = "%s.qs" % script_form_record if script_form_record else ""

    def setScriptForm(self, script_form: str) -> None:
        """Set the name of the script associated with the master form."""

        self._script_form = "%s.qs" % script_form if script_form else ""

    def setTable(self, table: str) -> None:
        """Set the name of the source table of the master form."""

        self._table = table

    def setClass_(self, class_: str) -> None:
        """Set the name of class script."""

        self._class = class_ if class_ else ""

    def setForm(self, form: str) -> None:
        """Set the name of the master form."""

        self._form = "%s.ui" % form if form else ""

    def setFormRecord(self, form_record: str) -> None:
        """Set the name of the record editing form."""

        self._form_record = "%s.ui" % form_record if form_record else ""

    def setCaption(self, caption: str) -> None:
        """Set the text of the title bar of the master form."""

        self._caption = caption

    def setDescription(self, description: str) -> None:
        """Set description."""

        self._description = description

    def name(self) -> str:
        """Get the name of the action."""

        return self._name

    def scriptFormRecord(self) -> str:
        """Get the name of the script associated with the record editing form."""

        return self._script_form_record

    def scriptForm(self) -> str:
        """Get the name of the script associated with the master form."""

        return self._script_form

    def table(self) -> str:
        """Get the table associated with the action."""

        return self._table

    def caption(self) -> str:
        """Get the text from the form's title bar."""

        return self._caption

    def description(self) -> str:
        """Get the description."""

        return self._description

    def form(self) -> str:
        """Get the name of the mestro form."""

        return self._form

    def formRecord(self) -> str:
        """Get the name of the record editing form."""

        return self._form_record

    def class_(self) -> str:
        """Get class script."""

        return self._class
