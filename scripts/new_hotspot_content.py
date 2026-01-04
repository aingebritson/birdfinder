#!/usr/bin/env python3
"""
Scaffold a new hotspot content file from the template.

Usage:
    python scripts/new_hotspot_content.py L123456
"""

import sys
import shutil
from pathlib import Path


def create_hotspot_content(loc_id, base_dir='regions/washtenaw/hotspots'):
    """Create a new content file from the template."""
    base_dir = Path(base_dir)
    content_dir = base_dir / 'content'
    template_path = content_dir / '_template.md'
    output_path = content_dir / f'{loc_id}.md'

    # Check if template exists
    if not template_path.exists():
        print(f"Error: Template file not found at {template_path}")
        return False

    # Check if content file already exists
    if output_path.exists():
        response = input(f"Content file {output_path} already exists. Overwrite? [y/N] ")
        if response.lower() != 'y':
            print("Cancelled.")
            return False

    # Copy template to new file
    shutil.copy(template_path, output_path)
    print(f"✓ Created new content file: {output_path}")
    print(f"\nNext steps:")
    print(f"  1. Edit {output_path} to add hotspot information")
    print(f"  2. Run: python scripts/build_enriched_hotspots.py")
    return True


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python scripts/new_hotspot_content.py LOC_ID")
        print("Example: python scripts/new_hotspot_content.py L123456")
        sys.exit(1)

    loc_id = sys.argv[1]

    # Validate loc_id format
    if not loc_id.startswith('L'):
        print("Error: Location ID should start with 'L' (e.g., L123456)")
        sys.exit(1)

    success = create_hotspot_content(loc_id)
    sys.exit(0 if success else 1)
