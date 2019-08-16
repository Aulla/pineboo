"""Flcodbar module."""

# # -*- coding: utf-8 -*-
from PyQt5 import QtCore, Qt  # type: ignore
from PyQt5.Qt import QRectF  # type: ignore
from PyQt5.QtGui import QPixmap, QColor  # type: ignore
from pineboolib.core.utils.utils_base import load2xml
from PyQt5.QtSvg import QSvgRenderer  # type: ignore

from pineboolib import logging

import barcode  # type: ignore # pip3 install python-barcode
from typing import Dict, Any, Union, cast, Optional

logger = logging.getLogger(__name__)

BARCODE_ANY: int = 0
BARCODE_EAN: int = 1
BARCODE_EAN_8: int = 2
BARCODE_EAN_13: int = 3
BARCODE_EAN_14: int = 4
BARCODE_UPC: int = 5
BARCODE_UPC_A: int = 6
BARCODE_JAN: int = 7
BARCODE_ISBN: int = 8
BARCODE_ISBN_10: int = 9
BARCODE_ISBN_13: int = 10
BARCODE_ISSN: int = 11
BARCODE_39: int = 12
BARCODE_128: int = 13
BARCODE_PZN: int = 14
BARCODE_ITF: int = 15
BARCODE_GS1: int = 16
BARCODE_GTIN: int = 17


