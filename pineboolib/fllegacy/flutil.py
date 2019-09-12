"""Flutil module."""
# -*- coding: utf-8 -*-
import hashlib
import datetime

from PyQt5 import QtCore  # type: ignore

from pineboolib.application.qsatypes.sysbasetype import SysBaseType
from pineboolib.core import decorators
from pineboolib import logging

from typing import List, Optional, Union, Any, TYPE_CHECKING
from pineboolib.application.types import Date

if TYPE_CHECKING:
    from PyQt5.QtXml import QDomDocument  # type: ignore
    from pineboolib.application.database.pnsqlcursor import PNSqlCursor  # noqa: F401

logger = logging.getLogger(__name__)


class FLUtil(QtCore.QObject):
    """
    Class with methods, tools and tools necessary for certain operations.

    Is this class generic methods that
    perform very specific operations but that
    they are necessary for certain usual processes
    in the different tasks to perform in management
    business.

    @author InfoSiAL S.L.
    """

    vecUnidades: List[str] = [
        "",
        "uno",
        "dos",
        "tres",
        "cuatro",
        "cinco",
        "seis",
        "siete",
        "ocho",
        "nueve",
        "diez",
        "once",
        "doce",
        "trece",
        "catorce",
        "quince",
        "dieciseis",
        "diecisiete",
        "dieciocho",
        "diecinueve",
        "veinte",
        "veintiun",
        "veintidos",
        "veintitres",
        "veinticuatro",
        "veinticinco",
        "veintiseis",
        "veintisiete",
        "veintiocho",
        "veintinueve",
    ]

    vecDecenas: List[str] = [
        "",
        "",
        "",
        "treinta",
        "cuarenta",
        "cincuenta",
        "sesenta",
        "setenta",
        "ochenta",
        "noventa",
    ]
    vecCentenas: List[str] = [
        "",
        "ciento",
        "doscientos",
        "trescientos",
        "cuatrocientos",
        "quinientos",
        "seiscientos",
        "setecientos",
        "ochocientos",
        "novecientos",
    ]

    # @staticmethod
    # def deleteCascade(collector, field, sub_objs, using) -> None:  # FIXME TIPEADO
    #    for o in sub_objs:
    #        try:
    #            from pineboolib.application.database.pnsqlcursor import PNSqlCursor

    #            cursor = PNSqlCursor(field.model._meta.db_table)
    #            cursor.select(field.model._meta.pk.name + "=" + str(o.pk))
    #            if cursor.next():
    #                cursor.setModeAccess(cursor.Del)
    #                if not cursor.commitBuffer():
    #                    raise Exception(
    #                        "No pudo eliminar "
    #                        + str(field.model._meta.db_table)
    #                        + " : "
    #                        + str(o.pk)
    #                    )
    #        except Exception:
    #            raise Exception(
    #                "No pudo eliminar " + str(field.model._meta.db_table) + " : " + str(o.pk)
    #            )

    @staticmethod
    def partInteger(n: float) -> int:
        """
        Return the integer part of a number.

        Given a number returns the corresponding integer, that is,
        figures on the left side of the decimal point.

        @param n Number to get the whole part from. Must be positive
        @return The whole part of the number, which can be zero
        """
        i, d = divmod(n, 1)
        return int(i)

    @staticmethod
    def partDecimal(n: float) -> int:
        """
        Return the decimal part of a number.

        Given a number returns the corresponding decimal part, that is,
        figures on the right side of the decimal point
        @param n Number from which to obtain the decimal part. Must be positive
        @return The decimal part of the number, which can be zero
        """
        i, d = divmod(n, 1)
        d = round(d, 2)
        d = d * 100
        return int(d)

    @classmethod
    def unidades(cls, n: int) -> str:
        """
        Statement of the units of a number.

        @param n Number to deal with. Must be positive.
        """
        if n >= 0:
            return cls.vecUnidades[n]
        else:
            raise ValueError("Parameter 'n' must be a positive integer")

    @staticmethod
    @decorators.NotImplementedWarn
    def utf8(s: str) -> str:
        """
        Return a string to utf-8 encoding.

        @param s: Chain
        @return String in UTF-8 format
        """
        return s

    @classmethod
    def centenamillar(cls, n: int) -> str:
        """
        Statement of the hundreds of thousands of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""
        if n < 0:
            raise ValueError("Param n must be positive integer")
        if n < 10000:
            buffer = cls.decenasmillar(n)
            return buffer

        buffer = cls.centenas(n / 1000)
        buffer = buffer + " mil "
        buffer = buffer + cls.centenas(n % 1000)

        return buffer

    @classmethod
    def decenas(cls, n: Union[int, float]) -> str:
        """
        Statement of the tens of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""

        if n < 0:
            raise ValueError("Param n must be positive integer")
        if n < 30:
            buffer = cls.unidades(int(n))
        else:
            buffer = cls.vecDecenas[cls.partInteger(n / 10)]
            if n % 10:
                buffer = buffer + " y "
                buffer = buffer + cls.unidades(int(n % 10))

        return buffer

    @classmethod
    def centenas(cls, n: Union[int, float]) -> str:
        """
        Statement of the hundreds of a number.

        @param n Number to deal with. It must be positive.
        """
        buffer = ""
        if n < 0:
            raise ValueError("Param n must be positive integer")
        if n == 100:
            buffer = "cien"

        elif n < 100:
            buffer = cls.decenas(int(n))
        else:
            buffer = buffer + cls.vecCentenas[cls.partInteger(n / 100)]
            buffer = buffer + " "
            buffer = buffer + cls.decenas(int(n % 100))

        return buffer

    @classmethod
    def unidadesmillar(cls, n: int) -> str:
        """
        Statement of the thousand units of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""
        if n < 1000:
            buffer = ""

        if n / 1000 == 1:
            buffer = "mil "

        if n / 1000 > 1:
            buffer = cls.unidades(int(n / 1000))
            buffer = buffer + " mil "

        buffer = buffer + cls.centenas(int(n % 1000))

        return buffer

    @classmethod
    def decenasmillar(cls, n: int) -> str:
        """
        Statement of tens of thousands of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""
        if n < 10000:
            buffer = cls.unidadesmillar(n)
            return buffer

        buffer = cls.decenas(n / 1000)
        buffer = buffer + " mil "
        buffer = buffer + cls.centenas(int(n % 10000))
        return buffer

    @classmethod
    def enLetra(cls, n: int) -> str:
        """
        Return the expression in text of how a number is stated, in Spanish.

        Given an integer, return its expression in text as it is
        speaks in a spoken way; for example given the number 130,
        will return the text string "one hundred and thirty".

        @param n Number to be transferred to your spoken form. Must be positive
        @return Text string with its spoken expression.
        """
        buffer = ""
        if n > 1000000000:
            buffer = "Sólo hay capacidad hasta mil millones"
            return buffer

        if n < 1000000:
            buffer = cls.centenamillar(int(n))
            return buffer
        else:
            if n / 1000000 == 1:
                buffer = "un millon"
            else:
                buffer = cls.centenas(int(n / 1000000))
                buffer = buffer + " millones "

        buffer = buffer + cls.centenamillar(int(n % 1000000))
        return buffer.upper()

    @classmethod
    @decorators.BetaImplementation
    def enLetraMoneda(cls, n: Union[int, str, float], m: str) -> str:
        """
        Return the expression in text of how a monetary amount is stated, in Spanish and in any currency indicated.

        Given a double number, it returns its expression in text as it is
        state in spoken form in the indicated currency; for example given the number 130.25,
        will return the text string "one hundred thirty 'currency' with twenty-five cents".

        @param n Number to be transferred to your spoken form. Must be positive
        @param m Currency name
        @return Text string with its spoken expression.
        """
        if isinstance(n, str):
            n = float(n)

        nTemp = n * -1.00 if n < 0.00 else n
        entero = cls.partInteger(nTemp)
        decimal = cls.partDecimal(nTemp)
        res = ""

        if entero > 0:
            res = cls.enLetra(entero) + " " + m

        if entero > 0 and decimal > 0:
            # res += QString(" ") + QT_TR_NOOP("con") + " " + enLetra(decimal) + " " + QT_TR_NOOP("céntimos");
            res += " " + "con" + " " + cls.enLetra(decimal) + " " + "céntimos"

        if entero <= 0 and decimal > 0:
            # res = enLetra(decimal) + " " + QT_TR_NOOP("céntimos");
            res = cls.enLetra(decimal) + " " + "céntimos"

        if n < 0.00:
            # res = QT_TR_NOOP("menos") + QString(" ") + res;
            res = "menos" + " " + res

        return res.upper()

    @classmethod
    @decorators.BetaImplementation
    def enLetraMonedaEuro(cls, n: int) -> str:
        """
        Return the expression in text of how a monetary amount is stated, in Spanish and in Euros.

        Given a double number, it returns its expression in text as it is
        states in a spoken way in euros; for example given the number 130.25,
        will return the text string "one hundred thirty euros with twenty-five cents".

        @param n Number to be transferred to your spoken form. Must be positive
        @return Text string with its spoken expression.
        """
        # return enLetraMoneda(n, QT_TR_NOOP("euros"));
        return cls.enLetraMoneda(n, "euros")

    @classmethod
    def letraDni(cls, n: int) -> str:
        """
        Return the letter associated with the number of the D.N.I. Spanish.

        @param n Number of D.N.I
        @return Character associated with the number of D.N.I
        """
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letras[n % 23]

    @classmethod
    def nombreCampos(cls, tablename: str) -> List[Union[str, int]]:
        """
        Return the list of field names from the specified table.

        The first string in the list contains the number of fields in the table

        @param table. Table name.
        @return Field List.
        """

        from pineboolib.fllegacy.flapplication import aqApp

        campos = aqApp.db().manager().metadata(tablename).fieldNames()
        return [len(campos)] + campos

    @classmethod
    def calcularDC(cls, n: int) -> str:
        """
        Return the control digit number, for bank accounts.

        The current account numbers are organized as follows:

        4 Digits -----> Bank code (ex. 0136 Spanish Arab Bank)
        4 Digits -----> Office Code
        1 Control digit ------> of the first 8 digits
        1 Control digit ------> of the account number (of the last 10 digits)
        10 Digits of the account number

        To check the account number, the first 8 digits are passed first
        obtaining the first control digit, then the 10 digits are passed
        of the account number obtaining the second check digit.

        @param n Number from which the check digit must be obtained
        @return Character with the check digit associated with the given number
        """

        Tabla: List[int] = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]

        DC = None
        Suma = 0
        nDigitos = len(str(n)) - 1

        ct = 1

        while ct <= len(str(n)):
            valor_tabla: int = Tabla[nDigitos]
            valor_n = str(n)[ct - 1]
            Suma += valor_tabla * int(valor_n)
            nDigitos = nDigitos - 1
            ct = ct + 1

        DC = 11 - (Suma % 11)
        if DC == 11:
            DC = 0
        elif DC == 10:
            DC = 1

        char = chr(DC + 48)
        return char

    @classmethod
    def dateDMAtoAMD(cls, f) -> Optional[str]:
        """
        Return dates of type DD-MM-YYYY, DD / MM / YYYY or DDMMAAAA to type YYYY-MM-DD.

        @param f Text string with the date to transform.
        @return Text string with the date transformed.
        """
        from pineboolib.application.utils.date_conversion import date_dma_to_amd

        return date_dma_to_amd(f)

    @classmethod
    def dateAMDtoDMA(cls, f) -> Optional[str]:
        """
        Return dates of type YYYY-MM-DD, YYYY-MM-DD or YYYYMMDD to type DD-MM-YYYY.

        @param f Text string with the date to transform
        @return Text string with the date transformed
        """
        from pineboolib.application.utils.date_conversion import date_amd_to_dma

        return date_amd_to_dma(f)

    @classmethod
    @decorators.BetaImplementation
    def formatoMiles(cls, s: str) -> str:
        """
        Format a text string by placing thousands separators.

        The string that is passed is supposed to be a number, converting it
        with QString :: toDouble (), if the string is not number the result is unpredictable.

        @param s Text string that wants thousands of separators
        @return Returns the formatted string with thousands separators
        """
        s = str(s)
        decimal = ""
        entera = ""
        ret = ""
        # dot = QApplication::tr(".")
        dot = "."
        neg = s[0] == "-"

        if "." in s:
            # decimal = QApplication::tr(",") + s.section('.', -1, -1)
            aStr = s.split(".")
            decimal = "," + aStr[-1]
            entera = aStr[-2].replace(".", "")
        else:
            entera = s

        if neg:
            entera.replace("-", "")

        length = len(entera)

        while length > 3:
            ret = dot + entera[-3:] + ret
            entera = entera[:-3]
            length = len(entera)

        ret = entera + ret + decimal

        if neg:
            ret = "-" + ret

        return ret

    @classmethod
    def translate(cls, group: str, text_: str) -> str:
        """
        Translate a string into the local language.

        A call to the tr () function of the QObject class is made to do the translation.
        It is used for translations from outside QObject objects

        @param group Context in which the string is located, generally refers to the class in which it is defined
        @param s Text string to translate
        @return Returns the string translated into the local language
        """

        from pineboolib.fllegacy.fltranslations import FLTranslate

        if text_ == "MetaData":
            group, text_ = text_, group

        text_ = text_.replace(" % ", " %% ")

        return str(FLTranslate(group, text_))

    @classmethod
    def numCreditCard(cls, num: str) -> bool:
        """
        Return if the credit card number is valid.

        The parameter that is passed is the text string that contains the card number.

        @param num Text string with card number
        @return Returns true if the card number is valid
        """
        n_sum = 0
        n_rest = int(num)
        i = 0
        while i < 10:
            n_sum += int(num[i])
            n_rest = int(num[i + 1]) * 2
            if n_rest > 9:
                n_rest -= 9

            n_sum += n_rest
            i += 2

        return True if n_sum % 10 == 0 else False

    @classmethod
    def nextCounter(
        cls,
        name_or_series: str,
        cursor_or_name: Union[str, "PNSqlCursor"],
        cursor_: Optional["PNSqlCursor"] = None,
    ) -> Optional[Union[str, int]]:
        """Return next counter value."""

        from pineboolib.application.database.utils import nextCounter

        return nextCounter(name_or_series, cursor_or_name, cursor_)

    @classmethod
    @decorators.NotImplementedWarn
    def nextSequence(cls, nivel: int, secuencia: str, ultimo: str) -> str:
        """
        Return the next value of the sequence according to the depth indicated by level.

        To explain the operation we will give an example. Assume a sequence type% A-% N.
        % A indicates that a sequence in letters and% N a sequence in number be placed in that position.
        The numbering of levels goes from right to left so level 1 is% N and level 2% A.
        If we do a nextSequence at level 1 the return value will be a% A that was and a% N adding 1
        the previous. If the level is 2 we will get a% A + 1, transformed to letters, and all levels to
        the right of this is set to 1 or its corresponding letter that would be A.

        @param level Indicates the depth at which the increase is made.
        @param sequence Structure of the sequence.
        @param last Last value of the sequence to be able to give the next value.
        @return The sequence in the format provided.
        @author Andrés Otón Urbano
        """
        return ""

    @classmethod
    def isFLDefFile(cls, head: str) -> bool:
        """
        Return if the header of a definition file corresponds with those supported by AbanQ.

        This method does not work for scripts, only for definition files;
        mtd, ui, qry, xml, ts and kut.

        @param head Character string with the file header, it would suffice
            with the first three or four lines of the file you don't empty.
        @return TRUE if it is a supported file, FALSE otherwise.
        """
        while head.startswith(" "):
            head = head[1:]

        ret = False

        if head.find("<!DOCTYPE UI>") == 0:
            ret = True
        elif head.find("<!DOCTYPE QRY>") == 0:
            ret = True
        elif head.find("<!DOCTYPE KugarTemplate") == 0:
            ret = True
        elif head.find("<!DOCTYPE TMD>") == 0:
            ret = True
        elif head.find("<!DOCTYPE TS>") == 0:
            ret = True
        elif head.find("<ACTIONS>") == 0:
            ret = True
        elif head.find("<jasperReport") == 0:
            ret = True

        return ret

    @classmethod
    def addDays(cls, fecha: Any, offset: int) -> Optional["Date"]:
        """
        Add days to a date.

        @param date Date to operate with
        @param offset Number of days to add. If negative, subtract days
        @return Date with day shift
        """

        if isinstance(fecha, str):
            fecha = Date(fecha, "yyyy-MM-dd")
        if not isinstance(fecha, Date):
            logger.error("addDays: No reconozco el tipo de dato %s", type(fecha))
            logger.trace("Detalle:", stack_info=True)
            return None
        return fecha.addDays(offset)

    @classmethod
    def addMonths(cls, fecha: Any, offset: int) -> Optional["Date"]:
        """
        Add months to a date.

        @param date Date to operate with
        @param offset Number of months to add. If negative, subtract months
        @return Date with month offset
        """

        if isinstance(fecha, str):
            fecha = Date(fecha)
        if not isinstance(fecha, Date):
            logger.error("addMonths: No reconozco el tipo de dato %s", type(fecha))
            logger.trace("Detalle:", stack_info=True)
            return None
        return fecha.addMonths(offset)

    @classmethod
    def addYears(cls, fecha: Any, offset: int) -> Optional["Date"]:
        """
        Add years to a date.

        @param date Date to operate with
        @param offset Number of years to add. If negative, subtract years
        @return Date with displacement of years
        """

        if isinstance(fecha, str):
            fecha = Date(fecha)
        if not isinstance(fecha, Date):
            logger.error("addYears: No reconozco el tipo de dato %s", type(fecha), stack_info=True)
            return None
        return fecha.addYears(offset)

    @classmethod
    def daysTo(cls, d1: Any, d2: Any) -> Optional[int]:
        """
        Return difference of days from one date to another.

        @param d1 Date of departure
        @param d2 Destination Date
        @return Number of days between d1 and d2. It will be negative if d2 is earlier than d1.
        """
        from datetime import date

        if isinstance(d1, Date):
            d1 = d1.toString()

        if isinstance(d1, date):
            d1 = str(d1)

        if isinstance(d1, str):
            d1 = d1[:10]

        if not isinstance(d1, str) or d1 == "":
            if d1 not in (None, ""):
                logger.error("daysTo: No reconozco el tipo de dato %s", type(d1))
            return None

        if isinstance(d2, Date):
            d2 = d2.toString()

        if isinstance(d2, date):
            d2 = str(d2)

        if isinstance(d2, str):
            d2 = d2[:10]

        if not isinstance(d2, str) or d2 == "":
            if d2 not in (None, ""):
                logger.error("daysTo: No reconozco el tipo de dato %s", type(d2))
            return None
        d1 = datetime.datetime.strptime(d1, "%Y-%m-%d").date()
        d2 = datetime.datetime.strptime(d2, "%Y-%m-%d").date()
        return (d2 - d1).days

    @classmethod
    def buildNumber(cls, v: Union[int, float, str], tipo: str, partDecimal: int) -> str:
        """
        Return a string from a number, specifying the format and accuracy.

        @param v. Number to convert to QString
        @param type. Number format
        @param partDecimal. Accuracy (number of decimal places) of the number

        @return String containing the formatted number
        """
        val_str: str = str(v)
        if val_str.endswith("5"):
            val_str += "1"

        ret = round(float(val_str)) if partDecimal == 0 else round(float(val_str), partDecimal)
        """
        d = float(v) * 10**partDecimal
        d = round(d)
        d = d / 10**partDecimal
        # ret.setNum(d, tipo, partDecimal)
        # formamos algo de este tipo: '{:.3f}'.format(34.14159265358979)
        # '34.142'
        f = '{:.' + str(partDecimal) + 'f}'
        ret = f.format(d)
        if tipo == "float":
            ret = float(ret)
        return ret
        """
        return str(ret)

    @classmethod
    def readSettingEntry(cls, key: str, def_: Any = u"") -> Any:
        """
        Return the value of a setting in the AbanQ installation directory.

        @param key. Setting identification key
        @param def. Default value in case the setting is not set
        @param ok. Indicator that the reading is correct

        @return Setting value
        """
        from pineboolib.core.settings import settings

        return settings.value(key, def_)

    @classmethod
    def writeSettingEntry(cls, key: str, value: Any) -> None:
        """
        Set the value of a setting in the AbanQ installation directory.

        @param key. Setting identification key.
        @param Setting value.

        @return Indicator if the writing of the settings is successful
        """
        from pineboolib.core.settings import settings

        return settings.set_value(key, value)

    @classmethod
    def readDBSettingEntry(cls, key: str) -> Any:
        """
        Read the value of a setting in the flsettings table.

        @param key. Setting identification key.

        @return Setting value.
        """
        from pineboolib.fllegacy.flsqlquery import FLSqlQuery

        ret = None
        q = FLSqlQuery()
        q.setSelect("valor")
        q.setFrom("flsettings")
        q.setWhere("flkey = '%s'" % key)
        q.setTablesList("flsettings")
        if q.exec_() and q.first():
            ret = q.value(0)
            if ret in ["false", "False"]:
                ret = False
            elif ret in ["true", "True"]:
                ret = True

        return ret

    @classmethod
    def writeDBSettingEntry(cls, key: str, value: Any) -> bool:
        """
        Set the value of a setting in the flsettings table.

        @param key. Setting identification key
        @param Setting value

        @return Indicator if the writing of the settings is successful
        """
        # result = False
        from pineboolib.application import project

        where = "flkey = '%s'" % key
        found = cls.readDBSettingEntry(key)
        cursor = project.conn.cursor()
        if found is None:
            sql = "INSERT INTO flsettings (flkey, valor) VALUES ('%s', '%s')" % (key, value)
        else:
            sql = "UPDATE flsettings SET valor = '%s' WHERE %s" % (value, where)
        try:
            cursor.execute(sql)

        except Exception:
            logger.exception("writeDBSettingEntry: Error al ejecutar SQL: %s", sql)
            # FIXME: Quito el rollback porque esta función no inicia transacción
            # cursor.rollback()
            return False

        cursor.close()
        return True

    @classmethod
    def roundFieldValue(
        cls, value: Union[float, int, str], table_name: str, field_name: str
    ) -> str:
        """
        Round a value based on the specified accuracy for a double type field in the database.

        @param n. Number to be rounded
        @param table. Table name
        @param field. Field Name

        @return Rounded Number
        """

        from pineboolib.fllegacy.flapplication import aqApp

        tmd = aqApp.db().manager().metadata(table_name)
        if tmd is None:
            return ""
        fmd = tmd.field(field_name)
        return cls.buildNumber(value, "float", fmd.partDecimal()) if fmd is not None else ""

    @classmethod
    def sqlSelect(
        cls,
        f: str,
        s: str,
        w: str,
        tL: Optional[Union[str, List]] = None,
        size: int = 0,
        connName: str = "default",
    ) -> Any:
        """Return a value from a query."""
        from pineboolib.application.database.utils import sqlSelect

        return sqlSelect(f, s, w, tL, size, connName)

    @classmethod
    def quickSqlSelect(cls, f: str, s: str, w: str, connName: str = "default") -> Any:
        """Return a value from a quick query."""
        from pineboolib.application.database.utils import quickSqlSelect

        return quickSqlSelect(f, s, w, connName)

    @classmethod
    def sqlInsert(
        cls,
        t: str,
        fL: Union[str, List],
        vL: Union[str, List, bool, int, float],
        connName: str = "default",
    ) -> Any:
        """Insert values to a table."""
        from pineboolib.application.database.utils import sqlInsert

        return sqlInsert(t, fL, vL, connName)

    @classmethod
    def sqlUpdate(
        cls,
        t: str,
        fL: Union[str, List],
        vL: Union[str, List, bool, int, float],
        w: str,
        connName: str = "default",
    ) -> Any:
        """Update values to a table."""
        from pineboolib.application.database.utils import sqlUpdate

        return sqlUpdate(t, fL, vL, w, connName)

    @classmethod
    def sqlDelete(cls, t: str, w: str, connName: str = "default"):
        """Delete a value from a table."""
        from pineboolib.application.database.utils import sqlDelete

        return sqlDelete(t, w, connName)

    @classmethod
    def quickSqlDelete(cls, t: str, w: str, connName: str = "default"):
        """Quick delete a value from a table."""

        from pineboolib.application.database.utils import quickSqlDelete

        return quickSqlDelete(t, w, connName)

    @classmethod
    def execSql(cls, sql: str, connName: str = "default"):
        """Set a query to a database."""
        from pineboolib.application.database.utils import execSql

        return execSql(sql, connName)

    @classmethod
    def createProgressDialog(
        cls, title: str, steps: Union[int, float], id_: str = "default"
    ) -> Any:
        """
        Create a progress dialog.

        @param l Label of the dialogue
        @param tS Total number of steps to perform
        """
        from pineboolib.application import project

        return project.message_manager().send(
            "progress_dialog_manager", "create", [title, steps, id_]
        )

    @classmethod
    def destroyProgressDialog(cls, id_: str = "default") -> None:
        """
        Destroy the progress dialog.
        """

        from pineboolib.application import project

        project.message_manager().send("progress_dialog_manager", "destroy", [id_])

    @classmethod
    def setProgress(cls, step_number: Union[int, float], id_: str = "default") -> None:
        """
        Set the degree of progress of the dialogue.

        @param p Degree of progress
        """

        from pineboolib.application import project

        project.message_manager().send("progress_dialog_manager", "setProgress", [step_number, id_])

    @classmethod
    def setLabelText(cls, l: str, id_: str = "default") -> None:
        """
        Change the text of the dialog label.

        @param l Tag
        """

        from pineboolib.application import project

        project.message_manager().send("progress_dialog_manager", "setLabelText", [l, id_])

    @classmethod
    def setTotalSteps(cls, tS: int, id_: str = "default") -> None:
        """
        Set the total number of steps in the dialog.

        @param ts Total number of steps
        """

        from pineboolib.application import project

        project.message_manager().send("progress_dialog_manager", "setTotalSteps", [tS, id_])

    @classmethod
    def domDocumentSetContent(cls, doc: "QDomDocument", content: Any) -> bool:
        """
        Return the content of an XML document.

        Set a DOM document from the XML. Check for errors, and if they exist
        It shows the error found and the line and column where it is located.

        @param doc DOM document to be established
        @param content XML content
        @return FALSE if there was a failure, TRUE otherwise.
        """
        if not content:
            logger.warning("Se ha intentado cargar un fichero XML vacío", stack_info=False)
            return False

        ErrMsg = ""
        errLine = 0
        errColumn = 0

        # if not doc.setContent(content, ErrMsg, errLine, errColumn):
        if not doc.setContent(content):
            logger.warning(
                "Error en fichero XML.\nError : %s\nLinea : %s\nColumna : %s",
                ErrMsg,
                errLine,
                errColumn,
            )
            return False

        return True

    @classmethod
    def sha1(cls, value: Union[str, bytes, None]) -> str:
        """
        Return the SHA1 key of a text string.

        @param str String from which to obtain the SHA1 key.
        @return Corresponding key in hexadecimal digits.
        """
        if value is None:
            value = ""

        if isinstance(value, str):
            value = value.encode()

        sha_ = hashlib.new("sha1", value)
        st = "%s" % sha_.hexdigest()
        return st.upper()

    @classmethod
    @decorators.NotImplementedWarn
    def usha1(cls, data, _len):
        """
        Return the SHA1 key of a data.

        @param str String from which to obtain the SHA1 key.
        @return Corresponding key in hexadecimal digits.
        """
        pass

    @classmethod
    @decorators.NotImplementedWarn
    def snapShotUI(cls, n):
        """
        Return the image or screenshot of a form.

        @param n Name of the file that contains the description of the form.
        """
        pass

    @classmethod
    @decorators.NotImplementedWarn
    def saveSnapShotUI(cls, n, pathFile):
        """
        Save the image or screenshot of a form in a PNG format file.

        @param n Name of the file that contains the description of the form.
        @param pathFile Path and file name where to save the image
        """
        pass

    @classmethod
    @decorators.NotImplementedWarn
    def flDecodeType(cls, fltype):
        """
        Decode a type of AbanQ to a QVariant type.

        @param fltype AbanQ data type.
        @return QVariant data type.
        """
        pass

    @classmethod
    @decorators.NotImplementedWarn
    def saveIconFile(cls, data, pathFile):
        """
        Save the icon image of a button on a form in a png file. Used for documentation.

        @param data Image content in a character string
        @param pathFile Full path to the file where the image will be saved
        """
        pass

    @classmethod
    def getIdioma(cls) -> str:
        """
        Return a two character string with the system language code.

        @return System language code
        """
        return QtCore.QLocale().name()[:2]

    @classmethod
    def getOS(cls) -> str:
        """Return OS name."""

        return SysBaseType.osName()

    @classmethod
    @decorators.NotImplementedWarn
    def serialLettertoNumber(cls, letter: str) -> str:
        """
        Convert a string that is a series of letters into its corresponding numerical value.

        @param letter String with the series.
        @return A string but containing numbers.
        """
        return ""

    @classmethod
    @decorators.NotImplementedWarn
    def serialNumbertoLetter(cls, number: Union[int, float]) -> str:
        """
        Convert a number to its corresponding sequence of letters.

        @param number Number to convert.
        """
        return ""

    @classmethod
    @decorators.NotImplementedWarn
    def findFiles(
        cls, paths: str, filter_: str = "*", break_on_first_match: bool = False
    ) -> List[str]:
        """
        Search files recursively on the indicated paths and according to the indicated pattern.

        @param paths Search paths
        @param filter Filter pattern for files. Supports several separated by spaces "* .gif * .png".
                      By default all, "*"
        @param breakOnFirstMatch If it is TRUE when you find the first file that meets the indicated pattern, it ends
                                search and return the name of that file
        @return List of the names of the files found
        """

        import glob

        files_found = []
        for p in paths:
            for file_name in glob.iglob("%s/**/%s" % (p, filter_), recursive=True):
                files_found.append(file_name)
                if break_on_first_match:
                    break

        return files_found

    @classmethod
    @decorators.NotImplementedWarn
    def savePixmap(cls, data: str, filename: str, format_: str) -> None:
        """
        Save Pixmap image on a specific path.

        @param data Image content in a character string
        @param filename: Path to the file where the image will be saved
        @param fmt Indicates the format in which to save the image
        @author Silix
        """
        pass

    @classmethod
    def fieldType(cls, fn: str, tn: str, conn_name: str = "default") -> Optional[str]:
        """
        Return the numeric type of a field.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return field type id
        """

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return None if mtd is None else mtd.fieldType(fn)

    @classmethod
    def fieldLength(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> int:
        """
        Return the length of a field.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return requested field length
        """
        if tn is None:
            return 0

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return 0 if mtd is None else mtd.fieldLength(fn)

    @classmethod
    def fieldNameToAlias(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> str:
        """
        Return the alias of a field from its name.

        @param fn. Field Name.
        @param tn. Name of the table containing the field.
        @param conn_name. Name of the connection to use.
        @return Alias ​​of the specified field.
        """
        if tn is None:
            return fn

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return fn if mtd is None else mtd.fieldNameToAlias(fn)

    @classmethod
    def tableNameToAlias(cls, tn: Optional[str], conn_name: str = "default") -> Optional[str]:
        """
        Return the name of a table from its alias.

        @param tn. Table name
        @param conn_name. Name of the connection to use
        @return Alias ​​of the specified table
        """

        if tn is None:
            return None

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return None if mtd is None else mtd.alias()

    @classmethod
    def fieldAliasToName(cls, an: str, tn: Optional[str], conn_name: str = "default") -> str:
        """
        Return the name of a field from its alias.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Alias ​​of the specified field
        """

        if tn is None:
            return an

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return an if mtd is None else mtd.fieldAliasToName(an)

    @classmethod
    def fieldAllowNull(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> bool:
        """
        Return if the field allows to be left blank.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. Whether or not to accept the value of the field
        """

        if tn is None:
            return False

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return False if mtd is None else mtd.fieldAllowNull(fn)

    @classmethod
    def fieldIsPrimaryKey(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> bool:
        """
        Return if the field is the primary key of the table.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. If it is primary key or not
        """
        if tn is None:
            return False

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        return False if mtd is None else mtd.fieldIsPrimaryKey(fn)

    @classmethod
    def fieldIsCompoundKey(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> bool:
        """
        Return if the field is a composite key of the table.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. If it is a composite key or not
        """
        if tn is None:
            return False

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        if mtd is None:
            return False
        return False
        # field = None  # FIXME: field is not defined anywhere
        # return False if field is None else field.isCompoundKey()

    @classmethod
    def fieldDefaultValue(cls, fn: str, tn: Optional[str], conn_name: str = "default") -> Any:
        """
        Return the default value of a field.

        @param fn. Field Name
        @param tn. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Default field value
        """
        if tn is None:
            return None  # return QVariant

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        mtd = conn.manager().metadata(tn)

        if mtd is None:
            return None  # return QVariant

        field = mtd.field(fn)
        if field is None:
            return None  # return QVariant

        return field.defaultValue()

    @classmethod
    def formatValue(cls, t: str, v: Any, upper: bool, conn_name: str = "default") -> Any:
        """
        Return formatted value.

        @param t. Field type
        @param v. Field Value
        @param conn_name. Name of the connection to use
        @return Formatted Value
        """

        from pineboolib.fllegacy.flapplication import aqApp

        conn = aqApp.db().useConn(conn_name)
        return conn.manager().formatValue(t, v, upper)

    @classmethod
    def nameUser(cls) -> str:
        """Return user name."""
        return SysBaseType.nameUser()

    # FIXME: Missing in SysType:
    # @classmethod
    # def userGroups(cls) -> str:
    #
    #     return SysType().userGroups()
    #
    # @classmethod
    # def isInProd(cls) -> bool:
    #
    #     return SysType().isInProd()
    #
    # @classmethod
    # def request(cls) -> str:
    #
    #     return SysType().request()

    @classmethod
    def nameBD(cls) -> str:
        """Return database name."""

        return SysBaseType.nameBD()
