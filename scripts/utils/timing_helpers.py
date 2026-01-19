#!/usr/bin/env python3
"""
Helper functions for calculating bird arrival/departure timing.

This module provides reusable functions for searching through frequency data
to find arrival weeks, peak weeks, and departure weeks. It handles the
complexity of year-wraparound cases (e.g., winter spanning December-February).
"""

from typing import List, Tuple, Optional

try:
    from .constants import WEEKS_PER_YEAR
except ImportError:
    from constants import WEEKS_PER_YEAR


def normalize_week(week: int) -> int:
    """
    Normalize a week number to be within [0, 47].

    Args:
        week: Week number (may be negative or >= 48)

    Returns:
        Normalized week number in range [0, 47]
    """
    return week % WEEKS_PER_YEAR


def week_range(start: int, end: int) -> List[int]:
    """
    Generate a list of weeks from start to end (exclusive), handling wraparound.

    If start > end, the range wraps around the year boundary.
    For example, week_range(45, 5) returns [45, 46, 47, 0, 1, 2, 3, 4].

    Args:
        start: Starting week (inclusive)
        end: Ending week (exclusive)

    Returns:
        List of week numbers in order
    """
    if start < end:
        return list(range(start, end))
    else:
        # Wraparound case
        return list(range(start, WEEKS_PER_YEAR)) + list(range(0, end))


def find_arrival_week(
    frequencies: List[float],
    search_start: int,
    search_end: int,
    threshold: float
) -> Optional[int]:
    """
    Find the first week where frequency exceeds threshold in a search range.

    Handles wraparound cases where search_start > search_end.

    Args:
        frequencies: List of 48 frequency values
        search_start: First week to search (inclusive)
        search_end: Last week to search (exclusive)
        threshold: Minimum frequency to consider as "arrived"

    Returns:
        Week number of arrival, or None if not found
    """
    for week in week_range(search_start, search_end):
        if frequencies[week] >= threshold:
            return week
    return None


def find_peak_week(
    frequencies: List[float],
    search_start: int,
    search_end: int
) -> Tuple[int, float]:
    """
    Find the week with highest frequency in a search range.

    Handles wraparound cases where search_start > search_end.

    Args:
        frequencies: List of 48 frequency values
        search_start: First week to search (inclusive)
        search_end: Last week to search (exclusive)

    Returns:
        Tuple of (peak_week, peak_frequency)
    """
    weeks = week_range(search_start, search_end)
    if not weeks:
        return (search_start, 0.0)

    peak_week = weeks[0]
    peak_freq = frequencies[peak_week]

    for week in weeks[1:]:
        if frequencies[week] > peak_freq:
            peak_freq = frequencies[week]
            peak_week = week

    return (peak_week, peak_freq)


def find_departure_week(
    frequencies: List[float],
    peak_week: int,
    search_end: int,
    threshold: float
) -> Optional[int]:
    """
    Find the last week before frequency drops below threshold.

    Searches from peak_week to search_end for when frequency drops below
    threshold, and returns the week before that drop.

    Handles wraparound cases.

    Args:
        frequencies: List of 48 frequency values
        peak_week: Week to start searching from
        search_end: Last week to search (exclusive)
        threshold: Minimum frequency to consider as "present"

    Returns:
        Week number of departure, or search_end-1 if threshold never crossed
    """
    weeks = week_range(peak_week, search_end)

    for week in weeks:
        if frequencies[week] < threshold:
            # Found where it drops below - return previous week
            prev_week = normalize_week(week - 1)
            return prev_week

    # Never dropped below threshold - return last week of search range
    return normalize_week(search_end - 1)


def find_last_week_above_threshold(
    frequencies: List[float],
    search_start: int,
    search_end: int,
    threshold: float
) -> Optional[int]:
    """
    Find the last week where frequency exceeds threshold in a search range.

    Useful for finding departure in single-season patterns where we search
    backwards through the presence period.

    Args:
        frequencies: List of 48 frequency values
        search_start: First week of search range (inclusive)
        search_end: Last week of search range (exclusive)
        threshold: Minimum frequency threshold

    Returns:
        Week number, or None if not found
    """
    weeks = week_range(search_start, search_end)

    # Search backwards
    for week in reversed(weeks):
        if frequencies[week] >= threshold:
            return week
    return None


