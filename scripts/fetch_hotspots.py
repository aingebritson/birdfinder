#!/usr/bin/env python3
"""
Fetch eBird hotspot data for a region.

This script fetches hotspot data from the eBird API and saves it in two formats:
1. Raw timestamped JSON in regions/<region>/hotspots/raw/
2. Cleaned JSON for web app use in regions/<region>/hotspots/<region>_hotspots.json

Usage:
    python3 scripts/fetch_hotspots.py <region_name>

Example:
    python3 scripts/fetch_hotspots.py washtenaw
    python3 scripts/fetch_hotspots.py oakland

Requires:
    - python-dotenv: pip install python-dotenv
    - requests: pip install requests
"""

import os
import sys
import json
import csv
import requests
from datetime import datetime
from pathlib import Path
from io import StringIO
from dotenv import load_dotenv

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from utils.region_config import load_region_config, ConfigError


API_BASE_URL = "https://api.ebird.org/v2"


def load_api_key():
    """Load eBird API key from .env file."""
    load_dotenv()
    api_key = os.getenv("EBIRD_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        print("ERROR: eBird API key not found or not configured.", file=sys.stderr)
        print("Please create a .env file with your EBIRD_API_KEY.", file=sys.stderr)
        print("See .env.example for the format.", file=sys.stderr)
        print("\nGet your API key from: https://ebird.org/api/keygen", file=sys.stderr)
        sys.exit(1)

    return api_key


def fetch_hotspots(api_key, county_code):
    """Fetch hotspot data from eBird API."""
    url = f"{API_BASE_URL}/ref/hotspot/{county_code}"
    headers = {"X-eBirdApiToken": api_key}

    print(f"Fetching hotspots for {county_code}...")

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse CSV response
        csv_data = StringIO(response.text)
        reader = csv.reader(csv_data)

        hotspots = []
        for row in reader:
            if len(row) >= 9:  # Ensure row has expected columns
                hotspot = {
                    "locId": row[0],
                    "countryCode": row[1],
                    "subnational1Code": row[2],
                    "subnational2Code": row[3],
                    "lat": float(row[4]) if row[4] else None,
                    "lng": float(row[5]) if row[5] else None,
                    "locName": row[6],
                    "latestObsDt": row[7] if row[7] else None,
                    "numSpeciesAllTime": int(row[8]) if row[8] else 0
                }
                hotspots.append(hotspot)

        return hotspots
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Failed to fetch hotspot data: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}", file=sys.stderr)
            print(f"Response text: {e.response.text[:500]}", file=sys.stderr)
        sys.exit(1)
    except (csv.Error, ValueError) as e:
        print(f"ERROR: Failed to parse CSV response: {e}", file=sys.stderr)
        print(f"Response text: {response.text[:500]}", file=sys.stderr)
        sys.exit(1)


def clean_hotspot_data(hotspot):
    """Transform raw hotspot data into cleaned format for web app."""
    return {
        "locId": hotspot.get("locId"),
        "name": hotspot.get("locName"),
        "lat": hotspot.get("lat"),
        "lng": hotspot.get("lng"),
        "numSpecies": hotspot.get("numSpeciesAllTime", 0),
        "latestObs": hotspot.get("latestObsDt"),
        "knowledge": None
    }


def compare_hotspots(old_data, new_data):
    """Compare old and new hotspot data and print a summary of changes."""
    old_by_id = {h["locId"]: h for h in old_data}
    new_by_id = {h["locId"]: h for h in new_data}

    old_ids = set(old_by_id.keys())
    new_ids = set(new_by_id.keys())

    added = new_ids - old_ids
    removed = old_ids - new_ids
    common = old_ids & new_ids

    # Check for name changes
    name_changes = []
    for loc_id in common:
        if old_by_id[loc_id]["name"] != new_by_id[loc_id]["name"]:
            name_changes.append({
                "locId": loc_id,
                "old_name": old_by_id[loc_id]["name"],
                "new_name": new_by_id[loc_id]["name"]
            })

    # Print summary
    print("\n" + "="*60)
    print("HOTSPOT DATA COMPARISON")
    print("="*60)
    print(f"Previous count: {len(old_data)}")
    print(f"New count:      {len(new_data)}")
    print(f"Net change:     {len(new_data) - len(old_data):+d}")

    if added:
        print(f"\n✓ Added ({len(added)}):")
        for loc_id in sorted(added):
            print(f"  + {new_by_id[loc_id]['name']} ({loc_id})")

    if removed:
        print(f"\n✗ Removed ({len(removed)}):")
        for loc_id in sorted(removed):
            print(f"  - {old_by_id[loc_id]['name']} ({loc_id})")

    if name_changes:
        print(f"\n~ Name Changes ({len(name_changes)}):")
        for change in name_changes:
            print(f"  ~ {change['locId']}")
            print(f"    Old: {change['old_name']}")
            print(f"    New: {change['new_name']}")

    if not added and not removed and not name_changes:
        print("\n✓ No changes detected")

    print("="*60 + "\n")


def main():
    """Main execution function."""
    if len(sys.argv) != 2:
        print("Usage: python3 fetch_hotspots.py <region_name>")
        print("Example: python3 fetch_hotspots.py washtenaw")
        sys.exit(1)

    region_name = sys.argv[1]

    # Determine project root
    project_root = Path(__file__).parent.parent

    # Load region config
    try:
        region_config = load_region_config(region_name, project_root)
    except ConfigError as e:
        print(f"Error loading region config: {e}")
        sys.exit(1)

    if not region_config.ebird_region_code:
        print(f"Error: No ebird_region_code set in config for region '{region_name}'.")
        sys.exit(1)

    county_code = region_config.ebird_region_code
    region_path = project_root / "regions" / region_name
    raw_dir = region_path / "hotspots" / "raw"
    output_file = region_path / "hotspots" / f"{region_name}_hotspots.json"

    # Load API key
    api_key = load_api_key()

    # Fetch raw data
    raw_data = fetch_hotspots(api_key, county_code)
    print(f"✓ Fetched {len(raw_data)} hotspots")

    # Save raw data with timestamp
    raw_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d")
    raw_file = raw_dir / f"ebird_hotspots_{timestamp}.json"

    with open(raw_file, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved raw data to {raw_file}")

    # Clean data
    cleaned_data = [clean_hotspot_data(h) for h in raw_data]

    # Compare with existing data if it exists
    if output_file.exists():
        with open(output_file, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        compare_hotspots(old_data, cleaned_data)
    else:
        print(f"\nNo existing data found. Creating new file with {len(cleaned_data)} hotspots.")

    # Save cleaned data
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    print(f"✓ Saved cleaned data to {output_file}")

    print("\n✓ Done!")


if __name__ == "__main__":
    main()
