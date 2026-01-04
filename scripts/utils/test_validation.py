#!/usr/bin/env python3
"""
Tests for validation utilities.
"""

from validation import (
    ValidationError,
    validate_frequency_array,
    validate_week_index,
    validate_species_name,
    validate_category,
    validate_pattern_type,
    validate_species_code,
    validate_region_name,
    validate_valley_tuple
)


def test_validate_frequency_array():
    """Test frequency array validation."""
    # Valid array
    valid_freq = [0.5] * 48
    validate_frequency_array(valid_freq, "Test Species")
    print("✓ Valid frequency array accepted")

    # Test wrong length
    try:
        validate_frequency_array([0.5] * 47, "Test Species")
        assert False, "Should have raised ValidationError for wrong length"
    except ValidationError as e:
        assert "48 values" in str(e)
        print("✓ Detected wrong array length")

    # Test out of range value
    try:
        invalid_freq = [0.5] * 47 + [1.5]
        validate_frequency_array(invalid_freq, "Test Species")
        assert False, "Should have raised ValidationError for out of range"
    except ValidationError as e:
        assert "range [0.0, 1.0]" in str(e)
        print("✓ Detected out of range value")

    # Test negative value
    try:
        invalid_freq = [0.5] * 47 + [-0.1]
        validate_frequency_array(invalid_freq, "Test Species")
        assert False, "Should have raised ValidationError for negative value"
    except ValidationError as e:
        assert "range [0.0, 1.0]" in str(e)
        print("✓ Detected negative value")

    # Test None
    try:
        validate_frequency_array(None, "Test Species")
        assert False, "Should have raised ValidationError for None"
    except ValidationError as e:
        assert "None" in str(e)
        print("✓ Detected None value")


def test_validate_week_index():
    """Test week index validation."""
    # Valid weeks
    validate_week_index(0)
    validate_week_index(47)
    validate_week_index(24)
    print("✓ Valid week indices accepted")

    # Invalid weeks
    try:
        validate_week_index(-1)
        assert False, "Should have raised ValidationError for -1"
    except ValidationError as e:
        assert "range [0, 47]" in str(e)
        print("✓ Detected negative week index")

    try:
        validate_week_index(48)
        assert False, "Should have raised ValidationError for 48"
    except ValidationError as e:
        assert "range [0, 47]" in str(e)
        print("✓ Detected week index too large")


def test_validate_species_name():
    """Test species name validation."""
    # Valid names
    validate_species_name("American Robin")
    validate_species_name("Red-tailed Hawk")
    validate_species_name("Canada Goose")
    print("✓ Valid species names accepted")

    # Empty name
    try:
        validate_species_name("")
        assert False, "Should have raised ValidationError for empty string"
    except ValidationError as e:
        assert "empty" in str(e).lower()
        print("✓ Detected empty species name")

    # Whitespace only
    try:
        validate_species_name("   ")
        assert False, "Should have raised ValidationError for whitespace"
    except ValidationError as e:
        assert "whitespace" in str(e).lower()
        print("✓ Detected whitespace-only species name")

    # Invalid characters
    try:
        validate_species_name("Unidentified sp.")
        assert False, "Should have raised ValidationError for 'sp.'"
    except ValidationError as e:
        assert "sp." in str(e)
        print("✓ Detected 'sp.' in species name")


def test_validate_category():
    """Test category validation."""
    # Valid categories
    for cat in ['resident', 'single-season', 'two-passage-migrant', 'vagrant', 'irregular']:
        validate_category(cat, "Test Species")
    print("✓ Valid categories accepted")

    # Invalid category
    try:
        validate_category("unknown", "Test Species")
        assert False, "Should have raised ValidationError for invalid category"
    except ValidationError as e:
        assert "Invalid category" in str(e)
        print("✓ Detected invalid category")


def test_validate_pattern_type():
    """Test pattern type validation."""
    # Valid patterns
    for pattern in ['year-round', 'irregular', 'two-passage', 'summer', 'winter']:
        validate_pattern_type(pattern, "Test Species")
    print("✓ Valid pattern types accepted")

    # Invalid pattern
    try:
        validate_pattern_type("unknown", "Test Species")
        assert False, "Should have raised ValidationError for invalid pattern"
    except ValidationError as e:
        assert "Invalid pattern type" in str(e)
        print("✓ Detected invalid pattern type")


def test_validate_species_code():
    """Test species code validation."""
    # Valid codes
    validate_species_code("amrobi", "American Robin")
    validate_species_code("rethaw", "Red-tailed Hawk")
    print("✓ Valid species codes accepted")

    # Wrong length
    try:
        validate_species_code("abc", "Test Species")
        assert False, "Should have raised ValidationError for wrong length"
    except ValidationError as e:
        assert "6 characters" in str(e)
        print("✓ Detected wrong code length")

    # Uppercase
    try:
        validate_species_code("AMROBI", "Test Species")
        assert False, "Should have raised ValidationError for uppercase"
    except ValidationError as e:
        assert "lowercase" in str(e)
        print("✓ Detected uppercase code")

    # Special characters
    try:
        validate_species_code("am-rob", "Test Species")
        assert False, "Should have raised ValidationError for special chars"
    except ValidationError as e:
        assert "alphanumeric" in str(e)
        print("✓ Detected non-alphanumeric code")


def test_validate_region_name():
    """Test region name validation."""
    # Valid names
    validate_region_name("washtenaw")
    validate_region_name("oakland_county")
    validate_region_name("wayne-county")
    print("✓ Valid region names accepted")

    # Path traversal attempt
    try:
        validate_region_name("../etc")
        assert False, "Should have raised ValidationError for path traversal"
    except ValidationError as e:
        assert "path separators" in str(e)
        print("✓ Detected path traversal attempt")

    # Invalid characters
    try:
        validate_region_name("region/name")
        assert False, "Should have raised ValidationError for slash"
    except ValidationError as e:
        assert "path separators" in str(e)
        print("✓ Detected invalid characters in region name")


def test_validate_valley_tuple():
    """Test valley tuple validation."""
    # Valid valleys
    validate_valley_tuple((10, 20), "Test Species")
    validate_valley_tuple((0, 47), "Test Species")
    validate_valley_tuple((43, 7), "Test Species")  # Wraparound
    print("✓ Valid valley tuples accepted")

    # Wrong type
    try:
        validate_valley_tuple([10, 20], "Test Species")
        assert False, "Should have raised ValidationError for list instead of tuple"
    except ValidationError as e:
        assert "tuple" in str(e)
        print("✓ Detected wrong type (list instead of tuple)")

    # Wrong length
    try:
        validate_valley_tuple((10,), "Test Species")
        assert False, "Should have raised ValidationError for single element"
    except ValidationError as e:
        assert "2 elements" in str(e)
        print("✓ Detected wrong tuple length")

    # Invalid week index
    try:
        validate_valley_tuple((10, 50), "Test Species")
        assert False, "Should have raised ValidationError for invalid week"
    except ValidationError as e:
        assert "range [0, 47]" in str(e)
        print("✓ Detected invalid week index in valley")


if __name__ == "__main__":
    print("Running validation tests...\n")

    test_validate_frequency_array()
    print()
    test_validate_week_index()
    print()
    test_validate_species_name()
    print()
    test_validate_category()
    print()
    test_validate_pattern_type()
    print()
    test_validate_species_code()
    print()
    test_validate_region_name()
    print()
    test_validate_valley_tuple()

    print("\n✓ All validation tests passed!")
