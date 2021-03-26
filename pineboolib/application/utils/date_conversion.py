"""
Convert a date to different formats.
"""

import datetime
from PyQt5 import QtCore  # type: ignore
from PyQt5.QtCore import QDate  # type: ignore
from typing import Optional, List, Any


def date_dma_to_amd(date_str: str) -> Optional[str]:
    """
    Convert day, month, year to year, month day.

    @param date_str: date string.
    @return date string formated.
    """

    if not date_str:
        return None

    date_str = str(date_str)
    if date_str.find("T") > -1:
        date_str = date_str[: date_str.find("T")]

    array_: List[str] = []
    dia_ = None
    mes_ = None
    ano_ = None

    if date_str.find("-") > -1:
        array_ = date_str.split("-")
    elif date_str.find("/") > -1:
        array_ = date_str.split("/")

    if array_:
        if len(array_) == 3:
            if len(array_[0]) == 2:
                dia_ = array_[0]
                mes_ = array_[1]
                ano_ = array_[2]
            else:
                dia_ = array_[2]
                mes_ = array_[1]
                ano_ = array_[0]
        else:
            dia_ = date_str[0:2]
            mes_ = date_str[2:2]
            ano_ = date_str[4:4]

    return "%s-%s-%s" % (ano_, mes_, dia_) if ano_ else ""


def date_amd_to_dma(date_str: str) -> Optional[str]:
    """
    Convert year, month day to day, month, year.

    @param date_str: date string.
    @return date string formated.
    """

    if not date_str:
        return None

    date_str = str(date_str)
    if date_str.find("T") > -1:
        date_str = date_str[: date_str.find("T")]

    array_: List[str] = []
    dia_ = None
    mes_ = None
    ano_ = None
    if date_str.find("-") > -1:
        array_ = date_str.split("-")
    elif date_str.find("/") > -1:
        array_ = date_str.split("/")

    if array_:
        if len(array_) == 3:
            if len(array_[0]) == 4:
                dia_ = array_[2]
                mes_ = array_[1]
                ano_ = array_[0]
            else:
                dia_ = array_[0]
                mes_ = array_[1]
                ano_ = array_[2]
        else:
            ano_ = date_str[0:4]
            mes_ = date_str[4:2]
            dia_ = date_str[6:2]

    return "%s-%s-%s" % (dia_, mes_, ano_) if ano_ else ""


def convert_to_qdate(date: Any) -> QDate:
    """
    Convert different date formats to QDate.

    @param date: Date to convert.
    @return QDate with the value of the given date.
    """

    internal_date = getattr(date, "date_", None)  # For types.Date
    if internal_date is not None:
        date = date.toString()  # QDate -> str
    elif isinstance(date, datetime.date):
        date = str(date)

    if isinstance(date, str):
        if "T" in date:
            date = date[: date.find("T")]

        date = date_amd_to_dma(date) if len(date.split("-")[0]) == 4 else date
        date = QtCore.QDate.fromString(date, "dd-MM-yyyy")

    return date
