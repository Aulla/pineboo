"""Pdf_qr module."""

from PyQt5 import QtGui, QtCore

from pineboolib import application
from pineboolib.core.utils import logging

from pdf2image import convert_from_path  # type: ignore[import]
from PIL.ImageQt import ImageQt  # type: ignore[import] # toqimage
from PIL import Image  # type: ignore[import]
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
    _signed_data: List["QtGui.QImage"]

    def __init__(self, orig, pos_x, pos_y, all_pages: bool = False) -> None:
        """Initialize."""

        self._orig = orig
        self._pos_x = pos_x
        self._pos_y = pos_y
        self._all_pages = all_pages
        self._size = 5  # 5
        self._text = ""
        self._signed_data = []

    def set_size(self, size: int) -> None:
        """Set size."""

        # (size * 4 ) + 17

        self._size = size

    def set_text(self, text: str) -> None:
        """Set text."""

        self._text = text

    def sign(self) -> bool:
        """Sing file."""

        pages = convert_from_path(
            self._orig, dpi=100, output_folder=application.PROJECT.tmpdir  # size=500
        )
        qr_ = qrcode.QRCode(
            version=self._size,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr_.add_data(self._text)
        qr_.make(fit=False)
        qr_image = qr_.make_image(fill_color="black", back_color="white")
        tmp_qr_file_name = os.path.join(application.PROJECT.tmpdir, "my_qr.jpg")
        qr_image.save(tmp_qr_file_name)

        mark = True
        self._signed_data = []
        for num, page in enumerate(pages):

            page_image = QtGui.QImage(ImageQt(page))
            if mark:
                painter = QtGui.QPainter()
                painter.begin(page_image)
                painter.setCompositionMode(QtGui.QPainter.CompositionMode_SourceOver)
                painter.drawImage(
                    int(self._pos_x), int(self._pos_y), QtGui.QImage(tmp_qr_file_name)
                )
                painter.end()

            self._signed_data.append(page_image)

            if not self._all_pages:
                mark = False

        return True

    def save_file(self, file_path: str) -> bool:
        """save file."""

        if not file_path:
            LOGGER.warning("File path %s is empty!", file_path)
            return False

        if not self._signed_data:
            LOGGER.warning("Data is empty!")
            return False

        image_list = []
        for img_data in self._signed_data:
            buffer = QtCore.QBuffer()
            buffer.open(QtCore.QBuffer.ReadWrite)
            img_data.save(buffer, "PNG")
            image_list.append(Image.open(io.BytesIO(buffer.data())))  # type: ignore[arg-type] # noqa: F821

        if len(image_list) > 1:
            image_list[0].save(file_path, save_all=True, append_images=image_list[1:])
        else:
            image_list[0].save(file_path, save_all=True)

        return True
