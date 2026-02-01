#!/usr/bin/env python3
"""
eBird Hotspot Guide Generator

Analyzes eBird data to identify the best hotspots for finding each bird species.
Works with any eBird Basic Dataset download - automatically detects data files.

Usage:
    python main.py

    Or via the region-based runner:
    python scripts/run_hotspot_guide.py <region_name>
"""

import logging
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hotspot_guide import config as hg_config
from hotspot_guide.processors import (
    count_checklists_per_hotspot,
    count_species_detections,
    calculate_occurrence_rates,
)
from hotspot_guide.output import (
    write_species_files,
    write_hotspot_files,
    write_index_files,
    write_notable_species_index,
    write_common_species_index,
    write_metadata,
)
from hotspot_guide.output.json_writer import build_species_code_map

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def main():
    """Main processing pipeline."""

    # Ensure config is initialized
    hg_config.ensure_initialized()

    # Access config values at runtime (after init_config was called)
    MAIN_FILE = hg_config.MAIN_FILE
    SAMPLING_FILE = hg_config.SAMPLING_FILE
    OUTPUT_DIR = hg_config.OUTPUT_DIR

    logger.info("=" * 60)
    logger.info("eBird Hotspot Guide Generator")
    logger.info("=" * 60)
    logger.info(f"Data directory: {MAIN_FILE.parent}")
    logger.info(f"Main file: {MAIN_FILE.name}")
    logger.info(f"Sampling file: {SAMPLING_FILE.name}")

    # Verify input files exist
    if not SAMPLING_FILE.exists():
        logger.error(f"Sampling file not found: {SAMPLING_FILE}")
        sys.exit(1)

    if not MAIN_FILE.exists():
        logger.error(f"Main data file not found: {MAIN_FILE}")
        sys.exit(1)

    # Step 1: Count complete checklists per hotspot (from sampling file)
    logger.info("")
    logger.info("Step 1: Counting checklists per hotspot from sampling file...")
    hotspot_data = count_checklists_per_hotspot(SAMPLING_FILE)
    logger.info(f"  Found {len(hotspot_data)} hotspots with complete checklists")

    total_checklists = sum(h['total_checklists'] for h in hotspot_data.values())
    logger.info(f"  Total complete checklists at hotspots: {total_checklists:,}")

    # Step 2: Count species detections per hotspot (from main file)
    logger.info("")
    logger.info("Step 2: Counting species detections from main file...")
    logger.info("  (This may take several minutes for large files)")
    species_detections = count_species_detections(MAIN_FILE)
    logger.info(f"  Found {len(species_detections)} unique species")

    # Step 3: Calculate occurrence rates
    logger.info("")
    logger.info("Step 3: Calculating occurrence rates...")
    species_guides = calculate_occurrence_rates(hotspot_data, species_detections)
    logger.info(f"  Calculated rates for {len(species_guides)} species")

    # Generate species codes for all species
    logger.info("")
    logger.info("Generating species codes...")
    code_map = build_species_code_map(list(species_guides.keys()))
    logger.info(f"  Generated {len(code_map)} species codes")

    # Step 4: Generate output files
    logger.info("")
    logger.info("Step 4: Writing output files...")

    # Create output directories
    species_dir = OUTPUT_DIR / "species"
    hotspots_dir = OUTPUT_DIR / "hotspots"
    index_dir = OUTPUT_DIR / "index"

    species_dir.mkdir(parents=True, exist_ok=True)
    hotspots_dir.mkdir(parents=True, exist_ok=True)
    index_dir.mkdir(parents=True, exist_ok=True)

    # Write files (now with code_map)
    write_species_files(species_guides, species_dir, code_map)
    logger.info(f"  Wrote {len(species_guides)} species files to {species_dir}")

    write_hotspot_files(hotspot_data, species_guides, hotspots_dir, code_map)
    logger.info(f"  Wrote {len(hotspot_data)} hotspot files to {hotspots_dir}")

    write_index_files(species_guides, hotspot_data, index_dir, code_map)
    logger.info(f"  Wrote index files to {index_dir}")

    write_notable_species_index(species_guides, hotspot_data, index_dir, code_map)
    logger.info(f"  Wrote notable_species_by_hotspot.json to {index_dir}")

    write_common_species_index(species_guides, hotspot_data, index_dir, code_map)
    logger.info(f"  Wrote common_species_by_hotspot.json to {index_dir}")

    write_metadata(OUTPUT_DIR, hotspot_data, species_guides, MAIN_FILE)
    logger.info(f"  Wrote metadata.json to {OUTPUT_DIR}")

    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Processing complete!")
    logger.info("=" * 60)
    logger.info(f"Output directory: {OUTPUT_DIR}")
    logger.info(f"  - {len(species_guides)} species files in species/")
    logger.info(f"  - {len(hotspot_data)} hotspot files in hotspots/")
    logger.info(f"  - Index files in index/")
    logger.info("")

    # Show a few example results
    logger.info("Sample results (top 3 hotspots for American Robin):")
    robin = species_guides.get('American Robin')
    if robin and robin.hotspots:
        robin_code = code_map.get('American Robin', 'amerob')
        logger.info(f"  Species code: {robin_code}")
        for i, h in enumerate(robin.hotspots[:3]):
            logger.info(
                f"  {i+1}. {h.hotspot_name}: "
                f"{h.occurrence_rate:.1%} ({h.detection_count}/{h.total_checklists})"
            )


if __name__ == "__main__":
    main()
