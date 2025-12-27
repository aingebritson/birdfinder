#!/usr/bin/env python3
"""
Classify bird species by valley detection (absence periods):
- Resident: 0 valleys (always present)
- Vagrant: < 10 weeks total presence
- Single-season summer: 1 valley in winter
- Single-season winter: 1 valley in summer (overwintering)
- Two-passage migrant: 2 valleys (summer + winter)
- Irregular: 3+ valleys or valleys that don't fit patterns
"""

import csv
import json
from pathlib import Path


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


def classify_valley_timing(valley_start, valley_end):
    """
    Classify when a valley primarily occurs.

    Returns: 'winter', 'summer', or 'mixed'

    Winter weeks: Expanded to 40-11 (Nov-Feb, wrapping around year)
    Summer weeks: Expanded to 16-35 (late April-early Sep)
    """
    # Expanded definitions to be more lenient
    # Winter: weeks 40-47 (Oct-Dec) + 0-11 (Jan-Mar)
    winter_weeks = set(range(40, 48)) | set(range(0, 12))
    # Summer: weeks 16-35 (late Apr-early Sep)
    summer_weeks = set(range(16, 36))

    valley_weeks = set(range(valley_start, valley_end + 1))

    winter_count = len(valley_weeks & winter_weeks)
    summer_count = len(valley_weeks & summer_weeks)
    total_valley_weeks = len(valley_weeks)

    # More lenient rule: 40% threshold instead of 50%
    if winter_count >= total_valley_weeks * 0.4:
        return 'winter'
    elif summer_count >= total_valley_weeks * 0.4:
        return 'summer'
    else:
        return 'mixed'


def detect_overwintering(frequencies):
    """
    Detect if a species is overwintering (present in winter but absent in summer).

    Criteria:
    - Frequency > 0.1% in both week 0 AND week 47
    - Has at least 8 consecutive weeks < 0.1% in middle of year

    Returns: True if overwintering, False otherwise
    """
    threshold = 0.001  # 0.1%

    # Check if present at both ends of the year
    if frequencies[0] <= threshold or frequencies[47] <= threshold:
        return False

    # Find longest consecutive stretch below threshold
    max_consecutive_low = 0
    current_consecutive = 0

    for freq in frequencies:
        if freq < threshold:
            current_consecutive += 1
            max_consecutive_low = max(max_consecutive_low, current_consecutive)
        else:
            current_consecutive = 0

    return max_consecutive_low >= 8


def calculate_metrics(species_data):
    """Calculate all classification metrics for a species"""

    frequencies = species_data['frequencies']
    species_name = species_data['species']

    # Basic frequency metrics
    peak_frequency = max(frequencies)
    min_frequency = min(frequencies)

    # Min/max ratio
    min_max_ratio = min_frequency / peak_frequency if peak_frequency > 0 else 0

    # Weeks with presence (frequency > 0)
    weeks_with_presence = sum(1 for f in frequencies if f > 0)

    # Detect valleys
    valleys = detect_valleys(frequencies)
    num_valleys = len(valleys)

    # Classify valley timing if applicable
    valley_types = []
    for valley_start, valley_end in valleys:
        valley_type = classify_valley_timing(valley_start, valley_end)
        valley_types.append(valley_type)

    # Check for overwintering
    is_overwintering = detect_overwintering(frequencies)

    return {
        'species': species_name,
        'frequencies': frequencies,
        'peak_frequency': peak_frequency,
        'min_frequency': min_frequency,
        'min_max_ratio': min_max_ratio,
        'weeks_with_presence': weeks_with_presence,
        'num_valleys': num_valleys,
        'valleys': valleys,
        'valley_types': valley_types,
        'is_overwintering': is_overwintering
    }


