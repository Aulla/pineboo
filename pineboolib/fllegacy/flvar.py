# -*- coding: utf-8 -*-
"""
Module for FLVar.

Store user variables in database.

Those variables are per session, so they are not shared even for same user.
"""

from pineboolib.application.database import utils
from pineboolib import application


from typing import Any


class FLVar(object):
    """Store user variables in database."""

    def set(self, name: str, value: Any) -> bool:
        """Save a variable to database."""
        from pineboolib.application.database import pnsqlquery

        id_sesion = application.ID_SESSION
        where = "idvar = '%s' AND idsesion ='%s'" % (name, id_sesion)

        qry = pnsqlquery.PNSqlQuery()
        qry.setTablesList("flvar")
        qry.setSelect("id")
        qry.setFrom("flvar")
        qry.setWhere(where)
        qry.setForwardOnly(True)

        if not qry.exec_():
            return False
        if qry.next():
            return utils.sql_update("flvar", "valor", str(value), "id='%s'" % str(qry.value(0)))

        values = "%s,%s,%s" % (name, id_sesion, str(value))
        return utils.sql_insert("flvar", "idvar,idsesion,valor", values)

    def get(self, name: str) -> Any:
        """Get variable from database."""
        id_sesion = application.PROJECT.aq_app.timeUser()
        where = "idvar = '%s' AND idsesion ='%s'" % (name, id_sesion)
        return utils.sql_select("flvar", "valor", where, "flvar")

    def del_(self, name: str) -> bool:
        """Delete variable from database."""
        id_sesion = application.PROJECT.aq_app.timeUser()
        where = "idvar = '%s' AND idsesion ='%s'" % (name, id_sesion)
        return utils.sql_delete("flvar", where)

    def clean(self) -> bool:
        """Clean variables for this session."""
        id_sesion = application.PROJECT.aq_app.timeUser()
        where = "idsesion = '%s'" % id_sesion
        return utils.sql_delete("flvar", where)
