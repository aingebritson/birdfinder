# eBird Migration Data Processing Pipeline

Process eBird regional barchart data to generate species migration timing and classification data for websites.

## Quick Start

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

The final JSON file will be in `regions/[region_name]/[region_name]_species_data.json`

## Example

```bash
# Create region directory
mkdir -p regions/washtenaw

# Move eBird file to region directory
mv ebird_US-MI-161__1900_2025_1_12_barchart.txt regions/washtenaw/

# Run the pipeline
python3 scripts/run_pipeline.py washtenaw
```

## Pipeline Steps

The pipeline runs four scripts in sequence:

### 1. `parse_ebird_data.py`
- Parses the eBird barchart `.txt` file
- Filters out unidentified species (sp.) and hybrids (/)
- Outputs: JSON, wide CSV, and long CSV formats

### 2. `classify_migration_patterns.py`
- Classifies each species into migration categories:
  - **Resident**: Year-round presence (min/max ratio ≥ 0.15)
  - **Single-season**: One arrival and departure
  - **Two-passage migrant**: Distinct spring and fall passages
  - **Vagrant**: Rare visitors (<10 weeks presence)
- Detects winter residents (bimodal pattern with summer low point)
- Outputs: Classification CSV with metrics and edge case flags

### 3. `calculate_arrival_departure.py`
- Calculates arrival, peak, and departure weeks for each species
- Uses threshold logic: 25% of peak OR 0.1% absolute (whichever higher)
- Converts week numbers to readable date ranges
- Outputs: Migration timing CSV

### 4. `merge_to_json.py`
- Merges all data into a single JSON file
- Generates 6-letter species codes
- Structures timing data by category
- Outputs: Final species data JSON for web use

## Individual Script Usage

You can also run scripts individually for debugging or customization:

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

## Directory Structure

```
.
├── scripts/                         # Processing scripts
│   ├── run_pipeline.py             # Run all steps in sequence
│   ├── parse_ebird_data.py         # Step 1: Parse eBird file
│   ├── classify_migration_patterns.py  # Step 2: Classify species
│   ├── calculate_arrival_departure.py  # Step 3: Calculate timing
│   └── merge_to_json.py            # Step 4: Merge to JSON
├── regions/                         # Region-specific data
│   └── [region_name]/              # e.g., washtenaw/
│       ├── ebird_*.txt             # Input: eBird barchart file
│       ├── [region]_species_data.json  # Output: Final JSON
│       └── intermediate/            # Intermediate files
│           ├── [region]_ebird_data.json
│           ├── [region]_ebird_data_wide.csv
│           ├── [region]_ebird_data_long.csv
│           ├── [region]_migration_pattern_classifications.csv
│           └── [region]_migration_timing.csv
└── README.md                        # This file

```

## Output Files

**Final output:**
- `regions/[region]/[region]_species_data.json` - Complete species data for website

**Intermediate files (in `regions/[region]/intermediate/`):**
- `[region]_ebird_data.json` - Parsed frequency data
- `[region]_ebird_data_wide.csv` - Wide format frequencies
- `[region]_ebird_data_long.csv` - Long format frequencies
- `[region]_migration_pattern_classifications.csv` - Classifications with metrics
- `[region]_migration_timing.csv` - Arrival/departure timing

## JSON Structure

```json
{
  "name": "Yellow-bellied Flycatcher",
  "code": "yelfly",
  "category": "two-passage-migrant",
  "flags": ["classic_bimodal"],
  "timing": {
    "spring_arrival": "late May",
    "spring_peak": "late May",
    "spring_departure": "early June",
    "fall_arrival": "late August",
    "fall_peak": "early September",
    "fall_departure": "late September"
  },
  "weekly_frequency": [0, 0, 0.001, ...]
}
```

## Customization

### Adjust Classification Thresholds

Edit `classify_migration_patterns.py`:
- Line 99: Vagrant threshold (weeks with presence < 10)
- Line 102: Resident threshold (min/max ratio > 0.15)
- Line 110: Seasonal threshold (weeks above 10% > 16)

### Adjust Timing Thresholds

Edit `calculate_arrival_departure.py`:
- Line 48-50: Arrival/departure threshold logic

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Example: Washtenaw County, Michigan

The included example processes data for Washtenaw County (US-MI-161):
- **Input**: `regions/washtenaw/ebird_US-MI-161__1900_2025_1_12_barchart.txt`
- **Output**: `regions/washtenaw/washtenaw_species_data.json`
- **340 species** after filtering
  - 29 Residents
  - 142 Single-season
  - 85 Two-passage migrants
  - 84 Vagrants

To run:
```bash
python3 scripts/run_pipeline.py washtenaw
```

## License

Scripts are free to use and modify for your birding projects.
