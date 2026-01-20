#!/usr/bin/env python3
"""
Merge frequency data, classifications, and timing data into a single JSON file.
"""

import csv
import json
from pathlib import Path
import sys

# Add parent directory to path to import utils
sys.path.insert(0, str(Path(__file__).parent))
from utils.validation import (
    ValidationError,
    validate_species_data_structure,
    validate_file_exists,
    validate_region_name
)
from utils.species_codes import generate_species_code


def normalize_category(category):
    """Convert category to lowercase hyphenated format"""
    return category.lower().replace(' ', '-')


def parse_flags(flag_string):
    """Parse pipe-separated flags into a list"""
    if not flag_string:
        return []
    return [f.strip() for f in flag_string.split('|')]


def build_timing(pattern_type, timing_row, flags):
    """
    Build the timing object based on pattern type.

    Pattern types:
    - year-round: Just status
    - irregular: Simplified timing (first_appears, peak, last_appears)
    - two-passage: Spring + Fall timing
    - summer: Arrival/peak/departure
    - winter: Winter arrival/peak/departure (wraps around year)
    """

    # Year-round resident
    if pattern_type == 'year-round':
        return {"status": "year-round"}

    # Irregular presence (vagrant or 3+ peaks or 2 peaks <12 weeks)
    if pattern_type == 'irregular':
        timing = {}
        if timing_row.get('status') == 'irregular':
            timing['status'] = 'irregular'
        if timing_row.get('first_appears'):
            timing['first_appears'] = timing_row['first_appears']
        if timing_row.get('peak'):
            timing['peak'] = timing_row['peak']
        if timing_row.get('last_appears'):
            timing['last_appears'] = timing_row['last_appears']
        return timing

    # Two-passage migrant
    if pattern_type == 'two-passage':
        timing = {}

        # Spring timing
        if timing_row.get('spring_arrival'):
            timing['spring_arrival'] = timing_row['spring_arrival']
        if timing_row.get('spring_peak'):
            timing['spring_peak'] = timing_row['spring_peak']
        if timing_row.get('spring_departure'):
            timing['spring_departure'] = timing_row['spring_departure']

        # Fall timing
        if timing_row.get('fall_arrival'):
            timing['fall_arrival'] = timing_row['fall_arrival']
        if timing_row.get('fall_peak'):
            timing['fall_peak'] = timing_row['fall_peak']
        if timing_row.get('fall_departure'):
            timing['fall_departure'] = timing_row['fall_departure']

        return timing

    # Single-season summer migrant
    if pattern_type == 'summer':
        timing = {}
        if timing_row.get('arrival'):
            timing['arrival'] = timing_row['arrival']
        if timing_row.get('peak'):
            timing['peak'] = timing_row['peak']
        if timing_row.get('departure'):
            timing['departure'] = timing_row['departure']
        return timing

    # Single-season winter migrant/resident (overwintering)
    if pattern_type == 'winter':
        timing = {}
        if timing_row.get('winter_arrival'):
            timing['winter_arrival'] = timing_row['winter_arrival']
        if timing_row.get('winter_peak'):
            timing['winter_peak'] = timing_row['winter_peak']
        if timing_row.get('winter_departure'):
            timing['winter_departure'] = timing_row['winter_departure']
        return timing

    # Fallback
    return {}


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 merge_to_json.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    # Validate region name
    try:
        validate_region_name(region_name)
    except ValidationError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    intermediate_path = region_path / "intermediate"

    # Validate input files exist
    required_files = [
        (intermediate_path / f"{region_name}_ebird_data_wide.csv", "Frequency data CSV"),
        (intermediate_path / f"{region_name}_migration_pattern_classifications.csv", "Classification data CSV"),
        (intermediate_path / f"{region_name}_migration_timing.csv", "Timing data CSV")
    ]

    for file_path, description in required_files:
        try:
            validate_file_exists(file_path, description)
        except ValidationError as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Load all three CSV files
    print("Loading data files...")

    # 1. Load frequency data
    frequency_data = {}
    with open(intermediate_path / f"{region_name}_ebird_data_wide.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            species_name = row['Species']
            # Extract weekly frequencies (all columns except Species)
            frequencies = [float(row[col]) for col in reader.fieldnames if col != 'Species']
            frequency_data[species_name] = frequencies

    print(f"  Loaded {len(frequency_data)} species frequency data")

    # 2. Load classification data
    classification_data = {}
    with open(intermediate_path / f"{region_name}_migration_pattern_classifications.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            species_name = row['species']
            classification_data[species_name] = {
                'category': normalize_category(row['category']),
                'pattern_type': row['pattern_type'],
                'flags': parse_flags(row['edge_case_flags'])
            }

    print(f"  Loaded {len(classification_data)} species classifications")

    # 3. Load timing data
    timing_data = {}
    with open(intermediate_path / f"{region_name}_migration_timing.csv", 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            species_name = row['species']
            timing_data[species_name] = {
                'pattern_type': row['pattern_type'],
                'row': row
            }

    print(f"  Loaded {len(timing_data)} species timing data")

    # Merge all data
    print("\nMerging data...")
    species_list = []
    existing_codes = set()

    for species_name in sorted(frequency_data.keys()):
        # Skip if missing classification or timing data
        if species_name not in classification_data or species_name not in timing_data:
            print(f"  Warning: Skipping {species_name} (missing data)")
            continue

        classification = classification_data[species_name]
        timing_info = timing_data[species_name]

        # Generate unique code
        code = generate_species_code(species_name, existing_codes)
        existing_codes.add(code)

        species_obj = {
            'name': species_name,
            'code': code,
            'category': classification['category'],
            'flags': classification['flags'],
            'timing': build_timing(
                timing_info['pattern_type'],
                timing_info['row'],
                classification['flags']
            ),
            'weekly_frequency': frequency_data[species_name]
        }

        # Validate species data structure
        try:
            validate_species_data_structure(species_obj, len(species_list))
            species_list.append(species_obj)
        except ValidationError as e:
            print(f"  Warning: Skipping species due to validation error: {e}")

    print(f"  Merged {len(species_list)} species")

    # Save to JSON
    output_file = region_path / f"{region_name}_species_data.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(species_list, f, indent=2)

    print(f"\n✓ JSON file created: {output_file}")
    print(f"  Total species: {len(species_list)}")

    # Print summary by category
    category_counts = {}
    pattern_counts = {}
    for species in species_list:
        cat = species['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

        # Get pattern type from timing
        if 'status' in species['timing']:
            pattern = species['timing']['status']
        elif 'spring_arrival' in species['timing']:
            pattern = 'two-passage'
        elif 'winter_arrival' in species['timing']:
            pattern = 'winter'
        elif 'arrival' in species['timing']:
            pattern = 'summer'
        elif 'first_appears' in species['timing']:
            pattern = 'irregular'
        else:
            pattern = 'unknown'
        pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

    print("\n=== Species by Category ===")
    for category in sorted(category_counts.keys()):
        print(f"  {category}: {category_counts[category]}")

    print("\n=== Species by Pattern Type ===")
    for pattern in sorted(pattern_counts.keys()):
        print(f"  {pattern}: {pattern_counts[pattern]}")

    # Show a few examples
    print("\n=== Example Species ===")
    for category in ['resident', 'vagrant', 'two-passage-migrant', 'single-season', 'irregular']:
        examples = [s for s in species_list if s['category'] == category][:1]
        if examples:
            ex = examples[0]
            print(f"\n{category}:")
            print(f"  {ex['name']} ({ex['code']})")
            print(f"  Timing: {json.dumps(ex['timing'], indent=4)}")


if __name__ == "__main__":
    main()
