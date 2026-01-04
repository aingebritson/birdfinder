#!/usr/bin/env python3
"""
Input validation utilities for BirdFinder data processing pipeline.

This module provides validation functions to ensure data integrity
throughout the pipeline and fail fast with clear error messages.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional

# Import constants for validation
from .constants import (
    WEEKS_PER_YEAR,
    WEEK_INDEX_MIN,
    WEEK_INDEX_MAX,
    FREQUENCY_MIN,
    FREQUENCY_MAX,
    SPECIES_CODE_LENGTH,
    VALID_CATEGORIES,
    VALID_PATTERN_TYPES
)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_frequency_array(frequencies: List[float], species_name: str = "Unknown") -> None:
    """
    Validate that frequency array is well-formed.

    Args:
        frequencies: List of weekly frequency values
        species_name: Name of species (for error messages)

    Raises:
        ValidationError: If validation fails

    Checks:
        - Array exists and is not None
        - Array length is exactly 48 (one per week)
        - All values are numeric
        - All values are in range [0.0, 1.0]
    """
    if frequencies is None:
        raise ValidationError(f"Frequency array is None for species: {species_name}")

    if not isinstance(frequencies, (list, tuple)):
        raise ValidationError(
            f"Frequency array must be a list or tuple for species: {species_name}, "
            f"got {type(frequencies).__name__}"
        )

    if len(frequencies) != WEEKS_PER_YEAR:
        raise ValidationError(
            f"Frequency array must have exactly {WEEKS_PER_YEAR} values (one per week) for species: {species_name}, "
            f"got {len(frequencies)} values"
        )

    for i, freq in enumerate(frequencies):
        if not isinstance(freq, (int, float)):
            raise ValidationError(
                f"Frequency value at week {i} must be numeric for species: {species_name}, "
                f"got {type(freq).__name__}: {freq}"
            )

        if freq < FREQUENCY_MIN or freq > FREQUENCY_MAX:
            raise ValidationError(
                f"Frequency value at week {i} must be in range [{FREQUENCY_MIN}, {FREQUENCY_MAX}] for species: {species_name}, "
                f"got {freq}"
            )


def validate_week_index(week: int, context: str = "") -> None:
    """
    Validate that week index is in valid range.

    Args:
        week: Week index (0-47)
        context: Additional context for error message

    Raises:
        ValidationError: If week index is out of range
    """
    if not isinstance(week, int):
        raise ValidationError(
            f"Week index must be an integer{' (' + context + ')' if context else ''}, "
            f"got {type(week).__name__}: {week}"
        )

    if week < WEEK_INDEX_MIN or week > WEEK_INDEX_MAX:
        raise ValidationError(
            f"Week index must be in range [{WEEK_INDEX_MIN}, {WEEK_INDEX_MAX}]{' (' + context + ')' if context else ''}, "
            f"got {week}"
        )


def validate_species_name(name: str) -> None:
    """
    Validate species name is well-formed.

    Args:
        name: Species name

    Raises:
        ValidationError: If name is invalid

    Checks:
        - Name is not empty
        - Name is a string
        - Name doesn't contain invalid characters
    """
    if not name:
        raise ValidationError("Species name cannot be empty")

    if not isinstance(name, str):
        raise ValidationError(
            f"Species name must be a string, got {type(name).__name__}: {name}"
        )

    if len(name.strip()) == 0:
        raise ValidationError("Species name cannot be whitespace only")

    # Check for problematic characters (these should have been filtered during parsing)
    if 'sp.' in name or '/' in name:
        raise ValidationError(
            f"Species name contains invalid characters (sp. or /): {name}"
        )


def validate_category(category: str, species_name: str = "Unknown") -> None:
    """
    Validate migration category is valid.

    Args:
        category: Category string
        species_name: Name of species (for error messages)

    Raises:
        ValidationError: If category is invalid
    """
    if not isinstance(category, str):
        raise ValidationError(
            f"Category must be a string for species: {species_name}, "
            f"got {type(category).__name__}: {category}"
        )

    if category not in VALID_CATEGORIES:
        raise ValidationError(
            f"Invalid category '{category}' for species: {species_name}. "
            f"Must be one of: {', '.join(sorted(VALID_CATEGORIES))}"
        )


def validate_pattern_type(pattern_type: str, species_name: str = "Unknown") -> None:
    """
    Validate pattern type is valid.

    Args:
        pattern_type: Pattern type string
        species_name: Name of species (for error messages)

    Raises:
        ValidationError: If pattern type is invalid
    """
    if not isinstance(pattern_type, str):
        raise ValidationError(
            f"Pattern type must be a string for species: {species_name}, "
            f"got {type(pattern_type).__name__}: {pattern_type}"
        )

    if pattern_type not in VALID_PATTERN_TYPES:
        raise ValidationError(
            f"Invalid pattern type '{pattern_type}' for species: {species_name}. "
            f"Must be one of: {', '.join(sorted(VALID_PATTERN_TYPES))}"
        )


def validate_species_code(code: str, species_name: str = "Unknown") -> None:
    """
    Validate species code format.

    Args:
        code: 6-character species code
        species_name: Name of species (for error messages)

    Raises:
        ValidationError: If code is invalid

    Checks:
        - Code is a string
        - Code is exactly 6 characters
        - Code is lowercase alphanumeric
    """
    if not isinstance(code, str):
        raise ValidationError(
            f"Species code must be a string for species: {species_name}, "
            f"got {type(code).__name__}: {code}"
        )

    if len(code) != SPECIES_CODE_LENGTH:
        raise ValidationError(
            f"Species code must be exactly {SPECIES_CODE_LENGTH} characters for species: {species_name}, "
            f"got {len(code)} characters: '{code}'"
        )

    if not code.islower():
        raise ValidationError(
            f"Species code must be lowercase for species: {species_name}, "
            f"got: '{code}'"
        )

    if not code.isalnum():
        raise ValidationError(
            f"Species code must be alphanumeric for species: {species_name}, "
            f"got: '{code}'"
        )


def validate_file_exists(file_path: Path, description: str = "File") -> None:
    """
    Validate that a file exists and is readable.

    Args:
        file_path: Path to file
        description: Human-readable description of file

    Raises:
        ValidationError: If file doesn't exist or isn't readable
    """
    if not isinstance(file_path, Path):
        file_path = Path(file_path)

    if not file_path.exists():
        raise ValidationError(
            f"{description} not found: {file_path}"
        )

    if not file_path.is_file():
        raise ValidationError(
            f"{description} is not a file: {file_path}"
        )

    if not file_path.stat().st_size > 0:
        raise ValidationError(
            f"{description} is empty: {file_path}"
        )


def validate_json_structure(data: Any, required_keys: List[str],
                           description: str = "JSON data") -> None:
    """
    Validate that JSON data has required structure.

    Args:
        data: Parsed JSON data
        required_keys: List of required top-level keys
        description: Human-readable description of data

    Raises:
        ValidationError: If structure is invalid
    """
    if not isinstance(data, dict):
        raise ValidationError(
            f"{description} must be a dictionary/object, "
            f"got {type(data).__name__}"
        )

    missing_keys = [key for key in required_keys if key not in data]
    if missing_keys:
        raise ValidationError(
            f"{description} missing required keys: {', '.join(missing_keys)}"
        )


def validate_species_data_structure(species: Dict[str, Any], index: int = 0) -> None:
    """
    Validate complete species data structure.

    Args:
        species: Species data dictionary
        index: Index in array (for error messages)

    Raises:
        ValidationError: If structure is invalid
    """
    # Check required keys
    required_keys = ['name', 'code', 'category', 'timing', 'weekly_frequency']
    missing_keys = [key for key in required_keys if key not in species]
    if missing_keys:
        raise ValidationError(
            f"Species at index {index} missing required keys: {', '.join(missing_keys)}"
        )

    # Validate individual fields
    validate_species_name(species['name'])
    validate_species_code(species['code'], species['name'])
    validate_category(species['category'], species['name'])
    validate_frequency_array(species['weekly_frequency'], species['name'])

    # Validate timing is a dict
    if not isinstance(species['timing'], dict):
        raise ValidationError(
            f"Timing must be a dictionary for species: {species['name']}, "
            f"got {type(species['timing']).__name__}"
        )

    # Validate flags if present
    if 'flags' in species:
        if not isinstance(species['flags'], list):
            raise ValidationError(
                f"Flags must be a list for species: {species['name']}, "
                f"got {type(species['flags']).__name__}"
            )


def validate_region_name(region_name: str) -> None:
    """
    Validate region name format.

    Args:
        region_name: Region name (directory name)

    Raises:
        ValidationError: If region name is invalid
    """
    if not region_name:
        raise ValidationError("Region name cannot be empty")

    if not isinstance(region_name, str):
        raise ValidationError(
            f"Region name must be a string, got {type(region_name).__name__}"
        )

    # Check for path traversal attempts
    if '..' in region_name or '/' in region_name or '\\' in region_name:
        raise ValidationError(
            f"Invalid region name (contains path separators): {region_name}"
        )

    # Must be valid directory name
    if not region_name.replace('_', '').replace('-', '').isalnum():
        raise ValidationError(
            f"Region name must be alphanumeric (with _ or -): {region_name}"
        )


def validate_valley_tuple(valley: tuple, species_name: str = "Unknown") -> None:
    """
    Validate valley tuple format.

    Args:
        valley: (start_week, end_week) tuple
        species_name: Name of species (for error messages)

    Raises:
        ValidationError: If valley tuple is invalid
    """
    if not isinstance(valley, tuple):
        raise ValidationError(
            f"Valley must be a tuple for species: {species_name}, "
            f"got {type(valley).__name__}"
        )

    if len(valley) != 2:
        raise ValidationError(
            f"Valley tuple must have exactly 2 elements (start, end) for species: {species_name}, "
            f"got {len(valley)} elements"
        )

    start, end = valley

    # Validate week indices
    validate_week_index(start, f"valley start for {species_name}")
    validate_week_index(end, f"valley end for {species_name}")

    # For non-wraparound valleys, start should be before end
    # For wraparound valleys, start > end is valid (e.g., week 43 to week 7)
    # So we don't validate ordering here
