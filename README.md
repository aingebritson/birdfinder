# BirdFinder

A bird phenology web application that displays migration timing and detection probabilities for species in your region. Built with eBird data.

**Live Example:** Washtenaw County, Michigan (340 species)

## Features

- **This Week View**: See which species are arriving, at peak, or departing this week
- **Browse All Species**: Search and filter by migration category
- **Species Detail Pages**: View annual frequency charts and detailed migration timing
- **Interactive Week Navigation**: Browse any week of the year
- **Responsive Design**: Works on desktop and mobile

## Quick Start

### View the Web Application

1. Copy your processed species data to the web app:
```bash
cp regions/[region_name]/[region_name]_species_data.json birdfinder/data/species_data.json
```

2. Open [index.html](index.html) in a web browser, or serve with a local server:
```bash
python3 -m http.server 8000
# Visit http://localhost:8000
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
cp regions/[region_name]/[region_name]_species_data.json birdfinder/data/species_data.json
```

## Project Structure

```
.
├── index.html                   # This Week view (main page)
├── browse.html                  # Browse All Species view
├── species.html                 # Species Detail view
├── birdfinder/                  # Web application assets
│   ├── css/
│   │   └── styles.css          # Custom styles (Kirtland's Warbler palette)
│   ├── js/
│   │   ├── data.js             # Data loading and search
│   │   ├── this-week.js        # This Week page logic
│   │   ├── browse.js           # Browse page logic
│   │   ├── species-detail.js   # Species detail page logic
│   │   └── week-calculator.js  # Date/week conversion utilities
│   └── data/
│       └── species_data.json   # Active species data (copy from regions/)
├── scripts/                     # Data processing pipeline
│   ├── run_pipeline.py         # Run all steps in sequence
│   ├── parse_ebird_data.py     # Step 1: Parse eBird file
│   ├── classify_migration_patterns.py  # Step 2: Classify species
│   ├── calculate_arrival_departure.py  # Step 3: Calculate timing
│   └── merge_to_json.py        # Step 4: Merge to JSON
└── regions/                     # Region-specific data
    └── [region_name]/          # e.g., washtenaw/
        ├── ebird_*.txt         # Input: eBird barchart file
        ├── [region]_species_data.json  # Output: Final JSON
        └── intermediate/        # Intermediate processing files
```

## Web Application

### Pages

**This Week ([index.html](index.html))**
- Shows species arriving, at peak, or departing in the current week
- Navigate to previous/next weeks or jump back to current week
- Click any species to view detailed information

**Browse All Species ([browse.html](browse.html))**
- Search species by name
- Filter by migration category (resident, single-season, two-passage migrant, vagrant)
- View all species with their frequency bars

**Species Detail ([species.html](species.html))**
- Annual frequency chart showing detection probability throughout the year
- Migration timing information (arrival, peak, departure dates)
- Category badge and species code

### Customization

**Color Palette**

The app uses a Kirtland's Warbler-inspired color scheme defined in [birdfinder/css/styles.css](birdfinder/css/styles.css):
- Primary (yellow): `#E8B831`
- Secondary (blue-gray): `#4A6670`
- Teal accent: `#2A9D8F`
- Rust accent: `#C17F59`

**Region Name**

Update the region name in HTML files:
- [index.html](index.html) line 14: `<p>Washtenaw County, Michigan</p>`
- [browse.html](browse.html) line 14: `<p>Washtenaw County, Michigan</p>`
- [species.html](species.html) line 19: `<p>Washtenaw County, Michigan</p>`

## Data Processing Pipeline

The pipeline processes raw eBird barchart data into a structured JSON format for the web application.

### Pipeline Steps

#### 1. `parse_ebird_data.py`
- Parses the eBird barchart `.txt` file
- Filters out unidentified species (sp.) and hybrids (/)
- Outputs: JSON, wide CSV, and long CSV formats

#### 2. `classify_migration_patterns.py`

Uses **valley detection** to classify species into migration categories. A valley is defined as 4+ consecutive weeks below 15% of peak frequency (or 0.5% absolute, whichever is higher).

**Categories:**
- **Resident**: Species with 0 valleys (never absent for 4+ weeks)
  - Flags species with seasonal variation (min/max ratio < 0.5)
- **Vagrant**: Rare visitors with <10 weeks presence OR peak frequency <0.5%
- **Two-passage Migrant**: Species with exactly 2 valleys (one in summer, one in winter)
  - Valleys must be ≥12 weeks apart
  - One valley in winter weeks (40-47, 0-11), one in summer weeks (16-35)
  - Flags: `classic_bimodal` or `separated_valleys`
- **Single-season**: Species with 1 valley
  - Valley in winter → summer migrant (pattern: "summer")
  - Valley in summer → overwintering bird (pattern: "winter", flag: `overwintering`)
- **Vagrant (irregular pattern)**: Species with 3+ valleys or valleys that don't fit patterns

**Outputs:** Classification CSV with category, pattern type, valley data, and diagnostic flags

#### 3. `calculate_arrival_departure.py`

Calculates precise arrival, peak, and departure timing for each migration category.

**Threshold Logic:**
- Arrival/departure detection: **10% of peak frequency OR 0.1% absolute** (whichever higher)
- Searches for timing between valleys based on category

