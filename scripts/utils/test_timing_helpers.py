#!/usr/bin/env python3
"""
Unit tests for timing helper functions.

Run with:
    python3 test_timing_helpers.py
"""

import unittest
from timing_helpers import (
    normalize_week,
    week_range,
    find_arrival_week,
    find_peak_week,
    find_departure_week,
    find_last_week_above_threshold,
    calculate_threshold,
    identify_valley_type,
    get_presence_weeks,
    find_passage_timing
)


class TestNormalizeWeek(unittest.TestCase):
    """Test cases for normalize_week function."""

    def test_normal_week(self):
        """Week in valid range should be unchanged."""
        self.assertEqual(normalize_week(0), 0)
        self.assertEqual(normalize_week(23), 23)
        self.assertEqual(normalize_week(47), 47)

    def test_negative_week(self):
        """Negative week should wrap around."""
        self.assertEqual(normalize_week(-1), 47)
        self.assertEqual(normalize_week(-5), 43)
        self.assertEqual(normalize_week(-48), 0)

    def test_overflow_week(self):
        """Week >= 48 should wrap around."""
        self.assertEqual(normalize_week(48), 0)
        self.assertEqual(normalize_week(50), 2)
        self.assertEqual(normalize_week(96), 0)


class TestWeekRange(unittest.TestCase):
    """Test cases for week_range function."""

    def test_normal_range(self):
        """Normal range without wraparound."""
        self.assertEqual(week_range(5, 10), [5, 6, 7, 8, 9])

    def test_same_start_end(self):
        """Same start and end produces full wraparound (all 48 weeks)."""
        result = week_range(5, 5)
        # Since start >= end triggers wraparound, we get all 48 weeks
        self.assertEqual(len(result), 48)
        self.assertEqual(result[0], 5)

    def test_wraparound_range(self):
        """Range that wraps around year boundary."""
        self.assertEqual(week_range(45, 5), [45, 46, 47, 0, 1, 2, 3, 4])

    def test_wraparound_single_week(self):
        """Wraparound range with just a few weeks."""
        self.assertEqual(week_range(47, 2), [47, 0, 1])


class TestFindArrivalWeek(unittest.TestCase):
    """Test cases for find_arrival_week function."""

    def test_simple_arrival(self):
        """Find arrival in a simple increasing pattern."""
        freqs = [0.0] * 10 + [0.5] * 10 + [0.0] * 28
        arrival = find_arrival_week(freqs, 0, 20, 0.1)
        self.assertEqual(arrival, 10)

    def test_no_arrival(self):
        """Return None when threshold never crossed."""
        freqs = [0.0] * 48
        arrival = find_arrival_week(freqs, 0, 20, 0.1)
        self.assertIsNone(arrival)

    def test_wraparound_arrival(self):
        """Find arrival when search range wraps around."""
        freqs = [0.5] * 5 + [0.0] * 38 + [0.0] * 5
        arrival = find_arrival_week(freqs, 45, 10, 0.1)
        self.assertEqual(arrival, 0)


class TestFindPeakWeek(unittest.TestCase):
    """Test cases for find_peak_week function."""

    def test_clear_peak(self):
        """Find a clear single peak."""
        freqs = [0.1, 0.2, 0.5, 0.3, 0.1] + [0.0] * 43
        peak, freq = find_peak_week(freqs, 0, 5)
        self.assertEqual(peak, 2)
        self.assertEqual(freq, 0.5)

    def test_plateau_peak(self):
        """Find first occurrence of plateau."""
        freqs = [0.1, 0.5, 0.5, 0.5, 0.1] + [0.0] * 43
        peak, freq = find_peak_week(freqs, 0, 5)
        self.assertEqual(peak, 1)  # First of the plateau
        self.assertEqual(freq, 0.5)

    def test_wraparound_peak(self):
        """Find peak when search wraps around year."""
        freqs = [0.3, 0.4, 0.2] + [0.0] * 42 + [0.5, 0.6, 0.4]
        peak, freq = find_peak_week(freqs, 45, 5)
        self.assertEqual(peak, 46)
        self.assertEqual(freq, 0.6)


class TestFindDepartureWeek(unittest.TestCase):
    """Test cases for find_departure_week function."""

    def test_simple_departure(self):
        """Find departure after peak drops below threshold."""
        freqs = [0.0] * 10 + [0.5, 0.6, 0.5, 0.3, 0.05] + [0.0] * 33
        departure = find_departure_week(freqs, 11, 20, 0.1)
        self.assertEqual(departure, 13)  # Week before drop below 0.1

    def test_never_drops(self):
        """Return last week when frequency never drops."""
        freqs = [0.5] * 20 + [0.0] * 28
        departure = find_departure_week(freqs, 10, 20, 0.1)
        self.assertEqual(departure, 19)  # search_end - 1


