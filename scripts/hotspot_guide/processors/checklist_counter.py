"""Count complete checklists per hotspot from the sampling file."""

import sys
import pandas as pd
from pathlib import Path
from typing import Dict, Any
from tqdm import tqdm

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from hotspot_guide.config import SAMPLING_COLS, SAMPLING_CHUNK_SIZE


def count_checklists_per_hotspot(sampling_file: Path) -> Dict[str, Dict[str, Any]]:
    """
    Read the sampling file and count complete checklists per hotspot.

    Args:
        sampling_file: Path to the sampling events file

    Returns:
        Dictionary mapping locality_id to hotspot metadata:
        {
            'L123456': {
                'name': 'Hotspot Name',
                'latitude': 42.28,
                'longitude': -83.74,
                'total_checklists': 500,
                'monthly_checklists': {1: 30, 2: 25, ...}
            }
        }
    """
    hotspot_data: Dict[str, Dict[str, Any]] = {}

    # Count total rows for progress bar
    total_rows = sum(1 for _ in open(sampling_file, 'r', encoding='utf-8')) - 1

    chunks = pd.read_csv(
        sampling_file,
        sep='\t',
        usecols=SAMPLING_COLS,
        chunksize=SAMPLING_CHUNK_SIZE,
        dtype={
            'ALL SPECIES REPORTED': 'Int64',
            'LOCALITY TYPE': 'category',
        },
        encoding='utf-8',
    )

    rows_processed = 0
    with tqdm(total=total_rows, desc="Reading sampling file") as pbar:
        for chunk in chunks:
            # Filter for complete checklists at hotspots
            mask = (chunk['LOCALITY TYPE'] == 'H') & (chunk['ALL SPECIES REPORTED'] == 1)
            filtered = chunk[mask]

            # Parse dates
            filtered = filtered.copy()
            filtered['month'] = pd.to_datetime(filtered['OBSERVATION DATE']).dt.month

            # Aggregate by hotspot
            for _, row in filtered.iterrows():
                loc_id = row['LOCALITY ID']
                month = row['month']

                if loc_id not in hotspot_data:
                    hotspot_data[loc_id] = {
                        'name': row['LOCALITY'],
                        'latitude': float(row['LATITUDE']),
                        'longitude': float(row['LONGITUDE']),
                        'total_checklists': 0,
                        'monthly_checklists': {m: 0 for m in range(1, 13)},
                    }

                hotspot_data[loc_id]['total_checklists'] += 1
                hotspot_data[loc_id]['monthly_checklists'][month] += 1

            rows_processed += len(chunk)
            pbar.update(len(chunk))

    return hotspot_data
