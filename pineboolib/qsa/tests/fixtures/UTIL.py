"""Util module."""

# -*- coding: utf-8 -*-
# Translated with pineboolib 1.0.2.52
from typing import Any
from pineboolib.qsa.qsa import *  # noqa: F403
from pineboolib.qsa import qsa
from pineboolib.application.utils import modules
import os

# /** @file */


# /** @class_declaration ifaceCtx */
class ifaceCtx(qsa.ObjectClass):
    """ifaceCtx class."""

    ctx: Any = None

    def __init__(self, context):
        """Just a comment."""
        self.ctx = context


# /** @class_declaration FormInternalObj */
class FormInternalObj(qsa.FormDBWidget):
    """FormInternalObj class."""

    codePath_: Any = None
    dependencies_: Any = None
    cacheClases_ = {}
    bloqueoIntervalo_: Any = None
    delegateCommitActivo_: Any = None
    cacheDecimales_: Any = None
    iface: "ifaceCtx"

    # /** @class_definition FormInternalObj */
    def _class_init(self):
        """Just a comment."""
        self.iface = ifaceCtx(self)

    # /** @class_definition getDependencies */
    def getDependencies(self):
        """Just a comment."""
        if not self.dependencies_:
            self.dependencies_ = self.buildDependencies()
        return self.dependencies_

    # /** @class_definition buildDependencies */
    def buildDependencies(self):
        """Just a comment."""
        return qsa.AttributeDict(
            {
                "test": (os.path.join(os.path.dirname(__file__), "test_require.qs")),
            }
        )

    # /** @class_definition getCodePath */
    def getCodePath(self):
        """Just a comment."""
        qsa.debug("getCodePath")
        path: Any = qsa.AQUtil.readSettingEntry(qsa.ustr("application/codepath/", qsa.sys.nameBD()))
        qsa.debug(qsa.ustr("getCodePath path ", path))
        self.codePath_ = path if path else None
        return self.codePath_

    # /** @class_definition loadScript */
    def loadScript(self, path):
        """Just a comment."""
        codigo: Any = None

        codigo = qsa.FileStatic.read(path)
        if not codigo:
            file_name: str = path.split("/").pop()

            codigo = qsa.AQUtil.sqlSelect(
                "flfiles", "contenido", qsa.ustr("nombre = '", file_name, "'")
            )
            if not codigo:
                error: Any = qsa.sys.translate("No se encontró contenido para el fichero %s") % (
                    str(file_name)
                )
                raise Exception(error)

        return codigo

    # /** @class_definition require */
    def require_(self, class_name):
        """Just a comment."""
        if class_name in self.cacheClases_.keys():
            return self.cacheClases_[class_name]
        path: Any = self.getDependencies()[class_name]

        if not path:
            error: Any = qsa.sys.translate("No se encontró el path para la clase %s") % (
                str(class_name)
            )
            raise Exception(error)

        self.cacheClases_[class_name] = self.loadModule(self.loadScript(path))

        return self.cacheClases_[class_name]

    def loadModule(self, data: str) -> Any:
        """Just a comment."""
        list_data = data.split("\n")
        class_name = list_data[len(list_data) - 1]
        new_data = "\n".join(list_data[:-1])

        mod_ = modules.text_to_module(new_data)
        class_ = getattr(mod_, class_name, None)
        return class_

    # /** @class_definition copiaRegistroEnTransaccion */
    def copiaRegistroEnTransaccion(self, curOrigen, paramCopia, curDestino, curPadreDestino):
        """Just a comment."""
        oParam: Any = qsa.AttributeDict(
            {
                "curOrigen": (curOrigen),
                "paramCopia": (paramCopia),
                "curDestino": (curDestino),
                "curPadreDestino": (curPadreDestino),
            }
        )
        if not qsa.sys.runTransaction(copiaRegistro, oParam):
            return False
        valorPk: Any = oParam["valorPk"]
        return valorPk

    # /** @class_definition delegateCommitActivo */
    def delegateCommitActivo(self):
        """Just a comment."""
        _i = qsa.from_project("formUTIL")
        if not _i.delegateCommitActivo_:
            _i.delegateCommitActivo_ = (
                "SI"
                if (qsa.AQUtil.readSettingEntry("application/delegateCommit") == "true")
                else "NO"
            )
        return _i.delegateCommitActivo_ == "SI"

    # /** @class_definition jsonToString */
    def jsonToString(self, o):
        """Just a comment."""
        _i: Any = qsa.from_project("formUTIL")
        s: Any = None
        tipo: Any = qsa.typeof_(o)
        if tipo == "string":
            s = qsa.ustr('"', o, '"')
        else:
            if tipo == "number":
                s = qsa.parseString(o)
            else:
                if tipo == "object":
                    if o is None:
                        s = "null"
                    else:
                        if hasattr(o, "length") or "length" in o:
                            s = "["
                            i: Any = 0
                            while_pass = True
                            while i < qsa.length(o):
                                if not while_pass:
                                    i += 1
                                    while_pass = True
                                    continue
                                while_pass = False
                                if i > 0:
                                    s += ", "
                                s += _i.jsonToString(o[i])
                                i += 1
                                while_pass = True
                                try:
                                    i < qsa.length(o)
                                except Exception:
                                    break

                            s += "]"

                        else:
                            if hasattr(o, "toString") or "toString" in o:
                                s = qsa.ustr('"', qsa.parseString(o), '"')
                            else:
                                s = "{"
                                j: Any = 0
                                # DEBUG:: FOR-IN: ['m', 'o']
                                for m in o:
                                    if j > 0:
                                        s += ", "
                                    s += qsa.ustr('"', m, '" : ', _i.jsonToString(o[m]))
                                    j += 1

                                s += "}"

                else:
                    if tipo == "boolean":
                        s = "true" if o else "false"
                    else:
                        qsa.debug(qsa.ustr("Error intentando parsear tipo ", tipo))
                        qsa.debug(o)

        return s

    # /** @class_definition nameUser */
    def nameUser(self):
        """Just a comment."""
        if qsa.parseString(qsa.sys.interactiveGUI()) == "Pinebooapi":
            return qsa.from_project("formAPI").user_id()
        else:
            return qsa.sys.nameUser()

    # /** @class_definition copiaRegistro */
    def copiaRegistro(self, oParam):
        """Just a comment."""
        curOrigen: Any = oParam["curOrigen"]
        paramCopia: Any = oParam["paramCopia"]
        curDestino: Any = False
        if hasattr(oParam, "curDestino") or "curDestino" in oParam:
            curDestino = oParam["curDestino"]
        curPadreDestino: Any = False
        if hasattr(oParam, "curPadreDestino") or "curPadreDestino" in oParam:
            curPadreDestino = oParam["curPadreDestino"]
        if not curOrigen:
            return False
        valorPk: Any = copiaCamposRegistro(curOrigen, paramCopia, curDestino, curPadreDestino)
        if not valorPk:
            return False
        if not copiaRegistrosHijos(curOrigen, curDestino, paramCopia):
            return False
        oParam["valorPk"] = valorPk
        return valorPk

    # /** @class_definition copiaCamposRegistro */
    def copiaCamposRegistro(self, curOrigen, paramCopia, curDestino, curPadreDestino):
        """Just a comment."""
        oCampos: Any = paramCopia["campos"]
        campoPadre: Any = False
        campoHijo: Any = False
        if (hasattr(paramCopia, "campohijo") or "campohijo" in paramCopia) and (
            hasattr(paramCopia, "campopadre") or "campopadre" in paramCopia
        ):
            campoHijo = paramCopia["campohijo"]
            campoPadre = paramCopia["campopadre"]
        tabla: Any = curOrigen.table()
        if not curDestino:
            curDestino = qsa.FLSqlCursor(curOrigen.table())
        curDestino.setModeAccess(curDestino.Insert)
        curDestino.refreshBuffer()
        aCampos: Any = qsa.AQUtil.nombreCampos(tabla)
        totalCampos: Any = aCampos[0]
        campo: Any = None
        i: Any = 1
        while_pass = True
        while i <= totalCampos:
            if not while_pass:
                i += 1
                while_pass = True
                continue
            while_pass = False
            campo = aCampos[i]
            if campoHijo and campo == campoHijo:
                curDestino.setValueBuffer(campoHijo, curPadreDestino.valueBuffer(campoPadre))
                continue
            if hasattr(oCampos, campo) or campo in oCampos:
                if not copiaCampoRegistro(curOrigen, curDestino, campo, oCampos[campo]):
                    return False
            else:
                qsa.from_project("formUI").ponMsgError(
                    qsa.sys.translate("El campo '%s' no está en el esquema de copia de la tabla %s")
                    % (str(campo), str(tabla))
                )
                return False

            i += 1
            while_pass = True
            try:
                i <= totalCampos
            except Exception:
                break

        valorPk: Any = curDestino.valueBuffer(
            qsa.from_project("formMETA").damePrimaryKeyDeTabla(tabla)
        )
        if not curDestino.commitBuffer():
            return False
        return valorPk

    # /** @class_definition copiaCampoRegistro */
    def copiaCampoRegistro(self, curOrigen, curDestino, campo, paramCopiaCampo):
        """Just a comment."""
        accionCopia: Any = paramCopiaCampo["accion"]
        if accionCopia == "copy":
            if curOrigen.isNull(campo):
                curDestino.setNull(campo)
            else:
                curDestino.setValueBuffer(campo, curOrigen.valueBuffer(campo))

        else:
            if accionCopia == "pass":
                return True
            else:
                if accionCopia == "calc":
                    if hasattr(paramCopiaCampo, "funcion") or "funcion" in paramCopiaCampo:
                        funcion: Any = paramCopiaCampo["funcion"]
                        valor: Any = funcion(curOrigen, curDestino, campo)
                        curDestino.setValueBuffer(campo, valor)
                    else:
                        qsa.from_project("formUI").ponMsgError(
                            qsa.sys.translate(
                                "El campo '%s' tiene un tipo de copia calc pero no tiene definida la función de copia"
                            )
                            % (str(campo))
                        )
                        return False

                else:
                    if accionCopia == "fixed":
                        if hasattr(paramCopiaCampo, "valor") or "valor" in paramCopiaCampo:
                            valor: Any = paramCopiaCampo["valor"]
                            curDestino.setValueBuffer(campo, valor)
                        else:
                            qsa.from_project("formUI").ponMsgError(
                                qsa.sys.translate(
                                    "El campo '%s' tiene un tipo de copia fixed pero no tiene definido el valor fijo a copiar"
                                )
                                % (str(campo))
                            )
                            return False

        return True

    # /** @class_definition copiaRegistrosHijos */
    def copiaRegistrosHijos(self, curOrigen, curDestino, paramCopia):
        """Just a comment."""
        oHijos: Any = None
        if hasattr(paramCopia, "hijos") or "hijos" in paramCopia:
            oHijos = paramCopia["hijos"]
        else:
            return True

        # DEBUG:: FOR-IN: ['hijo', 'oHijos']
        for hijo in oHijos:
            if not copiaRegistrosHijo(curOrigen, curDestino, oHijos[hijo]):
                return False
        return True

    # /** @class_definition copiaRegistrosHijo */
    def copiaRegistrosHijo(self, curOrigen, curDestino, oHijo):
        """Just a comment."""
        tablaHijo: Any = oHijo["tabla"]
        campoPadre: Any = oHijo["campopadre"]
        campoHijo: Any = oHijo["campohijo"]
        curHijoOrigen: Any = qsa.FLSqlCursor(tablaHijo)
        curHijoDestino: Any = qsa.FLSqlCursor(tablaHijo)
        curHijoOrigen.select(
            qsa.from_project("formMETA").dameClausulaWhere(
                tablaHijo, campoHijo, curOrigen.valueBuffer(campoPadre)
            )
        )
        while curHijoOrigen.next():
            curHijoOrigen.setModeAccess(curHijoOrigen.Browse)
            curHijoOrigen.refreshBuffer()
            oParam: Any = qsa.AttributeDict(
                {
                    "curOrigen": (curHijoOrigen),
                    "paramCopia": (oHijo),
                    "curDestino": (curHijoDestino),
                    "curPadreDestino": (curDestino),
                }
            )
            if not copiaRegistro(oParam):
                return False

        return True

    # /** @class_definition convierteStringHexEnFicheroBin */
    def convierteStringHexEnFicheroBin(self, stringHex, rutaFichero):
        """Just a comment."""
        baS: Any = qsa.QByteArray(qsa.length(stringHex))
        j: Any = 0
        while_pass = True
        while j < qsa.length(stringHex):
            if not while_pass:
                j += 1
                while_pass = True
                continue
            while_pass = False
            baS.set(j, ord(stringHex[j]))
            j += 1
            while_pass = True
            try:
                j < qsa.length(stringHex)
            except Exception:
                break

        ba: Any = qsa.QByteArray(baS.fromHex())
        if not guardaByteArrayEnFichero(ba, rutaFichero):
            return False
        return True

    # /** @class_definition guardaByteArrayEnFichero */
    def guardaByteArrayEnFichero(self, ba, rutaFichero):
        """Just a comment."""
        file: Any = qsa.File(rutaFichero)
        file.open(qsa.FileStatic.WriteOnly)
        j: Any = 0
        while_pass = True
        while j < ba.size:
            if not while_pass:
                j += 1
                while_pass = True
                continue
            while_pass = False
            file.writeByte(ba.get(j))
            j += 1
            while_pass = True
            try:
                j < ba.size
            except Exception:
                break

        file.close()
        return True

    # /** @class_definition dameTextoMes */
    def dameTextoMes(self, mesNumero, abreviado):
        """Just a comment."""
        if not mesNumero or mesNumero == "":
            return ""
        if qsa.length(qsa.parseString(mesNumero)) == 1:
            mesNumero = qsa.ustr("0", mesNumero)
        mesTexto: Any = mesNumero
        if mesNumero == "01":
            mesTexto = "Enero"
            if abreviado:
                mesTexto = "Ene"
        else:
            if mesNumero == "02":
                mesTexto = "Febrero"
                if abreviado:
                    mesTexto = "Feb"
            else:
                if mesNumero == "03":
                    mesTexto = "Marzo"
                    if abreviado:
                        mesTexto = "Mar"
                else:
                    if mesNumero == "04":
                        mesTexto = "Abril"
                        if abreviado:
                            mesTexto = "Abr"
                    else:
                        if mesNumero == "05":
                            mesTexto = "Mayo"
                            if abreviado:
                                mesTexto = "May"
                        else:
                            if mesNumero == "06":
                                mesTexto = "Junio"
                                if abreviado:
                                    mesTexto = "Jun"
                            else:
                                if mesNumero == "07":
                                    mesTexto = "Julio"
                                    if abreviado:
                                        mesTexto = "Jul"
                                else:
                                    if mesNumero == "08":
                                        mesTexto = "Agosto"
                                        if abreviado:
                                            mesTexto = "Ago"
                                    else:
                                        if mesNumero == "09":
                                            mesTexto = "Septiembre"
                                            if abreviado:
                                                mesTexto = "Sep"
                                        else:
                                            if mesNumero == "10":
                                                mesTexto = "Octubre"
                                                if abreviado:
                                                    mesTexto = "Oct"
                                            else:
                                                if mesNumero == "11":
                                                    mesTexto = "Noviembre"
                                                    if abreviado:
                                                        mesTexto = "Nov"
                                                else:
                                                    if mesNumero == "12":
                                                        mesTexto = "Diciembre"
                                                        if abreviado:
                                                            mesTexto = "Dic"

        return mesTexto

    # /** @class_definition redondea */
    def redondea(self, v, tabla, campo):
        """Just a comment."""
        clave: Any = qsa.ustr(tabla, "_", campo)
        decimales: Any = None
        if not self.cacheDecimales_:
            self.cacheDecimales_ = qsa.Object()
        if hasattr(self.cacheDecimales_, clave) or clave in self.cacheDecimales_:
            decimales = self.cacheDecimales_[clave]
        else:
            mgr_: Any = qsa.from_project("flfactppal").iface.managerDB()
            mtdT: Any = mgr_.metadata(tabla)
            mtdF: Any = mtdT.field(campo)
            decimales = mtdF.partDecimal()
            self.cacheDecimales_[clave] = decimales

        potencia10: Any = qsa.Math.pow(10, decimales)
        res: Any = v * potencia10
        if res > 0:
            s: Any = qsa.parseString(res)
            res = qsa.parseFloat(res)
            res = qsa.Math.floor(res)
            posPunto: Any = s.find(".")
            if posPunto > 0:
                dec1 = s[posPunto + 1]
                if qsa.parseInt(dec1) >= 5:
                    res += 1

        else:
            s: Any = qsa.parseString(res)
            res = qsa.parseFloat(res)
            res = qsa.Math.ceil(res)
            posPunto: Any = s.find(".")
            if posPunto > 0:
                dec1 = s[posPunto + 1]
                if qsa.parseInt(dec1) >= 5:
                    res -= 1

        res = res / potencia10
        return res

    # /** @class_definition redondeaDecimales */
    def redondeaDecimales(self, v, decimales):
        """Just a comment."""
        potencia10: Any = qsa.Math.pow(10, decimales)
        res: Any = v * potencia10
        if res > 0:
            s: Any = qsa.parseString(res)
            res = qsa.parseFloat(res)
            res = qsa.Math.floor(res)
            posPunto: Any = s.find(".")
            if posPunto > 0:
                dec1 = s[posPunto + 1]
                if qsa.parseInt(dec1) >= 5:
                    res += 1

        else:
            s: Any = qsa.parseString(res)
            res = qsa.parseFloat(res)
            res = qsa.Math.ceil(res)
            posPunto: Any = s.find(".")
            if posPunto > 0:
                dec1 = s[posPunto + 1]
                if qsa.parseInt(dec1) >= 5:
                    res -= 1

        res = res / potencia10
        return res

    # /** @class_definition anyoBisiesto */
    def anyoBisiesto(self, anyo):
        """Just a comment."""
        res: Any = None
        res = False
        if (anyo % 4) == 0:
            res = True
            if (anyo % 100) == 0:
                res = False
                if anyo == 0:
                    res = True

        return res

    # /** @class_definition gestionIntervalo */
    def gestionIntervalo(self, cursor, fN, aCampos):
        """Just a comment."""
        if qsa.from_project("formUTIL").bloqueoIntervalo_:
            return
        desde: Any = 0
        hasta: Any = 1
        intervalo: Any = 2
        if fN != aCampos[desde] and fN != aCampos[hasta] and fN != aCampos[intervalo]:
            return
        qsa.from_project("formUTIL").bloqueoIntervalo_ = True
        for case in qsa.switch(fN):
            if case(aCampos[intervalo]):
                intervalo: Any = qsa.from_project("flfactppal").iface.pub_calcularIntervalo(
                    cursor.valueBuffer(aCampos[intervalo])
                )
                cursor.setValueBuffer(aCampos[desde], intervalo.desde)
                cursor.setValueBuffer(aCampos[hasta], intervalo.hasta)
                break

            if case(aCampos[desde]):
                pass
            if case(aCampos[hasta]):
                cursor.setValueBuffer(aCampos[intervalo], "")
                cursor.setNull(aCampos[intervalo])
                break

        qsa.from_project("formUTIL").bloqueoIntervalo_ = False

    # /** @class_definition revisarIntervalo */
    def revisarIntervalo(self, cursor, aCampos):
        """Just a comment."""
        desde: Any = 0
        hasta: Any = 1
        codIntervalo: Any = 2
        cursor.setModeAccess(cursor.Edit)
        cursor.refreshBuffer()
        if cursor.valueBuffer(aCampos[codIntervalo]):
            intervalo: Any = qsa.Array()
            intervalo = qsa.from_project("flfactppal").iface.pub_calcularIntervalo(
                cursor.valueBuffer(aCampos[codIntervalo])
            )
            cursor.setValueBuffer(aCampos[desde], intervalo.desde)
            cursor.setValueBuffer(aCampos[hasta], intervalo.hasta)
            cursor.commitBuffer()

    # /** @class_definition validaDUA */
    def validaDUA(self, valor):
        """Just a comment."""
        if valor != "" and qsa.length(valor) != 18:
            return False
        return True

    # /** @class_definition nextCounter */
    def nextCounter(self, field, table):
        """Just a comment."""
        fieldMetadata: Any = qsa.from_project("formMETA").getFieldMetadata(table, field)
        fieldLength: Any = qsa.length(fieldMetadata)
        where: Any = qsa.ustr("LENGTH(", field, ") = ", fieldLength)
        maxValue: Any = qsa.AQUtil.sqlSelect(
            table, field, qsa.ustr(where, " ORDER BY ", field, " DESC")
        )
        nextValue: Any = (
            qsa.Math.round(qsa.parseFloat((0 if (maxValue is False) else maxValue))) + 1
        )
        return qsa.from_project("formSTR").padStart(qsa.parseString(nextValue), fieldLength, "0")
