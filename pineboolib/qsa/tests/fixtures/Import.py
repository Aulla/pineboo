"""Import module."""

# -*- coding: utf-8 -*-
# Translated with pineboolib 0.99.70
from typing import Any, Dict
from pineboolib.qsa import qsa
from pineboolib.application.utils import modules


# /** @file */

# /** @class_declaration ifaceCtx */
class ifaceCtx(qsa.ObjectClass):
    """ifaceCtx class."""

    ctx: Dict[str, Any]

    def __init__(self, context):
        """Just a comment."""
        self.ctx = context


# /** @class_declaration FormInternalObj */
class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    cacheClases_: Any = {}
    base: str = ""
    iface: "ifaceCtx"

    # /** @class_definition FormInternalObj */
    def _class_init(self):
        """Just a comment."""
        self.iface = ifaceCtx(self)
        self.base = qsa.AQUtil.readSettingEntry(qsa.ustr("application/codepath/", qsa.sys.nameBD()))
        self.cacheClases_ = {}

    def loadCode(self, filePath: str, fullPath: str = "") -> str:
        """Just a comment."""
        codigo: Any = None
        try:
            file_ = open(filePath, "r", encoding="UTF-8")
            codigo = file_.read()
            file_.close()
        except Exception as error:
            raise Exception("No se pudo importar el fichero %s\n:%s" % (filePath, str(error)))

        return codigo

    def getExportByRegexp(self, code: str, re):
        """Just a comment."""
        pos: Any = re.find("code")
        if pos != -1:
            return re.capturedTexts[1]
        return None

    def evaluateCode(self, code: str) -> Any:
        """Just a comment."""
        list_data = code.split("\n")
        idx = 0
        class_name = None
        while not class_name:
            idx -= 1
            class_name = list_data[idx]

        new_data = "\n".join(list_data[:idx])

        mod_ = modules.text_to_module(new_data)
        print("*", class_name, mod_.__name__)

        class_ = getattr(mod_, class_name, None)
        return class_

    def from_(self, filePath: str, fullPath: str = ""):
        """Just a comment."""
        codigo: Any = self.loadCode(filePath, fullPath)
        try:
            evaluado: Any = self.evaluateCode(codigo)
            self.cacheClases_[filePath] = {
                "code": (codigo),
                "evaluado": (evaluado),
            }

        except Exception as error:
            raise Exception("No se pudo parsear el fichero %s\n:%s" % (filePath, str(error)))

        return self.cacheClases_[filePath]["evaluado"]
