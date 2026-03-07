# Flightcall

*Know what to find, and where to look.*

A bird phenology web application that displays migration timing, detection probabilities, and birding hotspots for species in your region. Built with eBird data. The root landing page serves as a county directory; each county's app lives in its own subdirectory.

**Live Example:** Washtenaw County, Michigan (327 species, 315 hotspots)

## Features

- **This Week View**: See which species are arriving, at peak, or departing this week
- **Browse All Species**: Search and filter by migration category
- **Species Detail Pages**: View annual frequency charts, migration timing, and top hotspots
- **Hotspot Directory**: Browse birding locations with species counts and detailed guides
- **Hotspot Detail Pages**: View parking, hours, habitats, tips, and notable species per location
- **Interactive Week Navigation**: Browse any week of the year
- **Responsive Design**: Works on desktop and mobile

## Quick Start

### View the Web Application

1. Copy your processed species data to the web app:
```bash
cp regions/[region_name]/[region_name]_species_data.json washtenaw/data/species_data.json
```

2. Serve with a local server from the repo root (serves both landing page and county app):
```bash
python3 -m http.server 8000
# Landing page:  http://localhost:8000
# County app:    http://localhost:8000/washtenaw/
```

### Process Data for Your Region

1. Download eBird barchart data for your region from [eBird](https://ebird.org/barchart)
2. Create a region directory and place the `.txt` file in it:
```bash
mkdir -p regions/[region_name]
mv ebird_*.txt regions/[region_name]/
```

3. Run the pipeline:
```bash
python3 scripts/run_pipeline.py [region_name]
```

4. Copy the output to the web app:
```bash
cp regions/[region_name]/[region_name]_species_data.json washtenaw/data/species_data.json
```

## Project Structure

```
.
├── index.html                   # Landing page — county directory (Flightcall home)
├── washtenaw/                   # Washtenaw County app (deployed to /washtenaw/ on gh-pages)
│   ├── index.html              # This Week view (main page)
│   ├── browse.html             # Browse All Species view
│   ├── species.html            # Species Detail view
│   ├── hotspots.html           # Hotspot directory
│   ├── hotspot-detail.html     # Individual hotspot details
│   ├── css/
│   │   └── styles.css          # Custom styles (Field Journal aesthetic)
│   ├── js/
│   │   ├── data-loader.js      # Robust data loading with retry logic
│   │   ├── data.js             # Species data access functions
│   │   ├── week-calculator.js  # Date/week conversion utilities
│   │   ├── this-week.js        # This Week page logic
│   │   ├── browse.js           # Browse page logic
│   │   ├── species-detail.js   # Species detail page logic
│   │   ├── hotspots.js         # Hotspot directory logic
│   │   ├── hotspot-detail.js   # Hotspot detail page logic
│   │   ├── debounce.js         # Search debouncing utility
│   │   └── sanitizer.js        # XSS protection utility
│   └── data/
│       ├── species_data.json                # Species data (copy from regions/)
│       ├── washtenaw_hotspots.json          # Base hotspot data from eBird
│       ├── washtenaw_hotspots_enriched.json # Hotspots with manual content
│       ├── hotspot_index.json               # Hotspot metadata index
│       ├── common_species_by_hotspot.json   # Top 15 species per hotspot
│       ├── notable_species_by_hotspot.json  # Rare/specialty species per hotspot
│       └── top_hotspots_by_species.json     # Best hotspots for each species
├── scripts/                     # Data processing pipeline
│   ├── run_pipeline.py         # Run species data pipeline
│   ├── run_all.py              # Run pipeline for all regions
│   ├── parse_ebird_data.py     # Step 1: Parse eBird barchart file
│   ├── classify_migration_patterns.py  # Step 2: Classify species
│   ├── calculate_arrival_departure.py  # Step 3: Calculate timing
│   ├── merge_to_json.py        # Step 4: Merge to JSON
│   ├── fetch_hotspots.py       # Fetch eBird hotspot data via API
│   ├── build_enriched_hotspots.py      # Merge content with hotspot data
│   ├── new_hotspot_content.py  # Scaffold new hotspot content files
│   ├── run_hotspot_guide.py    # Build hotspot guides
│   └── utils/                  # Shared utilities
│       ├── region_config.py    # Region configuration management
│       ├── valley_detection.py # Valley detection algorithm
│       ├── timing_helpers.py   # Timing calculation helpers
│       ├── constants.py        # Migration classification constants
│       ├── validation.py       # Data validation utilities
│       ├── species_codes.py    # Species code generation
│       └── tests/              # Unit tests
├── regions/                     # Region-specific data
│   └── [region_name]/          # e.g., washtenaw/
│       ├── ebird_*.txt         # Input: eBird barchart file
│       ├── [region]_species_data.json  # Output: Final species JSON
│       ├── intermediate/       # Processing intermediate files
│       └── hotspots/
│           ├── [region]_hotspots.json  # Base eBird hotspot data
│           ├── content/        # Manual hotspot content (Markdown)
│           │   ├── _template.md
│           │   └── L123456.md  # Per-hotspot content files
│           └── raw/            # Timestamped API responses
├── .github/
│   └── workflows/
│       └── deploy-gh-pages.yml # GitHub Actions auto-deployment
├── .env.example                # Template for eBird API key
├── requirements.txt            # Python dependencies
└── README.md
```

## Web Application

### Pages

**This Week** ([washtenaw/index.html](washtenaw/index.html))
- Shows species arriving, at peak, or departing in the current week
- Navigate to previous/next weeks or jump back to current week
- Click any species to view detailed information

**Browse All Species** ([washtenaw/browse.html](washtenaw/browse.html))
- Search species by name
- Filter by migration category (resident, single-season, two-passage migrant, vagrant)
- View all species with their frequency bars

**Species Detail** ([washtenaw/species.html](washtenaw/species.html))
- Annual frequency chart showing detection probability throughout the year
- Migration timing information (arrival, peak, departure dates)
- Top hotspots for finding this species
- Category badge and species code

**Hotspots Directory** ([washtenaw/hotspots.html](washtenaw/hotspots.html))
- Search and sort hotspots by name or species count
- View total species recorded at each location
- Link to eBird location pages

**Hotspot Detail** ([washtenaw/hotspot-detail.html](washtenaw/hotspot-detail.html))
- Practical info: parking, hours, fees, facilities
- Habitat descriptions and birding tips
- Common species list (top 15 most frequently detected)
- Notable species (rare or specialty birds for the location)

### Design System

The app uses a "Field Journal" aesthetic - warm, naturalist-inspired design with a cozy, professional feel. Defined in [washtenaw/css/styles.css](washtenaw/css/styles.css).

**Typography:**
- **Headings**: Bitter (warm slab-serif)
- **Body**: DM Sans (friendly, modern sans-serif)

**Color Palette:**
- **Header/footer**: `#2D3E36` (forest green) with terracotta/ochre accent stripe
- **Main background**: `#FAF6F1` (warm cream)
- **Cards**: White with soft shadows and colored left borders
- **Primary accent**: `#C17F59` (terracotta)
- **Secondary accent**: `#C9A55C` (ochre)
- **Category badges**: Resident (forest), Single-season (ochre), Two-passage (moss), Vagrant (terracotta)
- **Status indicators**: Arriving (green), At peak (ochre), Departing (rust)

### Adding a New County

To add a new county, create a new county directory (e.g., `genesee/`) modeled after `washtenaw/`. Then:
1. Run the data pipeline for the new region: `python3 scripts/run_pipeline.py genesee`
2. Copy the output data files into `genesee/data/`
3. Update all HTML files in `genesee/` to reference the correct county name
4. Add the county card to the root `index.html` landing page
5. Update `.github/workflows/deploy-gh-pages.yml` to include `genesee/**` in the deploy step

To rename the county in an existing app directory, change the `<p>Washtenaw County, Michigan</p>` text in the header and footer of each HTML file.

## Data Processing Pipeline

The pipeline processes raw eBird barchart data into structured JSON for the web application.

### Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up eBird API key (for hotspot fetching)
cp .env.example .env
# Edit .env and add: EBIRD_API_KEY=your_key_here
```

Get a free eBird API key at: https://ebird.org/api/keygen

### Species Data Pipeline

```bash
# Run complete pipeline for a region
python3 scripts/run_pipeline.py [region_name]

# Or run steps individually:
python3 scripts/parse_ebird_data.py [region_name]           # Parse eBird file
python3 scripts/classify_migration_patterns.py [region_name] # Classify species
python3 scripts/calculate_arrival_departure.py [region_name] # Calculate timing
python3 scripts/merge_to_json.py [region_name]              # Generate final JSON
```

### Hotspot Data Pipeline

```bash
# Fetch hotspot data from eBird API
python3 scripts/fetch_hotspots.py

# Create content file for a new hotspot
python3 scripts/new_hotspot_content.py L320822

# Build enriched hotspot JSON (merges content with base data)
python3 scripts/build_enriched_hotspots.py
```

### Pipeline Steps

**1. parse_ebird_data.py**
- Parses eBird barchart `.txt` file
- Filters out unidentified species (sp.) and hybrids
- Outputs JSON and CSV formats

**2. classify_migration_patterns.py**
- Uses valley detection to classify species
- Categories: Resident, Single-season, Two-passage Migrant, Vagrant
- Valley = 4+ consecutive weeks below 15% of peak frequency

**3. calculate_arrival_departure.py**
- Calculates arrival, peak, and departure timing
- Converts week numbers to date ranges
- Threshold: 10% of peak frequency or 0.1% absolute

**4. merge_to_json.py**
- Merges all data into final JSON
- Generates unique 6-letter species codes
- Structures timing by category

### Output Files

**Final outputs:**
- `regions/[region]/[region]_species_data.json` - Species data for web app
- `regions/[region]/hotspots/[region]_hotspots.json` - Hotspot data

**Intermediate files** (in `regions/[region]/intermediate/`):
- `[region]_ebird_data.json` - Parsed frequency data
- `[region]_migration_pattern_classifications.csv` - Species classifications
- `[region]_migration_timing.csv` - Arrival/departure timing

## Hotspot Content Authoring

Hotspot content files are Markdown with YAML frontmatter. See `regions/washtenaw/hotspots/content/_template.md` for the full template.

```markdown
---
parking: "Free lot off Geddes Ave"
hours: "Dawn to dusk"
fee: "Free"
features:
  - Restrooms at Nature Center
  - Paved and unpaved trails
habitats:
  - Mature oak-hickory forest
  - River edge
tips:
  - Check the river overlook for waterfowl
  - Warblers peak in mid-May
links:
  - label: "Official Website"
    url: "https://example.org"
lastUpdated: "2025-01-15"
---

Additional notes about the hotspot can go here as free-form Markdown.
```

## Requirements

- **Web Application**: Modern web browser (Chrome, Firefox, Safari, Edge)
- **Data Processing**: Python 3.6+
- **Python packages**: `python-dotenv`, `requests`, `python-frontmatter`

## Deployment

### GitHub Pages (Automated)

The repository is configured for automatic deployment:

1. Push changes to `main` branch (touching `index.html` or `washtenaw/**`)
2. GitHub Actions deploys to `gh-pages` branch:
   - `index.html` → site root (`/`)
   - `washtenaw/` → `/washtenaw/` subdirectory
3. Site updates at `https://[username].github.io/[repo-name]/`

**Setup** (one-time):
1. Repository Settings → Pages
2. Source: Deploy from branch `gh-pages`, folder `/ (root)`

### Other Hosting

**Netlify / Vercel / Cloudflare Pages:**
- Publish directory: repo root
- No build command needed
- Both `index.html` and `washtenaw/` will be served correctly

**Traditional hosting:**
- Upload `index.html` and the `washtenaw/` directory to web root
- Ensure all `washtenaw/data/*.json` files are included

## License

Free to use and modify for your birding projects.
