# Hotspot Content Authoring

This directory contains manually-authored content for birding hotspots in Washtenaw County.

## File Structure

```
content/
├── _template.md          # Template for new hotspot content files
├── L320822.md            # Example: Nichols Arboretum
└── README.md             # This file
```

## Creating New Hotspot Content

### Method 1: Using the Scaffolding Script

```bash
# Create a virtual environment (first time only)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create a new content file
python scripts/new_hotspot_content.py L123456
```

### Method 2: Manual Creation

Copy `_template.md` to a new file named `{locId}.md`:

```bash
cp regions/washtenaw/hotspots/content/_template.md regions/washtenaw/hotspots/content/L123456.md
```

## Content File Format

Each content file uses YAML frontmatter followed by Markdown content:

```markdown
---
parking:
  type: lot  # lot | street | roadside | none
  notes: "Description of parking location and access"
hours: "Dawn to dusk"
fee: null  # null for free, or string like "$5/vehicle"
features:
  - restrooms
  - accessible-full
  - dogs-leashed
habitats:
  - deciduous-forest
  - wetland
  - prairie
tips:
  - "Tip 1 about birding this location"
  - "Tip 2 about best times or locations"
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

## Available Values

### parking.type
- `lot` - Dedicated parking lot
- `street` - Street parking
- `roadside` - Roadside pulloff
- `none` - No parking available

### features
- `restrooms`
- `accessible-full` - Fully accessible trails/facilities
- `accessible-partial` - Some accessible features
- `dogs-leashed` - Dogs allowed on leash
- `dogs-prohibited` - No dogs allowed
- `no-facilities` - No amenities

### habitats
- `deciduous-forest`
- `coniferous-forest`
- `wetland`
- `marsh`
- `river`
- `lake`
- `pond`
- `prairie`
- `grassland`
- `agricultural`

## Building the Enriched JSON

After creating or editing content files, rebuild the enriched hotspots JSON:

```bash
source venv/bin/activate
python scripts/build_enriched_hotspots.py
```

This will create `washtenaw_hotspots_enriched.json` with your content merged into the base hotspot data.

## Example

See [L320822.md](L320822.md) for a complete example (Nichols Arboretum).
