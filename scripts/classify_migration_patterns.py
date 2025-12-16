#!/usr/bin/env python3
"""
Classify bird species by arrival/departure patterns:
- Vagrant: < 10 weeks presence
- Resident: min/max ratio >= 0.15
- Two-passage migrant: Bimodal with valley < 0.15 of peak (excluding winter residents)
- Single-season: One arrival, one departure
"""

import csv
import json
from pathlib import Path


def detect_bimodal_pattern(frequencies, min_peak_ratio=0.25, min_secondary_absolute=0.02):
    """
    Detect if species has bimodal pattern (two distinct peaks).
    Returns: (is_bimodal, valley_ratio, peak_indices)

    Primary peaks must be at least min_peak_ratio of the species' overall max.
    Secondary peaks can be lower (min_secondary_absolute absolute threshold) to catch
    asymmetric migration patterns like Palm Warbler.

    Valley ratio is the minimum frequency between the two highest peaks,
    expressed as a ratio to the overall peak.
    """
    if not frequencies or len(frequencies) < 5:
        return False, 0.0, []

    max_freq = max(frequencies)
    if max_freq == 0:
        return False, 0.0, []

    threshold = max_freq * min_peak_ratio
    peaks = []

    # Find all peaks meeting the primary threshold
    for i in range(2, len(frequencies) - 2):
        current = frequencies[i]

        # Must be above threshold
        if current < threshold:
            continue

        # Check if it's a local maximum (higher than 2 weeks on each side)
        left_2 = frequencies[i-2:i]
        right_2 = frequencies[i+1:i+3]

        if all(current > v for v in left_2) and all(current > v for v in right_2):
            peaks.append((i, current))

    # If we have < 2 primary peaks, look for secondary peaks with lower threshold
    if len(peaks) < 2:
        for i in range(2, len(frequencies) - 2):
            current = frequencies[i]

            # Must be above absolute threshold and not already in peaks
            if current < min_secondary_absolute or any(p[0] == i for p in peaks):
                continue

            # Check if it's a local maximum
            left_2 = frequencies[i-2:i]
            right_2 = frequencies[i+1:i+3]

            if all(current > v for v in left_2) and all(current > v for v in right_2):
                peaks.append((i, current))

    # Need at least 2 peaks for bimodal
    if len(peaks) < 2:
        return False, 0.0, [p[0] for p in peaks]

    # Sort peaks by height and get the two highest
    peaks_sorted = sorted(peaks, key=lambda x: x[1], reverse=True)
    peak1_idx, peak1_val = peaks_sorted[0]
    peak2_idx, peak2_val = peaks_sorted[1]

    # Get the valley between the two highest peaks
    start_idx = min(peak1_idx, peak2_idx)
    end_idx = max(peak1_idx, peak2_idx)

    valley_min = min(frequencies[start_idx:end_idx+1])
    valley_ratio = valley_min / max_freq if max_freq > 0 else 0.0

    return True, valley_ratio, [p[0] for p in peaks]


def is_winter_resident(frequencies, peak_frequency):
    """
    Check if a bimodal species is actually a winter resident.

    Winter residents have:
    1. Minimum frequency occurs in summer (weeks 21-31, roughly Jun-Aug, 0-indexed)
    2. Average winter frequency (Dec-Feb, weeks 47-51 and 0-7) > 0.15 of peak
    """
    if peak_frequency == 0:
        return False

    # Summer weeks (Jun-Aug): weeks 21-31 (0-indexed)
    summer_weeks = frequencies[21:32]
    min_freq_overall = min(frequencies)

    # Check if minimum occurs in summer
    if min_freq_overall not in summer_weeks:
        return False

    # Winter weeks (Dec-Feb): weeks 47-51 (Dec) and 0-7 (Jan-Feb), 0-indexed
    winter_weeks = frequencies[47:52] + frequencies[0:8]
    avg_winter_freq = sum(winter_weeks) / len(winter_weeks) if winter_weeks else 0

    # Check if winter average > 0.15 of peak
    winter_ratio = avg_winter_freq / peak_frequency if peak_frequency > 0 else 0

    return winter_ratio > 0.15


def calculate_metrics(species_data, sample_sizes):
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

    # Check for bimodal pattern
    is_bimodal, valley_ratio, peak_indices = detect_bimodal_pattern(frequencies, min_peak_ratio=0.25, min_secondary_absolute=0.02)
    num_peaks = len(peak_indices)

    # Check if winter resident
    is_winter_res = False
    if is_bimodal:
        is_winter_res = is_winter_resident(frequencies, peak_frequency)

    return {
        'species': species_name,
        'frequencies': frequencies,  # Keep for winter resident check
        'peak_frequency': peak_frequency,
        'min_frequency': min_frequency,
        'min_max_ratio': min_max_ratio,
        'weeks_with_presence': weeks_with_presence,
        'is_bimodal': is_bimodal,
        'valley_ratio': valley_ratio,
        'num_peaks': num_peaks,
        'is_winter_resident': is_winter_res
    }


