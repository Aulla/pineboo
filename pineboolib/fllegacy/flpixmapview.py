"""Flpixmapview module."""
# -*- coding: utf-8 -*-
from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore
from typing import cast


class FLPixmapView(QtWidgets.QScrollArea):
    """FLPixmapView class."""

    # frame_ = None
    # scrollView = None
    _auto_scaled: bool
    _path: str
    _pixmap: QtGui.QPixmap
    _pixmapview: QtWidgets.QLabel
    _lay: QtWidgets.QHBoxLayout
    # gB_ = None
    _parent: QtWidgets.QWidget

    def __init__(self, parent: QtWidgets.QWidget) -> None:
        """Inicialize."""

        super(FLPixmapView, self).__init__(parent)
        self._auto_scaled = False
        self._lay = QtWidgets.QHBoxLayout(self)
        self._lay.setContentsMargins(0, 2, 0, 2)
        self._pixmap = QtGui.QPixmap()
        self._pixmapview = QtWidgets.QLabel(self)
        self._lay.addWidget(self._pixmapview)
        self._pixmapview.setAlignment(
            cast(
                QtCore.Qt.AlignmentFlag,
                QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignCenter,
            )
        )
        self._pixmapview.installEventFilter(self)
        self.setStyleSheet("QScrollArea { border: 1px solid darkgray; border-radius: 3px; }")
        self._parent = parent

    def setPixmap(self, pix: QtGui.QPixmap) -> None:
        """Set pixmap to object."""
        # if not project.DGI.localDesktop():
        #    project.DGI._par.addQueque("%s_setPixmap" % self._parent.objectName(
        #    ), self._parent.cursor_.valueBuffer(self._parent.fieldName_))
        #    return

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        self._pixmap = pix
        if self._pixmapview is not None:
            self._pixmapview.clear()
            self._pixmapview.setPixmap(self._pixmap)
        self.repaint()
        QtWidgets.QApplication.restoreOverrideCursor()

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Event filter process."""

        if isinstance(obj, QtWidgets.QLabel) and isinstance(event, QtGui.QResizeEvent):
            self.resizeContents()

        return super().eventFilter(obj, event)

    def resizeContents(self) -> None:
        """Resize contents to actual control size."""

        if self._pixmap is None or self._pixmap.isNull():
            return

        new_pix = self._pixmap
        if (
            self._auto_scaled is not None
            and self._pixmap is not None
            and self._pixmapview is not None
        ):
            if (
                self._pixmap.height() > self._pixmapview.height()
                or self._pixmap.width() > self._pixmapview.width()
            ):
                new_pix = self._pixmap.scaled(
                    self._pixmapview.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )

            elif (
                self._pixmap.height() < self._pixmapview.pixmap().height()
                or self._pixmap.width() < self._pixmapview.pixmap().width()
            ):
                new_pix = self._pixmap.scaled(
                    self._pixmapview.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio
                )

        if self._pixmapview is not None:
            self._pixmapview.clear()
            self._pixmapview.setPixmap(new_pix)

    def previewUrl(self, url: str) -> None:
        """Set image from url."""

        qurl = QtCore.QUrl(url)
        if qurl.isLocalFile():
            path = qurl.path()

        if not path == self._path:
            self._path = path
            img = QtGui.QImage(self._path)

            if img is None:
                return

            pix = QtGui.QPixmap()
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
            pix.convertFromImage(img)
            QtWidgets.QApplication.restoreOverrideCursor()

            if pix is not None:
                self.setPixmap(pix)

    def clear(self) -> None:
        """Clear image into object."""

        if self._pixmapview is not None:
            self._pixmapview.clear()

    def pixmap(self) -> QtGui.QPixmap:
        """Return pixmap stored."""

        return self._pixmap

    def setAutoScaled(self, auto_scaled: bool) -> None:
        """Set auto sclate to the control."""

        self._auto_scaled = auto_scaled
