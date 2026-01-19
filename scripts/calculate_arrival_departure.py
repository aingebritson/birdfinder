#!/usr/bin/env python3
"""
Calculate arrival and departure weeks for bird species based on migration patterns.
Handles different pattern types: year-round, irregular, two-passage, summer, winter.
"""

import csv
import json
from pathlib import Path
import sys

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.valley_detection import detect_valleys
from utils.constants import (
    WEEKS_PER_YEAR,
    ARRIVAL_THRESHOLD_PEAK_RATIO,
    ARRIVAL_THRESHOLD_ABSOLUTE
)
from utils.timing_helpers import (
    find_arrival_week,
    find_peak_week,
    find_departure_week,
    find_last_week_above_threshold,
    calculate_threshold,
    identify_valley_type,
    get_presence_weeks,
    find_passage_timing,
    week_range
)


def week_to_date_range(week_num):
    """Convert week number (0-47) to readable date range like 'May 1-7'"""
    months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]

    # Days in each month (non-leap year)
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    month_idx = week_num // 4
    week_in_month = week_num % 4

    month = months[month_idx]

    # Calculate day ranges for each week
    day_starts = [1, 8, 15, 22]

    start_day = day_starts[week_in_month]

    # Week 4 ends on the last day of the month, other weeks end on start_day + 6
    if week_in_month == 3:
        end_day = days_in_month[month_idx]
    else:
        end_day = start_day + 6

    return f"{month} {start_day}-{end_day}"


def calculate_timing_year_round(species_name, frequencies, category, pattern_type):
    """
    Year-round resident: no timing data needed
    Display: "Year-round Resident"
    """
    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'status': 'year-round'
    }


def calculate_timing_irregular(species_name, frequencies, category, pattern_type):
    """
    Irregular presence (vagrant or 3+ peaks or 2 peaks <12 weeks apart)
    Display: Simplified timing
    - First appears: First week > 0.1%
    - Peak: Week with highest frequency
    - Last appears: Last week > 0.1%
    """
    threshold = 0.001  # 0.1%

    # Find first appearance
    first_week = None
    for i, freq in enumerate(frequencies):
        if freq > threshold:
            first_week = i
            break

    # Find last appearance
    last_week = None
    for i in range(len(frequencies) - 1, -1, -1):
        if frequencies[i] > threshold:
            last_week = i
            break

    # Find peak
    max_freq = max(frequencies)
    peak_week = frequencies.index(max_freq)

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'status': 'irregular',
        'first_appears': week_to_date_range(first_week) if first_week is not None else '',
        'peak': week_to_date_range(peak_week),
        'last_appears': week_to_date_range(last_week) if last_week is not None else ''
    }


def calculate_timing_two_passage(species_name, frequencies, category, pattern_type, valleys):
    """
    Two-passage migrant (2 valleys: one summer, one winter).

    Display: Spring arrival/peak/departure + Fall arrival/peak/departure

    Args:
        species_name: Name of the species
        frequencies: List of 48 weekly frequency values
        category: Migration category
        pattern_type: Pattern type classification
        valleys: List of (start, end) tuples for detected valleys

    Returns:
        Dictionary with timing data for spring and fall passages
    """
    if len(valleys) != 2:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Identify which valley is winter and which is summer
    if identify_valley_type(valleys[0]) == 'winter':
        winter_valley = valleys[0]
        summer_valley = valleys[1]
    else:
        summer_valley = valleys[0]
        winter_valley = valleys[1]

    threshold = calculate_threshold(frequencies, ARRIVAL_THRESHOLD_PEAK_RATIO, ARRIVAL_THRESHOLD_ABSOLUTE)

    # Spring passage: after winter valley ends, before summer valley begins
    spring_start = (winter_valley[1] + 1) % WEEKS_PER_YEAR
    spring_end = summer_valley[0]

    # Fall passage: after summer valley ends, before winter valley begins
    fall_start = (summer_valley[1] + 1) % WEEKS_PER_YEAR
    fall_end = winter_valley[0]

    # Calculate spring timing using helpers
    spring_timing = find_passage_timing(frequencies, spring_start, spring_end, threshold)

    # Calculate fall timing using helpers
    fall_timing = find_passage_timing(frequencies, fall_start, fall_end, threshold)

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'spring_arrival': week_to_date_range(spring_timing['arrival']) if spring_timing['arrival'] is not None else '',
        'spring_peak': week_to_date_range(spring_timing['peak']),
        'spring_departure': week_to_date_range(spring_timing['departure']) if spring_timing['departure'] is not None else '',
        'fall_arrival': week_to_date_range(fall_timing['arrival']) if fall_timing['arrival'] is not None else '',
        'fall_peak': week_to_date_range(fall_timing['peak']),
        'fall_departure': week_to_date_range(fall_timing['departure']) if fall_timing['departure'] is not None else ''
    }


