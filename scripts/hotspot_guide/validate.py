#!/usr/bin/env python3
"""
Validation script for eBird Hotspot Guide output.

Checks data integrity and validates JSON output files.

Usage:
    python validate.py [output_dir]
"""

import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hotspot_guide.config import OUTPUT_DIR


def validate_occurrence_rates(species_dir: Path) -> bool:
    """Verify all occurrence rates are between 0 and 1."""
    errors = []

    for json_file in species_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        species_name = data['species']['common_name']

        for hotspot in data['hotspots']:
            rate = hotspot['occurrence']['rate']
            if not (0 <= rate <= 1):
                errors.append(
                    f"{species_name} at {hotspot['name']}: "
                    f"invalid rate {rate}"
                )

            # Detection count should not exceed total checklists
            detections = hotspot['occurrence']['detection_count']
            total = hotspot['occurrence']['total_checklists']
            if detections > total:
                errors.append(
                    f"{species_name} at {hotspot['name']}: "
                    f"detections ({detections}) > total ({total})"
                )

    if errors:
        print("FAIL: Invalid occurrence rates found:")
        for e in errors[:10]:  # Show first 10
            print(f"  - {e}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        return False

    print(f"PASS: All occurrence rates valid in {len(list(species_dir.glob('*.json')))} species files")
    return True


def validate_hotspot_coverage(index_dir: Path) -> bool:
    """Verify expected hotspot and species counts."""
    hotspot_index = index_dir / "hotspot_index.json"
    species_index = index_dir / "species_index.json"

    if not hotspot_index.exists():
        print("FAIL: hotspot_index.json not found")
        return False

    if not species_index.exists():
        print("FAIL: species_index.json not found")
        return False

    with open(hotspot_index, 'r', encoding='utf-8') as f:
        hotspots = json.load(f)

    with open(species_index, 'r', encoding='utf-8') as f:
        species = json.load(f)

    print(f"Hotspots processed: {hotspots['total_hotspots']}")
    print(f"Species processed: {species['total_species']}")

    # Check for reasonable counts
    if hotspots['total_hotspots'] < 100:
        print("WARNING: Fewer than 100 hotspots - check filters")

    if species['total_species'] < 200:
        print("WARNING: Fewer than 200 species - check filters")

    return True


def spot_check_common_species(species_dir: Path) -> bool:
    """Verify results for well-known common species."""
    # Species codes (6-letter) for common species
    common_species = [
        'amerob',  # American Robin
        'norcar',  # Northern Cardinal
        'blujay',  # Blue Jay
        'bkcchi',  # Black-capped Chickadee
    ]

    for species_file in common_species:
        filepath = species_dir / f"{species_file}.json"
        if not filepath.exists():
            print(f"WARNING: Common species file not found: {species_file}.json")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        name = data['species']['common_name']
        hotspot_count = data['summary']['total_hotspots_detected']
        highest_rate = data['summary']['highest_occurrence_rate']

        print(f"  {name}:")
        print(f"    - Found at {hotspot_count} hotspots")
        print(f"    - Highest occurrence rate: {highest_rate:.1%}")

        if data['hotspots']:
            top = data['hotspots'][0]
            print(f"    - Top hotspot: {top['name']} ({top['occurrence']['rate']:.1%})")

        # Common species should be widespread
        if hotspot_count < 50:
            print(f"    WARNING: {name} found at fewer hotspots than expected")

        # Common species should have high occurrence rates somewhere
        if highest_rate < 0.3:
            print(f"    WARNING: {name} has lower than expected highest rate")

    return True


def validate_json_structure(species_dir: Path) -> bool:
    """Validate JSON files have required fields."""
    required_species_fields = ['species', 'summary', 'hotspots', 'metadata']
    required_hotspot_fields = ['rank', 'locality_id', 'name', 'coordinates', 'occurrence']

    errors = []
    sample_files = list(species_dir.glob("*.json"))[:10]

    for json_file in sample_files:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for field in required_species_fields:
            if field not in data:
                errors.append(f"{json_file.name}: missing field '{field}'")

        if data.get('hotspots'):
            hotspot = data['hotspots'][0]
            for field in required_hotspot_fields:
                if field not in hotspot:
                    errors.append(f"{json_file.name}: hotspot missing field '{field}'")

    if errors:
        print("FAIL: JSON structure errors:")
        for e in errors:
            print(f"  - {e}")
        return False

    print(f"PASS: JSON structure valid (sampled {len(sample_files)} files)")
    return True


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("eBird Hotspot Guide Validation")
    print("=" * 60)
    print()

    if not OUTPUT_DIR.exists():
        print(f"ERROR: Output directory not found: {OUTPUT_DIR}")
        print("Run main.py first to generate output files.")
        sys.exit(1)

    species_dir = OUTPUT_DIR / "species"
    hotspots_dir = OUTPUT_DIR / "hotspots"
    index_dir = OUTPUT_DIR / "index"

    all_passed = True

    print("1. Checking coverage...")
    if not validate_hotspot_coverage(index_dir):
        all_passed = False
    print()

    print("2. Validating occurrence rates...")
    if not validate_occurrence_rates(species_dir):
        all_passed = False
    print()

    print("3. Validating JSON structure...")
    if not validate_json_structure(species_dir):
        all_passed = False
    print()

    print("4. Spot-checking common species...")
    spot_check_common_species(species_dir)
    print()

    print("=" * 60)
    if all_passed:
        print("All validation checks passed!")
    else:
        print("Some validation checks failed. Review output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
