#!/usr/bin/env python3
"""
Valley detection utilities for bird migration pattern analysis.

A valley is defined as a period of absence or very low detection frequency,
indicating when a species is not present in the region.
"""


def detect_valleys(frequencies):
    """
    Detect valleys (absence periods) in frequency data.

    A valley is 4+ consecutive weeks below 15% of species' peak frequency,
    with a minimum threshold of 0.5% to ensure consistency with peak classification.

    Args:
        frequencies: List of 48 weekly frequency values (0.0 to 1.0)

    Returns:
        List of (start_week, end_week) tuples for each valley.
        Week indices are 0-indexed (0-47).

    Example:
        >>> frequencies = [0.5] * 10 + [0.01] * 5 + [0.5] * 33
        >>> detect_valleys(frequencies)
        [(10, 14)]
    """
    if not frequencies or len(frequencies) < 5:
        return []

    peak_freq = max(frequencies)
    if peak_freq == 0:
        return []

    # Use the maximum of 15% of peak OR 0.5% absolute threshold
    # This ensures weeks below 0.5% are always considered part of valleys
    threshold = max(peak_freq * 0.15, 0.005)

    valleys = []
    in_valley = False
    valley_start = None

    for i, freq in enumerate(frequencies):
        if freq < threshold:
            if not in_valley:
                # Start of a new valley
                in_valley = True
                valley_start = i
        else:
            if in_valley:
                # End of valley
                valley_length = i - valley_start
                if valley_length >= 4:
                    valleys.append((valley_start, i - 1))
                in_valley = False
                valley_start = None

    # Check if we ended in a valley
    if in_valley:
        valley_length = len(frequencies) - valley_start
        if valley_length >= 4:
            valleys.append((valley_start, len(frequencies) - 1))

    # Merge valleys that wrap around the year
    # If we have a valley at the end (touching week 47) and a valley at the start (touching week 0)
    # they should be merged into a single valley that wraps around
    if len(valleys) >= 2:
        first_valley = valleys[0]
        last_valley = valleys[-1]

        # Check if first valley starts at 0 and last valley ends at 47
        if first_valley[0] == 0 and last_valley[1] == 47:
            # Merge them: new valley goes from last_valley start to first_valley end
            merged_valley = (last_valley[0], first_valley[1])
            # Remove both valleys and add the merged one
            valleys = valleys[1:-1]  # Remove first and last
            valleys.append(merged_valley)

    return valleys