class TestFindLastWeekAboveThreshold(unittest.TestCase):
    """Test cases for find_last_week_above_threshold function."""

    def test_simple_last(self):
        """Find last week above threshold."""
        freqs = [0.0] * 5 + [0.5] * 10 + [0.0] * 33
        last = find_last_week_above_threshold(freqs, 0, 20, 0.1)
        self.assertEqual(last, 14)

    def test_none_above_threshold(self):
        """Return None when nothing above threshold."""
        freqs = [0.05] * 48
        last = find_last_week_above_threshold(freqs, 0, 10, 0.1)
        self.assertIsNone(last)

    def test_wraparound_last(self):
        """Find last week when range wraps around."""
        freqs = [0.5, 0.5, 0.0] + [0.0] * 42 + [0.5, 0.5, 0.5]
        last = find_last_week_above_threshold(freqs, 45, 5, 0.1)
        self.assertEqual(last, 1)  # Last in the wraparound range


class TestCalculateThreshold(unittest.TestCase):
    """Test cases for calculate_threshold function."""

    def test_high_peak_uses_ratio(self):
        """High peak should use ratio calculation."""
        freqs = [0.0] * 24 + [1.0] + [0.0] * 23  # Peak at 1.0
        threshold = calculate_threshold(freqs, 0.10, 0.001)
        self.assertEqual(threshold, 0.10)  # 10% of 1.0

    def test_low_peak_uses_absolute(self):
        """Low peak should use absolute minimum."""
        freqs = [0.0] * 24 + [0.005] + [0.0] * 23  # Peak at 0.5%
        threshold = calculate_threshold(freqs, 0.10, 0.001)
        self.assertEqual(threshold, 0.001)  # Absolute minimum


class TestIdentifyValleyType(unittest.TestCase):
    """Test cases for identify_valley_type function."""

    def test_winter_valley(self):
        """Valley in winter should be identified as winter."""
        self.assertEqual(identify_valley_type((44, 7)), 'winter')
        self.assertEqual(identify_valley_type((46, 5)), 'winter')

    def test_summer_valley(self):
        """Valley in summer should be identified as summer."""
        self.assertEqual(identify_valley_type((20, 30)), 'summer')
        self.assertEqual(identify_valley_type((18, 32)), 'summer')


class TestGetPresenceWeeks(unittest.TestCase):
    """Test cases for get_presence_weeks function."""

    def test_summer_breeder_presence(self):
        """Summer breeder (winter valley) should have spring-fall presence."""
        # Winter valley from week 44 to week 7
        weeks = get_presence_weeks(44, 7, is_winter_valley=True)
        self.assertEqual(weeks, list(range(8, 44)))

    def test_winter_visitor_presence(self):
        """Winter visitor (summer valley) should have fall-spring presence."""
        # Summer valley from week 20 to week 30
        weeks = get_presence_weeks(20, 30, is_winter_valley=False)
        expected = list(range(31, 48)) + list(range(0, 20))
        self.assertEqual(weeks, expected)


class TestFindPassageTiming(unittest.TestCase):
    """Test cases for find_passage_timing function."""

    def test_simple_passage(self):
        """Find timing in a simple passage pattern."""
        freqs = [0.0] * 10 + [0.2, 0.5, 0.8, 0.5, 0.2] + [0.0] * 33
        timing = find_passage_timing(freqs, 8, 18, 0.1)

        self.assertEqual(timing['arrival'], 10)
        self.assertEqual(timing['peak'], 12)
        self.assertEqual(timing['departure'], 14)

    def test_passage_with_wraparound(self):
        """Find timing when passage wraps around year."""
        # Passage from week 45 to week 5 (wraparound)
        # freqs[43]=0.0, freqs[44]=0.0, freqs[45]=0.2, freqs[46]=0.5, freqs[47]=0.8
        # freqs[0]=0.5, freqs[1]=0.2, freqs[2]=0.0
        freqs = [0.5, 0.2, 0.0, 0.0, 0.0] + [0.0] * 38 + [0.0, 0.0, 0.2, 0.5, 0.8]
        timing = find_passage_timing(freqs, 45, 5, 0.1)

        self.assertEqual(timing['arrival'], 45)  # First week >= 0.1 in range
        self.assertEqual(timing['peak'], 47)     # 0.8 is at week 47


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestNormalizeWeek))
    suite.addTests(loader.loadTestsFromTestCase(TestWeekRange))
    suite.addTests(loader.loadTestsFromTestCase(TestFindArrivalWeek))
    suite.addTests(loader.loadTestsFromTestCase(TestFindPeakWeek))
    suite.addTests(loader.loadTestsFromTestCase(TestFindDepartureWeek))
    suite.addTests(loader.loadTestsFromTestCase(TestFindLastWeekAboveThreshold))
    suite.addTests(loader.loadTestsFromTestCase(TestCalculateThreshold))
    suite.addTests(loader.loadTestsFromTestCase(TestIdentifyValleyType))
    suite.addTests(loader.loadTestsFromTestCase(TestGetPresenceWeeks))
    suite.addTests(loader.loadTestsFromTestCase(TestFindPassageTiming))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("Timing Helpers Tests - Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
