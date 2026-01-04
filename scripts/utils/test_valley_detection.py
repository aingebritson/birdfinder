#!/usr/bin/env python3
"""
Simple tests for valley detection functionality.

These tests verify that the valley detection algorithm works correctly
for common migration patterns.
"""

from valley_detection import detect_valleys


def test_simple_valley():
    """Test detection of a simple valley in the middle."""
    # High frequency, then 5 weeks of near-zero, then high again
    frequencies = [0.5] * 10 + [0.01] * 5 + [0.5] * 33
    valleys = detect_valleys(frequencies)

    assert len(valleys) == 1, f"Expected 1 valley, found {len(valleys)}"
    assert valleys[0] == (10, 14), f"Expected valley (10, 14), got {valleys[0]}"
    print("✓ Simple valley test passed")


def test_wraparound_valley():
    """Test valley that wraps around year boundary."""
    # Low at start, high in middle, low at end
    frequencies = [0.01] * 5 + [0.5] * 38 + [0.01] * 5
    valleys = detect_valleys(frequencies)

    assert len(valleys) == 1, f"Expected 1 merged valley, found {len(valleys)}"
    # Should be merged into single valley spanning from week 43 to week 4
    assert valleys[0] == (43, 4), f"Expected wraparound valley (43, 4), got {valleys[0]}"
    print("✓ Wraparound valley test passed")


def test_two_valleys():
    """Test two-passage migrant pattern with two valleys."""
    # Spring presence, summer valley, fall presence, winter valley
    frequencies = (
        [0.01] * 8 +      # Winter valley (weeks 0-7)
        [0.5] * 8 +       # Spring presence (weeks 8-15)
        [0.01] * 16 +     # Summer valley (weeks 16-31)
        [0.5] * 8 +       # Fall presence (weeks 32-39)
        [0.01] * 8        # Winter valley continues (weeks 40-47)
    )
    valleys = detect_valleys(frequencies)

    # Should detect summer valley and wraparound winter valley
    assert len(valleys) == 2, f"Expected 2 valleys, found {len(valleys)}"
    print(f"✓ Two valleys test passed (found {valleys})")


def test_no_valleys():
    """Test resident species with no valleys."""
    frequencies = [0.5] * 48
    valleys = detect_valleys(frequencies)

    assert len(valleys) == 0, f"Expected 0 valleys, found {len(valleys)}"
    print("✓ No valleys (resident) test passed")


def test_short_dip_not_valley():
    """Test that short dips (<4 weeks) are not counted as valleys."""
    # High frequency with 3-week dip (not long enough)
    frequencies = [0.5] * 20 + [0.01] * 3 + [0.5] * 25
    valleys = detect_valleys(frequencies)

    assert len(valleys) == 0, f"Expected 0 valleys (dip too short), found {len(valleys)}"
    print("✓ Short dip test passed")


def test_empty_input():
    """Test handling of empty or invalid input."""
    assert detect_valleys([]) == []
    assert detect_valleys([0.0] * 48) == []
    print("✓ Empty input test passed")


if __name__ == "__main__":
    print("Running valley detection tests...\n")

    test_simple_valley()
    test_wraparound_valley()
    test_two_valleys()
    test_no_valleys()
    test_short_dip_not_valley()
    test_empty_input()

    print("\n✓ All tests passed!")
