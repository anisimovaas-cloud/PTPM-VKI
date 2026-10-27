import unittest
from lab4.converter import Converter

class TestConverter(unittest.TestCase):

    def test_positive_number(self):
        result = Converter.do(25.8)
        self.assertEqual(result, 25)
    def test_upper_boundary(self):
        result = Converter.do(100.7)
        self.assertEqual(result, 1000)
    def test_before_upper_boundary(self):
        result = Converter.do(100.6)
        self.assertEqual(result, 100)
    def test_above_upper_boundary(self):
        result = Converter.do(150.5)
        self.assertEqual(result, 1000)
    def test_zero_raises_value_error(self):
        with self.assertRaises(ValueError):
            Converter.do(0.0)
    def test_negative_number(self):
        result = Converter.do(-10.2)
        self.assertEqual(result, -15)
    def test_negative_boundary(self):
        result = Converter.do(-30.4)
        self.assertEqual(result, -35)
    def test_lower_boundary(self):
        result = Converter.do(-30.5)
        self.assertEqual(result, -2000)
    def test_below_lower_boundary(self):
        result = Converter.do(-30.6)
        self.assertEqual(result, -2000)
    def test_negative_near_zero(self):
        result = Converter.do(-0.1)
        self.assertEqual(result, -5)