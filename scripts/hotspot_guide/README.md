# eBird Hotspot Guide Generator

Analyzes eBird Basic Dataset downloads to identify the best hotspots for finding each bird species in a region. For each species, ranks hotspots by **occurrence rate** (the percentage of complete checklists where the species was detected).

## Quick Start

1. Download an eBird Basic Dataset from [eBird](https://ebird.org/data/download)
2. Copy this `ebird_hotspot_guide/` folder into the download directory
3. Run:

```bash
cd ebird_hotspot_guide
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Output files will be created in `output/`.

## What It Does

The pipeline processes eBird data to answer: **"Where should I go to find [species]?"**

For example, if Blue Grosbeak is rare in your county but reliably shows up at one particular park, this tool will identify that park as the top hotspot for Blue Grosbeak.

### Key Features

- **Occurrence rate ranking**: Hotspots are ranked by the percentage of complete checklists where a species was found, not raw observation counts. This normalizes for heavily-birded locations.
- **Seasonal breakdown**: Shows occurrence rates by season (spring, summer, fall, winter) and month
- **Confidence levels**: Hotspots are tagged as high/medium/low confidence based on checklist count
- **Portable**: Works with any eBird Basic Dataset download—automatically detects data files

## Output Files

```
output/
├── species/                    # One JSON file per species
│   ├── american_robin.json
│   ├── blue_grosbeak.json
│   └── ...
├── hotspots/                   # One JSON file per hotspot
│   ├── L320822_nichols_arboretum.json
│   └── ...
├── index/
│   ├── species_index.json      # All species with top hotspot
│   ├── hotspot_index.json      # All hotspots sorted by checklist count
│   └── top_hotspots_by_species.json  # Top 5 hotspots per species
└── metadata.json               # Processing stats and methodology
```

### Example: Species File

`output/species/blue_grosbeak.json`:

```json
{
  "species": {
    "common_name": "Blue Grosbeak",
    "scientific_name": "Passerina caerulea"
  },
  "summary": {
    "total_hotspots_detected": 5,
    "total_detections": 435,
    "highest_occurrence_rate": 0.3055
  },
  "hotspots": [
    {
      "rank": 1,
      "locality_id": "L20533360",
      "name": "Sharon Mills Co. Park--north",
      "coordinates": { "latitude": 42.18, "longitude": -84.09 },
      "occurrence": {
        "rate": 0.3055,
        "detection_count": 238,
        "total_checklists": 779,
        "confidence": "high"
      },
      "seasonal": {
        "spring": 0.31,
        "summer": 0.36,
        "fall": 0.27,
        "winter": 0.0
      },
      "monthly": {
        "5": 0.41,
        "6": 0.17,
        "7": 0.47,
        "8": 0.38
      }
    }
  ]
}
```

## Methodology

### Occurrence Rate

```
Occurrence Rate = (checklists where species detected) / (total complete checklists at hotspot)
```

This metric answers: "If I bird this hotspot, what's my chance of finding this species?"

### Data Filters

Only high-quality data is used:

- **Hotspots only** (`LOCALITY TYPE = 'H'`): Excludes personal locations for consistency
- **Complete checklists only** (`ALL SPECIES REPORTED = 1`): Ensures observers reported everything they saw, not just highlights
- **Species-level taxa only** (`CATEGORY = 'species'`): Excludes hybrids, slashes, and spuhs

### Confidence Thresholds

- **High**: 100+ complete checklists at hotspot
- **Medium**: 30-99 complete checklists
- **Low**: 10-29 complete checklists
- Hotspots with fewer than 10 checklists are excluded

## Configuration

Edit `config.py` to adjust:

```python
MIN_CHECKLISTS_THRESHOLD = 10   # Minimum checklists to include a hotspot
HIGH_CONFIDENCE_MIN = 100       # Threshold for "high" confidence
MEDIUM_CONFIDENCE_MIN = 30      # Threshold for "medium" confidence

SEASONS = {
    'spring': [3, 4, 5],
    'summer': [6, 7],
    'fall': [8, 9, 10, 11],
    'winter': [12, 1, 2]
}
```

## Validation

Run the validation script to check output integrity:

```bash
python validate.py
```

This verifies:
- All occurrence rates are between 0 and 1
- JSON structure is valid
- Common species appear at expected hotspot counts

## Requirements

- Python 3.10+
- pandas
- tqdm

## File Structure

```
ebird_hotspot_guide/
├── main.py                     # Main pipeline script
├── config.py                   # Configuration and file detection
├── validate.py                 # Output validation
├── requirements.txt
├── processors/
│   ├── checklist_counter.py    # Counts checklists per hotspot
│   ├── species_detector.py     # Counts species detections
│   └── occurrence_calculator.py # Calculates occurrence rates
└── output/
    └── json_writer.py          # Generates JSON output files
```

## Performance

Processing time depends on dataset size:

| Dataset Size | Approximate Time |
|--------------|------------------|
| 100MB        | ~1 minute        |
| 500MB        | ~3 minutes       |
| 1.5GB        | ~8 minutes       |

Memory usage peaks at ~500MB regardless of file size (chunked processing).

## License

This tool is for use with eBird data, which is subject to [eBird's Terms of Use](https://www.birds.cornell.edu/home/ebird-data-access-terms-of-use/). eBird data is provided by the Cornell Lab of Ornithology.
