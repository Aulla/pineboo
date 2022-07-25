"""Flutil module."""
# -*- coding: utf-8 -*-
import hashlib
import datetime
import glob
from datetime import date

from PyQt6 import QtCore  # type: ignore[import]

from pineboolib.application.qsatypes import sysbasetype
from pineboolib.application.utils import date_conversion
from pineboolib.application.database import utils, pnsqlquery
from pineboolib.application import types

from pineboolib.core import decorators, translate, settings
from pineboolib import logging, application


from typing import List, Optional, Union, Any, TYPE_CHECKING


if TYPE_CHECKING:
    from PyQt6 import QtXml  # pragma: no cover
    from pineboolib.interfaces import isqlcursor, iconnection  # noqa : F401 # pragma: no cover

LOGGER = logging.get_logger(__name__)


class FLUtil(object):
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

    @staticmethod
    def partInteger(num: float) -> int:
        """
        Return the integer part of a number.

        Given a number returns the corresponding integer, that is,
        figures on the left side of the decimal point.

        @param n Number to get the whole part from. Must be positive
        @return The whole part of the number, which can be zero
        """
        integer, decimal = divmod(num, 1)
        return int(integer)

    @staticmethod
    def partDecimal(num: float) -> int:
        """
        Return the decimal part of a number.

        Given a number returns the corresponding decimal part, that is,
        figures on the right side of the decimal point
        @param n Number from which to obtain the decimal part. Must be positive
        @return The decimal part of the number, which can be zero
        """
        integer, decimal = divmod(num, 1)
        return int(round(decimal, 2) * 100)

    @classmethod
    def unidades(cls, num: int) -> str:
        """
        Statement of the units of a number.

        @param n Number to deal with. Must be positive.
        """
        if num >= 0:
            return cls.vecUnidades[num]
        else:
            raise ValueError("Parameter 'num' must be a positive integer")

    @classmethod
    def utf8(cls, text: str) -> str:
        """
        Return a string to utf-8 encoding.
        """
        return text.encode().decode("utf-8", "ignore")

    @classmethod
    def centenamillar(cls, num: int) -> str:
        """
        Statement of the hundreds of thousands of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""
        if num < 0:
            raise ValueError("Param n must be positive integer")
        if num < 10000:
            buffer = cls.decenasmillar(num)
        else:
            buffer = cls.centenas(num / 1000)
            buffer = buffer + " mil "
            buffer = buffer + cls.centenas(num % 1000)

        return buffer

    @classmethod
    def decenas(cls, num: Union[int, float]) -> str:
        """
        Statement of the tens of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""

        if num < 0:
            raise ValueError("Param n must be positive integer")
        if num < 30:
            buffer = cls.unidades(int(num))
        else:
            buffer = cls.vecDecenas[cls.partInteger(num / 10)]
            if num % 10:
                buffer = buffer + " y "
                buffer = buffer + cls.unidades(int(num % 10))

        return buffer

    @classmethod
    def centenas(cls, num: Union[int, float]) -> str:
        """
        Statement of the hundreds of a number.

        @param n Number to deal with. It must be positive.
        """
        buffer = ""
        if num < 0:
            raise ValueError("Param n must be positive integer")
        if num == 100:
            buffer = "cien"

        elif num < 100:
            buffer = cls.decenas(int(num))
        else:
            buffer += cls.vecCentenas[cls.partInteger(num / 100)]
            buffer += " "
            buffer += cls.decenas(int(num % 100))

        return buffer

    @classmethod
    def unidadesmillar(cls, num: int) -> str:
        """
        Statement of the thousand units of a number.

        @param num Number to deal with. Must be positive.
        """
        buffer = ""
        if num < 1000:
            buffer = ""

        elif num / 1000 == 1:
            buffer = "mil"

        elif num / 1000 > 1:
            buffer = cls.unidades(int(num / 1000))
            buffer += " mil"

        centenas = cls.centenas(int(num % 1000))

        if buffer and centenas:
            buffer += " "
        buffer += centenas

        return buffer

    @classmethod
    def decenasmillar(cls, num: int) -> str:
        """
        Statement of tens of thousands of a number.

        @param n Number to deal with. Must be positive.
        """
        buffer = ""
        if num < 10000:
            buffer = cls.unidadesmillar(num)
        else:
            buffer = cls.decenas(num / 1000)
            buffer = buffer + " mil "
            buffer = buffer + cls.centenas(int(num % 10000))
        return buffer

    @classmethod
    def enLetra(cls, num: int) -> str:
        """
        Return the expression in text of how a number is stated, in Spanish.

        Given an integer, return its expression in text as it is
        speaks in a spoken way; for example given the number 130,
        will return the text string "one hundred and thirty".

        @param n Number to be transferred to your spoken form. Must be positive
        @return Text string with its spoken expression.
        """
        buffer = ""
        if num > 1000000000:
            buffer = "Sólo hay capacidad hasta mil millones"

        elif num < 1000000:

            buffer = cls.centenamillar(int(num))

        else:
            if num / 1000000 == 1:
                buffer = "un millon"
            else:
                buffer = cls.centenas(int(num / 1000000))
                buffer = buffer + " millones "

            buffer = buffer + cls.centenamillar(int(num % 1000000))

        return buffer.upper()

    @classmethod
    def enLetraMoneda(cls, num: Union[int, str, float], currency: str) -> str:
        """
        Return the expression in text of how a monetary amount is stated, in Spanish and in any currency indicated.

        Given a double number, it returns its expression in text as it is
        state in spoken form in the indicated currency; for example given the number 130.25,
        will return the text string "one hundred thirty 'currency' with twenty-five cents".

        @param num Number to be transferred to your spoken form. Must be positive
        @param currency Currency name
        @return Text string with its spoken expression.
        """
        if isinstance(num, str):
            num = float(num)

        num_tmp = num * -1.00 if num < 0.00 else num
        entero = cls.partInteger(num_tmp)
        decimal = cls.partDecimal(num_tmp)
        res = ""

        if entero > 0:
            res = "%s %s" % (cls.enLetra(entero), currency)

            if decimal > 0:

                res += " con %s céntimos" % cls.enLetra(decimal)

        if entero <= 0 and decimal > 0:

            res = "%s céntimos" % cls.enLetra(decimal)

        if num < 0.00:

            res = "menos %s" % res

        return res.upper()

    @classmethod
    def enLetraMonedaEuro(cls, num: Union[int, float]) -> str:
        """
        Return the expression in text of how a monetary amount is stated, in Spanish and in Euros.

        Given a double number, it returns its expression in text as it is
        states in a spoken way in euros; for example given the number 130.25,
        will return the text string "one hundred thirty euros with twenty-five cents".

        @param num Number to be transferred to your spoken form. Must be positive
        @return Text string with its spoken expression.
        """
        # return enLetraMoneda(n, QT_TR_NOOP("euros"));
        return cls.enLetraMoneda(num, "euros")

    @classmethod
    def letraDni(cls, num: int) -> str:
        """
        Return the letter associated with the number of the D.N.I. Spanish.

        @param num Number of D.N.I
        @return Character associated with the number of D.N.I
        """
        letras = "TRWAGMYFPDXBNJZSQVHLCKE"
        return letras[num % 23]

    @classmethod
    def nombreCampos(cls, table_name: str) -> List[str]:
        """
        Return the list of field names from the specified table.

        The first string in the list contains the number of fields in the table

        @param table_name. Table name.
        @return Field List.
        """
        metadata = application.PROJECT.conn_manager.manager().metadata(table_name)
        campos: List[str] = []
        if metadata is not None:
            campos = metadata.fieldNames()

        return [str(len(campos))] + campos

    @classmethod
    def calcularDC(cls, num: int) -> str:
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

        table: List[int] = [6, 3, 7, 9, 10, 5, 8, 4, 2, 1]

        dc_ = None
        sum_ = 0
        digits_ = len(str(num)) - 1

        ct_ = 1

        while ct_ <= len(str(num)):
            valor_table: int = table[digits_]
            valor_n = str(num)[ct_ - 1]
            sum_ += valor_table * int(valor_n)
            digits_ = digits_ - 1
            ct_ += 1

        dc_ = 11 - (sum_ % 11)
        if dc_ == 11:
            dc_ = 0
        elif dc_ == 10:
            dc_ = 1

        char = chr(dc_ + 48)
        return char

    @classmethod
    def dateDMAtoAMD(cls, date_str) -> str:
        """
        Return dates of type DD-MM-YYYY, DD / MM / YYYY or DDMMAAAA to type YYYY-MM-DD.

        @param date_str Text string with the date to transform.
        @return Text string with the date transformed.
        """

        return date_conversion.date_dma_to_amd(date_str) or ""

    @classmethod
    def dateAMDtoDMA(cls, date_str: str) -> str:
        """
        Return dates of type YYYY-MM-DD, YYYY-MM-DD or YYYYMMDD to type DD-MM-YYYY.

        @param date_str Text string with the date to transform
        @return Text string with the date transformed
        """

        return date_conversion.date_amd_to_dma(date_str) or ""

    @classmethod
    def formatoMiles(cls, value: str) -> str:
        """
        Format a text string by placing thousands separators.

        The string that is passed is supposed to be a number, converting it
        with QString :: toDouble (), if the string is not number the result is unpredictable.

        @param value Text string that wants thousands of separators
        @return Returns the formatted string with thousands separators
        """
        value = str(value)
        decimal = ""
        entera = ""
        ret = ""
        # dot = QApplication::tr(".")
        dot = "."
        neg = value[0] == "-"

        if "." in value:
            # decimal = QApplication::tr(",") + s.section('.', -1, -1)
            value_list = value.split(".")
            decimal = "," + value_list[-1]
            entera = value_list[-2].replace(".", "")
        else:
            entera = value

        if neg:
            entera = entera.replace("-", "")

        length = len(entera)

        while length > 3:
            ret = dot + entera[-3:] + ret
            entera = entera[:-3]
            length = len(entera)

        ret = entera + ret + decimal

        if neg:
            ret = "-%s" % ret

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

        if text_ == "MetaData":
            group, text_ = text_, group

        text_ = text_.replace(" % ", " %% ")

        return translate.translate(group, text_)

    @classmethod
    def numCreditCard(cls, num: str) -> bool:
        """
        Return if the credit card number is valid.

        The parameter that is passed is the text string that contains the card number.

        @param num Text string with card number
        @return Returns true if the card number is valid
        """
        list_ = []
        for item in num:
            list_.append(int(item))

        for idx in range(0, len(list_), 2):
            list_[idx] = list_[idx] * 2
            if list_[idx] >= 10:
                list_[idx] = list_[idx] // 10 + list_[idx] % 10

        return sum(list_) % 10 == 0

    @classmethod
    def nextCounter(
        cls,
        name_or_series: str,
        cursor_or_name: Union[str, "isqlcursor.ISqlCursor"],
        cursor_: Optional["isqlcursor.ISqlCursor"] = None,
    ) -> Optional[Union[str, int]]:
        """Return next counter value."""

        return utils.next_counter(name_or_series, cursor_or_name, cursor_)

    @classmethod
    @decorators.not_implemented_warn
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

        return (
            True
            if str(head.strip()).startswith(
                (
                    "<!DOCTYPE UI>",
                    "<!DOCTYPE QRY>",
                    "<!DOCTYPE KugarTemplate",
                    "<!DOCTYPE TMD>",
                    "<!DOCTYPE TS>",
                    "<ACTIONS>",
                    "<jasperReport",
                )
            )
            else False
        )

    @classmethod
    def addDays(cls, fecha: Union[types.Date, str], offset: int) -> "types.Date":
        """
        Add days to a date.

        @param date Date to operate with
        @param offset Number of days to add. If negative, subtract days
        @return Date with day shift
        """

        if isinstance(fecha, str):
            fecha = types.Date(fecha)

        return fecha.addDays(offset)

    @classmethod
    def addMonths(cls, fecha: Union[types.Date, str], offset: int) -> "types.Date":
        """
        Add months to a date.

        @param date Date to operate with
        @param offset Number of months to add. If negative, subtract months
        @return Date with month offset
        """

        if isinstance(fecha, str):
            fecha = types.Date(fecha)

        return fecha.addMonths(offset)

    @classmethod
    def addYears(cls, fecha: Union[types.Date, str], offset: int) -> "types.Date":
        """
        Add years to a date.

        @param date Date to operate with
        @param offset Number of years to add. If negative, subtract years
        @return Date with displacement of years
        """

        if isinstance(fecha, str):
            fecha = types.Date(fecha)

        return fecha.addYears(offset)

    @classmethod
    def daysTo(
        cls, date1: Union[types.Date, str, date], date2: Union[types.Date, str, date]
    ) -> int:
        """
        Return difference of days from one date to another.

        @param date1 Date of departure
        @param date2 Destination Date
        @return Number of days between date1 and date2. It will be negative if date2 is earlier than date1.
        """

        if isinstance(date1, (types.Date, date, str)):
            date1 = str(date1)

        date1 = date1[:10]

        if isinstance(date2, (types.Date, date, str)):
            date2 = str(date2)

        date2 = date2[:10]

        r1_ = datetime.datetime.strptime(date1, "%Y-%m-%d").date()
        r2_ = datetime.datetime.strptime(date2, "%Y-%m-%d").date()
        return (r2_ - r1_).days

    @classmethod
    def buildNumber(cls, value: Union[int, float, str], type_: str, part_decimal: int = 0) -> str:
        """
        Return a string from a number, specifying the format and accuracy.

        @param value. Number to convert to QString
        @param type_. Number format
        @param part_decimal. Accuracy (number of decimal places) of the number

        @return String containing the formatted number
        """
        import math

        number = float(value)

        multiplier = 10**part_decimal
        result = str(math.floor(number * multiplier + 0.5) / multiplier)
        pos_comma = result.find(".") + 1

        decimals = len(result) - pos_comma
        if decimals != part_decimal:
            if decimals < part_decimal:
                while decimals < part_decimal:
                    result += "0"
                    decimals += 1
            else:
                while decimals > part_decimal:
                    result = result[:-1]
                    decimals -= 1

        return result

    @classmethod
    def readSettingEntry(cls, key: str, def_: Any = "") -> Any:
        """
        Return the value of a setting in the AbanQ installation directory.

        @param key. Setting identification key
        @param def. Default value in case the setting is not set
        @param ok. Indicator that the reading is correct

        @return Setting value
        """

        return settings.SETTINGS.value(key, def_)

    @classmethod
    def writeSettingEntry(cls, key: str, value: Any) -> None:
        """
        Set the value of a setting in the AbanQ installation directory.

        @param key. Setting identification key.
        @param Setting value.

        @return Indicator if the writing of the settings is successful
        """

        return settings.SETTINGS.set_value(key, value)

    @classmethod
    def readDBSettingEntry(cls, key: str) -> Any:
        """
        Read the value of a setting in the flsettings table.

        @param key. Setting identification key.

        @return Setting value.
        """

        qry = pnsqlquery.PNSqlQuery()
        qry.setSelect("valor")
        qry.setFrom("flsettings")
        qry.setWhere("flkey = '%s'" % key)
        qry.setTablesList("flsettings")
        if qry.exec_() and qry.first():
            return str(qry.value(0))

        return None

    @classmethod
    def writeDBSettingEntry(cls, key: str, value: Any) -> bool:
        """
        Set the value of a setting in the flsettings table.

        @param key. Setting identification key
        @param Setting value

        @return Indicator if the writing of the settings is successful
        """
        # result = False

        where = "flkey = '%s'" % key
        found = cls.readDBSettingEntry(key)
        session_ = application.PROJECT.conn_manager.useConn("default").session()
        if found is None:
            sql = "INSERT INTO flsettings (flkey, valor) VALUES ('%s', '%s')" % (key, value)
        else:
            sql = "UPDATE flsettings SET valor = '%s' WHERE %s" % (value, where)
        try:
            session_.execute(sql)

        except Exception:
            LOGGER.exception("writeDBSettingEntry: Error al ejecutar SQL: %s", sql)
            return False

        # session_.close()
        return True

    @classmethod
    def roundFieldValue(
        cls, value: Union[float, int, str], table_name: str, field_name: str
    ) -> str:
        """
        Round a value based on the specified accuracy for a double type field in the database.

        @param value. Number to be rounded
        @param table. Table name
        @param field. Field Name

        @return Rounded Number
        """

        metadata = application.PROJECT.conn_manager.manager().metadata(table_name)
        if metadata is not None:
            field_metadata = metadata.field(field_name)
            if field_metadata is not None:
                return cls.buildNumber(value or 0.00, "float", field_metadata.partDecimal())

        return ""

    @classmethod
    def sqlSelect(
        cls,
        from_: str,
        select_: str,
        where_: str = "1 = 1",
        tables_list: Optional[Union[str, List, types.Array]] = None,
        size_or_conn: Any = 0,
        conn: Union[str, "iconnection.IConnection"] = "default",
    ) -> Any:
        """
        Return a value from a query.

        @param from_ From clausule.
        @param select_ Select clausule.
        @param where_ Where clausule.
        @param tables_list Tables list.
        @param size_or_conn Size result limits or connection name.
        @param conn connection name.
        @return query value.
        """

        if not isinstance(size_or_conn, int):
            size = 0
            conn = size_or_conn
        else:
            size = size_or_conn

        return utils.sql_select(from_, select_, where_, tables_list, size, conn)

    @classmethod
    def quickSqlSelect(
        cls,
        from_: str,
        select_: str,
        where_: str,
        conn: Union[str, "iconnection.IConnection"] = "default",
    ) -> Any:
        """
        Return a value from a quick query.

        @param from_ From clausule.
        @param select_ Select clausule.
        @param where_ Where clausule.
        @param conn connection name.
        @return query value.
        """

        return utils.quick_sql_select(from_, select_, where_, conn)

    @classmethod
    def sqlInsert(
        cls,
        table_name: str,
        fields_list: Union[str, List, types.Array],
        values_list: Union[str, List, bool, int, float, types.Array],
        conn: Union[str, "iconnection.IConnection"] = "default",
    ) -> Any:
        """
        Insert values to a table.

        @param table_name Table name.
        @param fields_list Field names.
        @param values_list Values.
        @param conn connection name.
        @return query value.
        """

        return utils.sql_insert(table_name, fields_list, values_list, conn)

    @classmethod
    def sqlUpdate(
        cls,
        table_name: str,
        fields_list: Union[str, List, types.Array],
        values_list: Union[str, List, bool, int, float, types.Array],
        where: str,
        conn: Union[str, "iconnection.IConnection"] = "default",
    ) -> bool:
        """
        Update values to a table.

        @param table_name Table name.
        @param fields_list Field names.
        @param values_list Values.
        @param where Where.
        @param conn connection name.
        """

        return utils.sql_update(table_name, fields_list, values_list, where, conn)

    @classmethod
    def sqlDelete(
        cls, table_name: str, where: str, conn: Union[str, "iconnection.IConnection"] = "default"
    ) -> bool:
        """
        Delete a value from a table.

        @param table_name Table name.
        @param where Where.
        @param conn connection name.
        """

        return utils.sql_delete(table_name, where, conn)

    @classmethod
    def quickSqlDelete(
        cls, table_name: str, where: str, conn: Union[str, "iconnection.IConnection"] = "default"
    ) -> bool:
        """
        Quick delete a value from a table.

        @param table_name Table name.
        @param where Where.
        @param conn connection name.
        """

        return utils.quick_sql_delete(table_name, where, conn)

    @classmethod
    def execSql(cls, sql: str, conn: Union[str, "iconnection.IConnection"] = "default") -> bool:
        """
        Set a query to a database.

        @param sql Query.
        @param conn connection name.
        """

        return utils.exec_sql(sql, conn)

    @classmethod
    def createProgressDialog(
        cls, title: str, steps: Union[int, float], id_: str = "default"
    ) -> Any:
        """
        Create a progress dialog.

        @param steps Total number of steps to perform
        @param id_ Probressbar identifier.
        """

        return application.PROJECT.message_manager().send(
            "progress_dialog_manager", "create", [title, steps, id_]
        )

    @classmethod
    def destroyProgressDialog(cls, id_: str = "default") -> None:
        """
        Destroy the progress dialog.

        @param id_ Probressbar identifier.
        """

        application.PROJECT.message_manager().send("progress_dialog_manager", "destroy", [id_])

    @classmethod
    def setProgress(cls, num: Union[int, float], id_: str = "default") -> None:
        """
        Set the degree of progress of the dialogue.

        @param num Degree of progress.
        @param id_ Probressbar identifier.
        """

        application.PROJECT.message_manager().send(
            "progress_dialog_manager", "setProgress", [num, id_]
        )

    @classmethod
    def setLabelText(cls, label: str, id_: str = "default") -> None:
        """
        Change the text of the dialog label.

        @param label Tag.
        @param id_ Probressbar identifier.
        """

        application.PROJECT.message_manager().send(
            "progress_dialog_manager", "setLabelText", [label, id_]
        )

    @classmethod
    def setTotalSteps(cls, num: int, id_: str = "default") -> None:
        """
        Set the total number of steps in the dialog.

        @param num Total number of steps.
        @param id_ Probressbar identifier.
        """

        application.PROJECT.message_manager().send(
            "progress_dialog_manager", "setTotalSteps", [num, id_]
        )

    @classmethod
    def domDocumentSetContent(cls, doc: "QtXml.QDomDocument", content: Any) -> bool:
        """
        Return the content of an XML document.

        Set a DOM document from the XML. Check for errors, and if they exist
        It shows the error found and the line and column where it is located.

        @param doc DOM document to be established
        @param content XML content
        @return FALSE if there was a failure, TRUE otherwise.
        """
        if content:
            if doc.setContent(content):
                return True
            else:
                LOGGER.warning("Error en fichero XML", stack_info=True)
        else:
            LOGGER.warning("Se ha intentado cargar un fichero XML vacío", stack_info=True)

        return False

    @classmethod
    def sha1(cls, value: Union[str, bytes, None] = "") -> str:
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
        string = "%s" % sha_.hexdigest()
        return string.upper()

    @classmethod
    @decorators.not_implemented_warn
    def usha1(cls, data, _len):
        """
        Return the SHA1 key of a data.

        @param str String from which to obtain the SHA1 key.
        @return Corresponding key in hexadecimal digits.
        """
        pass

    @classmethod
    @decorators.not_implemented_warn
    def snapShotUI(cls, field_name):
        """
        Return the image or screenshot of a form.

        @param field_name Name of the file that contains the description of the form.
        """
        pass

    @classmethod
    @decorators.not_implemented_warn
    def saveSnapShotUI(cls, file_name, file_path):
        """
        Save the image or screenshot of a form in a PNG format file.

        @param file_name Name of the file that contains the description of the form.
        @param file_path Path and file name where to save the image
        """
        pass

    @classmethod
    @decorators.not_implemented_warn
    def flDecodeType(cls, fl_type):
        """
        Decode a type of AbanQ to a QVariant type.

        @param fl_type AbanQ data type.
        @return QVariant data type.
        """
        pass

    @classmethod
    @decorators.not_implemented_warn
    def saveIconFile(cls, data, file_path):
        """
        Save the icon image of a button on a form in a png file. Used for documentation.

        @param data Image content in a character string
        @param file_path Full path to the file where the image will be saved
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

        return sysbasetype.SysBaseType.osName()

    @classmethod
    @decorators.not_implemented_warn
    def serialLettertoNumber(cls, letter: str) -> str:
        """
        Convert a string that is a series of letters into its corresponding numerical value.

        @param letter String with the series.
        @return A string but containing numbers.
        """
        return ""

    @classmethod
    @decorators.not_implemented_warn
    def serialNumbertoLetter(cls, number: Union[int, float]) -> str:
        """
        Convert a number to its corresponding sequence of letters.

        @param number Number to convert.
        """
        return ""

    @classmethod
    def findFiles(
        cls, path_: Union[str, List[str]], filter_: str = "*", break_on_first_match: bool = False
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

        list_path: List[str] = []
        files_found: List[str] = []

        if isinstance(path_, str):
            list_path.append(path_)
        else:
            list_path = path_

        for item in list_path:
            for file_name in glob.iglob("%s/**/%s" % (item, filter_), recursive=True):
                files_found.append(file_name)
                if break_on_first_match:
                    break

        return files_found

    @classmethod
    @decorators.not_implemented_warn
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
    def fieldType(cls, field_name: str, table_name: str, conn_name: str = "default") -> int:
        """
        Return the numeric type of a field.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return field type id
        """

        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            return metadata.fieldType(field_name)

        return 0

    @classmethod
    def fieldLength(cls, field_name: str, table_name: str, conn_name: str = "default") -> int:
        """
        Return the length of a field.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return requested field length
        """
        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            return metadata.fieldLength(field_name)

        return 0

    @classmethod
    def fieldNameToAlias(cls, field_name: str, table_name: str, conn_name: str = "default") -> str:
        """
        Return the alias of a field from its name.

        @param field_name. Field Name.
        @param table_name. Name of the table containing the field.
        @param conn_name. Name of the connection to use.
        @return Alias ​​of the specified field.
        """
        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            return metadata.fieldNameToAlias(field_name)

        return field_name

    @classmethod
    def tableNameToAlias(cls, table_name: str = "", conn_name: str = "default") -> str:
        """
        Return the name of a table from its alias.

        @param table_name. Table name
        @param conn_name. Name of the connection to use
        @return Alias ​​of the specified table
        """
        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            return metadata.alias()

        return ""

    @classmethod
    def fieldAliasToName(cls, alias: str, table_name: str, conn_name: str = "default") -> str:
        """
        Return the name of a field from its alias.

        @param alias. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Alias ​​of the specified field
        """
        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            return metadata.fieldAliasToName(alias)

        return alias

    @classmethod
    def fieldAllowNull(cls, field_name: str, table_name: str, conn_name: str = "default") -> bool:
        """
        Return if the field allows to be left blank.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. Whether or not to accept the value of the field
        """

        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            field = metadata.field(field_name)
            if field is not None:
                return field.allowNull()

        return False

    @classmethod
    def fieldIsPrimaryKey(
        cls, field_name: str, table_name: str, conn_name: str = "default"
    ) -> bool:
        """
        Return if the field is the primary key of the table.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. If it is primary key or not
        """

        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            field = metadata.field(field_name)
            if field is not None:
                return field.isPrimaryKey()

        return False

    @classmethod
    def fieldIsCompoundKey(
        cls, field_name: str, table_name: str, conn_name: str = "default"
    ) -> bool:
        """
        Return if the field is a composite key of the table.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Boolean. If it is a composite key or not
        """

        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            field = metadata.field(field_name)
            if field is not None:
                return field.isCompoundKey()

        return False

    @classmethod
    def fieldDefaultValue(cls, field_name: str, table_name: str, conn_name: str = "default") -> Any:
        """
        Return the default value of a field.

        @param field_name. Field Name
        @param table_name. Name of the table containing the field
        @param conn_name. Name of the connection to use
        @return Default field value
        """

        conn = application.PROJECT.conn_manager.useConn(conn_name)
        metadata = conn.connManager().manager().metadata(table_name)
        if metadata is not None:
            field = metadata.field(field_name)
            if field is not None:
                return field.defaultValue()

        return None

    @classmethod
    def formatValue(cls, type_: str, value: Any, upper: bool, conn_name: str = "default") -> str:
        """
        Return formatted value.

        @param type_. Field type
        @param value. Field Value
        @param upper. True if upper else False
        @param conn_name. Name of the connection to use
        @return Formatted Value
        """
        conn = application.PROJECT.conn_manager.useConn(conn_name)
        return conn.connManager().manager().formatValue(type_, value, upper)

    @classmethod
    def nameUser(cls) -> str:
        """Return user name."""
        return sysbasetype.SysBaseType.nameUser()

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

        return sysbasetype.SysBaseType.nameBD()

    def timestamp(cls) -> str:
        """Return timestamp."""

        return QtCore.QDateTime.currentDateTime().toString("ddMMyyyyhhmmsszzz")