def calculate_timing_three_valley_migrant(species_name, frequencies, category, pattern_type, valleys):
    """
    Three-valley migrant (winter-summer-winter pattern).

    Common for species that pass through briefly in spring and fall.
    Valleys: [winter, summer, winter]
    Presence: Spring passage (between valley 0 and 1) + Fall passage (between valley 1 and 2)

    Args:
        species_name: Name of the species
        frequencies: List of 48 weekly frequency values
        category: Migration category
        pattern_type: Pattern type classification
        valleys: List of 3 (start, end) tuples for detected valleys

    Returns:
        Dictionary with timing data for spring and fall passages
    """
    if len(valleys) != 3:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    winter_valley_1 = valleys[0]  # First winter valley
    summer_valley = valleys[1]     # Summer valley
    winter_valley_2 = valleys[2]   # Second winter valley

    threshold = calculate_threshold(frequencies, ARRIVAL_THRESHOLD_PEAK_RATIO, ARRIVAL_THRESHOLD_ABSOLUTE)

    # Spring passage: between first winter valley end and summer valley start
    spring_start = (winter_valley_1[1] + 1) % WEEKS_PER_YEAR
    spring_end = summer_valley[0]

    # Fall passage: between summer valley end and second winter valley start
    fall_start = (summer_valley[1] + 1) % WEEKS_PER_YEAR
    fall_end = winter_valley_2[0]

    # Calculate spring timing
    spring_timing = find_passage_timing(frequencies, spring_start, spring_end, threshold)

    # Calculate fall timing
    fall_timing = find_passage_timing(frequencies, fall_start, fall_end, threshold)

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'spring_arrival': week_to_date_range(spring_timing['arrival']) if spring_timing['arrival'] is not None else '',
        'spring_peak': week_to_date_range(spring_timing['peak']),
        'spring_departure': week_to_date_range(spring_timing['departure']) if spring_timing['departure'] is not None else '',
        'fall_arrival': week_to_date_range(fall_timing['arrival']) if fall_timing['arrival'] is not None else '',
        'fall_peak': week_to_date_range(fall_timing['peak']),
        'fall_departure': week_to_date_range(fall_timing['departure']) if fall_timing['departure'] is not None else ''
    }


def calculate_timing_single_season_summer(species_name, frequencies, category, pattern_type, valleys):
    """
    Single-season summer migrant (1 valley in winter).

    Display: Arrival/peak/departure
    Valley is in winter (weeks 44-48, 0-7), presence is in spring/summer/fall.

    Args:
        species_name: Name of the species
        frequencies: List of 48 weekly frequency values
        category: Migration category
        pattern_type: Pattern type classification
        valleys: List of (start, end) tuples for detected valleys

    Returns:
        Dictionary with arrival, peak, and departure timing
    """
    if len(valleys) != 1:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    valley_start, valley_end = valleys[0]
    threshold = calculate_threshold(frequencies)

    # Presence period: from valley_end+1 to valley_start
    # (this handles wraparound automatically via week_range)
    presence_start = (valley_end + 1) % WEEKS_PER_YEAR
    presence_end = valley_start

    presence_weeks = week_range(presence_start, presence_end)
    if not presence_weeks:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find arrival, peak, and departure
    arrival_week = find_arrival_week(frequencies, presence_start, presence_end, threshold)
    peak_week, _ = find_peak_week(frequencies, presence_start, presence_end)
    departure_week = find_last_week_above_threshold(frequencies, presence_start, presence_end, threshold)

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'arrival': week_to_date_range(arrival_week) if arrival_week is not None else '',
        'peak': week_to_date_range(peak_week),
        'departure': week_to_date_range(departure_week) if departure_week is not None else ''
    }


def calculate_timing_single_season_winter(species_name, frequencies, category, pattern_type, valleys):
    """
    Single-season winter migrant/resident (1 or 2 valleys in summer, overwinters).

    Display: Arrival/peak/departure (wraps around the year)

    For overwintering species:
    - Valley is in summer (weeks 18-32)
    - Or 2 close summer valleys (merged conceptually)
    - Presence wraps around: fall -> winter -> spring

    Args:
        species_name: Name of the species
        frequencies: List of 48 weekly frequency values
        category: Migration category
        pattern_type: Pattern type classification
        valleys: List of (start, end) tuples for detected valleys

    Returns:
        Dictionary with winter arrival, peak, and departure timing
    """
    if len(valleys) == 1:
        valley_start, valley_end = valleys[0]
    elif len(valleys) == 2:
        # Merge 2 close summer valleys
        valley_start = valleys[0][0]
        valley_end = valleys[1][1]
    else:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    threshold = calculate_threshold(frequencies)

    # Presence period wraps around: from valley_end+1 through winter to valley_start
    presence_start = (valley_end + 1) % WEEKS_PER_YEAR
    presence_end = valley_start

    # Find arrival, peak, and departure
    arrival_week = find_arrival_week(frequencies, presence_start, presence_end, threshold)
    peak_week, _ = find_peak_week(frequencies, presence_start, presence_end)
    departure_week = find_last_week_above_threshold(frequencies, presence_start, presence_end, threshold)

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'winter_arrival': week_to_date_range(arrival_week) if arrival_week is not None else '',
        'winter_peak': week_to_date_range(peak_week),
        'winter_departure': week_to_date_range(departure_week) if departure_week is not None else ''
    }


