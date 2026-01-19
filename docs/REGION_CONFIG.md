# Region Configuration System

The BirdFinder pipeline includes a flexible configuration system for managing region-specific settings. This allows you to customize thresholds, file paths, display settings, and seasonal definitions for each region without modifying code.

## Table of Contents

- [Quick Start](#quick-start)
- [Configuration File Locations](#configuration-file-locations)
- [Configuration Schema](#configuration-schema)
- [Usage Examples](#usage-examples)
- [Advanced Configuration](#advanced-configuration)
- [API Reference](#api-reference)

---

## Quick Start

### Creating a New Region

1. **Create region directory:**
   ```bash
   mkdir -p regions/my_region
   ```

2. **Create configuration file:**
   ```bash
   cp config/region_template.json regions/my_region/config.json
   ```

3. **Edit the configuration:**
   ```json
   {
     "region_id": "my_region",
     "display_name": "My Region Name",
     "description": "Bird data for My Region",
     "ebird_region_code": "US-XX-123",
     "timezone": "America/New_York"
   }
   ```

4. **Add eBird data file:**
   ```bash
   # Place your eBird barchart .txt file in the region directory
   cp ~/Downloads/ebird_*.txt regions/my_region/
   ```

5. **Run the pipeline:**
   ```bash
   python3 scripts/run_pipeline.py my_region
   ```

---

## Configuration File Locations

The configuration system supports three approaches:

### 1. Region-Specific Config (Recommended)

**Location:** `regions/[region_id]/config.json`

**Use when:** You want to keep configuration with the data for a single region.

```
regions/
└── washtenaw/
    ├── config.json          ← Region config here
    ├── ebird_*.txt
    └── washtenaw_species_data.json
```

### 2. Global Multi-Region Config

**Location:** `config/regions.json`

**Use when:** Managing multiple regions in a single file.

```json
{
  "regions": {
    "washtenaw": {
      "display_name": "Washtenaw County, Michigan",
      "ebird_region_code": "US-MI-161",
      ...
    },
    "oakland": {
      "display_name": "Oakland County, Michigan",
      "ebird_region_code": "US-MI-125",
      ...
    }
  }
}
```

### 3. Default Config (Fallback)

**No config file needed.**

If no configuration file is found, the system creates a minimal default config:
- `region_id`: Directory name
- `display_name`: Titlecased directory name (e.g., `"washtenaw"` → `"Washtenaw"`)
- All other settings use global defaults from `scripts/utils/constants.py`

---

## Configuration Schema

### Required Fields

```json
{
  "region_id": "my_region",        // Must match directory name (alphanumeric, -, _)
  "display_name": "My Region Name" // Human-readable name
}
```

### Optional Fields

```json
{
  "description": "Detailed description of this region",
  "ebird_region_code": "US-XX-123",   // eBird API region code
  "timezone": "America/New_York",     // IANA timezone identifier

  "paths": {
    "input_pattern": "ebird_*.txt",           // Glob pattern for input file
    "output_file": "{region_id}_species_data.json",
    "intermediate_dir": "intermediate",
    "hotspots_dir": "hotspots"
  },

  "thresholds": {
    // Override algorithm thresholds (see below)
  },

  "seasonal_weeks": {
    // Override seasonal week ranges (see below)
  },

  "display_settings": {
    "copyright_year": 2025,
    "theme_name": "Kirtland's Warbler",
    "about_text": "BirdFinder helps you discover birds..."
  }
}
```

---

## Usage Examples

### Example 1: Basic Region Configuration

**File:** `regions/wayne/config.json`

```json
{
  "region_id": "wayne",
  "display_name": "Wayne County, Michigan",
  "description": "Detroit metropolitan area bird data",
  "ebird_region_code": "US-MI-163",
  "timezone": "America/Detroit"
}
```

### Example 2: Custom Algorithm Thresholds

For regions with different data characteristics, you can override classification thresholds:

**File:** `regions/upper_peninsula/config.json`

```json
{
  "region_id": "upper_peninsula",
  "display_name": "Upper Peninsula, Michigan",
  "ebird_region_code": "US-MI-000",
  "timezone": "America/Detroit",

  "thresholds": {
    "VALLEY_THRESHOLD_PEAK_RATIO": 0.20,      // More strict valley detection
    "MIN_WEEKS_PRESENCE": 8,                  // Lower threshold for vagrant
    "RESIDENT_MIN_MAX_RATIO_THRESHOLD": 0.25  // Stricter resident classification
  }
}
```

### Example 3: Custom Seasonal Definitions

For regions at different latitudes, adjust seasonal week ranges:

**File:** `regions/florida/config.json`

```json
{
  "region_id": "florida",
  "display_name": "Central Florida",
  "ebird_region_code": "US-FL-095",
  "timezone": "America/New_York",

  "seasonal_weeks": {
    "winter": {
      "start": 40,  // December
      "end": 11     // March (longer winter range)
    },
    "summer": {
      "start": 12,  // April (earlier summer)
      "end": 35     // Late August
    }
  }
}
```

### Example 4: Custom File Paths

**File:** `regions/custom_data/config.json`

```json
{
  "region_id": "custom_data",
  "display_name": "Custom Data Region",

  "paths": {
    "input_pattern": "bird_observations_*.txt",
    "output_file": "{region_id}_final_data.json",
    "intermediate_dir": "processing",
    "hotspots_dir": "sites"
  }
}
```

---

## Advanced Configuration

### Available Threshold Overrides

All thresholds from `scripts/utils/constants.py` can be overridden per region:

**Valley Detection:**
- `VALLEY_MIN_LENGTH_WEEKS` (default: 4)
- `VALLEY_THRESHOLD_PEAK_RATIO` (default: 0.15)
- `VALLEY_THRESHOLD_ABSOLUTE` (default: 0.005)

**Arrival/Departure Timing:**
- `ARRIVAL_THRESHOLD_PEAK_RATIO` (default: 0.10)
- `ARRIVAL_THRESHOLD_ABSOLUTE` (default: 0.001)
- `MIN_PEAK_FREQUENCY` (default: 0.005)

**Species Classification:**
- `MIN_WEEKS_PRESENCE` (default: 10)
- `RESIDENT_MIN_MAX_RATIO_THRESHOLD` (default: 0.20)
- `OVERWINTERING_MIN_WEEKS` (default: 8)
- `OVERWINTERING_FREQUENCY_THRESHOLD` (default: 0.05)

**Example:**
```json
{
  "thresholds": {
    "VALLEY_THRESHOLD_PEAK_RATIO": 0.12,
    "MIN_WEEKS_PRESENCE": 12,
    "ARRIVAL_THRESHOLD_PEAK_RATIO": 0.08
  }
}
```

### Seasonal Week Ranges

Override seasonal definitions for different latitudes:

```json
{
  "seasonal_weeks": {
    "winter": {"start": 44, "end": 7},    // Late Nov - Late Feb
    "summer": {"start": 16, "end": 35},   // Late Apr - Late Aug
    "spring": {"start": 8, "end": 19},    // Early Mar - Mid May
    "fall": {"start": 28, "end": 43}      // Mid Jul - Mid Nov
  }
}
```

**Week numbering:** 0-47 (4 weeks per month, starting in January)
- Weeks 0-3: January
- Weeks 4-7: February
- ...
- Weeks 44-47: December

### Display Settings

Configure UI and frontend display options:

```json
{
  "display_settings": {
    "copyright_year": 2025,
    "theme_name": "Kirtland's Warbler",
    "about_text": "Custom description for your region...",
    "contact_email": "birds@example.com",
    "website_url": "https://example.com/birds"
  }
}
```

---

## API Reference

### Python API

#### Loading Configuration

```python
from utils.region_config import load_region_config

# Load configuration for a region
config = load_region_config('washtenaw')

# Access config properties
print(config.display_name)  # "Washtenaw County, Michigan"
print(config.ebird_region_code)  # "US-MI-161"
```

#### Using Configuration in Scripts

```python
from utils.region_config import load_region_config

config = load_region_config(region_name)

# Get thresholds with fallback to defaults
valley_threshold = config.get_threshold('VALLEY_THRESHOLD_PEAK_RATIO', 0.15)

# Get paths
input_pattern = config.get_path('input_pattern', 'ebird_*.txt')

# Get seasonal weeks
winter_weeks = config.get_seasonal_weeks('winter')
if winter_weeks:
    start = winter_weeks['start']
    end = winter_weeks['end']

# Get display settings
copyright_year = config.get_display_setting('copyright_year', 2025)
```

#### Listing Available Regions

```python
from utils.region_config import list_available_regions

regions = list_available_regions()
print(f"Available regions: {', '.join(regions)}")
```

#### Saving Configuration

```python
from utils.region_config import RegionConfig, save_region_config
from pathlib import Path

config = RegionConfig(
    region_id="new_region",
    display_name="New Region Name",
    ebird_region_code="US-XX-999"
)

config_path = Path("regions/new_region/config.json")
save_region_config(config, config_path)
```

#### Error Handling

```python
from utils.region_config import load_region_config, ConfigError

try:
    config = load_region_config('my_region')
except ConfigError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
```

### Configuration Validation

The system automatically validates:
- ✅ Required fields present (`region_id`, `display_name`)
- ✅ Region ID format (alphanumeric, hyphens, underscores only)
- ✅ No path traversal in region IDs (e.g., `../etc` rejected)
- ✅ Threshold values are numeric and non-negative
- ✅ Seasonal week indices in valid range [0, 47]
- ✅ JSON syntax is valid
- ✅ Region ID matches directory name (for region-specific configs)

---

## Migration Guide

### Migrating Existing Regions

If you have existing regions without configuration files:

1. **No action required!** The system will use default configuration.

2. **Optional: Create config for better documentation:**
   ```bash
   cd regions/your_region
   cp ../../config/region_template.json config.json
   # Edit config.json with your region's details
   ```

3. **Verify configuration loads correctly:**
   ```bash
   python3 -c "from utils.region_config import load_region_config; \
               c = load_region_config('your_region'); \
               print(f'Loaded: {c.display_name}')"
   ```

### Adding New Regions

```bash
# 1. Create directory
mkdir -p regions/new_region

# 2. Copy template
cp config/region_template.json regions/new_region/config.json

# 3. Edit configuration
nano regions/new_region/config.json

# 4. Add eBird data
cp ~/Downloads/ebird_*.txt regions/new_region/

# 5. Run pipeline
python3 scripts/run_pipeline.py new_region
```

---

## Troubleshooting

### "Configuration Error: Region not found"

**Problem:** Config file references wrong region ID.

**Solution:** Ensure `region_id` in config.json matches directory name:
```json
{
  "region_id": "washtenaw",  // Must match: regions/washtenaw/
  "display_name": "Washtenaw County, Michigan"
}
```

### "Invalid JSON in config file"

**Problem:** JSON syntax error.

**Solution:** Validate JSON syntax:
```bash
python3 -m json.tool regions/your_region/config.json
```

### Pipeline uses wrong thresholds

**Problem:** Threshold overrides not applied.

**Solution:** Check threshold names match exactly those in `scripts/utils/constants.py`:
```json
{
  "thresholds": {
    "VALLEY_THRESHOLD_PEAK_RATIO": 0.20  // ✓ Correct
    // NOT: valley_threshold or ValleyThreshold
  }
}
```

### Config changes not reflected

**Problem:** Cached or old config being used.

**Solution:** The config is loaded fresh each pipeline run. No caching occurs.

---

## Testing

Run the configuration system tests:

```bash
cd scripts/utils
python3 test_region_config.py
```

Expected output:
```
======================================================================
Region Configuration Tests - Summary
======================================================================
Tests run: 20
Successes: 20
Failures: 0
Errors: 0

✓ ALL TESTS PASSED
```

---

## See Also

- [scripts/utils/constants.py](../scripts/utils/constants.py) - Global algorithm constants
- [scripts/utils/region_config.py](../scripts/utils/region_config.py) - Configuration implementation
- [config/region_template.json](../config/region_template.json) - Template for new regions
- [REFACTORING_LOG.md](../REFACTORING_LOG.md) - Development history
