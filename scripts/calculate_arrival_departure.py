#!/usr/bin/env python3
"""
Calculate arrival and departure weeks for bird species based on migration patterns.
"""

import csv
import json
from pathlib import Path


def week_to_date_range(week_num):
    """Convert week number (0-47) to readable date range like 'May 1-7' or 'early May'"""
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    month_idx = week_num // 4
    week_in_month = week_num % 4

    month = months[month_idx]

    # Calculate day ranges for each week
    day_starts = [1, 8, 15, 22]
    day_ends = [7, 14, 21, 28]  # Approximate, good enough

    start_day = day_starts[week_in_month]
    end_day = day_ends[week_in_month]

    # Also provide a shorthand version
    week_labels = ['early', 'mid', 'late', 'late']
    shorthand = f"{week_labels[week_in_month]} {month}"

    return f"{month} {start_day}-{end_day}", shorthand


def find_arrival_departure(frequencies, peak_frequency, is_winter_resident=False):
    """
    Find arrival and departure weeks for a single migration passage.

    Arrival = first week exceeding 25% of peak OR 0.1% absolute (whichever higher)
    Departure = last week exceeding 25% of peak OR 0.1% absolute (whichever higher)

    For winter residents, we need to handle year-wrap (arrival in fall, departure in spring)

    Returns: (arrival_week, departure_week, peak_week)
    """
    threshold_relative = peak_frequency * 0.25
    threshold_absolute = 0.001  # 0.1%
    threshold = max(threshold_relative, threshold_absolute)

    # Find peak week (handle floating point comparison)
    max_freq = max(frequencies)
    peak_week = frequencies.index(max_freq)

    if is_winter_resident:
        # For winter residents, the low point is in summer (weeks 21-31)
        # Arrival happens in fall (after summer), departure in spring (before summer)

        # Find arrival: scan forward from end of summer (week 31) wrapping around
        arrival_week = None
        for offset in range(48):
            week_idx = (31 + offset) % 48
            if frequencies[week_idx] >= threshold:
                arrival_week = week_idx
                break

        # Find departure: scan backward from beginning of summer (week 21)
        departure_week = None
        for offset in range(48):
            week_idx = (21 - offset) % 48
            if frequencies[week_idx] >= threshold:
                departure_week = week_idx
                break

    else:
        # Standard migration: find low point (usually winter or between passages)
        min_freq = min(frequencies)
        low_point = frequencies.index(min_freq)

        # Find arrival: scan forward from low point
        arrival_week = None
        for offset in range(48):
            week_idx = (low_point + offset) % 48
            if frequencies[week_idx] >= threshold:
                arrival_week = week_idx
                break

        # Find departure: scan forward from peak
        departure_week = None
        for offset in range(48):
            week_idx = (peak_week + offset) % 48
            if frequencies[week_idx] < threshold:
                # Found first week below threshold after peak
                # Departure is the previous week
                departure_week = (week_idx - 1) % 48
                break

        # If we never drop below threshold, departure is end of year
        if departure_week is None:
            departure_week = 47

    return arrival_week, departure_week, peak_week


def find_valley_between_peaks(frequencies, peak1_idx, peak2_idx):
    """Find the minimum frequency between two peaks"""
    start_idx = min(peak1_idx, peak2_idx)
    end_idx = max(peak1_idx, peak2_idx)

    valley_section = frequencies[start_idx:end_idx+1]
    valley_min = min(valley_section)
    valley_idx = start_idx + valley_section.index(valley_min)

    return valley_idx, valley_min


