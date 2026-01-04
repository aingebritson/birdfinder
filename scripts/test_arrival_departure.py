#!/usr/bin/env python3
"""
Tests for arrival/departure calculation algorithm.

Tests the logic that determines when species arrive, peak, and depart based on
their weekly frequency patterns and valley information.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.constants import (
    WEEKS_PER_YEAR,
    ARRIVAL_THRESHOLD_PEAK_RATIO,
    ARRIVAL_THRESHOLD_ABSOLUTE,
    WEEK_INDEX_MIN,
    WEEK_INDEX_MAX
)


def find_arrival_week(frequencies, valley_end, peak_week):
    """
    Find arrival week (when frequency crosses threshold after valley).
    Based on calculate_arrival_departure.py logic.
    """
    peak_freq = frequencies[peak_week]
    threshold = max(peak_freq * ARRIVAL_THRESHOLD_PEAK_RATIO, ARRIVAL_THRESHOLD_ABSOLUTE)

    # Search forward from valley end to peak
    week = valley_end
    while week != peak_week:
        if frequencies[week] >= threshold:
            return week
        week = (week + 1) % WEEKS_PER_YEAR

    return peak_week


def find_departure_week(frequencies, peak_week, valley_start):
    """
    Find departure week (when frequency drops below threshold before valley).
    Based on calculate_arrival_departure.py logic.
    """
    peak_freq = frequencies[peak_week]
    threshold = max(peak_freq * ARRIVAL_THRESHOLD_PEAK_RATIO, ARRIVAL_THRESHOLD_ABSOLUTE)

    # Search backward from valley start to peak
    week = valley_start
    while week != peak_week:
        prev_week = (week - 1) % WEEKS_PER_YEAR
        if frequencies[prev_week] >= threshold:
            return week
        week = prev_week

    return peak_week


def find_peak_week(frequencies, start_week, end_week):
    """
    Find the week with maximum frequency in a range.
    """
    max_freq = 0
    peak_week = start_week

    week = start_week
    while True:
        if frequencies[week] > max_freq:
            max_freq = frequencies[week]
            peak_week = week

        if week == end_week:
            break
        week = (week + 1) % WEEKS_PER_YEAR

    return peak_week


def test_simple_arrival():
    """Test arrival detection for straightforward patterns."""
    print("Testing simple arrival detection...")

    # Spring arrival pattern
    freq = [0.0] * WEEKS_PER_YEAR
    freq[10] = 0.05  # First presence
    freq[11] = 0.15  # Crossing threshold (10% of 0.8 peak = 0.08)
    freq[12] = 0.30
    freq[13] = 0.50
    freq[14] = 0.70
    freq[15] = 0.80  # Peak

    valley_end = 9
    peak_week = 15

    arrival = find_arrival_week(freq, valley_end, peak_week)
    assert arrival == 11, f"Expected arrival at week 11, got {arrival}"
    print("  ✓ Spring arrival detected correctly")

    # Test with very low initial values
    freq2 = [0.0] * WEEKS_PER_YEAR
    freq2[20] = 0.001  # Below threshold
    freq2[21] = 0.002  # Below threshold
    freq2[22] = 0.12   # Above threshold (10% of 1.0 peak)
    freq2[23] = 0.50
    freq2[24] = 1.0    # Peak

    arrival2 = find_arrival_week(freq2, 19, 24)
    assert arrival2 == 22, f"Expected arrival at week 22, got {arrival2}"
    print("  ✓ Arrival with gradual buildup detected correctly")

    print("✓ Simple arrival tests passed\n")


def test_simple_departure():
    """Test departure detection for straightforward patterns."""
    print("Testing simple departure detection...")

    # Fall departure pattern
    freq = [0.0] * WEEKS_PER_YEAR
    freq[20] = 0.80  # Peak
    freq[21] = 0.70
    freq[22] = 0.50
    freq[23] = 0.30
    freq[24] = 0.15
    freq[25] = 0.05  # Below threshold (10% of 0.8 = 0.08)
    freq[26] = 0.0

    peak_week = 20
    valley_start = 27

    departure = find_departure_week(freq, peak_week, valley_start)
    # Departure is when frequency drops below threshold
    # Week 24 is 0.15 (above threshold), week 25 is 0.05 (below)
    # So departure is week 25
    assert departure == 25, f"Expected departure at week 25, got {departure}"
    print("  ✓ Fall departure detected correctly")

    # Test with sharp drop-off
    freq2 = [0.0] * WEEKS_PER_YEAR
    freq2[30] = 0.90  # Peak
    freq2[31] = 0.80
    freq2[32] = 0.70
    freq2[33] = 0.05  # Sudden drop below threshold
    freq2[34] = 0.01
    freq2[35] = 0.0

    departure2 = find_departure_week(freq2, 30, 36)
    # Departure is when frequency drops below threshold
    # Week 32 is 0.70 (above threshold of 0.09), week 33 is 0.05 (below)
    # So departure is week 33
    assert departure2 == 33, f"Expected departure at week 33, got {departure2}"
    print("  ✓ Sharp departure detected correctly")

    print("✓ Simple departure tests passed\n")


def test_peak_detection():
    """Test peak week detection."""
    print("Testing peak week detection...")

    # Clear peak
    freq = [0.2] * WEEKS_PER_YEAR
    freq[25] = 0.9  # Clear peak

    peak = find_peak_week(freq, 20, 30)
    assert peak == 25, f"Expected peak at week 25, got {peak}"
    print("  ✓ Clear peak detected")

    # Multiple local maxima (should find global maximum)
    freq2 = [0.0] * WEEKS_PER_YEAR
    freq2[10] = 0.6  # Local max
    freq2[15] = 0.9  # Global max
    freq2[20] = 0.7  # Local max

    peak2 = find_peak_week(freq2, 8, 22)
    assert peak2 == 15, f"Expected peak at week 15, got {peak2}"
    print("  ✓ Global maximum found among local maxima")

    # Plateau (first occurrence of max should win)
    freq3 = [0.0] * WEEKS_PER_YEAR
    freq3[12] = 0.8
    freq3[13] = 0.8  # Plateau
    freq3[14] = 0.8

    peak3 = find_peak_week(freq3, 10, 16)
    assert peak3 == 12, f"Expected first occurrence of peak at week 12, got {peak3}"
    print("  ✓ First occurrence of plateau peak found")

    print("✓ Peak detection tests passed\n")


def test_wraparound_scenarios():
    """Test scenarios that cross year boundary."""
    print("Testing wraparound scenarios...")

    # Winter peak that wraps around year boundary
    freq = [0.0] * WEEKS_PER_YEAR
    # Late fall arrival
    freq[44] = 0.15  # Above threshold
    freq[45] = 0.30
    freq[46] = 0.50
    freq[47] = 0.70
    # Winter peak
    freq[0] = 0.90   # Peak in January
    freq[1] = 0.85
    freq[2] = 0.75
    # Early spring departure
    freq[3] = 0.50
    freq[4] = 0.30
    freq[5] = 0.15
    freq[6] = 0.05   # Below threshold
    freq[7] = 0.0

    valley_end = 43
    valley_start = 8
    peak_week = 0

    arrival = find_arrival_week(freq, valley_end, peak_week)
    departure = find_departure_week(freq, peak_week, valley_start)

    assert arrival == 44, f"Expected wraparound arrival at week 44, got {arrival}"
    # Departure is when frequency drops below threshold
    # Week 5 is 0.15 (above threshold of 0.09), week 6 is 0.05 (below)
    # So departure is week 6
    assert departure == 6, f"Expected wraparound departure at week 6, got {departure}"
    print("  ✓ Wraparound arrival/departure detected correctly")

    # Peak detection across boundary
    freq2 = [0.0] * WEEKS_PER_YEAR
    freq2[46] = 0.5
    freq2[47] = 0.7
    freq2[0] = 0.9   # Peak at boundary
    freq2[1] = 0.6
    freq2[2] = 0.4

    peak2 = find_peak_week(freq2, 46, 2)
    assert peak2 == 0, f"Expected wraparound peak at week 0, got {peak2}"
    print("  ✓ Wraparound peak detected correctly")

    print("✓ Wraparound scenario tests passed\n")


def test_threshold_calculations():
    """Test that thresholds are calculated correctly."""
    print("Testing threshold calculations...")

    # Test 1: High peak - threshold should be 10% of peak
    freq_high_peak = [0.0] * WEEKS_PER_YEAR
    freq_high_peak[20] = 1.0  # Peak

    # Threshold should be max(1.0 * 0.10, 0.001) = 0.10
    expected_threshold = ARRIVAL_THRESHOLD_PEAK_RATIO  # 0.10

    freq_high_peak[15] = 0.09   # Below threshold
    freq_high_peak[16] = 0.11   # Above threshold

    arrival = find_arrival_week(freq_high_peak, 14, 20)
    assert arrival == 16, f"Threshold not applied correctly for high peak"
    print(f"  ✓ High peak threshold ({ARRIVAL_THRESHOLD_PEAK_RATIO}) applied correctly")

    # Test 2: Low peak - threshold should be absolute minimum
    freq_low_peak = [0.0] * WEEKS_PER_YEAR
    freq_low_peak[20] = 0.005  # Very low peak

    # Threshold should be max(0.005 * 0.10, 0.001) = 0.001 (absolute minimum)
    freq_low_peak[15] = 0.0005  # Below absolute threshold
    freq_low_peak[16] = 0.0015  # Above absolute threshold

    arrival2 = find_arrival_week(freq_low_peak, 14, 20)
    assert arrival2 == 16, f"Absolute threshold not applied correctly for low peak"
    print(f"  ✓ Absolute threshold ({ARRIVAL_THRESHOLD_ABSOLUTE}) applied correctly")

    print("✓ Threshold calculation tests passed\n")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("Testing edge cases...")

    # Test 1: Arrival immediately after valley (week 0)
    freq = [0.0] * WEEKS_PER_YEAR
    freq[0] = 0.5  # Immediate presence after valley
    freq[1] = 0.8  # Peak

    arrival = find_arrival_week(freq, 47, 1)  # Valley ends at 47, peak at 1
    assert arrival == 0, f"Expected arrival at week 0, got {arrival}"
    print("  ✓ Immediate arrival after valley detected")

    # Test 2: Departure at week 47 (last week)
    freq2 = [0.0] * WEEKS_PER_YEAR
    freq2[45] = 0.8  # Peak
    freq2[46] = 0.5
    freq2[47] = 0.01  # Drops below threshold at last week

    departure = find_departure_week(freq2, 45, 0)  # Valley starts at week 0
    # Week 46 is 0.5 (above threshold of 0.08), week 47 is 0.01 (below)
    # So departure is week 47
    assert departure == 47, f"Expected departure at week 47, got {departure}"
    print("  ✓ Departure at year boundary detected")

    # Test 3: Peak equals valley end (immediate peak)
    freq3 = [0.0] * WEEKS_PER_YEAR
    freq3[10] = 0.9  # Peak immediately at valley end

    arrival3 = find_arrival_week(freq3, 10, 10)
    assert arrival3 == 10, f"Expected arrival equals peak, got {arrival3}"
    print("  ✓ Immediate peak handled correctly")

    # Test 4: Never crosses threshold (gradual buildup)
    freq4 = [0.0] * WEEKS_PER_YEAR
    for i in range(10, 20):
        freq4[i] = 0.05  # All below threshold of 0.1 (for peak of 1.0)
    freq4[20] = 1.0  # Sudden peak

    arrival4 = find_arrival_week(freq4, 9, 20)
    # Should find the week that first crosses threshold, or peak if never crosses
    # Since all weeks before peak are below threshold, should return peak
    assert arrival4 == 20, f"Expected arrival at peak when threshold never crossed, got {arrival4}"
    print("  ✓ Never-crosses-threshold case handled")

    print("✓ Edge case tests passed\n")


def test_realistic_patterns():
    """Test with realistic species timing patterns."""
    print("Testing realistic timing patterns...")

    # Test 1: Baltimore Oriole - typical summer breeder
    # Arrives mid-May (week ~16), peaks June (week ~20), departs September (week ~32)
    freq_oriole = [0.0] * WEEKS_PER_YEAR
    # Arrival
    freq_oriole[16] = 0.10
    freq_oriole[17] = 0.25
    freq_oriole[18] = 0.45
    # Peak
    freq_oriole[19] = 0.65
    freq_oriole[20] = 0.75  # Peak
    freq_oriole[21] = 0.73
    # Present through summer
    for i in range(22, 32):
        freq_oriole[i] = 0.65
    # Departure
    freq_oriole[32] = 0.50
    freq_oriole[33] = 0.30
    freq_oriole[34] = 0.10
    freq_oriole[35] = 0.02
    freq_oriole[36] = 0.0

    peak_oriole = find_peak_week(freq_oriole, 15, 35)
    arrival_oriole = find_arrival_week(freq_oriole, 15, peak_oriole)
    departure_oriole = find_departure_week(freq_oriole, peak_oriole, 36)

    assert peak_oriole == 20, f"Oriole peak should be week 20, got {peak_oriole}"
    assert 16 <= arrival_oriole <= 18, f"Oriole arrival should be weeks 16-18, got {arrival_oriole}"
    assert 34 <= departure_oriole <= 36, f"Oriole departure should be weeks 34-36, got {departure_oriole}"
    print("  ✓ Baltimore Oriole timing pattern correct")

    # Test 2: Dark-eyed Junco - winter resident
    # Arrives October (week ~36), peaks December-January, departs April (week ~12)
    freq_junco = [0.0] * WEEKS_PER_YEAR
    # Winter peak
    for i in range(44, 48):
        freq_junco[i] = 0.8
    for i in range(0, 8):
        freq_junco[i] = 0.8
    # Departure
    freq_junco[8] = 0.65
    freq_junco[9] = 0.45
    freq_junco[10] = 0.25
    freq_junco[11] = 0.08
    freq_junco[12] = 0.02
    # Absent summer
    for i in range(13, 36):
        freq_junco[i] = 0.0
    # Arrival
    freq_junco[36] = 0.05
    freq_junco[37] = 0.15
    freq_junco[38] = 0.35
    freq_junco[39] = 0.55
    freq_junco[40] = 0.70
    for i in range(41, 44):
        freq_junco[i] = 0.78

    peak_junco = find_peak_week(freq_junco, 36, 12)  # Wraparound search
    # Peak could be any week from 44-7 where freq is 0.8
    assert freq_junco[peak_junco] == 0.8, f"Junco peak should have max frequency"
    print(f"  ✓ Dark-eyed Junco timing pattern correct (peak at week {peak_junco})")

    print("✓ Realistic timing pattern tests passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Arrival/Departure Calculation Algorithm Test Suite")
    print("=" * 60)
    print()

    test_simple_arrival()
    test_simple_departure()
    test_peak_detection()
    test_wraparound_scenarios()
    test_threshold_calculations()
    test_edge_cases()
    test_realistic_patterns()

    print("=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