def classify_species(metrics):
    """
    Classify species based on valley detection.

    Classification order:
    1. Resident: 0 valleys
    2. Vagrant: < 10 weeks presence
    3. Two-passage: 2 valleys (one summer, one winter)
    4. Single-season summer: 1 valley in winter
    5. Single-season winter: 1 valley in summer (overwintering)
    6. Irregular: 3+ valleys or valleys that don't fit patterns

    Returns: (category, pattern_type, flags)
    """

    category = None
    pattern_type = None
    flags = []

    # 1. Resident: 0 valleys (never has 4+ consecutive weeks below 15% of peak)
    if metrics['num_valleys'] == 0:
        category = 'resident'
        pattern_type = 'year-round'

        # Flag if there's seasonal variation
        if metrics['min_max_ratio'] < 0.5:
            flags.append('seasonal_variation')

    # 2. Vagrant: Fewer than 10 weeks with any presence OR peak frequency below 0.5%
    elif metrics['weeks_with_presence'] < 10 or metrics['peak_frequency'] < 0.005:
        category = 'vagrant'
        pattern_type = 'irregular'
        if metrics['peak_frequency'] < 0.005:
            flags.append('low_peak_frequency')

    # 3. Two-passage migrant: 2 valleys (one summer, one winter)
    elif metrics['num_valleys'] == 2:
        valley_types = metrics['valley_types']
        valleys = metrics['valleys']

        # Check if we have one summer and one winter valley
        if 'summer' in valley_types and 'winter' in valley_types:
            category = 'two-passage-migrant'
            pattern_type = 'two-passage'
            flags.append('classic_bimodal')
        # Also accept if valleys are well-separated (>= 12 weeks apart) even if one is "mixed"
        elif len(valleys) == 2:
            valley1_start, valley1_end = valleys[0]
            valley2_start, valley2_end = valleys[1]

            # Calculate separation between valleys
            if valley2_start > valley1_end:
                separation = valley2_start - valley1_end
            else:
                # Valleys wrap around year
                separation = (48 - valley1_end) + valley2_start

            # If valleys are well separated (>= 12 weeks), treat as two-passage
            if separation >= 12:
                # Determine which is winter and which is summer based on midpoint
                valley1_mid = (valley1_start + valley1_end) // 2
                valley2_mid = (valley2_start + valley2_end) // 2

                # If one valley midpoint is in roughly winter (weeks 40-47, 0-11) and other in summer (16-35)
                winter_weeks = set(range(40, 48)) | set(range(0, 12))
                summer_weeks = set(range(16, 36))

                valley1_is_winter = valley1_mid in winter_weeks
                valley2_is_winter = valley2_mid in winter_weeks
                valley1_is_summer = valley1_mid in summer_weeks
                valley2_is_summer = valley2_mid in summer_weeks

                if (valley1_is_winter and valley2_is_summer) or (valley1_is_summer and valley2_is_winter):
                    category = 'two-passage-migrant'
                    pattern_type = 'two-passage'
                    flags.append('separated_valleys')
                else:
                    category = 'vagrant'
                    pattern_type = 'irregular'
                    flags.append('two_valleys_same_season')
            else:
                # Valleys too close together
                # Special case: if both valleys are in summer, this is likely an overwintering species
                # with a brief dip in mid-summer - treat as single-season winter
                if valley_types == ['summer', 'summer']:
                    # Merge the two summer valleys into one conceptual valley
                    # and treat as winter resident
                    category = 'single-season'
                    pattern_type = 'winter'
                    flags.append('overwintering|two_summer_valleys_merged')
                else:
                    category = 'vagrant'
                    pattern_type = 'irregular'
                    flags.append('two_valleys_close')

    # 4. Single-season: 1 valley
    elif metrics['num_valleys'] == 1:
        valley_type = metrics['valley_types'][0]
        valley_start, valley_end = metrics['valleys'][0]

        # Valley in winter = summer migrant
        if valley_type == 'winter':
            category = 'single-season'
            pattern_type = 'summer'
        # Valley in summer = winter resident/migrant (overwintering)
        elif valley_type == 'summer':
            category = 'single-season'
            pattern_type = 'winter'
            flags.append('overwintering')
        # Valley is "mixed" - check which season it leans towards based on midpoint
        else:
            valley_mid = (valley_start + valley_end) // 2

            winter_weeks = set(range(40, 48)) | set(range(0, 12))
            summer_weeks = set(range(16, 36))

            if valley_mid in winter_weeks:
                # Valley leans winter, so it's a summer migrant
                category = 'single-season'
                pattern_type = 'summer'
                flags.append('mixed_valley_winter_lean')
            elif valley_mid in summer_weeks:
                # Valley leans summer, so it's a winter resident
                category = 'single-season'
                pattern_type = 'winter'
                flags.append('overwintering|mixed_valley_summer_lean')
            else:
                # Valley truly in the middle (spring/fall)
                category = 'vagrant'
                pattern_type = 'irregular'
                flags.append('one_valley_mixed_season')

    # 5. Special case: 3 valleys in pattern winter-summer-winter = two-passage migrant
    # This happens when species are only present during brief migration windows
    elif metrics['num_valleys'] == 3:
        valley_types = metrics['valley_types']

        # Check for winter-summer-winter pattern (or summer-winter-summer)
        if (valley_types == ['winter', 'summer', 'winter'] or
            valley_types == ['summer', 'winter', 'summer']):
            category = 'two-passage-migrant'
            pattern_type = 'two-passage'
            flags.append('three_valley_migrant')
        else:
            category = 'vagrant'
            pattern_type = 'irregular'
            flags.append('three_valleys_irregular')

    # 6. Vagrant/Irregular: 4+ valleys or other edge cases
    else:
        category = 'vagrant'
        pattern_type = 'irregular'

        if metrics['num_valleys'] >= 4:
            flags.append('many_valleys')

    # Additional edge case flags

    # Flag species with few weeks of presence (just above vagrant threshold)
    if 10 <= metrics['weeks_with_presence'] < 15:
        flags.append('low_presence')

    # Flag residents near the threshold
    if category == 'resident' and metrics['min_max_ratio'] < 0.20:
        flags.append('min_max_near_boundary')

    return category, pattern_type, flags


