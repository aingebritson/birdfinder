#!/usr/bin/env python3
"""
Run all data pipelines for a region.

This script runs all three data pipelines in sequence:
1. Species pipeline - processes eBird barchart data
2. Hotspots pipeline - fetches from API and enriches with content
3. Hotspot guide pipeline - processes eBird Basic Dataset

Usage:
    # Run all pipelines
    python scripts/run_all.py washtenaw

    # Run specific pipelines only
    python scripts/run_all.py washtenaw --species
    python scripts/run_all.py washtenaw --hotspots
    python scripts/run_all.py washtenaw --hotspot-guide
    python scripts/run_all.py washtenaw --species --hotspots
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_path, args=None, description=None):
    """Run a Python script and return success status."""
    cmd = ["python3", str(script_path)]
    if args:
        cmd.extend(args)

    print(f"\n{'='*70}")
    print(f"Running: {description or script_path.name}")
    print('='*70 + "\n")

    try:
        result = subprocess.run(cmd, check=True, cwd=script_path.parent)
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Failed: {script_path.name}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Run all data pipelines for a region",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python scripts/run_all.py washtenaw           # Run all pipelines
    python scripts/run_all.py washtenaw --species # Run only species pipeline
    python scripts/run_all.py washtenaw --hotspots --hotspot-guide  # Skip species
        """
    )
    parser.add_argument("region", help="Region name (e.g., washtenaw)")
    parser.add_argument("--species", action="store_true",
                        help="Run species barchart pipeline")
    parser.add_argument("--hotspots", action="store_true",
                        help="Run hotspots fetch and enrich pipeline")
    parser.add_argument("--hotspot-guide", action="store_true",
                        help="Run hotspot guide pipeline (requires eBird Basic Dataset)")

    args = parser.parse_args()

    # If no specific pipeline selected, run all
    run_all = not (args.species or args.hotspots or args.hotspot_guide)

    scripts_dir = Path(__file__).parent
    region = args.region

    print("="*70)
    print("BirdFinder - Full Data Pipeline")
    print("="*70)
    print(f"\nRegion: {region}")

    pipelines_to_run = []
    if run_all or args.species:
        pipelines_to_run.append("species")
    if run_all or args.hotspots:
        pipelines_to_run.append("hotspots")
    if run_all or args.hotspot_guide:
        pipelines_to_run.append("hotspot-guide")

    print(f"Pipelines: {', '.join(pipelines_to_run)}")

    results = {}

    # 1. Species Pipeline
    if run_all or args.species:
        success = run_script(
            scripts_dir / "run_pipeline.py",
            args=[region],
            description="Species Pipeline (barchart data)"
        )
        results["species"] = success
        if not success:
            print("\n⚠️  Species pipeline failed, continuing with other pipelines...")

    # 2. Hotspots Pipeline (fetch + enrich)
    if run_all or args.hotspots:
        # Fetch from API
        success = run_script(
            scripts_dir / "fetch_hotspots.py",
            description="Hotspots Pipeline - Fetch from eBird API"
        )
        results["hotspots-fetch"] = success

        if success:
            # Enrich with content
            success = run_script(
                scripts_dir / "build_enriched_hotspots.py",
                description="Hotspots Pipeline - Enrich with content"
            )
            results["hotspots-enrich"] = success
        else:
            print("\n⚠️  Hotspot fetch failed, skipping enrichment...")
            results["hotspots-enrich"] = False

    # 3. Hotspot Guide Pipeline
    if run_all or args.hotspot_guide:
        success = run_script(
            scripts_dir / "run_hotspot_guide.py",
            args=[region],
            description="Hotspot Guide Pipeline (eBird Basic Dataset)"
        )
        results["hotspot-guide"] = success
        if not success:
            print("\n⚠️  Hotspot guide pipeline failed.")

    # Summary
    print("\n" + "="*70)
    print("Pipeline Summary")
    print("="*70)

    all_success = True
    for pipeline, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {pipeline}")
        if not success:
            all_success = False

    print()
    if all_success:
        print("✓ All pipelines completed successfully!")
    else:
        print("⚠️  Some pipelines failed. Check output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
