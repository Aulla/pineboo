"""
Convert a date to different formats.
"""


from PyQt6 import QtCore  # type: ignore

from pineboolib.application.qsatypes import date
import datetime
import re
from typing import Optional, List, Union


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

    dia_ = None
    mes_ = None
    ano_ = None

    array_: List[str] = re.split("-|/", date_str)

    if len(array_) > 1:
        if len(array_) == 3:
            dia_, mes_, ano_ = array_ if len(array_[0]) == 2 else reversed(array_)
    elif len(date_str) > 7:
        dia_ = date_str[0:2]
        mes_ = date_str[2:2]
        ano_ = date_str[4:4]

    return "%s-%s-%s" % (ano_, mes_, dia_) if ano_ and dia_ and mes_ else ""


def date_amd_to_dma(date_str: str) -> str:
    """
    Convert year, month day to day, month, year.

    @param date_str: date string.
    @return date string formated.
    """

    if not date_str:
        return ""

    date_str = str(date_str)
    if date_str.find("T") > -1:
        date_str = date_str[: date_str.find("T")]

    dia_ = None
    mes_ = None
    ano_ = None

    array_: List[str] = re.split("-|/", date_str)

    if len(array_) > 1:
        if len(array_) == 3:
            dia_, mes_, ano_ = reversed(array_) if len(array_[0]) == 4 else array_
    elif len(date_str) > 7:
        ano_ = date_str[0:4]
        mes_ = date_str[4:2]
        dia_ = date_str[6:2]

    return "%s-%s-%s" % (dia_, mes_, ano_) if ano_ and dia_ and mes_ else ""


def convert_to_qdate(
    value: Union["datetime.date", "date.Date", str, "QtCore.QDate"]
) -> "QtCore.QDate":
    """
    Convert different date formats to QDate.

    @param date: Date to convert.
    @return QDate with the value of the given date.
    """

    if isinstance(value, date.Date):
        value = value.toString()  # QDate -> str
    elif isinstance(value, datetime.date):
        value = str(value)

    if isinstance(value, str):
        if "T" in value:
            value = value[: value.find("T")]

        new_value = date_amd_to_dma(value) if len(value.split("-")[0]) == 4 else value
        value = QtCore.QDate.fromString(new_value, "dd-MM-yyyy")

    return value