def main():
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 classify_migration_patterns.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    intermediate_path = region_path / "intermediate"

    # Load the JSON data
    json_file = intermediate_path / f"{region_name}_ebird_data.json"

    print(f"Loading data from: {json_file}")
    with open(json_file, 'r') as f:
        data = json.load(f)

    sample_sizes = data['sample_sizes']
    species_data = data['species_data']

    print(f"Processing {len(species_data)} species...")

    # Load old classifications if they exist
    old_classifications = {}
    old_file = intermediate_path / f"{region_name}_migration_pattern_classifications.csv"
    if old_file.exists():
        with open(old_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                old_classifications[row['species']] = row['category']

    # Calculate metrics and classify each species
    results = []
    changes = []

    for species in species_data:
        metrics = calculate_metrics(species)
        category, pattern_type, flags = classify_species(metrics)

        # Track changes
        old_category = old_classifications.get(metrics['species'])
        if old_category and old_category != category:
            changes.append({
                'species': metrics['species'],
                'old': old_category,
                'new': category,
                'pattern_type': pattern_type,
                'flags': '|'.join(flags) if flags else ''
            })

        results.append({
            'species': metrics['species'],
            'category': category,
            'pattern_type': pattern_type,
            'peak_frequency': round(metrics['peak_frequency'], 6),
            'min_frequency': round(metrics['min_frequency'], 6),
            'min_max_ratio': round(metrics['min_max_ratio'], 4),
            'weeks_with_presence': metrics['weeks_with_presence'],
            'num_valleys': metrics['num_valleys'],
            'valley_types': '|'.join(metrics['valley_types']) if metrics['valley_types'] else '',
            'is_overwintering': 'Yes' if metrics['is_overwintering'] else 'No',
            'edge_case_flags': '|'.join(flags) if flags else ''
        })

    # Save to CSV
    output_file = intermediate_path / f"{region_name}_migration_pattern_classifications.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'species', 'category', 'pattern_type', 'peak_frequency', 'min_frequency',
            'min_max_ratio', 'weeks_with_presence', 'num_valleys', 'valley_types',
            'is_overwintering', 'edge_case_flags'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Classification complete!")
    print(f"Results saved to: {output_file}")

    # Print summary statistics
    category_counts = {}
    pattern_counts = {}
    edge_case_count = 0

    for result in results:
        cat = result['category']
        pat = result['pattern_type']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        pattern_counts[pat] = pattern_counts.get(pat, 0) + 1
        if result['edge_case_flags']:
            edge_case_count += 1

    print("\n=== Summary ===")
    print("By category:")
    for category in ['resident', 'vagrant', 'two-passage-migrant', 'single-season', 'irregular']:
        count = category_counts.get(category, 0)
        print(f"  {category}: {count}")

    print("\nBy pattern type:")
    for pattern in ['year-round', 'irregular', 'two-passage', 'summer', 'winter']:
        count = pattern_counts.get(pattern, 0)
        print(f"  {pattern}: {count}")

    print(f"\nEdge cases flagged: {edge_case_count}")

    # Show changes from previous classification
    if changes:
        print(f"\n=== Species that changed categories ({len(changes)}) ===")
        for change in changes[:20]:  # Show first 20
            print(f"{change['species']}: {change['old']} → {change['new']} ({change['pattern_type']})")
            if change['flags']:
                print(f"  Flags: {change['flags']}")
        if len(changes) > 20:
            print(f"  ... and {len(changes) - 20} more")

    # Show examples from each category
    print("\n=== Examples from each category ===")

    for category in ['resident', 'vagrant', 'two-passage-migrant', 'single-season', 'irregular']:
        examples = [r for r in results if r['category'] == category][:3]
        if not examples:
            continue

        print(f"\n{category}:")
        for ex in examples:
            flags = f" [{ex['edge_case_flags']}]" if ex['edge_case_flags'] else ""
            print(f"  - {ex['species']} ({ex['pattern_type']}){flags}")
            print(f"    min/max: {ex['min_max_ratio']}, weeks_present: {ex['weeks_with_presence']}, " +
                  f"valleys: {ex['num_valleys']} ({ex['valley_types']}), overwinter: {ex['is_overwintering']}")


if __name__ == "__main__":
    main()
