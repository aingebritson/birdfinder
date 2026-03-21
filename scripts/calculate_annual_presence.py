#!/usr/bin/env python3
"""
Calculate annual presence for each species from the eBird Basic Dataset (EBD).

For each species, counts the number of distinct years (within the last 10 complete
calendar years) in which the species was recorded on at least one complete checklist.

Output: regions/<region>/intermediate/<region>_annual_presence.json
    {
        "American Robin": 10,
        "Little Gull": 1,
        ...
    }

Only species with >= 1 detection in the window are included. Species absent from
the output had 0 years of presence in the window.

If EBD files are not found, a warning is printed and the script exits with code 0
so the pipeline can continue without the annual presence data.

Usage:
    python3 scripts/calculate_annual_presence.py <region_name>
"""

import json
import sys
from datetime import date
from pathlib import Path
from collections import defaultdict

import pandas as pd

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.validation import validate_region_name, ValidationError


ANNUAL_PRESENCE_COLS = [
    'COMMON NAME',
    'OBSERVATION DATE',
    'CATEGORY',
    'ALL SPECIES REPORTED',
]

CHUNK_SIZE = 100_000


def get_analysis_year_range():
    """
    Return (start_year, end_year) for the last 10 complete calendar years.

    "Complete" means the year has ended — the current year is excluded.
    Example: in 2026, returns (2016, 2025).
    """
    current_year = date.today().year
    end_year = current_year - 1
    start_year = end_year - 9
    return start_year, end_year


def find_ebd_file(ebd_dir: Path) -> Path:
    """
    Find the main EBD observations file (ebd_*.txt, not *_sampling.txt).
    Raises FileNotFoundError if not found or ambiguous.
    """
    candidates = [
        f for f in ebd_dir.glob("ebd_*.txt")
        if not f.name.endswith("_sampling.txt")
    ]
    if not candidates:
        raise FileNotFoundError(f"No EBD main file (ebd_*.txt) found in {ebd_dir}")
    if len(candidates) > 1:
        raise FileNotFoundError(
            f"Multiple EBD main files found in {ebd_dir}: {[f.name for f in candidates]}"
        )
    return candidates[0]


def calculate_annual_presence(ebd_file: Path, start_year: int, end_year: int) -> dict:
    """
    Read the EBD file in chunks and return a dict mapping species name to the
    number of distinct years (within [start_year, end_year]) in which it appeared
    on at least one complete checklist.
    """
    # Track distinct years per species using sets
    species_years: dict[str, set] = defaultdict(set)

    print(f"Reading EBD: {ebd_file.name}")
    print(f"Year window: {start_year}–{end_year}")

    chunks = pd.read_csv(
        ebd_file,
        sep='\t',
        usecols=ANNUAL_PRESENCE_COLS,
        chunksize=CHUNK_SIZE,
        dtype={
            'ALL SPECIES REPORTED': 'Int64',
            'CATEGORY': 'category',
        },
        encoding='utf-8',
        low_memory=False,
    )

    rows_processed = 0
    for chunk in chunks:
        # Filter: complete checklists, species-level taxa only
        mask = (
            (chunk['ALL SPECIES REPORTED'] == 1) &
            (chunk['CATEGORY'] == 'species')
        )
        filtered = chunk[mask].copy()

        if filtered.empty:
            rows_processed += len(chunk)
            continue

        # Parse year
        filtered['year'] = pd.to_datetime(
            filtered['OBSERVATION DATE'], errors='coerce'
        ).dt.year

        # Filter to window
        in_window = filtered[
            (filtered['year'] >= start_year) & (filtered['year'] <= end_year)
        ]

        # Accumulate distinct years per species
        for _, row in in_window.iterrows():
            species_years[row['COMMON NAME']].add(int(row['year']))

        rows_processed += len(chunk)
        if rows_processed % 500_000 == 0:
            print(f"  {rows_processed:,} rows processed...")

    print(f"  {rows_processed:,} rows total")

    # Convert sets to counts
    return {species: len(years) for species, years in species_years.items()}


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 calculate_annual_presence.py <region_name>")
        sys.exit(1)

    region_name = sys.argv[1]

    try:
        validate_region_name(region_name)
    except ValidationError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Determine project root
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    region_path = project_root / "regions" / region_name
    ebd_dir = region_path / "ebird_basic_dataset"
    intermediate_path = region_path / "intermediate"

    # Graceful failure if EBD data is not present
    if not ebd_dir.exists():
        print(f"⚠️  EBD directory not found: {ebd_dir}")
        print("   Skipping annual presence calculation. Classification will use barchart data only.")
        sys.exit(0)

    try:
        ebd_file = find_ebd_file(ebd_dir)
    except FileNotFoundError as e:
        print(f"⚠️  {e}")
        print("   Skipping annual presence calculation. Classification will use barchart data only.")
        sys.exit(0)

    start_year, end_year = get_analysis_year_range()
    print(f"\nCalculating annual presence for {region_name}")
    print(f"Analyzing last 10 complete years: {start_year}–{end_year}")

    presence = calculate_annual_presence(ebd_file, start_year, end_year)

    # Sort by species name for readability
    presence = dict(sorted(presence.items()))

    intermediate_path.mkdir(exist_ok=True)
    output_file = intermediate_path / f"{region_name}_annual_presence.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(presence, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Annual presence calculated for {len(presence)} species")
    print(f"  Year window: {start_year}–{end_year}")
    print(f"  Output: {output_file}")


if __name__ == "__main__":
    main()