def calculate_migration_timing(species_name, frequencies, category, pattern_type, flags, valleys):
    """Calculate arrival/departure timing based on species pattern type using valley detection"""

    # Year-round residents
    if pattern_type == 'year-round':
        return calculate_timing_year_round(species_name, frequencies, category, pattern_type)

    # Irregular visitors (vagrants or irregular presence)
    if pattern_type == 'irregular':
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Two-passage migrants
    if pattern_type == 'two-passage':
        # Check if this is a three-valley migrant (winter-summer-winter pattern)
        if len(valleys) == 3:
            return calculate_timing_three_valley_migrant(species_name, frequencies, category, pattern_type, valleys)
        else:
            return calculate_timing_two_passage(species_name, frequencies, category, pattern_type, valleys)

    # Single-season summer migrants
    if pattern_type == 'summer':
        return calculate_timing_single_season_summer(species_name, frequencies, category, pattern_type, valleys)

    # Single-season winter migrants/residents
    if pattern_type == 'winter':
        return calculate_timing_single_season_winter(species_name, frequencies, category, pattern_type, valleys)

    # Default fallback
    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'status': 'unknown'
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
                'pattern_type': row['pattern_type'],
                'flags': row['edge_case_flags'],
                'peak_frequency': float(row['peak_frequency'])
            }

    # Load the frequency data
    json_file = intermediate_path / f"{region_name}_ebird_data.json"

    print(f"Loading frequency data from: {json_file}")

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Calculate timing for each species
    # Valley detection is now imported from utils.valley_detection
    results = []

    for species_data in data['species_data']:
        species_name = species_data['species']
        frequencies = species_data['frequencies']

        if species_name not in classifications:
            continue

        classification = classifications[species_name]

        # Detect valleys for this species
        valleys = detect_valleys(frequencies)

        timing = calculate_migration_timing(
            species_name,
            frequencies,
            classification['category'],
            classification['pattern_type'],
            classification['flags'],
            valleys
        )

        results.append(timing)

    # Save results
    output_file = intermediate_path / f"{region_name}_migration_timing.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        # Determine all possible fieldnames from all results
        all_fieldnames = set()
        for result in results:
            all_fieldnames.update(result.keys())

        # Order fieldnames logically
        ordered_fieldnames = ['species', 'category', 'pattern_type', 'status']
        ordered_fieldnames += ['arrival', 'peak', 'departure']
        ordered_fieldnames += ['spring_arrival', 'spring_peak', 'spring_departure']
        ordered_fieldnames += ['fall_arrival', 'fall_peak', 'fall_departure']
        ordered_fieldnames += ['winter_arrival', 'winter_peak', 'winter_departure']
        ordered_fieldnames += ['first_appears', 'last_appears']

        # Keep only fieldnames that actually exist
        fieldnames = [f for f in ordered_fieldnames if f in all_fieldnames]

        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')

        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Migration timing calculated!")
    print(f"Results saved to: {output_file}")

    # Print some examples
    print("\n=== Examples ===")

    for pattern_type in ['year-round', 'irregular', 'two-passage', 'summer', 'winter']:
        examples = [r for r in results if r.get('pattern_type') == pattern_type][:2]
        if examples:
            print(f"\n{pattern_type}:")
            for ex in examples:
                print(f"  {ex['species']}:")
                if ex.get('status') == 'year-round':
                    print(f"    Status: Year-round")
                elif ex.get('status') == 'irregular':
                    print(f"    {ex.get('first_appears', '')} → {ex.get('peak', '')} → {ex.get('last_appears', '')}")
                elif ex.get('spring_arrival'):
                    print(f"    Spring: {ex['spring_arrival']} → {ex['spring_peak']} → {ex['spring_departure']}")
                    print(f"    Fall: {ex['fall_arrival']} → {ex['fall_peak']} → {ex['fall_departure']}")
                elif ex.get('winter_arrival'):
                    print(f"    {ex['winter_arrival']} → {ex['winter_peak']} → {ex['winter_departure']}")
                elif ex.get('arrival'):
                    print(f"    {ex['arrival']} → {ex['peak']} → {ex['departure']}")


if __name__ == "__main__":
    main()
