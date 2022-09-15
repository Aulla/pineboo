"""
Module for Date type.
"""
from typing import Union, Optional, Any
from PyQt6 import QtCore  # type: ignore[import]
from pineboolib.application.utils.date_conversion import date_dma_to_amd
import datetime


class Date(object):
    """
    Case que gestiona un objeto tipo Date.
    """

    date_: "QtCore.QDate"
    time_: "QtCore.QTime"

    def __init__(self, *args: Union["Date", QtCore.QDate, str, QtCore.QTime, int]) -> None:
        """Create new Date object."""
        super(Date, self).__init__()
        if not args:
            self.date_ = QtCore.QDate.currentDate()
            self.time_ = QtCore.QTime.currentTime()
        elif len(args) <= 2:
            date_ = args[0]
            format_ = args[1] if len(args) == 2 else "yyyy-MM-dd"
            if not isinstance(format_, str):
                raise ValueError("format must be string")
            self.time_ = QtCore.QTime(0, 0)
            if isinstance(date_, str):
                if len(date_) == 10:
                    tmp = date_.split("-")
                    if len(tmp[2]) == 4:
                        date_amd = date_dma_to_amd(date_)
                        if date_amd is None:
                            raise ValueError("Date %s is invalid" % date_)
                        date_ = date_amd

                    self.date_ = QtCore.QDate.fromString(date_, format_)
                else:
                    self.date_ = QtCore.QDate.fromString(date_[0:10], format_)
                    self.time_ = QtCore.QTime.fromString(date_[11:], "hh:mm:ss")

            elif isinstance(date_, Date):
                self.date_ = date_.date_
                self.time_ = date_.time_

            elif isinstance(date_, QtCore.QDate):
                self.date_ = date_
            elif isinstance(date_, (float, int)):
                date_time = QtCore.QDateTime()
                date_time.setMSecsSinceEpoch(int(date_))
                self.date_ = date_time.date()
                self.time_ = date_time.time()
            else:
                raise ValueError("Unexpected type %s" % type(date_))

            if not self.time_:
                self.time_ = QtCore.QTime(0, 0)
        else:
            year, month, day = args[0], args[1], args[2]
            if not isinstance(year, int) or not isinstance(month, int) or not isinstance(day, int):
                raise ValueError("Expected year, month, day as integers")
            self.date_ = QtCore.QDate(year, month, day)
            self.time_ = QtCore.QTime(0, 0)

    def toString(self, pattern: Optional[str] = None) -> str:
        """
        Return string with date & time data.

        @return cadena de texto con los datos de fecha y hora
        """
        if not pattern:
            pattern = "yyyy-MM-ddT%s" % self.time_.toString("hh:mm:ss")

        return self.date_.toString(pattern)

    def getTime(self) -> int:
        """Get integer representing date & time."""

        return int(self.date_.toString("yyyyMMdd%s" % self.time_.toString("hhmmss")))

    def getYear(self) -> int:
        """
        Return year from date.

        @return año
        """
        return self.date_.year()

    def setYear(self, year: Union[str, int]) -> "Date":
        """
        Set year into current date.

        @param yyyy. Año a setear
        """

        self.date_ = QtCore.QDate.fromString(self.date_.toString("%s-MM-dd" % year), "yyyy-MM-dd")

        return self

    def getMonth(self) -> int:
        """
        Get month as a number from current date.

        @return mes
        """
        return self.date_.month()

    def setMonth(self, month: Union[str, int]) -> "Date":
        """
        Set month into current date.

        @param mm. Mes a setear
        """
        month = str(month)
        if len(month) < 2:
            month = "0%s" % month

        self.date_ = QtCore.QDate.fromString(
            self.date_.toString("yyyy-%s-dd" % month), "yyyy-MM-dd"
        )

        return self

    def getDay(self) -> int:
        """
        Get day from current date.

        @return día
        """
        return self.date_.day()

    def setDay(self, day: Union[str, int]) -> "Date":
        """
        Set given day.

        @param dd. Dia a setear
        """
        day = str(day)

        if len(day) < 2:
            day = "0%s" % day

        self.date_ = QtCore.QDate.fromString(self.date_.toString("yyyy-MM-%s" % day), "yyyy-MM-dd")

        return self

    def getHours(self) -> int:
        """
        Get Hour from Date.

        @return horas
        """
        return self.time_.hour()

    def getMinutes(self) -> int:
        """
        Get Minutes from Date.

        @return minutos
        """
        return self.time_.minute()

    def getSeconds(self) -> int:
        """
        Get Seconds from Date.

        @return segundos
        """
        return self.time_.second()

    def getMilliseconds(self) -> int:
        """
        Get Milliseconds from Date.

        @return milisegundos
        """
        return self.time_.msec()

    getDate = getDay
    # setDate = setDay

    def setDate(self, date: Any) -> "Date":
        """
        Set Date from any format.

        @param date. Fecha a setear
        """
        year_ = self.date_.toString("yyyy")
        month_ = self.date_.toString("MM")
        day_ = str(date)
        if len(day_) == 1:
            day_ = "0" + day_

        str_ = "%s-%s-%s" % (year_, month_, day_)
        self.date_ = QtCore.QDate.fromString(str_, "yyyy-MM-dd")

        return self

    def addDays(self, days: int) -> "Date":
        """
        Return result of adding a particular amount of days to current date.

        @param d. Dias a sumar (o restar) a la fecha dada
        @return nueva fecha calculada
        """
        return Date(self.date_.addDays(days).toString("yyyy-MM-dd"))

    def addMonths(self, months: int) -> "Date":
        """
        Return result of adding given number of months to this date.

        @param m. Meses a sumar (o restar) a la fecha dada
        @return nueva fecha calculada
        """
        return Date(self.date_.addMonths(months).toString("yyyy-MM-dd"))

    def addYears(self, years: int) -> "Date":
        """
        Return result of adding given number of years to this date.

        @param y. Años a sumar (o restar) a la fecha dada
        @return nueva fecha calculada
        """
        return Date(self.date_.addYears(years).toString("yyyy-MM-dd"))

    @classmethod
    def parse(cls, value: str) -> float:
        """Parse a ISO string into a date."""
        # return Date(value, "yyyy-MM-dd")
        if "T" not in value:
            value = "%sT00:00:00" % value
        return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").timestamp()

    def __str__(self) -> str:
        """Support for str()."""
        return self.toString()

    def __repr__(self) -> str:
        """Support for str()."""
        return self.toString()

    def __lt__(self, other: Union[str, "Date"]) -> bool:
        """Support for comparisons."""
        return str(self) < str(other)

    def __le__(self, other: Union[str, "Date"]) -> bool:
        """Support for comparisons."""
        return str(self) <= str(other)

    def __ge__(self, other: Union[str, "Date"]) -> bool:
        """Support for comparisons."""
        return str(self) >= str(other)

    def __gt__(self, other: Union[str, "Date"]) -> bool:
        """Support for comparisons."""
        return str(self) > str(other)

    def __eq__(self, other: Any) -> bool:
        """Support for comparisons."""
        return str(other) == str(self)

    def __ne__(self, other: Any) -> bool:
        """Support for comparisons."""
        return not self.__eq__(other)
