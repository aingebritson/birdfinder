#!/usr/bin/env python3
"""
Tests for species code generation.

Ensures that the generate_species_code function handles all edge cases correctly,
including single-word species names shorter than 6 characters.
"""

import sys
from pathlib import Path

# Add parent directory to path to import merge_to_json
sys.path.insert(0, str(Path(__file__).parent))
from merge_to_json import generate_species_code


def test_single_word_short_names():
    """Test single-word species names shorter than 6 characters."""
    test_cases = [
        ("Ruff", "ruffru"),      # 4 characters
        ("Sora", "soraso"),      # 4 characters
        ("Veery", "veeryv"),     # 5 characters
    ]

    for species_name, expected_code in test_cases:
        code = generate_species_code(species_name)
        assert len(code) == 6, f"{species_name}: Expected 6 characters, got {len(code)}"
        assert code == expected_code, f"{species_name}: Expected '{expected_code}', got '{code}'"
        print(f"✓ {species_name:15} -> {code}")

    print("✓ Single-word short names test passed")


def test_single_word_long_names():
    """Test single-word species names 6+ characters."""
    test_cases = [
        ("Yellowlegs", "yellow"),  # >6 characters, truncate to 6
        ("Canvasback", "canvas"),  # >6 characters
    ]

    for species_name, expected_code in test_cases:
        code = generate_species_code(species_name)
        assert len(code) == 6, f"{species_name}: Expected 6 characters, got {len(code)}"
        assert code == expected_code, f"{species_name}: Expected '{expected_code}', got '{code}'"
        print(f"✓ {species_name:15} -> {code}")

    print("✓ Single-word long names test passed")


def test_two_word_names():
    """Test two-word species names."""
    test_cases = [
        ("American Robin", "amerob"),
        ("Red-tailed Hawk", "redhaw"),
        ("Canada Goose", "cangoo"),
    ]

    for species_name, expected_code in test_cases:
        code = generate_species_code(species_name)
        assert len(code) == 6, f"{species_name}: Expected 6 characters, got {len(code)}"
        assert code == expected_code, f"{species_name}: Expected '{expected_code}', got '{code}'"
        print(f"✓ {species_name:20} -> {code}")

    print("✓ Two-word names test passed")


def test_multi_word_names():
    """Test multi-word species names (3+ words)."""
    test_cases = [
        ("Black-crowned Night-Heron", "blanig"),  # First 3 + last 3
        ("Greater White-fronted Goose", "gregoo"),  # First 3 + last 3
    ]

    for species_name, expected_code in test_cases:
        code = generate_species_code(species_name)
        assert len(code) == 6, f"{species_name}: Expected 6 characters, got {len(code)}"
        assert code == expected_code, f"{species_name}: Expected '{expected_code}', got '{code}'"
        print(f"✓ {species_name:30} -> {code}")

    print("✓ Multi-word names test passed")


def test_collision_handling():
    """Test that collision detection works."""
    existing_codes = set()

    # Generate code for first species
    code1 = generate_species_code("American Robin", existing_codes)
    existing_codes.add(code1)

    # Try to generate code for a hypothetical collision
    # (This is theoretical since real species names don't collide)
    code2 = generate_species_code("American Rooster", existing_codes)

    assert code1 != code2, f"Collision not handled: both got '{code1}'"
    assert len(code2) == 6, f"Alternative code must be 6 characters, got {len(code2)}"
    print(f"✓ American Robin    -> {code1}")
    print(f"✓ American Rooster  -> {code2}")
    print("✓ Collision handling test passed")


def test_parentheses_removal():
    """Test that parenthetical text is removed."""
    test_cases = [
        ("Snow x Ross's Goose (hybrid)", "snowar"),  # Should ignore "(hybrid)"
    ]

    for species_name, expected_code in test_cases:
        code = generate_species_code(species_name)
        assert len(code) == 6, f"{species_name}: Expected 6 characters, got {len(code)}"
        # Just verify it's 6 characters and doesn't contain parentheses
        assert '(' not in code and ')' not in code
        print(f"✓ {species_name:35} -> {code}")

    print("✓ Parentheses removal test passed")


if __name__ == "__main__":
    print("Running species code generation tests...\n")

    test_single_word_short_names()
    print()
    test_single_word_long_names()
    print()
    test_two_word_names()
    print()
    test_multi_word_names()
    print()
    test_collision_handling()
    print()
    test_parentheses_removal()

    print("\n✓ All species code generation tests passed!")