**Date Conversion:**
Converts week numbers (0-47) to exact date ranges using eBird's week structure:
- Week 1: Days 1-7
- Week 2: Days 8-14
- Week 3: Days 15-21
- Week 4: Days 22-end of month (28, 30, or 31)

**Timing by Category:**
- **Resident**: Returns `"status": "year-round"` (no timing needed)
- **Vagrant/Irregular**: First appearance, peak, and last appearance
- **Two-passage Migrant**: Spring arrival/peak/departure + Fall arrival/peak/departure
- **Single-season**: Arrival, peak, and departure for the presence period

**Outputs:** Migration timing CSV with date ranges (e.g., "May 15-21")

#### 4. `merge_to_json.py`
- Merges all data into a single JSON file
- Generates unique 6-letter species codes (with collision detection)
- Structures timing data by category
- Outputs: Final species data JSON for web use

### Individual Script Usage

Run scripts individually for debugging or customization:

```bash
# Step 1: Parse raw eBird data
python3 scripts/parse_ebird_data.py [region_name]

# Step 2: Classify migration patterns
python3 scripts/classify_migration_patterns.py [region_name]

# Step 3: Calculate timing
python3 scripts/calculate_arrival_departure.py [region_name]

# Step 4: Merge to final JSON
python3 scripts/merge_to_json.py [region_name]
```

### Output Files

**Final output:**
- `regions/[region]/[region]_species_data.json` - Complete species data for website

**Intermediate files (in `regions/[region]/intermediate/`):**
- `[region]_ebird_data.json` - Parsed frequency data
- `[region]_ebird_data_wide.csv` - Wide format frequencies
- `[region]_ebird_data_long.csv` - Long format frequencies
- `[region]_migration_pattern_classifications.csv` - Classifications with metrics
- `[region]_migration_timing.csv` - Arrival/departure timing

### JSON Structure

```json
{
  "name": "Yellow-bellied Flycatcher",
  "code": "yelfly",
  "category": "two-passage-migrant",
  "flags": ["classic_bimodal"],
  "timing": {
    "spring_arrival": "May 15-21",
    "spring_peak": "May 22-31",
    "spring_departure": "June 1-7",
    "fall_arrival": "August 22-31",
    "fall_peak": "September 1-7",
    "fall_departure": "September 22-30"
  },
  "weekly_frequency": [0, 0, 0.001, ...]
}
```

**Timing format notes:**
- All timing values are exact date ranges (e.g., "May 15-21", "June 1-7")
- Date ranges follow eBird's 48-week system (4 weeks per month, indexed 0-47)
- Each week has specific date boundaries that align with eBird data
- For year-round residents: `"status": "year-round"`
- For irregular visitors: `"status": "irregular"`

## Configuration & Customization

### Adjust Classification Thresholds

Edit [scripts/classify_migration_patterns.py](scripts/classify_migration_patterns.py):

**Valley Detection** (function `detect_valleys`):
- Valley threshold: `max(peak_freq * 0.15, 0.005)` - weeks below 15% of peak OR 0.5% absolute
- Minimum valley length: 4 consecutive weeks

**Category Thresholds** (function `classify_species`):
- Vagrant: `weeks_with_presence < 10` OR `peak_frequency < 0.005` (0.5%)
- Resident seasonal variation flag: `min_max_ratio < 0.5`
- Two-passage valley separation: `separation >= 12` weeks
- Overwintering detection: `max_consecutive_low >= 8` weeks below 0.1%

**Season Definitions** (function `classify_valley_timing`):
- Winter weeks: 40-47, 0-11 (Nov-Mar)
- Summer weeks: 16-35 (late Apr-early Sep)
- Season threshold: 40% of valley must be in season

### Adjust Timing Thresholds

Edit [scripts/calculate_arrival_departure.py](scripts/calculate_arrival_departure.py):

**Arrival/Departure Detection:**
- Threshold: `max(peak_freq * 0.10, 0.001)` - 10% of peak OR 0.1% absolute
- Applied in functions: `calculate_timing_two_passage`, `calculate_timing_single_season_summer`, `calculate_timing_single_season_winter`

**Irregular Species:**
- First/last appearance threshold: `0.001` (0.1%)

## Requirements

- **Web Application**: Modern web browser (Chrome, Firefox, Safari, Edge)
- **Data Processing**: Python 3.6+ (no external dependencies)

## Example: Washtenaw County, Michigan

The included example processes data for Washtenaw County (US-MI-161):
- **Input**: `regions/washtenaw/ebird_US-MI-161__1900_2025_1_12_barchart.txt`
- **Output**: `regions/washtenaw/washtenaw_species_data.json`
- **340 species** after filtering
  - 37 Residents
  - 135 Single-season
  - 84 Two-passage migrants
  - 84 Vagrants

To process and view:
```bash
# Process the data
python3 scripts/run_pipeline.py washtenaw

# Copy to web app
cp regions/washtenaw/washtenaw_species_data.json birdfinder/data/species_data.json

# Open index.html in browser
```

## Deployment

To deploy the web application:

1. Upload all HTML files and the `birdfinder/` directory to your web server
2. Ensure `birdfinder/data/species_data.json` contains your processed region data
3. No server-side processing required - works as static files

**GitHub Pages**: Can be deployed directly to GitHub Pages (all static files)

**Custom Domain**: Works with any static hosting (Netlify, Vercel, Cloudflare Pages, etc.)

## License

Free to use and modify for your birding projects.
