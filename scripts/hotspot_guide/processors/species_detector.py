"""Count species detections per hotspot from the main observations file."""

import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Any, Set
from collections import defaultdict
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hotspot_guide.config import MAIN_COLS, CHUNK_SIZE


def count_species_detections(main_file: Path) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Read the main observations file and count species detections per hotspot.

    Args:
        main_file: Path to the main eBird observations file

    Returns:
        Nested dictionary: species -> locality_id -> detection data
        {
            'American Robin': {
                'L123456': {
                    'scientific_name': 'Turdus migratorius',
                    'checklist_ids': {'S123', 'S456', ...},
                    'monthly_checklist_ids': {1: {'S123'}, 2: {...}, ...},
                    'total_count': 150,
                    'max_count': 25
                }
            }
        }
    """
    # Nested defaultdict for species -> locality -> detection data
    species_detections: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(
        lambda: defaultdict(lambda: {
            'scientific_name': None,
            'checklist_ids': set(),
            'monthly_checklist_ids': {m: set() for m in range(1, 13)},
            'total_count': 0,
            'max_count': 0,
        })
    )

    # Count total rows for progress bar
    print("Counting rows in main file (this may take a moment)...")
    total_rows = sum(1 for _ in open(main_file, 'r', encoding='utf-8')) - 1
    print(f"Total rows: {total_rows:,}")

    chunks = pd.read_csv(
        main_file,
        sep='\t',
        usecols=MAIN_COLS,
        chunksize=CHUNK_SIZE,
        dtype={
            'ALL SPECIES REPORTED': 'Int64',
            'LOCALITY TYPE': 'category',
            'CATEGORY': 'category',
        },
        encoding='utf-8',
        low_memory=False,
    )

    rows_processed = 0
    with tqdm(total=total_rows, desc="Reading main file") as pbar:
        for chunk in chunks:
            # Filter for:
            # - Hotspots only (LOCALITY TYPE = 'H')
            # - Complete checklists (ALL SPECIES REPORTED = 1)
            # - Species-level taxa only (CATEGORY = 'species')
            mask = (
                (chunk['LOCALITY TYPE'] == 'H') &
                (chunk['ALL SPECIES REPORTED'] == 1) &
                (chunk['CATEGORY'] == 'species')
            )
            filtered = chunk[mask]

            # Parse dates
            filtered = filtered.copy()
            filtered['month'] = pd.to_datetime(filtered['OBSERVATION DATE']).dt.month

            # Process each observation
            for _, row in filtered.iterrows():
                species = row['COMMON NAME']
                sci_name = row['SCIENTIFIC NAME']
                loc_id = row['LOCALITY ID']
                checklist_id = row['SAMPLING EVENT IDENTIFIER']
                month = row['month']

                data = species_detections[species][loc_id]
                data['scientific_name'] = sci_name
                data['checklist_ids'].add(checklist_id)
                data['monthly_checklist_ids'][month].add(checklist_id)

                # Handle observation count (can be 'X' for presence-only)
                obs_count = row['OBSERVATION COUNT']
                if obs_count != 'X' and pd.notna(obs_count):
                    try:
                        count = int(obs_count)
                        data['total_count'] += count
                        data['max_count'] = max(data['max_count'], count)
                    except (ValueError, TypeError):
                        pass

            rows_processed += len(chunk)
            pbar.update(len(chunk))

    # Convert defaultdicts to regular dicts for easier handling
    return {
        species: dict(hotspots)
        for species, hotspots in species_detections.items()
    }
