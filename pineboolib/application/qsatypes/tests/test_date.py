"""Test_date module."""

import unittest
import datetime


class TestDate(unittest.TestCase):
    """TestDate Class."""

    def test_basic(self) -> None:
        """Test Date class."""

        from pineboolib.application.qsatypes import date

        date_ = date.Date("2019-11-03")
        self.assertEqual(date_.toString(), "2019-11-03T00:00:00")
        self.assertEqual(date_.toString("yyyy-MM-dd"), "2019-11-03")
        self.assertEqual(date_.toString("MM:yyyy-dd"), "11:2019-03")
        self.assertEqual(date_.getTime(), 20191103000000)
        self.assertEqual(date_.getYear(), 2019)
        self.assertEqual(date_.getMonth(), 11)
        self.assertEqual(date_.getDay(), 3)
        date_.setDay(26)
        self.assertEqual(date_.toString(), "2019-11-26T00:00:00")
        self.assertEqual(date_.getDay(), 26)
        self.assertEqual(date_.addDays(3).toString("yyyy-MM-dd"), "2019-11-29")
        self.assertEqual(date_.addMonths(-2).toString("yyyy-MM-dd"), "2019-09-26")
        self.assertEqual(date_.addYears(1).toString("yyyy-MM-dd"), "2020-11-26")

        date2_ = date.Date("2020-01-31T12:10:59")
        self.assertEqual(date2_.getHours(), 12)
        date2_.setYear("2021")
        date2_.setMonth("12")
        date2_.setDay(16)
        self.assertEqual(date2_.getHours(), 12)
        self.assertEqual(date2_.getMinutes(), 10)
        self.assertEqual(date2_.getSeconds(), 59)
        self.assertEqual(date2_.getMilliseconds(), 0)

        self.assertEqual(date2_.getYear(), 2021)
        self.assertTrue(date_ < date2_)
        self.assertFalse(date_ == date2_)
        self.assertTrue(date_ != date2_)
        date2_.setDate(14)
        self.assertEqual(date2_.getDay(), 14)

        date3_ = date2_.parse("2019-06-02T00:00:00")
        self.assertEqual(datetime.datetime.strptime("2019-06-02", "%Y-%m-%d").timestamp(), date3_)