def classify_species(metrics):
    """
    Classify species based on arrival/departure patterns.
    Returns: (category, edge_case_flags)
    """

    category = None
    flags = []

    # Apply classification logic in order

    # 1. Vagrant: Weeks with presence < 10
    if metrics['weeks_with_presence'] < 10:
        category = 'Vagrant'

    # 2. Resident: Min/max ratio >= 0.15 OR present all 48 weeks with min/max >= 0.08
    elif metrics['min_max_ratio'] >= 0.15:
        category = 'Resident'

        # Flag edge cases near boundary
        if 0.10 <= metrics['min_max_ratio'] < 0.20:
            flags.append('min_max_near_boundary')

    # 2b. Year-round with seasonal variation: Present all 48 weeks but min/max < 0.15
    elif metrics['weeks_with_presence'] == 48 and metrics['min_max_ratio'] >= 0.08:
        category = 'Resident'
        flags.append('seasonal_variation')

    # 3. Two-passage migrant: Bimodal AND valley < 0.15 AND NOT winter resident
    elif metrics['is_bimodal'] and metrics['valley_ratio'] < 0.15:
        # Check for winter resident before classifying as two-passage
        if metrics['is_winter_resident']:
            category = 'Single-season'
            flags.append('winter_resident')
        else:
            category = 'Two-passage migrant'

            # Flag edge cases near valley threshold
            if 0.10 <= metrics['valley_ratio'] < 0.20:
                flags.append('valley_near_boundary')

    # 4. Single-season: Everything else
    else:
        category = 'Single-season'

        # Flag if bimodal but valley is too high
        if metrics['is_bimodal']:
            flags.append('bimodal_high_valley')

    # Additional edge case flags

    # Flag species with few weeks of presence (just above vagrant threshold)
    if 10 <= metrics['weeks_with_presence'] < 15:
        flags.append('low_presence')

    # Flag if exactly 2 peaks detected (classic migration pattern)
    if metrics['num_peaks'] == 2 and category == 'Two-passage migrant':
        flags.append('classic_bimodal')

    # Flag if many peaks detected (noisy data)
    if metrics['num_peaks'] > 3:
        flags.append('many_peaks')

    # Flag residents with bimodal pattern (seasonal variation)
    if category == 'Resident' and metrics['is_bimodal']:
        flags.append('resident_bimodal')

    return category, flags


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
        metrics = calculate_metrics(species, sample_sizes)
        category, flags = classify_species(metrics)

        # Track changes
        old_category = old_classifications.get(metrics['species'])
        if old_category and old_category != category:
            changes.append({
                'species': metrics['species'],
                'old': old_category,
                'new': category,
                'flags': '|'.join(flags) if flags else ''
            })

        results.append({
            'species': metrics['species'],
            'category': category,
            'peak_frequency': round(metrics['peak_frequency'], 6),
            'min_frequency': round(metrics['min_frequency'], 6),
            'min_max_ratio': round(metrics['min_max_ratio'], 4),
            'weeks_with_presence': metrics['weeks_with_presence'],
            'is_bimodal': 'Yes' if metrics['is_bimodal'] else 'No',
            'valley_ratio': round(metrics['valley_ratio'], 4) if metrics['is_bimodal'] else '',
            'num_peaks': metrics['num_peaks'],
            'edge_case_flags': '|'.join(flags) if flags else ''
        })

    # Save to CSV
    output_file = intermediate_path / f"{region_name}_migration_pattern_classifications.csv"

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = [
            'species', 'category', 'peak_frequency', 'min_frequency',
            'min_max_ratio', 'weeks_with_presence', 'is_bimodal',
            'valley_ratio', 'num_peaks', 'edge_case_flags'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(results)

    print(f"\n✓ Classification complete!")
    print(f"Results saved to: {output_file}")

    # Print summary statistics
    category_counts = {}
    edge_case_count = 0

    for result in results:
        cat = result['category']
        category_counts[cat] = category_counts.get(cat, 0) + 1
        if result['edge_case_flags']:
            edge_case_count += 1

    print("\n=== Summary ===")
    for category in ['Resident', 'Single-season', 'Two-passage migrant', 'Vagrant']:
        count = category_counts.get(category, 0)
        print(f"{category}: {count}")

    print(f"\nEdge cases flagged: {edge_case_count}")

    # Show changes from previous classification
    if changes:
        print(f"\n=== Species that changed categories ({len(changes)}) ===")
        for change in changes:
            print(f"{change['species']}: {change['old']} → {change['new']}")
            if change['flags']:
                print(f"  Flags: {change['flags']}")

    # Show examples from each category
    print("\n=== Examples from each category ===")
    for category in ['Resident', 'Single-season', 'Two-passage migrant', 'Vagrant']:
        examples = [r for r in results if r['category'] == category][:3]
        print(f"\n{category}:")
        for ex in examples:
            flags = f" [{ex['edge_case_flags']}]" if ex['edge_case_flags'] else ""
            print(f"  - {ex['species']}{flags}")
            valley_str = f", valley: {ex['valley_ratio']}" if ex['valley_ratio'] != '' else ""
            print(f"    min/max: {ex['min_max_ratio']}, weeks_present: {ex['weeks_with_presence']}, " +
                  f"bimodal: {ex['is_bimodal']}{valley_str}, peaks: {ex['num_peaks']}")


if __name__ == "__main__":
    main()