def calculate_migration_timing(species_name, frequencies, category, flags, peak_frequency):
    """Calculate arrival/departure timing based on species category"""

    is_winter_resident = 'winter_resident' in flags

    # Resident: year-round
    if category == 'Resident':
        return {
            'species': species_name,
            'category': category,
            'pattern': 'Year-round',
            'spring_arrival': '',
            'spring_arrival_short': '',
            'spring_peak': '',
            'spring_peak_short': '',
            'spring_departure': '',
            'spring_departure_short': '',
            'fall_arrival': '',
            'fall_arrival_short': '',
            'fall_peak': '',
            'fall_peak_short': '',
            'fall_departure': '',
            'fall_departure_short': ''
        }

    # Vagrant: irregular
    if category == 'Vagrant':
        return {
            'species': species_name,
            'category': category,
            'pattern': 'Irregular',
            'spring_arrival': '',
            'spring_arrival_short': '',
            'spring_peak': '',
            'spring_peak_short': '',
            'spring_departure': '',
            'spring_departure_short': '',
            'fall_arrival': '',
            'fall_arrival_short': '',
            'fall_peak': '',
            'fall_peak_short': '',
            'fall_departure': '',
            'fall_departure_short': ''
        }

    # Single-season: one arrival, one departure
    if category == 'Single-season':
        arrival_week, departure_week, peak_week = find_arrival_departure(
            frequencies, peak_frequency, is_winter_resident
        )

        arrival_long, arrival_short = week_to_date_range(arrival_week) if arrival_week is not None else ('', '')
        departure_long, departure_short = week_to_date_range(departure_week) if departure_week is not None else ('', '')
        peak_long, peak_short = week_to_date_range(peak_week)

        pattern_type = 'Winter resident' if is_winter_resident else 'Single passage'

        return {
            'species': species_name,
            'category': category,
            'pattern': pattern_type,
            'spring_arrival': arrival_long,
            'spring_arrival_short': arrival_short,
            'spring_peak': peak_long,
            'spring_peak_short': peak_short,
            'spring_departure': departure_long,
            'spring_departure_short': departure_short,
            'fall_arrival': '',
            'fall_arrival_short': '',
            'fall_peak': '',
            'fall_peak_short': '',
            'fall_departure': '',
            'fall_departure_short': ''
        }

    # Two-passage migrant: spring and fall passages
    if category == 'Two-passage migrant':
        # Split the year into spring (weeks 0-23, Jan-Jun) and fall (weeks 24-47, Jul-Dec)
        spring_freqs = frequencies[0:24]
        fall_freqs = frequencies[24:48]

        # Find peak in each half
        spring_max = max(spring_freqs)
        spring_peak_week = spring_freqs.index(spring_max)

        fall_max = max(fall_freqs)
        fall_peak_week = 24 + fall_freqs.index(fall_max)

        # Find valley between peaks (dividing point between passages)
        valley_week, valley_freq = find_valley_between_peaks(frequencies, spring_peak_week, fall_peak_week)

        # Calculate spring passage
        # Arrival: first week exceeding threshold, scanning forward from year start
        spring_arrival_week = None
        spring_threshold = max(spring_max * 0.25, 0.001)
        for week in range(spring_peak_week + 1):
            if frequencies[week] >= spring_threshold:
                spring_arrival_week = week
                break

        # Departure: last week exceeding threshold, scanning forward from spring peak
        spring_departure_week = None
        for week in range(spring_peak_week, valley_week + 1):
            if frequencies[week] < spring_threshold:
                spring_departure_week = week - 1
                break
        # If we never dropped below threshold before valley, use the week before valley
        if spring_departure_week is None:
            spring_departure_week = valley_week

        # Calculate fall passage
        # Arrival: first week exceeding threshold, scanning forward from valley
        fall_arrival_week = None
        fall_threshold = max(fall_max * 0.25, 0.001)
        for week in range(valley_week, fall_peak_week + 1):
            if frequencies[week] >= fall_threshold:
                fall_arrival_week = week
                break

        # Departure: last week exceeding threshold, scanning forward from fall peak
        fall_departure_week = None
        for week in range(fall_peak_week, 48):
            if frequencies[week] < fall_threshold:
                fall_departure_week = week - 1
                break
        if fall_departure_week is None:
            fall_departure_week = 47

        # Convert to date ranges
        spring_arr_long, spring_arr_short = week_to_date_range(spring_arrival_week) if spring_arrival_week is not None else ('', '')
        spring_peak_long, spring_peak_short = week_to_date_range(spring_peak_week)
        spring_dep_long, spring_dep_short = week_to_date_range(spring_departure_week)

        fall_arr_long, fall_arr_short = week_to_date_range(fall_arrival_week)
        fall_peak_long, fall_peak_short = week_to_date_range(fall_peak_week)
        fall_dep_long, fall_dep_short = week_to_date_range(fall_departure_week)

        return {
            'species': species_name,
            'category': category,
            'pattern': 'Two passages',
            'spring_arrival': spring_arr_long,
            'spring_arrival_short': spring_arr_short,
            'spring_peak': spring_peak_long,
            'spring_peak_short': spring_peak_short,
            'spring_departure': spring_dep_long,
            'spring_departure_short': spring_dep_short,
            'fall_arrival': fall_arr_long,
            'fall_arrival_short': fall_arr_short,
            'fall_peak': fall_peak_long,
            'fall_peak_short': fall_peak_short,
            'fall_departure': fall_dep_long,
            'fall_departure_short': fall_dep_short
        }


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 calculate_arrival_departure.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    intermediate_path = region_path / "intermediate"

    # Load the migration pattern classifications
    classifications_file = intermediate_path / f"{region_name}_migration_pattern_classifications.csv"

    print(f"Loading classifications from: {classifications_file}")

    classifications = {}
    with open(classifications_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            classifications[row['species']] = {
                'category': row['category'],
                'flags': row['edge_case_flags'],
                'peak_frequency': float(row['peak_frequency'])
            }

    # Load the frequency data
    json_file = intermediate_path / f"{region_name}_ebird_data.json"

    print(f"Loading frequency data from: {json_file}")

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Calculate timing for each species
    results = []

    for species_data in data['species_data']:
        species_name = species_data['species']
        frequencies = species_data['frequencies']

        if species_name not in classifications:
            continue

        classification = classifications[species_name]

        timing = calculate_migration_timing(
            species_name,
            frequencies,
            classification['category'],
            classification['flags'],
            classification['peak_frequency']
        )

        results.append(timing)

    # Save results
    output_file = intermediate_path / f"{region_name}_migration_timing.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'species', 'category', 'pattern',
            'spring_arrival', 'spring_arrival_short',
            'spring_peak', 'spring_peak_short',
            'spring_departure', 'spring_departure_short',
            'fall_arrival', 'fall_arrival_short',
            'fall_peak', 'fall_peak_short',
            'fall_departure', 'fall_departure_short'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Migration timing calculated!")
    print(f"Results saved to: {output_file}")

    # Print some examples
    print("\n=== Examples ===")

    for pattern in ['Year-round', 'Irregular', 'Single passage', 'Winter resident', 'Two passages']:
        examples = [r for r in results if r['pattern'] == pattern][:2]
        if examples:
            print(f"\n{pattern}:")
            for ex in examples:
                print(f"  {ex['species']}:")
                if ex['spring_arrival']:
                    print(f"    Spring: {ex['spring_arrival_short']} → {ex['spring_peak_short']} → {ex['spring_departure_short']}")
                if ex['fall_arrival']:
                    print(f"    Fall: {ex['fall_arrival_short']} → {ex['fall_peak_short']} → {ex['fall_departure_short']}")


if __name__ == "__main__":
    main()
