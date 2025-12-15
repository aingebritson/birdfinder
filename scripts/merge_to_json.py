#!/usr/bin/env python3
"""
Merge frequency data, classifications, and timing data into a single JSON file.
"""

import csv
import json
import re
from pathlib import Path


def generate_species_code(species_name):
    """
    Generate a 6-letter eBird-style species code.
    Takes first 3 letters of first word + first 3 letters of last word.
    """
    # Remove parentheses and their contents
    clean_name = re.sub(r'\([^)]*\)', '', species_name).strip()

    # Split into words
    words = clean_name.split()

    if len(words) == 1:
        # Single word: take first 6 letters
        code = words[0][:6].lower()
    elif len(words) == 2:
        # Two words: 3 letters from each
        code = (words[0][:3] + words[1][:3]).lower()
    else:
        # Multiple words: first 3 of first word + first 3 of last word
        code = (words[0][:3] + words[-1][:3]).lower()

    return code


def normalize_category(category):
    """Convert category to lowercase hyphenated format"""
    return category.lower().replace(' ', '-')


def parse_flags(flag_string):
    """Parse pipe-separated flags into a list"""
    if not flag_string:
        return []
    return [f.strip() for f in flag_string.split('|')]


def build_timing(pattern, timing_row, flags):
    """Build the timing object based on pattern type"""

    # Resident: year-round
    if pattern == 'Year-round':
        return {"status": "year-round"}

    # Vagrant: irregular
    if pattern == 'Irregular':
        return {"status": "irregular"}

    # Single-season
    if pattern in ['Single passage', 'Winter resident']:
        is_winter = 'winter_resident' in flags
        prefix = 'winter_' if is_winter else ''

        timing = {}
        if timing_row['spring_arrival_short']:
            timing[f'{prefix}arrival'] = timing_row['spring_arrival_short']
        if timing_row['spring_peak_short']:
            timing[f'{prefix}peak'] = timing_row['spring_peak_short']
        if timing_row['spring_departure_short']:
            timing[f'{prefix}departure'] = timing_row['spring_departure_short']

        return timing

    # Two passages
    if pattern == 'Two passages':
        timing = {}

        # Spring timing
        if timing_row['spring_arrival_short']:
            timing['spring_arrival'] = timing_row['spring_arrival_short']
        if timing_row['spring_peak_short']:
            timing['spring_peak'] = timing_row['spring_peak_short']
        if timing_row['spring_departure_short']:
            timing['spring_departure'] = timing_row['spring_departure_short']

        # Fall timing
        if timing_row['fall_arrival_short']:
            timing['fall_arrival'] = timing_row['fall_arrival_short']
        if timing_row['fall_peak_short']:
            timing['fall_peak'] = timing_row['fall_peak_short']
        if timing_row['fall_departure_short']:
            timing['fall_departure'] = timing_row['fall_departure_short']

        return timing

    return {}


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 merge_to_json.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    intermediate_path = region_path / "intermediate"

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
                'pattern': row['pattern'],
                'row': row
            }

    print(f"  Loaded {len(timing_data)} species timing data")

    # Merge all data
    print("\nMerging data...")
    species_list = []

    for species_name in sorted(frequency_data.keys()):
        # Skip if missing classification or timing data
        if species_name not in classification_data or species_name not in timing_data:
            print(f"  Warning: Skipping {species_name} (missing data)")
            continue

        classification = classification_data[species_name]
        timing_info = timing_data[species_name]

        species_obj = {
            'name': species_name,
            'code': generate_species_code(species_name),
            'category': classification['category'],
            'flags': classification['flags'],
            'timing': build_timing(
                timing_info['pattern'],
                timing_info['row'],
                classification['flags']
            ),
            'weekly_frequency': frequency_data[species_name]
        }

        species_list.append(species_obj)

    print(f"  Merged {len(species_list)} species")

    # Save to JSON
    output_file = region_path / f"{region_name}_species_data.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(species_list, f, indent=2)

    print(f"\n✓ JSON file created: {output_file}")
    print(f"  Total species: {len(species_list)}")

    # Print summary by category
    category_counts = {}
    for species in species_list:
        cat = species['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1

    print("\n=== Species by Category ===")
    for category in sorted(category_counts.keys()):
        print(f"  {category}: {category_counts[category]}")

    # Show a few examples
    print("\n=== Example Species ===")
    for category in ['resident', 'single-season', 'two-passage-migrant', 'vagrant']:
        examples = [s for s in species_list if s['category'] == category][:1]
        if examples:
            ex = examples[0]
            print(f"\n{category}:")
            print(f"  {ex['name']} ({ex['code']})")
            print(f"  Timing: {json.dumps(ex['timing'], indent=4)}")


if __name__ == "__main__":
    main()
