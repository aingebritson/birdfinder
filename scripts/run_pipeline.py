#!/usr/bin/env python3
"""
Run the complete eBird data processing pipeline for a specific region.

This script runs all four processing steps in sequence:
1. Parse eBird barchart data (removes sp. and hybrids)
2. Classify migration patterns (resident, single-season, two-passage, vagrant)
3. Calculate arrival/departure timing
4. Merge all data into final JSON

Usage:
    # From the project root directory:
    python3 scripts/run_pipeline.py washtenaw

    # Or from the scripts directory:
    cd scripts
    python3 run_pipeline.py washtenaw

The pipeline expects:
- Input: regions/[region_name]/ebird_*.txt file
- Output: regions/[region_name]/[region_name]_species_data.json
"""

import shutil
import subprocess
import sys
from pathlib import Path
import os

# Add parent directory to path for imports
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))

from utils.region_config import load_region_config, ConfigError


def find_input_file(region_path, config):
    """Find the eBird barchart .txt file in the region directory"""
    # Use configured input pattern if available
    input_pattern = config.get_path('input_pattern', 'ebird_*.txt')
    txt_files = list(region_path.glob(input_pattern))
    if not txt_files:
        return None
    if len(txt_files) > 1:
        print(f"⚠️  Warning: Multiple eBird files found. Using: {txt_files[0].name}")
    return txt_files[0]


def run_script(script_path, region_name, region_path):
    """Run a Python script and handle errors"""
    script_name = script_path.name
    print(f"\n{'='*70}")
    print(f"Running: {script_name}")
    print('='*70)

    # Set environment variable for region info
    env = os.environ.copy()
    env['EBIRD_REGION_NAME'] = region_name
    env['EBIRD_REGION_PATH'] = str(region_path)

    try:
        result = subprocess.run(
            ["python3", str(script_path), region_name],
            check=True,
            capture_output=False,
            text=True,
            cwd=script_path.parent,
            env=env
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error running {script_name}")
        print(f"Exit code: {e.returncode}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 run_pipeline.py <region_name>")
        print("\nExample:")
        print("  python3 run_pipeline.py washtenaw")
        print("\nThis will process: regions/washtenaw/ebird_*.txt")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root (go up from scripts/ if needed)
    if Path.cwd().name == 'scripts':
        project_root = Path.cwd().parent
    else:
        project_root = Path.cwd()

    # Load region configuration
    try:
        config = load_region_config(region_name, project_root)
    except ConfigError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)

    scripts_dir = project_root / "scripts"
    region_path = project_root / "regions" / region_name

    print("="*70)
    print("eBird Data Processing Pipeline")
    print("="*70)
    print(f"\nRegion: {config.display_name}")
    print(f"Region ID: {region_name}")
    print(f"Region path: {region_path}")
    if config.config_path:
        print(f"Config file: {config.config_path.relative_to(project_root)}")

    # Check that region directory exists
    if not region_path.exists():
        print(f"\n❌ Error: Region directory not found: {region_path}")
        print(f"\nCreate it with:")
        print(f"  mkdir -p {region_path}")
        print(f"  # Then place your eBird barchart .txt file in that directory")
        sys.exit(1)

    # Find input file
    input_file = find_input_file(region_path, config)
    if not input_file:
        input_pattern = config.get_path('input_pattern', 'ebird_*.txt')
        print(f"\n❌ Error: No eBird barchart file found in {region_path}")
        print(f"\nExpected: regions/{region_name}/{input_pattern}")
        sys.exit(1)

    print(f"Input file: {input_file.name}")

    print("\nThis will run all processing steps in sequence:")
    print("  1. Parse eBird barchart data")
    print("  2. Classify migration patterns")
    print("  3. Calculate arrival/departure timing")
    print("  4. Merge into final JSON")
    print()

    # Define the pipeline steps
    scripts = [
        "parse_ebird_data.py",
        "classify_migration_patterns.py",
        "calculate_arrival_departure.py",
        "merge_to_json.py"
    ]

    # Check that all scripts exist
    for script in scripts:
        script_path = scripts_dir / script
        if not script_path.exists():
            print(f"❌ Error: Script not found: {script_path}")
            sys.exit(1)

    # Run each script in sequence
    for i, script in enumerate(scripts, 1):
        print(f"\n[Step {i}/{len(scripts)}]")
        script_path = scripts_dir / script
        success = run_script(script_path, region_name, region_path)

        if not success:
            print(f"\n❌ Pipeline failed at step {i}: {script}")
            print("Fix the error and run the pipeline again.")
            sys.exit(1)

    # Success!
    output_file = region_path / f"{region_name}_species_data.json"
    intermediate_dir = region_path / "intermediate"

    # Copy species data to birdfinder/data/ so the frontend stays in sync
    birdfinder_data = project_root / "birdfinder" / "data"
    if birdfinder_data.exists() and output_file.exists():
        dest = birdfinder_data / "species_data.json"
        shutil.copy(output_file, dest)
        print(f"\nCopied to birdfinder/data/species_data.json")

    print("\n" + "="*70)
    print("✓ Pipeline Complete!")
    print("="*70)
    print(f"\nFinal output:")
    print(f"  📁 regions/{region_name}/")
    print(f"     📄 {region_name}_species_data.json  ← Use this for your website")

    if intermediate_dir.exists():
        print(f"\nIntermediate files (for debugging):")
        print(f"  📁 regions/{region_name}/intermediate/")
        for file in sorted(intermediate_dir.glob("*")):
            print(f"     📄 {file.name}")
    print()


if __name__ == "__main__":
    main()