def calculate_threshold(frequencies: List[float], peak_ratio: float = 0.10, absolute_min: float = 0.001) -> float:
    """
    Calculate the threshold for arrival/departure detection.

    Uses the greater of:
    - peak_ratio of the maximum frequency
    - absolute_min value

    Args:
        frequencies: List of 48 frequency values
        peak_ratio: Ratio of peak frequency to use (default 10%)
        absolute_min: Absolute minimum threshold (default 0.1%)

    Returns:
        Threshold value
    """
    peak_freq = max(frequencies)
    return max(peak_freq * peak_ratio, absolute_min)


def identify_valley_type(valley: Tuple[int, int]) -> str:
    """
    Determine if a valley is a winter or summer valley.

    Winter weeks: 44-47, 0-7 (December through February)
    Summer weeks: 18-32 (May through August)

    Args:
        valley: Tuple of (start_week, end_week)

    Returns:
        'winter' or 'summer'
    """
    valley_start, valley_end = valley

    # Winter weeks (wraps around year boundary)
    winter_weeks = set(range(44, 48)) | set(range(0, 8))

    # Count how many valley weeks fall in winter
    if valley_start <= valley_end:
        valley_weeks = set(range(valley_start, valley_end + 1))
    else:
        # Valley wraps around year
        valley_weeks = set(range(valley_start, 48)) | set(range(0, valley_end + 1))

    winter_overlap = len(valley_weeks & winter_weeks)

    # If more than half the valley is in winter, it's a winter valley
    if winter_overlap > len(valley_weeks) / 2:
        return 'winter'
    return 'summer'


def get_presence_weeks(
    valley_start: int,
    valley_end: int,
    is_winter_valley: bool
) -> List[int]:
    """
    Get the list of weeks when a species is present based on its valley.

    For a winter valley (species absent in winter), presence is from
    valley_end+1 to valley_start-1.

    For a summer valley (species absent in summer), presence wraps around
    the year from valley_end+1 through winter to valley_start-1.

    Args:
        valley_start: First week of valley (when species becomes absent)
        valley_end: Last week of valley (before species returns)
        is_winter_valley: True if valley is in winter (species is a summer breeder)

    Returns:
        List of week numbers when species is present
    """
    if is_winter_valley:
        # Summer breeder: present from valley_end+1 to valley_start-1
        if valley_end < valley_start:
            # Valley wraps around year (typical winter valley, e.g., weeks 44-7)
            return list(range(valley_end + 1, valley_start))
        else:
            # Unusual: valley doesn't wrap
            return list(range(valley_end + 1, 48)) + list(range(0, valley_start))
    else:
        # Winter visitor: present from valley_end+1 through winter to valley_start-1
        # This wraps around the year
        return week_range(valley_end + 1, valley_start)


def find_passage_timing(
    frequencies: List[float],
    passage_start: int,
    passage_end: int,
    threshold: float
) -> dict:
    """
    Calculate arrival, peak, and departure for a migration passage.

    This is the core timing calculation used for spring/fall passages
    in two-passage migrants.

    Args:
        frequencies: List of 48 frequency values
        passage_start: First week of passage period (after valley ends)
        passage_end: Last week of passage period (before next valley starts)
        threshold: Frequency threshold for arrival/departure detection

    Returns:
        Dictionary with 'arrival', 'peak', 'departure' week numbers (or None)
    """
    # Find arrival
    arrival = find_arrival_week(frequencies, passage_start, passage_end, threshold)

    # Find peak
    peak, _ = find_peak_week(frequencies, passage_start, passage_end)

    # Find departure
    departure = find_departure_week(frequencies, peak, passage_end, threshold)

    return {
        'arrival': arrival,
        'peak': peak,
        'departure': departure
    }
