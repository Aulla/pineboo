# -*- coding: utf-8 -*-
"""
AQSobjectsFactory Module.

This module provides the different classes and AQS functions to be used in the module scripts.
"""
from pineboolib.core.utils.utils_base import is_deployed as __is_deployed
from pineboolib.core.utils.utils_base import is_library as __is_library

# AQSObjects
from pineboolib.fllegacy.aqsobjects.aqsettings import AQSettings  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsqlquery import AQSqlQuery  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsqlcursor import AQSqlCursor  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqutil import AQUtil  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsql import AQSql  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsmtpclient import AQSmtpClient  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqs import AQS  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqboolflagstate import (  # noqa: F401
    AQBoolFlagState,
    AQBoolFlagStateList,
)
from pineboolib.fllegacy.aqsobjects.aqformdb import aq_form_db as AQFormDB  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqssproject import AQSSProject  # noqa: F401
from pineboolib.fllegacy.aqsobjects.aqsbuttongroup import AQSButtonGroup  # noqa: F401


if (
    not __is_deployed() and not __is_library()
):  # FIXME: No module named 'xml.sax.expatreader' in deploy
    from pineboolib.fllegacy.aqsobjects.aqods import (  # noqa: F401
        AQOdsGenerator,
        AQOdsSpreadSheet,
        AQOdsSheet,
        AQOdsRow,
    )
    from pineboolib.fllegacy.aqsobjects.aqods import AQOdsStyle, AQOdsImage  # noqa: F401
    from pineboolib.fllegacy.aqsobjects.aqods import aq_ods_color as AQOdsColor  # noqa: F401