class FLCodBar(object):
    """FLCodBar class."""

    barcode: Dict[str, Any]
    p: Optional[QPixmap]
    pError: QPixmap

    def __init__(
        self,
        value: Union[None, int, str, Dict[str, Any]] = None,
        type_: int = BARCODE_128,
        margin: int = 10,
        scale: float = 1.0,
        cut: float = 1.0,
        rotation: int = 0,
        text_flag: bool = False,
        fg: QColor = cast(QColor, QtCore.Qt.black),
        bg: QColor = cast(QColor, QtCore.Qt.white),
        res: int = 72,
    ) -> None:
        """Inicialize."""

        dict_ = {"barcode": "python-barcode"}
        from pineboolib.application.utils.check_dependencies import check_dependencies

        check_dependencies(dict_)
        self.pError = QPixmap()
        self.barcode = {}
        self.barcode["value"] = ""
        self.p = None

        if value in [None, 0]:
            self.readingStdout = False
            self.writingStdout = False
            self.fillDefault(self.barcode)
        else:
            if isinstance(value, str):
                self.readingStdout = False
                self.writingStdout = False
                self.barcode["value"] = value
                self.barcode["type"] = type_
                self.barcode["margin"] = margin
                self.barcode["scale"] = scale
                self.barcode["cut"] = cut
                self.barcode["rotation"] = rotation
                self.barcode["text"] = text_flag
                self.barcode["fg"] = fg
                self.barcode["bg"] = bg
                self.barcode["valid"] = False
                self.barcode["res"] = res
            elif isinstance(value, int):
                raise ValueError("Not supported")
            elif isinstance(value, dict):
                self._copyBarCode(value, self.barcode)

    def pixmap(self) -> QPixmap:
        """Return pixmap barcode."""

        self._createBarcode()

        if not self.p:
            self.barcode["valid"] = False
            return self.pixmapError()

        return self.p

    def pixmapError(self) -> QPixmap:
        """Return empy pixmap barcode."""

        return self.pError

    def value(self) -> Any:
        """Return value."""
        return self.barcode["value"]

    def type_(self) -> int:
        """Return type."""

        return self.barcode["type"]

    def margin(self) -> int:
        """Return margin."""

        return self.barcode["margin"]

    def scale(self) -> float:
        """Return scale."""

        return self.barcode["scale"]

    def cut(self) -> float:
        """Return cut."""
        return self.barcode["cut"]

    def text(self) -> str:
        """Return text."""

        return self.barcode["text"]

    def rotation(self) -> int:
        """Return rotation."""

        return self.barcode["rotation"]

    def fg(self) -> QColor:
        """Return fore ground color."""

        return self.barcode["fg"]

    def bg(self) -> QColor:
        """Return back ground color."""
        return self.barcode["bg"]

    def setData(self, d: Dict[str, Any]) -> None:
        """Set barcode data."""

        self.barcode = d

    def validBarcode(self) -> bool:
        """Return if is a valid barcode."""

        return self.barcode["valid"]

    def setCaption(self, caption: str) -> None:
        """Set caption barcode."""

        self.barcode["caption"] = caption

    def caption(self) -> str:
        """Return caption barcode."""

        return self.barcode["caption"]

    def setValue(self, value: Any) -> None:
        """Set value."""

        self.barcode["value"] = value

    def setType(self, type_: int) -> None:
        """Set type."""
        self.barcode["type"] = type_

    def setMargin(self, margin: int) -> None:
        """Set margin size."""
        self.barcode["margin"] = margin

    def setScale(self, scale: float) -> None:
        """Set scale."""
        self.barcode["scale"] = scale

    def setCut(self, cut: float) -> None:
        """Set cut size."""
        self.barcode["cut"] = cut

    def setText(self, text: str) -> None:
        """Set text size."""
        self.barcode["text"] = text

    def setRotation(self, rotation: int) -> None:
        """Set rotation size."""
        self.barcode["rotation"] = rotation

    def setFg(self, fg) -> None:
        """Set fore ground color."""
        self.barcode["fg"] = fg

    def setBg(self, bg: QColor) -> None:
        """Set back ground color."""
        self.barcode["bg"] = bg

    def setRes(self, res: int) -> None:
        """Set resolution."""

        self.barcode["res"] = res

    def data(self) -> Dict[str, Any]:
        """Return barcode data."""
        return self.barcode

    def fillDefault(self, data: Dict[str, Any]) -> None:
        """Fill with default values."""

        data["bg"] = "white"
        data["fg"] = "black"
        data["margin"] = 10
        data["text"] = True
        data["value"] = "1234567890"
        data["type"] = BARCODE_39
        data["scale"] = 1.0
        data["cut"] = 1.0
        data["rotation"] = 0
        data["caption"] = "Static"
        data["valid"] = False
        data["res"] = 72

    def cleanUp(self) -> None:
        """Clean barcode data."""

        if self.p:
            self.p.resize(0, 0)
        self.pError.resize(0, 0)

    def nameToType(self, name: str) -> int:
        """Return barcode  name from type."""
        n = name.lower()
        if n == "any":
            return BARCODE_ANY
        elif n == "ean":
            return BARCODE_EAN
        elif n == "ean-8":
            return BARCODE_EAN_8
        elif n == "ean-13":
            return BARCODE_EAN_13
        elif n == "ean-14":
            return BARCODE_EAN_14
        elif n == "upc":
            return BARCODE_UPC
        elif n == "upc-a":
            return BARCODE_UPC_A
        elif n == "jan":
            return BARCODE_JAN
        elif n == "isbn":
            return BARCODE_ISBN
        elif n == "isbn-10":
            return BARCODE_ISBN_10
        elif n == "isbn-13":
            return BARCODE_ISBN_13
        elif n == "issn":
            return BARCODE_ISSN
        elif n == "code39":
            return BARCODE_39
        elif n == "code128":
            return BARCODE_128
        elif n == "pzn":
            return BARCODE_PZN
        elif n == "itf":
            return BARCODE_ITF
        elif n == "gs1":
            return BARCODE_GS1
        elif n == "gtin":
            return BARCODE_GTIN
        else:
            logger.warning(
                "Formato no soportado (%s)\nSoportados: %s." % (n, barcode.PROVIDED_BARCODES)
            )
            return BARCODE_ANY

    def typeToName(self, type_: int) -> str:
        """Return barcode type from barcode name."""
        if type_ == BARCODE_ANY:
            return "ANY"
        elif type_ == BARCODE_EAN:
            return "EAN"
        elif type_ == BARCODE_EAN_8:
            return "EAN-8"
        elif type_ == BARCODE_EAN_13:
            return "EAN-13"
        elif type_ == BARCODE_EAN_14:
            return "EAN-14"
        elif type_ == BARCODE_UPC:
            return "UPC"
        elif type_ == BARCODE_UPC_A:
            return "UPC-A"
        elif type_ == BARCODE_JAN:
            return "JAN"
        elif type_ == BARCODE_ISBN:
            return "ISBN"
        elif type_ == BARCODE_ISBN_10:
            return "ISBN-10"
        elif type_ == BARCODE_ISBN_13:
            return "ISBN-13"
        elif type_ == BARCODE_ISSN:
            return "ISSN"
        elif type_ == BARCODE_39:
            return "Code39"
        elif type_ == BARCODE_128:
            return "Code128"
        elif type_ == BARCODE_PZN:
            return "PZN"
        elif type_ == BARCODE_ITF:
            return "ITF"
        elif type_ == BARCODE_GS1:
            return "GS1"
        elif type_ == BARCODE_GTIN:
            return "GTIN"
        else:
            return "ANY"

    def _createBarcode(self) -> None:
        """Create barcode."""
        if self.barcode["value"] == "":
            return
        if self.barcode["type"] == BARCODE_ANY:
            logger.warning("Usando %s por defecto" % self.typeToName(BARCODE_128))
            self.barcode["type"] = BARCODE_128

        type_ = self.typeToName(self.barcode["type"])
        value_ = self.barcode["value"]
        bg_ = self.barcode["bg"]
        fg_ = self.barcode["fg"]
        if not isinstance(self.barcode["bg"], str):
            bg_ = QColor(self.barcode["bg"]).name()

        if not isinstance(self.barcode["fg"], str):
            fg_ = QColor(self.barcode["fg"]).name()

        margin_ = self.barcode["margin"] / 10

        render_options: Dict[str, Any] = {}
        render_options["module_width"] = 0.6
        render_options["module_height"] = 10
        render_options["background"] = bg_.lower()
        render_options["foreground"] = fg_.lower()
        render_options["font_size"] = 8
        render_options["write_text"] = self.barcode["text"]
        render_options["text_distance"] = 35
        render_options["quiet_zone"] = margin_
        if self.barcode["text"]:
            render_options["text"] = value_
        else:
            render_options["text"] = " "

        barC = barcode.get_barcode_class(type_.lower())
        try:
            bar_ = barC(u"%s" % value_)
        except Exception:
            bar_ = barC("000000000000")

        svg = bar_.render(render_options)
        xml_svg = load2xml(svg.decode("utf-8")).getroot()
        xwidth, xheight = xml_svg.get("width"), xml_svg.get("height")
        if xwidth and xheight:
            svg_w = 3.779 * float(xwidth[0:6])
            svg_h = 3.779 * float(xheight[0:6])
        else:
            logger.warning("width or height missing")
            svg_w = 0.0
            svg_h = 0.0
        self.p = QPixmap(int(svg_w), int(svg_h))
        render = QSvgRenderer(svg)
        self.p.fill(QtCore.Qt.transparent)
        painter = Qt.QPainter(self.p)
        render.render(painter, QRectF(0, 0, svg_w * 3.4, svg_h * 3.4))

        if self.p.isNull():
            self.barcode["valid"] = False
        else:

            if self.barcode["scale"] != 1.0:
                wS_ = self.barcode["x"] * self.barcode["scale"]
                hS_ = self.barcode["y"] * self.barcode["scale"]
                self.p = self.p.scaled(wS_, hS_)

            self.barcode["x"] = self.p.width()
            self.barcode["y"] = self.p.height()

            self.barcode["valid"] = True

    def _copyBarCode(self, source: Dict[str, Any], dest: Dict[str, Any]) -> None:
        """Copy a new barcode from another."""

        dest["value"] = source["value"]
        dest["type"] = source["type"]
        dest["margin"] = source["margin"]
        dest["scale"] = source["scale"]
        dest["cut"] = source["cut"]
        dest["rotation"] = source["rotation"]
        dest["text"] = source["text"]
        dest["caption"] = source["caption"]
        dest["valid"] = source["valid"]
        dest["fg"] = source["fg"]
        dest["bg"] = source["bg"]
        dest["x"] = source["x"]
        dest["y"] = source["y"]
        dest["res"] = source["res"]
