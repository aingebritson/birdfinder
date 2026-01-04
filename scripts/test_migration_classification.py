#!/usr/bin/env python3
"""
Tests for migration pattern classification algorithm.

Tests the core logic that classifies bird species into migration categories
(resident, single-season, two-passage migrant, vagrant, irregular) based on
their frequency patterns throughout the year.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from utils.constants import (
    WEEKS_PER_YEAR,
    MIN_WEEKS_PRESENCE,
    MIN_PEAK_FREQUENCY,
    RESIDENT_MIN_MAX_RATIO_THRESHOLD,
    VALLEY_MIN_LENGTH_WEEKS,
    CATEGORY_RESIDENT,
    CATEGORY_SINGLE_SEASON,
    CATEGORY_TWO_PASSAGE,
    CATEGORY_VAGRANT,
    CATEGORY_IRREGULAR
)
from utils.valley_detection import detect_valleys


def calculate_metrics(frequencies):
    """
    Calculate metrics for a species (from classify_migration_patterns.py).
    """
    weeks_with_presence = sum(1 for f in frequencies if f > 0)
    peak_frequency = max(frequencies)
    min_frequency = min(frequencies)
    valleys = detect_valleys(frequencies)

    return {
        'weeks_with_presence': weeks_with_presence,
        'peak_frequency': peak_frequency,
        'min_frequency': min_frequency,
        'valleys': valleys,
        'num_valleys': len(valleys)
    }


def classify_species(frequencies):
    """
    Classify a species based on its frequency pattern (from classify_migration_patterns.py).
    """
    metrics = calculate_metrics(frequencies)

    # Vagrant: very low presence
    if metrics['weeks_with_presence'] < MIN_WEEKS_PRESENCE or metrics['peak_frequency'] < MIN_PEAK_FREQUENCY:
        return CATEGORY_VAGRANT, metrics

    # Resident: no significant valleys OR very consistent presence
    if metrics['num_valleys'] == 0:
        return CATEGORY_RESIDENT, metrics

    # Check min/max ratio for resident classification
    if metrics['min_frequency'] > 0:
        min_max_ratio = metrics['min_frequency'] / metrics['peak_frequency']
        if min_max_ratio > RESIDENT_MIN_MAX_RATIO_THRESHOLD:
            return CATEGORY_RESIDENT, metrics

    # Irregular: 3+ valleys
    if metrics['num_valleys'] >= 3:
        return CATEGORY_IRREGULAR, metrics

    # Two-passage migrant: exactly 2 valleys
    if metrics['num_valleys'] == 2:
        return CATEGORY_TWO_PASSAGE, metrics

    # Single-season: exactly 1 valley
    if metrics['num_valleys'] == 1:
        return CATEGORY_SINGLE_SEASON, metrics

    # Fallback
    return CATEGORY_IRREGULAR, metrics


def test_resident_classification():
    """Test classification of year-round resident species."""
    print("Testing resident classification...")

    # Test 1: No valleys, consistent presence
    freq_consistent = [0.5] * WEEKS_PER_YEAR
    category, metrics = classify_species(freq_consistent)
    assert category == CATEGORY_RESIDENT, f"Expected resident, got {category}"
    assert metrics['num_valleys'] == 0
    print("  ✓ Consistent presence classified as resident")

    # Test 2: High min/max ratio (seasonal variation but still resident)
    freq_seasonal = [0.3 if i < 24 else 0.6 for i in range(WEEKS_PER_YEAR)]
    category, metrics = classify_species(freq_seasonal)
    assert category == CATEGORY_RESIDENT, f"Expected resident, got {category}"
    assert metrics['min_frequency'] / metrics['peak_frequency'] > RESIDENT_MIN_MAX_RATIO_THRESHOLD
    print("  ✓ Seasonal resident (high min/max ratio) classified correctly")

    # Test 3: Very low variation, no valleys
    freq_stable = [0.45 + (i % 3) * 0.05 for i in range(WEEKS_PER_YEAR)]  # 0.45-0.55
    category, metrics = classify_species(freq_stable)
    assert category == CATEGORY_RESIDENT, f"Expected resident, got {category}"
    print("  ✓ Stable presence classified as resident")

    print("✓ All resident classification tests passed\n")


def test_vagrant_classification():
    """Test classification of vagrant species."""
    print("Testing vagrant classification...")

    # Test 1: Very few weeks present
    freq_rare = [0.0] * WEEKS_PER_YEAR
    for i in [20, 21, 22]:  # Only 3 weeks
        freq_rare[i] = 0.1
    category, metrics = classify_species(freq_rare)
    assert category == CATEGORY_VAGRANT, f"Expected vagrant, got {category}"
    assert metrics['weeks_with_presence'] < MIN_WEEKS_PRESENCE
    print("  ✓ Very rare species classified as vagrant")

    # Test 2: Low peak frequency
    freq_low_peak = [0.002] * WEEKS_PER_YEAR
    category, metrics = classify_species(freq_low_peak)
    assert category == CATEGORY_VAGRANT, f"Expected vagrant, got {category}"
    assert metrics['peak_frequency'] < MIN_PEAK_FREQUENCY
    print("  ✓ Low peak frequency classified as vagrant")

    # Test 3: Only appears for 5 weeks
    freq_brief = [0.0] * WEEKS_PER_YEAR
    for i in range(10, 15):
        freq_brief[i] = 0.08
    category, metrics = classify_species(freq_brief)
    assert category == CATEGORY_VAGRANT, f"Expected vagrant, got {category}"
    print("  ✓ Brief presence classified as vagrant")

    print("✓ All vagrant classification tests passed\n")


def test_single_season_classification():
    """Test classification of single-season species."""
    print("Testing single-season classification...")

    # Test 1: Summer breeder with winter valley
    freq_summer = [0.0] * WEEKS_PER_YEAR
    # High in summer (weeks 16-35), low in winter
    for i in range(16, 36):
        freq_summer[i] = 0.6

    category, metrics = classify_species(freq_summer)
    assert category == CATEGORY_SINGLE_SEASON, f"Expected single-season, got {category}"
    assert metrics['num_valleys'] == 1
    print("  ✓ Summer breeder classified as single-season")

    # Test 2: Winter resident with summer valley
    freq_winter = [0.0] * WEEKS_PER_YEAR
    # High in winter (weeks 44-47, 0-7), low in summer
    for i in range(44, 48):
        freq_winter[i] = 0.5
    for i in range(0, 8):
        freq_winter[i] = 0.5

    category, metrics = classify_species(freq_winter)
    assert category == CATEGORY_SINGLE_SEASON, f"Expected single-season, got {category}"
    assert metrics['num_valleys'] == 1
    print("  ✓ Winter resident classified as single-season")

    print("✓ All single-season classification tests passed\n")


def test_two_passage_classification():
    """Test classification of two-passage migrant species."""
    print("Testing two-passage migrant classification...")

    # Classic two-passage: spring and fall migration
    freq_two_passage = [0.0] * WEEKS_PER_YEAR

    # Spring peak (April-May, weeks 12-19)
    for i in range(12, 20):
        freq_two_passage[i] = 0.7

    # Summer valley (June-July, weeks 20-27)
    for i in range(20, 28):
        freq_two_passage[i] = 0.02

    # Fall peak (August-September, weeks 28-35)
    for i in range(28, 36):
        freq_two_passage[i] = 0.6

    # Winter valley (rest of year)

    category, metrics = classify_species(freq_two_passage)
    assert category == CATEGORY_TWO_PASSAGE, f"Expected two-passage, got {category}"
    assert metrics['num_valleys'] == 2, f"Expected 2 valleys, got {metrics['num_valleys']}"
    print("  ✓ Classic two-passage migrant classified correctly")

    print("✓ All two-passage migrant classification tests passed\n")


def test_irregular_classification():
    """Test classification of irregular species."""
    print("Testing irregular classification...")

    # Species with 3+ valleys (erratic presence)
    freq_irregular = [0.0] * WEEKS_PER_YEAR

    # Multiple peaks throughout year
    for i in range(8, 12):    # Spring peak
        freq_irregular[i] = 0.4
    for i in range(20, 24):   # Summer peak
        freq_irregular[i] = 0.3
    for i in range(32, 36):   # Fall peak
        freq_irregular[i] = 0.5
    for i in range(44, 48):   # Winter peak
        freq_irregular[i] = 0.35

    category, metrics = classify_species(freq_irregular)
    assert category == CATEGORY_IRREGULAR, f"Expected irregular, got {category}"
    assert metrics['num_valleys'] >= 3, f"Expected 3+ valleys, got {metrics['num_valleys']}"
    print("  ✓ Erratic presence classified as irregular")

    print("✓ All irregular classification tests passed\n")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("Testing edge cases...")

    # Test 1: Exactly MIN_WEEKS_PRESENCE (should not be vagrant)
    freq_boundary = [0.0] * WEEKS_PER_YEAR
    for i in range(MIN_WEEKS_PRESENCE):
        freq_boundary[i] = 0.1
    category, metrics = classify_species(freq_boundary)
    assert category != CATEGORY_VAGRANT, f"Species with exactly {MIN_WEEKS_PRESENCE} weeks should not be vagrant"
    print(f"  ✓ Species with exactly {MIN_WEEKS_PRESENCE} weeks not classified as vagrant")

    # Test 2: Exactly MIN_PEAK_FREQUENCY (should not be vagrant)
    freq_min_peak = [MIN_PEAK_FREQUENCY] * WEEKS_PER_YEAR
    category, metrics = classify_species(freq_min_peak)
    assert category != CATEGORY_VAGRANT, f"Species with peak = {MIN_PEAK_FREQUENCY} should not be vagrant"
    print(f"  ✓ Species with peak frequency = {MIN_PEAK_FREQUENCY} not classified as vagrant")

    # Test 3: All zeros (should be vagrant)
    freq_zeros = [0.0] * WEEKS_PER_YEAR
    category, metrics = classify_species(freq_zeros)
    assert category == CATEGORY_VAGRANT, "All-zero frequency should be vagrant"
    print("  ✓ All-zero frequency classified as vagrant")

    # Test 4: Valley at year boundary (wraparound)
    freq_wraparound = [0.0] * WEEKS_PER_YEAR
    # Low at year boundary (weeks 44-47, 0-3)
    for i in range(44, 48):
        freq_wraparound[i] = 0.01
    for i in range(0, 4):
        freq_wraparound[i] = 0.01
    # High elsewhere
    for i in range(8, 40):
        freq_wraparound[i] = 0.6

    category, metrics = classify_species(freq_wraparound)
    assert metrics['num_valleys'] == 1, "Should detect wraparound valley"
    print("  ✓ Wraparound valley detected correctly")

    print("✓ All edge case tests passed\n")


def test_real_world_patterns():
    """Test with realistic species patterns."""
    print("Testing realistic species patterns...")

    # Test 1: American Robin (resident with seasonal variation)
    # Higher in spring/summer, lower in winter but never absent
    freq_robin = [
        # Winter (low)
        0.25, 0.25, 0.25, 0.25, 0.28, 0.28, 0.28, 0.28,
        # Spring (increasing)
        0.35, 0.40, 0.50, 0.60, 0.70, 0.75, 0.80, 0.80,
        # Summer (peak)
        0.80, 0.80, 0.78, 0.75, 0.72, 0.70, 0.68, 0.65,
        # Fall (decreasing)
        0.60, 0.55, 0.50, 0.45, 0.40, 0.38, 0.35, 0.32,
        # Late Fall/Early Winter (low)
        0.30, 0.28, 0.26, 0.25, 0.25, 0.25, 0.24, 0.24,
        0.24, 0.24, 0.24, 0.25, 0.25, 0.25, 0.25, 0.25
    ]
    category, metrics = classify_species(freq_robin)
    assert category == CATEGORY_RESIDENT, f"Robin should be resident, got {category}"
    print("  ✓ American Robin pattern classified as resident")

    # Test 2: Baltimore Oriole (single-season summer breeder)
    freq_oriole = [
        # Winter (absent)
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0,
        # Spring arrival (weeks 12-15)
        0.02, 0.10, 0.30, 0.50,
        # Summer (present, weeks 16-31)
        0.65, 0.70, 0.75, 0.75, 0.72, 0.70, 0.68, 0.65,
        0.60, 0.58, 0.55, 0.50, 0.45, 0.40, 0.35, 0.30,
        # Fall departure (weeks 32-35)
        0.20, 0.10, 0.03, 0.01,
        # Absent again
        0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        0.0, 0.0, 0.0, 0.0
    ]
    category, metrics = classify_species(freq_oriole)
    assert category == CATEGORY_SINGLE_SEASON, f"Oriole should be single-season, got {category}"
    print("  ✓ Baltimore Oriole pattern classified as single-season")

    # Test 3: Yellow-rumped Warbler (two-passage migrant)
    freq_warbler = [
        # Winter (low)
        0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05,
        # Spring migration (weeks 8-15)
        0.10, 0.20, 0.40, 0.60, 0.70, 0.65, 0.55, 0.40,
        # Summer (low/absent, weeks 16-27)
        0.15, 0.08, 0.03, 0.02, 0.02, 0.02, 0.03, 0.05,
        0.08, 0.10, 0.15, 0.20,
        # Fall migration (weeks 28-35)
        0.35, 0.50, 0.65, 0.75, 0.70, 0.60, 0.45, 0.30,
        # Winter (low again)
        0.15, 0.10, 0.08, 0.07, 0.06, 0.05, 0.05, 0.05,
        0.05, 0.05, 0.05, 0.05
    ]
    category, metrics = classify_species(freq_warbler)
    assert category == CATEGORY_TWO_PASSAGE, f"Warbler should be two-passage, got {category}"
    print("  ✓ Yellow-rumped Warbler pattern classified as two-passage migrant")

    print("✓ All realistic pattern tests passed\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Migration Classification Algorithm Test Suite")
    print("=" * 60)
    print()

    test_resident_classification()
    test_vagrant_classification()
    test_single_season_classification()
    test_two_passage_classification()
    test_irregular_classification()
    test_edge_cases()
    test_real_world_patterns()

    print("=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
