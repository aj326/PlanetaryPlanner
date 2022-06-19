from unittest import TestCase

import pytz
from astral import LocationInfo

from planetaryhours import my_location


class Test(TestCase):
    def test_my_location_lat1(self):
        with self.assertRaises(ValueError):
            my_location("test1","T","Asia/Riyadh",-97,55)
    def test_my_location_long(self):
        with self.assertRaises(ValueError):
            my_location("test1","T","Asia/Riyadh",-90,-555)
    def test_my_location_tz(self):
        with self.assertRaises(pytz.UnknownTimeZoneError):
            my_location("test1","T","Asia/Riyadhhhhhhh",-90,-55)
    def test_my_location(self):
        self.assertIsInstance(my_location("test1","T","Asia/Riyadh",-90,-55),LocationInfo)
