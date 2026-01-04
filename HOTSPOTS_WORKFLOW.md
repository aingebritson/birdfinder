# Hotspot Content Authoring Workflow

This document explains how to add detailed information to hotspot pages in the BirdFinder web application.

## Overview

The hotspot system uses a content authoring workflow that allows you to add rich information (parking, hours, birding tips, etc.) to individual hotspot pages. This content is stored in Markdown files with YAML frontmatter and then merged with the base eBird hotspot data.

## File Structure

```
regions/washtenaw/hotspots/
├── washtenaw_hotspots.json              # Base hotspot data from eBird API
├── content/                              # Manual content files
│   ├── _template.md                      # Template for new hotspots
│   ├── README.md                         # Content authoring guide
│   └── L320822.md                        # Example: Nichols Arboretum

birdfinder/data/
└── washtenaw_hotspots_enriched.json     # Generated: merged data for web app

scripts/
├── build_enriched_hotspots.py           # Build script
└── new_hotspot_content.py               # Scaffolding script
```

## Workflow

### 1. Create New Content File

Use the scaffolding script to create a new content file for a hotspot:

```bash
# Activate virtual environment
source venv/bin/activate

# Create content file (replace L123456 with actual location ID)
python scripts/new_hotspot_content.py L123456
```

This creates a new file at `regions/washtenaw/hotspots/content/L123456.md` with the template structure.

### 2. Edit Content File

Open the newly created file and fill in the information:

```markdown
---
parking:
  type: lot  # lot | street | roadside | none
  notes: "Main parking lot on Geddes Ave"
hours: "Dawn to dusk"
fee: null  # null for free, or string like "$5/vehicle"
features:
  - restrooms
  - accessible-partial
  - dogs-leashed
habitats:
  - deciduous-forest
  - wetland
  - river
tips:
  - "Best birding is early morning before foot traffic"
  - "Check the river overlook for waterfowl"
links:
  - label: "Official Website"
    url: "https://example.com"
lastUpdated: "2026-01-03"
---

## How to Bird Here

Write free-form prose about birding this location. Include:
- Best seasons and what to look for
- Habitat descriptions
- Notable species
- Trail or access information
```

### 3. Build Enriched Data

After editing content files, rebuild the enriched JSON:

```bash
source venv/bin/activate
python scripts/build_enriched_hotspots.py
```

This merges your content with the base hotspot data and outputs to `birdfinder/data/washtenaw_hotspots_enriched.json`.

### 4. View on Web

The hotspot detail page will automatically display your content:
- Visit `hotspots.html`
- Click on a hotspot card
- The detail page shows all enriched information

## Available Fields

### Parking Types
- `lot` - Dedicated parking lot
- `street` - Street parking
- `roadside` - Roadside pulloff
- `none` - No parking available

### Features
- `restrooms`
- `accessible-full` - Fully accessible
- `accessible-partial` - Partially accessible
- `dogs-leashed` - Dogs allowed on leash
- `dogs-prohibited` - No dogs allowed
- `no-facilities` - No amenities

### Habitats
- `deciduous-forest`, `coniferous-forest`
- `wetland`, `marsh`
- `river`, `lake`, `pond`
- `prairie`, `grassland`
- `agricultural`

## Example

See [regions/washtenaw/hotspots/content/L320822.md](regions/washtenaw/hotspots/content/L320822.md) for a complete example (Nichols Arboretum).

## How It Works

1. **Base Data**: `washtenaw_hotspots.json` contains basic info from eBird (name, location, species count)
2. **Content Files**: Markdown files in `content/` contain manual enrichments
3. **Build Script**: Merges base data + content files → `washtenaw_hotspots_enriched.json`
4. **Web App**: Loads enriched JSON and displays on hotspot detail pages

Hotspots without content files will still appear on the site, they just won't have the additional details.
