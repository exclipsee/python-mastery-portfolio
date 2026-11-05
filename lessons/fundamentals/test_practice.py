"""Tests for the first Python fundamentals lesson."""

import unittest

from lessons.fundamentals.practice import (
    calculate_total,
    count_vowels,
    greet,
    is_even,
)


class FundamentalsTests(unittest.TestCase):
    def test_greet(self) -> None:
        self.assertEqual(greet("Ada"), "Hello, Ada!")

    def test_is_even(self) -> None:
        self.assertTrue(is_even(4))
        self.assertFalse(is_even(5))
        self.assertTrue(is_even(0))

    def test_count_vowels_ignores_case(self) -> None:
        self.assertEqual(count_vowels("Education"), 5)
        self.assertEqual(count_vowels("rhythm"), 0)

    def test_calculate_total(self) -> None:
        self.assertEqual(calculate_total([2.50, 1.25, 3.00]), 6.75)
        self.assertEqual(calculate_total([]), 0.0)


if __name__ == "__main__":
    unittest.main()
