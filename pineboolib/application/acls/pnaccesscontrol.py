# -*- coding: utf-8 -*-
r"""
Base class for Access Controls, also called Access Control Rules.

An access control rule applies to a user and a high-level object or container
(main windows, tables, etc.), which in turn will contain other objects (actions, fields, etc.).
The rule is defined by the following information as its header, which identifies it
uniquely:

\\ code

         kind           ; first name         ; user           ; permission
-------------------------------------------------- ------------------------------------------------
PNAccessControl :: type; PNAccessControl :: name; PNAccessControl :: user; PNAccessControl :: perm

\\ endcode

The type will be that of the high level object, the name will be that of the object, the user will correspond to the
name of the user in the database to which the rule applies and permission will be an identifier
of text that defines the type of permission attributed to the object for the given user. This permission
It is general or global and will be applied by default to all child objects that belong to the object
high level.

At the same time a rule may have a list of Access Control Objects (called ACOs,
Access Control Objects), to which you want to apply a permission other than the general one. The ACOs will be
child objects or belonging to the high level object. Internally the list of ACOs is composed of
tuples of two elements; 'object name' and 'permission', the object name will be the one assigned
within the hierarchy of objects belonging to the high level object and permission will be the permission for that
object and that will overwrite the general permit.

The values ​​of the rule can be set from a DOM node of a DOM / XML document, using
PNAccessControl :: set. Reciprocally you can obtain a DOM node with the content of the rule,
to insert into a DOM / XML document, using PNAccessControl :: get. The general XML structure of the DOM node
which represents an access control rule is as follows:

\\ code

<[mainwindow, table, etc ..] perm = 'XXX'>
  <name> XXX </name>
  <user> XXX </user>
  <aco perm = 'XXX'> XXX </aco>
  ....
  <aco perm = 'XXX'> XXX </aco>
 </ [mainwindow, table, etc ..]>

\\ endcode

For convenience, the PNAccessControl :: setAcos method is also provided, which allows you to establish the list of
ACOs of a rule directly from a list of text strings.

This class is not intended to be used directly, but as a basis for derived classes that are
specifically responsible for processing high-level objects. An example would be PNAccessControlMainWindow,
which is responsible for access control for high-level objects of type 'mainwindow', ie main windows,
as the module selector, or each of the main windows of the modules.

@author InfoSiAL S.L.
"""


from typing import List, Dict, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from PyQt6 import QtXml, QtWidgets  # pragma: no cover
    from pineboolib.application.metadata import pntablemetadata  # pragma: no cover


class PNAccessControl(object):
    """PNAccessControl Class."""

    """
    Almacena el nombre del objeto de alto nivel.
    """

    _name: str
    """
    Almacena el nombre del usuario de la base de datos.
    """
    _user: str
    """
    Almacena el permiso general de la regla de control de acceso.
    """
    _perm: str

    """
    Diccionario de permisos específicos de los ACOs (Access Control Objects)
    hijos o pertenecientes al objeto de alto nivel. El diccionario almacena la
    correspondencia entre el nombre del ACO (utilizado como clave de búsqueda)
    y el permiso a aplicar.
    """
    _acos_perms: Dict[str, str]

    def __init__(self) -> None:
        """Initialize."""
        self._name = ""
        self._user = ""
        self._perm = ""
        self._acos_perms = {}

    def __del__(self) -> None:
        """Remove values ​​when closed."""

        self._acos_perms.clear()
        del self._acos_perms

    def name(self) -> str:
        """
        Get the name of the high level object.

        @return Text string with the name of the object.
        """

        return self._name

    def user(self) -> str:
        """
        Get the name of the database user.

        @return Text string with the user's name (login).
        """

        return self._user

    def perm(self) -> str:
        """
        Get general permission.

        @return Text string that identifies the permission to apply.
        """

        return self._perm

    def setName(self, name: str) -> None:
        """
        Set the name of the high level object.

        @param n Object name.
        """

        self._name = name

    def setUser(self, user: str) -> None:
        """
        Set the name of the database user.

        @param u Name (login) of the user.
        """

        self._user = user

    def setPerm(self, perm: str) -> None:
        """
        Set the general permission.

        @param p Text string with the permission identifier.
        """

        self._perm = perm

    def clear(self) -> None:
        """
        Clean the rule by emptying it and freeing all resources.
        """

        self._name = ""
        self._user = ""
        self._perm = ""

        self._acos_perms.clear()

    def type(self) -> str:
        """
        Return a text constant that identifies the type.

        This function must be reimplemented in the derived classes that are
        responsible for processing a specific object type and return the relevant identifier

        @return A text string that identifies the general object type of the rule, eg "table".
        """

        return ""

    def set(self, element: Optional["QtXml.QDomElement"]) -> None:
        """
        Define the access control rule from the information of a DOM node of a given DOM / XML document.

        @param e Element corresponding to the DOM node that will be used to define the rule.
        """

        if element is None:
            return

        self._acos_perms.clear()

        self._perm = element.attribute("perm")
        node = element.firstChild()

        while not node.isNull():
            node_elem = node.toElement()
            if not node_elem.isNull():
                tag_name = node_elem.tagName()
                if tag_name == "name":
                    self._name = node_elem.text()

                elif tag_name == "user":
                    self._user = node_elem.text()

                elif tag_name == "aco":
                    self._acos_perms[node_elem.text()] = node_elem.attribute("perm")

            node = node.nextSibling()

    def get(self, document: Optional["QtXml.QDomDocument"]) -> None:
        """
        From the content of the access control rule create a DOM node.

        This will be inserted as child of the first node of a DOM / XML document.

        @param d DOM / XML document where the node built from the access control rule will be inserted.
        """

        if document is None:
            return  # type: ignore [unreachable] # noqa: F821

        type_ = self.type()
        if not type_:
            return

        root = document.firstChild().toElement()
        element = document.createElement(type_)
        element.setAttribute("perm", self._perm)
        root.appendChild(element)

        name_element = document.createElement("name")
        name_element.appendChild(document.createTextNode(self._name))
        element.appendChild(name_element)

        user_element = document.createElement("user")
        user_element.appendChild(document.createTextNode(self._user))
        element.appendChild(user_element)

        for key in self._acos_perms.keys():
            aco_element = document.createElement("aco")
            aco_element.setAttribute("perm", self._acos_perms[key])
            aco_element.appendChild(document.createTextNode(key))
            element.appendChild(aco_element)

    def setAcos(self, acos: List[str]) -> None:
        """
        Set the list of Acos from a list of text strings.

        This list of texts must have in their order components the names of the objects, and in the
        odd order components the permission to apply to that object, eg: "pbOpen", "r-", "lblText", "-", "tbErase", "rw", ...

        @param acos List of text strings with objects and permissions.
        """

        self._acos_perms.clear()
        i = 0
        while i < len(acos):
            self._acos_perms[acos[i]] = acos[i + 1]
            i += 2

    def getAcos(self) -> List[str]:
        """
        Get a list of text strings corresponding to the list of ACOs set.

        The format of this list is the same as described in PNAccessControl :: setAcos
        eg 'pbOpen', 'r-', 'lblText', '--', 'tbErase', 'rw', ...

        @return List of text strings with objects and permissions.
        """

        acos = []

        for key, value in self._acos_perms.items():
            acos.append(key)
            acos.append(value)

        return acos

    def processObject(
        self,
        obj: Union["QtWidgets.QMainWindow", "QtWidgets.QWidget", "pntablemetadata.PNTableMetaData"],
    ) -> None:
        """Process object overload function."""

        return None
