# -*- coding: utf-8 -*-
"""
Variety of tools for KUT.
"""
import os
import sys
import datetime
import fnmatch
from xml.etree.ElementTree import Element, ElementTree
from typing import Any, Iterable, Optional, List

from pineboolib import logging
from pineboolib.core.utils.utils_base import load2xml
from pineboolib.application.utils import date_conversion, xpm
from pineboolib.core import settings

from PyQt6 import QtXml, QtCore  # type: ignore[import]

from pineboolib.application.database import pnsqlquery

LOGGER = logging.get_logger(__name__)


class KParserTools(object):
    """
    Common functions for different KUT parsers.
    """

    _fix_altura = None

    def __init__(self) -> None:
        """Create base class for tools."""

        self.pagina = 0
        self._fix_ratio_h = 0.927  # Corrector de altura 0.927
        self._fix_ratio_w = 0.92

    def loadKut(self, data: str) -> "ElementTree":
        """
        Parse KUT xml from text.

        @param data. Input text (kut sources)
        @return xml.
        """
        return load2xml(data)

    def ratio_correction_h(self, value: float) -> int:
        """
        Revise height to become similar to the original kut.

        @param value. Input number to revise.
        @return Revised number.
        """
        return int(value * self._fix_ratio_h)

    def ratio_correction_w(self, value: float) -> int:
        """
        Revise width to become similar to the original kut.

        @param value. Input number to revise.
        @return Revised number.
        """
        return int(value * self._fix_ratio_w)

    def convertToNode(self, data: Element) -> "QtXml.QDomElement":
        """
        Convert XML line to Node XML.

        When it's a calculatedField sends data to QSA of Node type.
        @param data. xml with related line info.
        @return Node with original data contents.
        """

        # node = Node()

        doc = QtXml.QDomDocument()
        ele = doc.createElement("element")
        for k in data.keys():
            attr_node = doc.createAttribute(k)
            attr_node.setValue(data.get(k) or "")
            ele.setAttributeNode(attr_node)

        return ele

    def getHeight(self, xml: Element) -> int:
        """
        Retrieve height specified in xaml.

        @param xml. Element to extract the height from.
        @return Height or zero if does not exist.
        """
        return int(xml.get("Height") or "0")

    def getSpecial(self, name: str, page_num: Optional[int] = None) -> str:
        """
        Retrieve value of special type.

        @param name. Name of special type to load.
        @param page_num. PAge number if it is "PageNo" type.
        @return Required value.
        """
        LOGGER.debug("%s:getSpecial %s" % (__name__, name))
        ret = "None"
        if name:
            if name[0] == "[":
                name = name[1:-1]
            if name in ("Fecha", "Date"):
                ret = str(datetime.date.__format__(datetime.date.today(), "%d-%m-%Y"))
            elif name in ("NúmPágina", "PageNo", "NÃºmPÃ¡gina"):
                ret = str(page_num)

        return ret

    def calculated(
        self, value: Any, data_type: int, xml: "Element" = None, data: "Element" = None
    ) -> Any:
        """
        Get value of type "calculated".

        @param field. Field name
        @param dataType. Data type. Changes how value is returned.
        @param precision. Number of decimal places.
        @param data. XML data line related.
        @return calculated value.
        """

        precision = 0
        type_ = None
        date_format_num = None

        if xml is not None:
            precision = int(xml.get("Precision") or 0)
            type_ = xml.get("Type")
            date_format_num = xml.get("DateFormat")

        if data_type in (0, 1) and data is not None:  # str
            value = data.get(value)

        elif data_type == 2:  # float

            if type_ is None:
                if value not in (None, "None"):
                    value = QtCore.QLocale.system().toString(float(value), "f", precision)

        elif data_type == 3:  # time
            if value.find("T") > -1:
                value = date_conversion.date_amd_to_dma(value[: value.find("T")])

            sep = "-"
            if date_format_num is not None:
                if date_format_num == "11":
                    value = value.replace(sep, ".")
                elif date_format_num == "18":
                    value = value.replace(sep, "/")
                elif date_format_num == "19":
                    value = value.replace(sep, "-")
                else:
                    LOGGER.warning("UNKNOWN DateFormat %s --> %s", date_format_num, value)
        elif data_type == 4:  # currency

            if value not in (None, "None"):
                float_value = float(value)
                if float_value < -0.01 or float_value > 0.01:
                    value = QtCore.QLocale.system().toString(float_value, "f", 2)

        elif data_type == 5:  # 5 pixmap
            pass

        elif data_type == 6:  # 6 barcode
            pass

        elif data_type == 7:  # bool
            value = "No" if str(value).upper() in ["FALSE", "F", "0"] else "Sí"

        elif data is not None:
            value = data.get(value)

        return value

    def parseKey(self, ref_key: Optional[str] = None) -> Optional[str]:
        """
        Get filename of .png file cached on tempdata. If it does not exist it is created.

        @param. String of related tuple in fllarge.
        @return. Path to the file in tempdata.
        """

        ret = None
        table_name = "fllarge"
        if ref_key is not None:
            from PyQt6.QtGui import QPixmap  # type: ignore[import]

            value = None
            tmp_dir = settings.CONFIG.value("ebcomportamiento/temp_dir")
            img_file = "%s/%s.png" % (tmp_dir, ref_key)

            if not os.path.exists(img_file) and ref_key[0:3] == "RK@":

                single_query = pnsqlquery.PNSqlQuery()
                single_query.exec_("SELECT valor FROM flsettings WHERE flkey='FLLargeMode'")
                one_fllarge = True

                if single_query.next():
                    if single_query.value(0) == "True":
                        one_fllarge = False

                if (
                    not one_fllarge
                ):  # Si no es FLLarge modo único añadimos sufijo "_nombre" a fllarge
                    table_name += "_%s" % ref_key.split("@")[1]

                qry = pnsqlquery.PNSqlQuery()
                if qry.exec_("SELECT contenido FROM %s WHERE refkey='%s'" % (table_name, ref_key)):
                    if qry.next():
                        value = xpm.cache_xpm(qry.value(0))

                if value:
                    ret = img_file
                    pix = QPixmap(value)
                    if not pix.save(img_file):
                        LOGGER.warning(
                            "%s:refkey2cache No se ha podido guardar la imagen %s"
                            % (__name__, img_file)
                        )
                        ret = None
                    else:
                        ret = img_file
            elif ref_key.endswith(".xpm"):
                pix = QPixmap(ref_key)
                img_file = ref_key.replace(".xpm", ".png")
                if not pix.save(img_file):
                    LOGGER.warning(
                        "%s:refkey2cache No se ha podido guardar la imagen %s"
                        % (__name__, img_file)
                    )
                    ret = None
                else:
                    ret = img_file

            else:

                ret = img_file

        return ret

    def convertPageSize(
        self, size: int, orientation: int, custom: Optional[List[int]] = None
    ) -> List[int]:
        """
        Get page size for the page code specified on .kut file.

        @param size. Size code specified on doc (0..31).
        @param orientation. 0 portrait, 1 landscape.
        @param custom. Where size is (30 or 31), custom is returned.
        @return Array with the size values.
        """
        result = None
        if size == 0:
            result = [595, 842]  # "A4"
        elif size == 1:
            result = [709, 499]  # "B5"
        elif size == 2:
            result = [612, 791]  # "LETTER"
        elif size == 3:
            result = [612, 1009]  # "legal"
        elif size == 5:
            result = [2384, 3370]  # "A0"
        elif size == 6:
            result = [1684, 2384]  # "A1"
        elif size == 7:
            result = [1191, 1684]  # "A2"
        elif size == 8:
            result = [842, 1191]  # "A3"
        elif size == 9:
            result = [420, 595]  # "A5"
        elif size == 10:
            result = [298, 420]  # "A6"
        elif size == 11:
            result = [210, 298]  # "A7"
        elif size == 12:
            result = [147, 210]  # "A8"
        elif size == 13:
            result = [105, 147]  # "A9"
        elif size == 14:
            result = [4008, 2835]  # "B0"
        elif size == 15:
            result = [2835, 2004]  # "B1"
        elif size == 16:
            result = [125, 88]  # "B10"
        elif size == 17:
            result = [2004, 1417]  # "B2"
        elif size == 18:
            result = [1417, 1001]  # "B3"
        elif size == 19:
            result = [1001, 709]  # "B4"
        elif size == 20:
            result = [499, 354]  # "B6"
        elif size == 21:
            result = [324, 249]  # "B7"
        elif size == 22:
            result = [249, 176]  # "B8"
        elif size == 23:
            result = [176, 125]  # "B9"
        elif size == 24:
            result = [649, 459]  # "C5"
        elif size == 25:
            result = [113, 79]  # "C10"
        elif size == 28:
            result = [1255, 791]  # "LEDGER"
        elif size == 29:
            result = [791, 1255]  # "TABLOID"
        elif size in (30, 31):
            result = custom  # "CUSTOM"
        if result is None:
            LOGGER.warning("porcessXML:No se encuentra pagesize para %s. Usando A4" % size)
            result = [595, 842]

        # if orientation != 0:
        #    r = [r[1], r[0]]

        return result

    def find_font(self, font_name: str, font_style: str) -> Optional[str]:
        """
        Find and retrieve path for a specified font.

        @param font_name. Font name required
        @return Path to ".ttf" or None
        """
        fonts_folders: List[str] = []
        if sys.platform.find("darwin") > -1:
            fonts_folders = ["/Library/Fonts", "/System/Library/Fonts", "~/Library/Fonts"]

        elif sys.platform.find("win") > -1:
            windirs = os.environ.get("WINDIR")
            if windirs is None:
                raise Exception("WINDIR environ not found!")

            for win_dir in windirs.split(";"):
                fonts_folders.append(os.path.join(win_dir, "fonts"))

        elif sys.platform.find("linux") > -1:
            lindirs = os.environ.get("XDG_DATA_DIRS", "")
            if not lindirs:
                lindirs = "usr/share"

            for lin_dir in lindirs.split(":"):
                fonts_folders.append(os.path.join(lin_dir, "fonts"))
        else:
            LOGGER.warning("KUTPARSERTOOLS: Plataforma desconocida %s", sys.platform)
            return None

        font_name = font_name.replace(" ", "_")

        font_name = font_name
        font_name2 = font_name
        font_name3 = font_name

        if font_name.endswith("BI"):
            font_name2 = font_name.replace("BI", "_Bold_Italic")
            font_name3 = font_name.replace("BI", "bi")

        if font_name.endswith("B"):
            font_name2 = font_name.replace("B", "_Bold")
            font_name3 = font_name.replace("B", "b")

        if font_name.endswith("I"):
            font_name2 = font_name.replace("I", "_Italic")
            font_name3 = font_name.replace("I", "i")

        for folder in fonts_folders:
            for root, dirnames, filenames in os.walk(folder):

                for filename in fnmatch.filter(filenames, "%s.ttf" % font_name):
                    ret_ = os.path.join(root, filename)
                    return ret_

                for filename in fnmatch.filter(
                    filenames, "%s%s.ttf" % (font_name[0].upper(), font_name[1:])
                ):
                    ret_ = os.path.join(root, filename)
                    return ret_

                for filename in fnmatch.filter(filenames, "%s.ttf" % font_name2):
                    ret_ = os.path.join(root, filename)
                    return ret_

                for filename in fnmatch.filter(
                    filenames, "%s%s.ttf" % (font_name2[0].upper(), font_name2[1:])
                ):
                    ret_ = os.path.join(root, filename)
                    return ret_

                for filename in fnmatch.filter(filenames, "%s.ttf" % font_name3):
                    ret_ = os.path.join(root, filename)
                    return ret_

                for filename in fnmatch.filter(
                    filenames, "%s%s.ttf" % (font_name3[0].upper(), font_name3[1:])
                ):
                    ret_ = os.path.join(root, filename)
                    return ret_

        return None

    def calculate_sum(self, field_name: str, line: Element, xml_list: Iterable, level: int) -> str:
        """
        Calculate sum for specified element line. level equal or upper.
        """
        val = 0.0
        min_level = -1
        last_level = -1
        for item in xml_list:
            lev_ = int(item.get("level"))
            val_ = float(item.get(field_name))

            if min_level < lev_ or lev_ < last_level:
                # print("nuevo min_level", lev_, "previo", min_level)
                min_level = lev_
                val = 0.0

            if min_level >= level and lev_ >= level:
                val += val_

            # print(
            #    "line_level:",
            #    lev_,
            #    "line_val:",
            #    val_,
            #    "obj_level:",
            #    level,
            #    "current_val:",
            #    val,
            #    "min_level:",
            #    min_level,
            # )
            if item is line:
                break

            last_level = lev_

        return str(val)

    def restore_text(self, text: str) -> str:
        """Un-replace text for special characters."""
        ret_ = text
        ret_ = ret_.replace("__RPAREN__", ")")
        ret_ = ret_.replace("__LPAREN__", "(")
        ret_ = ret_.replace("__ASTERISK__", "*")
        ret_ = ret_.replace("__PLUS__", "+")

        return ret_
