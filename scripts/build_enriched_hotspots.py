#!/usr/bin/env python3
"""
Build enriched hotspots JSON by merging base data with manual content files.

This script:
1. Loads the base hotspots data from washtenaw_hotspots.json
2. For each hotspot, checks if a matching content/{locId}.md file exists
3. If it exists, parses the YAML frontmatter and markdown body
4. Merges the manual content into the base hotspot data
5. Outputs to washtenaw_hotspots_enriched.json
"""

import json
import os
from pathlib import Path
import frontmatter


def load_base_hotspots(base_path):
    """Load the base hotspots JSON data."""
    with open(base_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_content_file(content_path):
    """Load and parse a markdown content file with YAML frontmatter."""
    if not content_path.exists():
        return None

    post = frontmatter.load(content_path)

    # Extract frontmatter and content
    metadata = post.metadata
    how_to_bird = post.content.strip() if post.content else None

    return {
        'parking': metadata.get('parking'),
        'hours': metadata.get('hours'),
        'fee': metadata.get('fee'),
        'features': metadata.get('features', []),
        'habitats': metadata.get('habitats', []),
        'tips': metadata.get('tips', []),
        'links': metadata.get('links', []),
        'lastUpdated': metadata.get('lastUpdated'),
        'howToBird': how_to_bird
    }


def enrich_hotspot(hotspot, content_data):
    """Merge content data into a hotspot record."""
    enriched = hotspot.copy()

    if content_data:
        # Merge all content fields
        enriched.update(content_data)
    else:
        # Set default null values for all enrichment fields
        enriched.update({
            'parking': None,
            'hours': None,
            'fee': None,
            'features': [],
            'habitats': [],
            'tips': [],
            'links': [],
            'lastUpdated': None,
            'howToBird': None
        })

    return enriched


def build_enriched_hotspots(base_dir='regions/washtenaw/hotspots', output_dir='birdfinder/data'):
    """Main function to build enriched hotspots JSON."""
    base_dir = Path(base_dir)
    output_dir = Path(output_dir)

    # Paths
    base_json_path = base_dir / 'washtenaw_hotspots.json'
    content_dir = base_dir / 'content'
    output_path = output_dir / 'washtenaw_hotspots_enriched.json'

    # Load base data
    print(f"Loading base data from {base_json_path}...")
    hotspots = load_base_hotspots(base_json_path)
    print(f"Loaded {len(hotspots)} hotspots")

    # Process each hotspot
    enriched_hotspots = []
    content_count = 0

    for hotspot in hotspots:
        loc_id = hotspot['locId']
        content_path = content_dir / f"{loc_id}.md"

        # Load content if it exists
        content_data = load_content_file(content_path)
        if content_data:
            content_count += 1
            print(f"  ✓ Found content for {hotspot['name']} ({loc_id})")

        # Enrich and add to list
        enriched = enrich_hotspot(hotspot, content_data)
        enriched_hotspots.append(enriched)

    # Write output
    print(f"\nWriting enriched data to {output_path}...")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched_hotspots, f, indent=2, ensure_ascii=False)

    print(f"✓ Done! Enriched {content_count}/{len(hotspots)} hotspots with content")
    print(f"  Output: {output_path}")


if __name__ == '__main__':
    build_enriched_hotspots()
