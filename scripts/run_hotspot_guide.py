#!/usr/bin/env python3
"""
Run eBird Hotspot Guide pipeline for a region.

This script integrates the hotspot guide pipeline with the region configuration
system, allowing region-specific settings and standardized input/output paths.

Usage:
    python scripts/run_hotspot_guide.py <region_name>

Example:
    python scripts/run_hotspot_guide.py washtenaw

Input:
    regions/<region>/ebird_basic_dataset/
    - ebd_*.txt (main observations file)
    - *_sampling.txt (sampling events file)

Output:
    regions/<region>/hotspot_guide_output/
    - species/<code>.json (one file per species)
    - hotspots/<locality_id>_<name>.json (one file per hotspot)
    - index/species_index.json
    - index/hotspot_index.json
    - index/top_hotspots_by_species.json
    - metadata.json
"""

import shutil
import sys
from pathlib import Path

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.region_config import load_region_config, ConfigError
from hotspot_guide import config as hg_config
from hotspot_guide.main import main as run_pipeline


def main():
    """Run the hotspot guide pipeline for a specified region."""
    if len(sys.argv) != 2:
        print("Usage: python run_hotspot_guide.py <region_name>")
        print("Example: python run_hotspot_guide.py washtenaw")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root
    project_root = Path(__file__).parent.parent

    # Load region configuration
    try:
        region_config = load_region_config(region_name, project_root)
    except ConfigError as e:
        print(f"Error loading region config: {e}")
        sys.exit(1)

    # Get hotspot guide settings
    hg_settings = region_config.get_hotspot_guide_config()

    if not hg_settings.get('enabled', False):
        print(f"Hotspot guide is not enabled for region '{region_name}'.")
        print("To enable, add 'hotspot_guide.enabled: true' to the region config.")
        sys.exit(1)

    # Set up paths
    region_path = project_root / "regions" / region_name
    input_dir = region_path / "ebird_basic_dataset"
    output_dir = region_path / "hotspot_guide_output"

    # Verify input directory exists
    if not input_dir.exists():
        print(f"Error: Input directory not found: {input_dir}")
        print("")
        print("Please place your eBird Basic Dataset files in this directory:")
        print(f"  {input_dir}/")
        print("")
        print("Required files:")
        print("  - ebd_*.txt (main observations file)")
        print("  - *_sampling.txt (sampling events file)")
        print("")
        print("You can download the eBird Basic Dataset from:")
        print("  https://ebird.org/data/download")
        sys.exit(1)

    # Initialize hotspot guide configuration
    try:
        hg_config.init_config(
            data_dir=input_dir,
            output_dir=output_dir,
            min_checklists_threshold=hg_settings.get('min_checklists_threshold'),
            high_confidence_min=hg_settings.get('high_confidence_min'),
            medium_confidence_min=hg_settings.get('medium_confidence_min'),
        )
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    print(f"Running hotspot guide pipeline for region: {region_config.display_name}")
    print(f"Input:  {input_dir}")
    print(f"Output: {output_dir}")
    print("")

    # Run the pipeline
    run_pipeline()

    # Copy hotspot data to birdfinder for web access
    hotspot_source = output_dir / "index" / "top_hotspots_by_species.json"
    birdfinder_data = project_root / "birdfinder" / "data"
    if hotspot_source.exists() and birdfinder_data.exists():
        shutil.copy(hotspot_source, birdfinder_data / "top_hotspots_by_species.json")
        print(f"\nCopied hotspot data to birdfinder/data/")


if __name__ == "__main__":
    main()
