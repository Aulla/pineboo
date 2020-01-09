# -*- coding: utf-8 -*-
"""
PNAccessControlList Module.

Manage access lists to limit the application to users..
"""
from PyQt5 import QtCore, QtXml

from pineboolib.application.database import pnsqlquery
from . import pnaccesscontrolfactory

from pineboolib import logging
from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from . import pnaccesscontrol  # noqa : F401


LOGGER = logging.getLogger(__name__)


class PNAccessControlLists(object):
    """PNAccessControlList Class."""

    """
    Nombre que identifica la lista de control de acceso actualmente establecida.

    Generalmente corresponderá con el identificador del registro de la tabla "flacls" que se utilizó para crear "acl.xml".
    """
    _name: Optional[str]

    """
    Diccionario (lista) que mantiene los objetos de las reglas de control de acceso establecidas.
    La clave que identifica a cada objeto está formada por el siguiente literal:

    \\code

    PNAccessControl::type + "::" + PNAccessControl::name + "::" + PNAccessControl::user

    \\endcode
    """

    _access_control_list: Dict[str, "pnaccesscontrol.PNAccessControl"]

    def __init__(self):
        """Initialize the class."""

        self._name = None
        self._access_control_list = {}

    def __del__(self) -> None:
        """Process when destroying the class."""

        if self._access_control_list:
            self._access_control_list.clear()
            del self._access_control_list

    def name(self) -> Optional[str]:
        """
        Return the name that identifies the currently established access control list.

        @return Name the current access control list.
        """
        return self._name

    def init(self, _acl_xml: str = None) -> None:
        """
        Read the file "acl.xml" and establish a new access control list.

        If the file "acl.xml" cannot be read, the access control list is empty and
        no access control will be processed on any object.

        @param _acl_xml XML content with the definition of the access control list.
        """
        if _acl_xml is None:
            from pineboolib import application

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")

            _acl_xml = application.PROJECT.conn_manager.managerModules().content("acl.xml")

        doc = QtXml.QDomDocument("ACL")
        if self._access_control_list:
            self._access_control_list.clear()

        if _acl_xml and not doc.setContent(_acl_xml):
            QtCore.qWarning(
                "PNAccessControlList : " + QtCore.QObject().tr("Lista de control de acceso errónea")
            )
            return

        self._access_control_list = {}
        # self._access_control_list.setAutoDelete(True)

        doc_elem = doc.documentElement()
        no = doc_elem.firstChild()

        while not no.isNull():
            e = no.toElement()
            if e:
                if e.tagName() == "name":
                    self._name = e.text()
                    no = no.nextSibling()
                    continue

                ac = pnaccesscontrolfactory.PNAccessControlFactory().create(e.tagName())
                if ac:
                    ac.set(e)
                    self._access_control_list["%s::%s::%s" % (ac.type(), ac.name(), ac.user())] = ac
                    no = no.nextSibling()
                    continue

            no = no.nextSibling()

    def process(self, obj: Any) -> None:
        """
        Process a high-level object according to the established access control list.

        @param obj High-level object to which access control is applied. It must be or inherit from the QObject class.
        """

        if obj is None or not self._access_control_list:
            return

        if not self._access_control_list:
            return
        type_ = pnaccesscontrolfactory.PNAccessControlFactory().type(obj)
        name = ""

        if hasattr(obj, "name"):
            name = obj.name()
        elif hasattr(obj, "objectName"):
            name = obj.objectName()

        from pineboolib import application

        if application.PROJECT.conn_manager is None:
            raise Exception("Project is not connected yet")

        user = application.PROJECT.conn_manager.mainConn().user()
        if type_ == "" or name == "" or user == "":
            return

        key = "%s::%s::%s" % (type_, name, user)
        if key in self._access_control_list.keys():
            self._access_control_list[key].processObject(obj)

    def install_acl(self, idacl: str) -> None:
        """
        Create a new file "acl.xml" and store it replacing the previous one, if it exists.

        @param idacl Record identifier of the "flacls" table to use to create "acl.xml".
        """
        doc = QtXml.QDomDocument("ACL")

        root = doc.createElement("ACL")
        doc.appendChild(root)

        name = doc.createElement("name")
        root.appendChild(name)
        text_node = doc.createTextNode(idacl)
        name.appendChild(text_node)

        qry = pnsqlquery.PNSqlQuery()

        qry.setTablesList("flacs")
        qry.setSelect("idac,tipo,nombre,iduser,idgroup,degrupo,permiso")
        qry.setFrom("flacs")
        qry.setWhere("idacl='%s'" % idacl)
        qry.setOrderBy("prioridad DESC, tipo")
        qry.setForwardOnly(True)

        if qry.exec_():
            # step = 0
            # progress = util.ProgressDialog(util.tr("Instalando control de acceso..."), None, q.size(), None, None, True)
            # progress.setCaption(util.tr("Instalando ACL"))
            # progress.setMinimumDuration(0)
            # progress.setProgress(++step)
            while qry.next():
                self.make_rule(qry, doc)
                # progress.setProgress(++step)

            from pineboolib import application

            if application.PROJECT.conn_manager is None:
                raise Exception("Project is not connected yet")

            application.PROJECT.conn_manager.managerModules().setContent(
                "acl.xml", "sys", doc.toString()
            )

    def make_rule(self, qry: pnsqlquery.PNSqlQuery, dom_document: QtXml.QDomDocument) -> None:
        """
        Create the corresponding DOM node (s) to a record in the "flacs" table.

        Use PNAccessControlLists :: makeRuleUser or PNAccessControlLists :: makeRuleGroup depending on whether the registry
        to which the query points indicates that the rule is for a user or a group. If the record indicates a
        user will create a user rule, if you indicate a group a user rule will be created for each of
        Group member users.

        @param q Query about the "flacs" table positioned in the register to be used to construct the rule (s).
        @param d DOM / XML document in which you will insert the node (s) that describe the access control rule (s).
        """
        if not qry or not dom_document:
            return

        if qry.value(5):
            self.make_rule_group(qry, dom_document, str(qry.value(4)))
        else:
            self.make_rule_user(qry, dom_document, str(qry.value(3)))

    def make_rule_user(
        self, qry: pnsqlquery.PNSqlQuery, dom_document: QtXml.QDomDocument, iduser: str
    ) -> None:
        """
        Create a DOM node corresponding to a record in the "flacs" table and for a given user.

        @param q Query about the "flacs" table positioned in the register to be used to construct the rule.
        @param d DOM / XML document in which you will insert the node that describes the access control rule.
        @param iduser Identifier of the user used in the access control rule.
        """
        if not iduser or not qry or not dom_document:
            return

        ac = pnaccesscontrolfactory.PNAccessControlFactory().create(str(qry.value(1)))
        if ac:
            ac.setName(str(qry.value(2)))
            ac.setUser(iduser)
            ac.setPerm(str(qry.value(6)))

            qAcos = pnsqlquery.PNSqlQuery()
            qAcos.setTablesList("flacos")
            qAcos.setSelect("nombre,permiso")
            qAcos.setFrom("flacos")
            qAcos.setWhere("idac ='%s'" % qry.value(0))
            qAcos.setForwardOnly(True)

            acos = []

            if qAcos.exec_():
                while qAcos.next():
                    acos.append(str(qAcos.value(0)))
                    acos.append((qAcos.value(1)))

            ac.setAcos(acos)
            ac.get(dom_document)

    def make_rule_group(
        self, qry: pnsqlquery.PNSqlQuery, dom_document: QtXml.QDomDocument, idgroup: str = ""
    ) -> None:
        """
        Create several DOM nodes corresponding to a record in the "flacs" table and for a specific user group.

        The function of this method is to create a rule for each of the group member users, using
        PNAccessControlLists :: makeRuleUser.

        @param q Query about the "flacs" table positioned in the register to use to build the rules.
        @param d DOM / XML document in which the nodes that describe the access control rules will be inserted.
        @param idgroup Identifier of the user group.
        """
        if idgroup == "" or not qry or not dom_document:
            return

        qry_users = pnsqlquery.PNSqlQuery()

        qry_users.setTablesList("flusers")
        qry_users.setSelect("iduser")
        qry_users.setFrom("flusers")
        qry_users.setWhere("idgroup='%s'" % idgroup)
        qry_users.setForwardOnly(True)

        if qry_users.exec_():
            while qry_users.next():
                self.make_rule_user(qry, dom_document, str(qry_users.value(0)))
