#!/usr/bin/env python3
"""
Calculate arrival and departure weeks for bird species based on migration patterns.
Handles different pattern types: year-round, irregular, two-passage, summer, winter.
"""

import csv
import json
from pathlib import Path


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
    Two-passage migrant (2 valleys: one summer, one winter)
    Display: Spring arrival/peak/departure + Fall arrival/peak/departure
    """
    if len(valleys) != 2:
        # Fallback to irregular if we don't have exactly 2 valleys
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Determine which valley is summer and which is winter
    valley1_start, valley1_end = valleys[0]
    valley2_start, valley2_end = valleys[1]

    winter_weeks = set(range(44, 48)) | set(range(0, 8))
    summer_weeks = set(range(18, 33))

    valley1_weeks = set(range(valley1_start, valley1_end + 1))
    valley2_weeks = set(range(valley2_start, valley2_end + 1))

    valley1_winter_count = len(valley1_weeks & winter_weeks)
    valley2_winter_count = len(valley2_weeks & winter_weeks)

    # Identify summer and winter valleys
    if valley1_winter_count > len(valley1_weeks) / 2:
        winter_valley = valleys[0]
        summer_valley = valleys[1]
    else:
        summer_valley = valleys[0]
        winter_valley = valleys[1]

    peak_freq = max(frequencies)
    threshold = max(peak_freq * 0.25, 0.001)

    # Spring passage: after winter valley ends, before summer valley begins
    winter_valley_end = winter_valley[1]
    summer_valley_start = summer_valley[0]

    spring_start_search = winter_valley_end + 1
    spring_end_search = summer_valley_start

    # Validate search range
    if spring_start_search >= spring_end_search or spring_start_search >= 48:
        # Invalid range, fallback to irregular
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find spring arrival
    spring_arrival_week = None
    for week in range(spring_start_search, min(spring_end_search, 48)):
        if frequencies[week] >= threshold:
            spring_arrival_week = week
            break

    # Find spring peak
    spring_peak_week = spring_start_search
    spring_peak_freq = 0
    for week in range(spring_start_search, min(spring_end_search, 48)):
        if frequencies[week] > spring_peak_freq:
            spring_peak_freq = frequencies[week]
            spring_peak_week = week

    # Find spring departure
    spring_departure_week = None
    for week in range(spring_peak_week, min(summer_valley_start, 48)):
        if frequencies[week] < threshold:
            spring_departure_week = week - 1
            break
    if spring_departure_week is None:
        spring_departure_week = min(summer_valley_start, 48) - 1

    # Fall passage: after summer valley ends, before winter valley begins
    summer_valley_end = summer_valley[1]
    winter_valley_start = winter_valley[0]

    fall_start_search = summer_valley_end + 1
    fall_end_search = winter_valley_start if winter_valley_start > summer_valley_end else 48

    # Validate search range
    if fall_start_search >= fall_end_search or fall_start_search >= 48:
        # Invalid range, fallback to irregular
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find fall arrival
    fall_arrival_week = None
    for week in range(fall_start_search, min(fall_end_search, 48)):
        if frequencies[week] >= threshold:
            fall_arrival_week = week
            break

    # Find fall peak
    fall_peak_week = fall_start_search
    fall_peak_freq = 0
    for week in range(fall_start_search, min(fall_end_search, 48)):
        if frequencies[week] > fall_peak_freq:
            fall_peak_freq = frequencies[week]
            fall_peak_week = week

    # Find fall departure
    fall_departure_week = None
    for week in range(fall_peak_week, min(fall_end_search, 48)):
        if frequencies[week] < threshold:
            fall_departure_week = week - 1
            break
    if fall_departure_week is None:
        fall_departure_week = min(fall_end_search, 48) - 1

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'spring_arrival': week_to_date_range(spring_arrival_week) if spring_arrival_week is not None else '',
        'spring_peak': week_to_date_range(spring_peak_week),
        'spring_departure': week_to_date_range(spring_departure_week) if spring_departure_week is not None else '',
        'fall_arrival': week_to_date_range(fall_arrival_week) if fall_arrival_week is not None else '',
        'fall_peak': week_to_date_range(fall_peak_week),
        'fall_departure': week_to_date_range(fall_departure_week) if fall_departure_week is not None else ''
    }


def calculate_timing_three_valley_migrant(species_name, frequencies, category, pattern_type, valleys):
    """
    Three-valley migrant (winter-summer-winter pattern)
    Common for species that pass through briefly in spring and fall
    Valleys: [winter, summer, winter]
    Presence: Spring passage (between valley 0 and 1) + Fall passage (between valley 1 and 2)
    """
    if len(valleys) != 3:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    winter_valley_1 = valleys[0]  # First winter valley
    summer_valley = valleys[1]     # Summer valley
    winter_valley_2 = valleys[2]   # Second winter valley (wraps to beginning)

    peak_freq = max(frequencies)
    threshold = max(peak_freq * 0.25, 0.001)

    # Spring passage: between first winter valley end and summer valley start
    spring_start_search = winter_valley_1[1] + 1
    spring_end_search = summer_valley[0]

    # Validate spring range
    if spring_start_search >= spring_end_search or spring_start_search >= 48:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find spring timing
    spring_arrival_week = None
    for week in range(spring_start_search, min(spring_end_search, 48)):
        if frequencies[week] >= threshold:
            spring_arrival_week = week
            break

    spring_peak_week = spring_start_search
    spring_peak_freq = 0
    for week in range(spring_start_search, min(spring_end_search, 48)):
        if frequencies[week] > spring_peak_freq:
            spring_peak_freq = frequencies[week]
            spring_peak_week = week

    spring_departure_week = None
    for week in range(spring_peak_week, min(summer_valley[0], 48)):
        if frequencies[week] < threshold:
            spring_departure_week = week - 1
            break
    if spring_departure_week is None:
        spring_departure_week = min(summer_valley[0], 48) - 1

    # Fall passage: between summer valley end and second winter valley start
    fall_start_search = summer_valley[1] + 1
    fall_end_search = winter_valley_2[0] if winter_valley_2[0] > summer_valley[1] else 48

    # Validate fall range
    if fall_start_search >= fall_end_search:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find fall timing
    fall_arrival_week = None
    for week in range(fall_start_search, min(fall_end_search, 48)):
        if frequencies[week] >= threshold:
            fall_arrival_week = week
            break

    fall_peak_week = fall_start_search
    fall_peak_freq = 0
    for week in range(fall_start_search, min(fall_end_search, 48)):
        if frequencies[week] > fall_peak_freq:
            fall_peak_freq = frequencies[week]
            fall_peak_week = week

    fall_departure_week = None
    for week in range(fall_peak_week, min(fall_end_search, 48)):
        if frequencies[week] < threshold:
            fall_departure_week = week - 1
            break
    if fall_departure_week is None:
        fall_departure_week = min(fall_end_search, 48) - 1

    return {
        'species': species_name,
        'category': category,
        'pattern_type': pattern_type,
        'spring_arrival': week_to_date_range(spring_arrival_week) if spring_arrival_week is not None else '',
        'spring_peak': week_to_date_range(spring_peak_week),
        'spring_departure': week_to_date_range(spring_departure_week) if spring_departure_week is not None else '',
        'fall_arrival': week_to_date_range(fall_arrival_week) if fall_arrival_week is not None else '',
        'fall_peak': week_to_date_range(fall_peak_week),
        'fall_departure': week_to_date_range(fall_departure_week) if fall_departure_week is not None else ''
    }


def calculate_timing_single_season_summer(species_name, frequencies, category, pattern_type, valleys):
    """
    Single-season summer migrant (1 valley in winter)
    Display: Arrival/peak/departure

    Valley is in winter (weeks 44-48, 0-7), presence is in spring/summer/fall
    """
    if len(valleys) != 1:
        # Fallback to irregular
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    valley_start, valley_end = valleys[0]

    peak_freq = max(frequencies)
    threshold = max(peak_freq * 0.25, 0.001)

    # Presence period: after winter valley ends (spring) until it begins again (fall)
    # Winter valley typically wraps around year (e.g., week 44-7)
    # Presence is from valley_end+1 through valley_start-1

    # Build list of weeks in presence period
    if valley_end < valley_start:
        # Valley wraps around year end (e.g., weeks 44-7)
        # Presence is from valley_end+1 to valley_start-1
        presence_weeks = list(range(valley_end + 1, valley_start))
    else:
        # Valley doesn't wrap (unusual for winter valley but handle it)
        presence_weeks = list(range(valley_end + 1, 48)) + list(range(0, valley_start))

    if not presence_weeks:
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    # Find arrival: first week in presence period exceeding threshold
    arrival_week = None
    for week in presence_weeks:
        if frequencies[week] >= threshold:
            arrival_week = week
            break

    # Find peak: highest frequency week in presence period
    peak_week = presence_weeks[0]
    max_freq = 0
    for week in presence_weeks:
        if frequencies[week] > max_freq:
            max_freq = frequencies[week]
            peak_week = week

    # Find departure: last week in presence period exceeding threshold
    departure_week = None
    for week in reversed(presence_weeks):
        if frequencies[week] >= threshold:
            departure_week = week
            break

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
    Single-season winter migrant/resident (1 or 2 valleys in summer, overwinters)
    Display: Arrival/peak/departure (wraps around the year)

    For overwintering species:
    - Valley is in summer (weeks 18-32)
    - Or 2 close summer valleys (merged conceptually)
    - Presence wraps around: fall → winter → spring
    """
    if len(valleys) == 1:
        # Normal case: 1 valley in summer
        valley_start, valley_end = valleys[0]
    elif len(valleys) == 2:
        # Special case: 2 summer valleys merged (e.g., Hooded Merganser, American Herring Gull)
        # Treat the span from first valley start to second valley end as the absence period
        valley_start = valleys[0][0]
        valley_end = valleys[1][1]
    else:
        # Fallback to irregular if not 1 or 2 valleys
        return calculate_timing_irregular(species_name, frequencies, category, pattern_type)

    peak_freq = max(frequencies)
    threshold = max(peak_freq * 0.25, 0.001)

    # Presence period wraps around the year: after summer valley ends (fall) → winter → before valley begins (spring)
    # Search from valley_end+1 to end of year, then from 0 to valley_start-1

    # Find arrival: first week in fall after valley ends where frequency > threshold
    arrival_week = None
    for week in range(valley_end + 1, 48):
        if frequencies[week] >= threshold:
            arrival_week = week
            break
    # If not found in fall, check early winter
    if arrival_week is None:
        for week in range(0, min(5, valley_start)):
            if frequencies[week] >= threshold:
                arrival_week = week
                break

    # Find peak: highest frequency week in presence period (fall → winter → spring)
    peak_week = 0
    max_freq = 0
    # Check fall/winter (valley_end+1 to 48)
    for week in range(valley_end + 1, 48):
        if frequencies[week] > max_freq:
            max_freq = frequencies[week]
            peak_week = week
    # Check winter/spring (0 to valley_start)
    for week in range(0, valley_start):
        if frequencies[week] > max_freq:
            max_freq = frequencies[week]
            peak_week = week

    # Find departure: last week in spring before valley begins where frequency > threshold
    departure_week = None
    for week in range(valley_start - 1, -1, -1):
        if frequencies[week] >= threshold:
            departure_week = week
            break

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

    # Valley detection function (must match classify script exactly)
    def detect_valleys(frequencies):
        """
        Detect valleys (absence periods) in frequency data.
        A valley is 4+ consecutive weeks below 15% of species' peak frequency,
        with a minimum threshold of 0.5% to ensure consistency with peak classification.
        Returns: list of (start_week, end_week) tuples for each valley
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

    # Calculate timing for each species
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
