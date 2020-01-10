# -*- coding: utf-8 -*-
"""
Module for FLVar.

Store user variables in database.

Those variables are per session, so they are not shared even for same user.
"""

from pineboolib.application.database import utils
from pineboolib.fllegacy import flapplication

from PyQt5 import QtCore  # type: ignore
from typing import Any


class FLVar(object):
    """Store user variables in database."""

    def set(self, n: str, v: Any) -> bool:
        """Save a variable to database."""
        from pineboolib.application.database.pnsqlquery import PNSqlQuery

        id_sesion = flapplication.aqApp.timeUser().toString(QtCore.Qt.ISODate)
        where = "idvar = '%s' AND idsesion ='%s'" % (n, id_sesion)

        qry = PNSqlQuery()
        qry.setTablesList("flvar")
        qry.setSelect("id")
        qry.setFrom("flvar")
        qry.setWhere(where)
        qry.setForwardOnly(True)

        if not qry.exec_():
            return False
        if qry.next():
            return utils.sql_update("flvar", "valor", str(v), "id='%s'" % str(qry.value(0)))

        values = "%s,%s,%s" % (n, id_sesion, str(v))
        return utils.sql_insert("flvar", "idvar,idsesion,valor", values)

    def get(self, name: str) -> Any:
        """Get variable from database."""
        id_sesion = flapplication.aqApp.timeUser().toString(QtCore.Qt.ISODate)
        where = "idvar = '%s' AND idsesion ='%s'" % (name, id_sesion)
        return utils.sql_select("flvar", "valor", where, "flvar")

    def del_(self, name: str) -> bool:
        """Delete variable from database."""
        id_sesion = flapplication.aqApp.timeUser().toString(QtCore.Qt.ISODate)
        where = "idvar = '%s' AND idsesion ='%s'" % (name, id_sesion)
        return utils.sql_delete("flvar", where)

    def clean(self) -> bool:
        """Clean variables for this session."""
        id_sesion = flapplication.aqApp.timeUser().toString(QtCore.Qt.ISODate)
        where = "idsesion = '%s'" % id_sesion
        return utils.sql_delete("flvar", where)
