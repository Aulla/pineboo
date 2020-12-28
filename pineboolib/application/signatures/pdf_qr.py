"""Pdf_qr module."""

from PyQt5 import QtGui, QtCore

from pineboolib import application
from pineboolib.core.utils import logging

from pdf2image import convert_from_path  # type: ignore[import]
from PIL import Image, ImageQt  # type: ignore[import]
import os
import io
import qrcode  # type: ignore[import]


from typing import List

LOGGER = logging.get_logger(__name__)


class pdfQr:
    """PdfQr class."""

    _orig: str
    _pos_x: int
    _pos_y: int
    _all_pages: bool
    _size: int
    _text: str
    _qr_text: str
    _signed_data: List["QtGui.QImage"]
    _font_name: str
    _font_size: int
    _show_text: bool
    _dpi: int

    def __init__(self, orig) -> None:
        """Initialize."""

        self._orig = orig
        self._pos_x = 100
        self._pos_y = 100
        self._all_pages = False
        self._size = 5  # 5
        self._text = ""
        self._qr_text = ""
        self._signed_data = []
        self._font_name = "Arial"
        self._font_size = 8
        self._show_text = False
        self._dpi = 300

    def set_size(self, size: int) -> None:
        """Set size."""

        # (size * 4 ) + 17

        self._size = size

    def set_dpi(self, dpi: int = 300) -> None:
        """Set dpi."""

        self._dpi = int(dpi)

    def set_text(self, qr_text: str, text: str = "") -> None:
        """Set text."""

        self._qr_text = qr_text
        if not text:
            self._show_text = False
            text = qr_text
        else:
            self._show_text = True
        self._text = text

    def set_font(self, name: str, size: int) -> None:
        """Set font name and size."""

        self._font_name = name
        self._font_size = size

    def set_position(self, pos_x: int, pos_y: int) -> None:
        """Set Possition. 0,0 = Bottom Right."""
        self._pos_x = int(pos_x)
        self._pos_y = int(pos_y)

    def sign(self, all_pages: bool = False) -> bool:
        """Sing file."""

        self._all_pages = all_pages

        qr_ = qrcode.QRCode(
            version=self._size,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=3,
            border=4,
        )  # 135 px x 135 px = (35.89 mm x 35.89 mm)
        qr_.add_data(self._qr_text)
        qr_.make(fit=False)
        qr_image = qr_.make_image(fill_color="black", back_color="white")

        tmp_qr_file_name = os.path.join(application.PROJECT.tmpdir, "my_qr.PNG")
        qr_image.save(tmp_qr_file_name, "PNG")

        # qr_image.height
        signed_image = None
        factor = self._dpi / 100
        if self._show_text:
            image_qr = QtGui.QImage(tmp_qr_file_name)
            image_label = QtGui.QImage(tmp_qr_file_name)
            text_width = len(self._text) * 2.7
            image_label_resized = image_label.scaled(
                (qr_image.height + text_width) * factor,
                (qr_image.height + (self._font_size + 2)) * factor,
            )
            image_qr = image_qr.scaled(
                int(image_qr.width() * factor), int(image_qr.height() * factor)
            )
            image_label_resized.fill(0)
            label_painter = QtGui.QPainter()
            label_painter.begin(image_label_resized)
            label_painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            label_painter.setPen(QtGui.QPen(QtCore.Qt.black))
            label_painter.setFont(
                QtGui.QFont(self._font_name, int(self._font_size * factor), QtGui.QFont.Bold)
            )
            label_painter.drawText(image_label_resized.rect(), QtCore.Qt.AlignTop, " " + self._text)
            label_painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
            label_painter.drawImage(
                image_label_resized.width() - image_qr.width(),
                int((self._font_size + 2) * factor),
                image_qr,
            )
            label_painter.end()
            signed_image = image_label_resized
        else:
            signed_image = QtGui.QImage(tmp_qr_file_name)
            signed_image = signed_image.scaled(
                int(signed_image.width() * factor), int(signed_image.height() * factor)
            )

        mark = True
        pos_x = self._pos_x
        pos_y = self._pos_y
        self._signed_data = []
        pages = convert_from_path(
            self._orig, dpi=self._dpi, output_folder=application.PROJECT.tmpdir  # size=500
        )
        for num, page in enumerate(pages):
            page_image = ImageQt.ImageQt(page)
            if mark:
                painter = QtGui.QPainter()
                painter.begin(page_image)
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
                painter.drawImage(
                    page_image.width() - (pos_x * factor) - signed_image.width(),
                    page_image.height() - (pos_y * factor) - signed_image.height(),
                    signed_image,
                )
                painter.end()

            self._signed_data.append(page_image)

            if not self._all_pages:
                mark = False

        return True

    def save_file(self, file_path: str) -> bool:
        """Save file."""

        if not file_path:
            LOGGER.warning("File path %s is empty!", file_path)
            return False

        if not self._signed_data:
            LOGGER.warning("Data is empty!")
            return False

        first = True
        for img_data in self._signed_data:

            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QBuffer.ReadWrite)
            img_data.save(buffer, "PNG")
            page = Image.open(io.BytesIO(buffer.data()))  # type: ignore[arg-type]
            page.save(
                file_path,
                resolution=self._dpi,
                append=not first,
                author="Pineboo ERP",
                title="pdf signed",
            )
            first = False

        return True
