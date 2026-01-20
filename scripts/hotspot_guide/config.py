"""Configuration for the eBird hotspot guide pipeline."""

from pathlib import Path
from typing import Optional


def find_ebird_files(data_dir: Path) -> tuple[Path, Path]:
    """
    Auto-detect eBird data files in the given directory.

    Looks for:
    - Main file: ebd_*.txt (excluding *_sampling.txt)
    - Sampling file: *_sampling.txt

    Returns:
        Tuple of (main_file, sampling_file) paths

    Raises:
        FileNotFoundError if files cannot be found
    """
    # Find sampling file
    sampling_files = list(data_dir.glob("*_sampling.txt"))
    if not sampling_files:
        raise FileNotFoundError(
            f"No sampling file (*_sampling.txt) found in {data_dir}"
        )
    if len(sampling_files) > 1:
        raise FileNotFoundError(
            f"Multiple sampling files found in {data_dir}: {sampling_files}"
        )
    sampling_file = sampling_files[0]

    # Find main file (ebd_*.txt but not *_sampling.txt)
    main_files = [
        f for f in data_dir.glob("ebd_*.txt")
        if not f.name.endswith("_sampling.txt")
    ]
    if not main_files:
        raise FileNotFoundError(
            f"No main data file (ebd_*.txt) found in {data_dir}"
        )
    if len(main_files) > 1:
        raise FileNotFoundError(
            f"Multiple main data files found in {data_dir}: {main_files}"
        )
    main_file = main_files[0]

    return main_file, sampling_file


# Configuration state - set via init_config()
_initialized = False

# Paths (set by init_config)
DATA_DIR: Optional[Path] = None
OUTPUT_DIR: Optional[Path] = None
MAIN_FILE: Optional[Path] = None
SAMPLING_FILE: Optional[Path] = None

# Processing parameters
CHUNK_SIZE = 100000          # Rows per chunk for main file
SAMPLING_CHUNK_SIZE = 50000  # Rows per chunk for sampling file

# Confidence thresholds (can be overridden via init_config)
MIN_CHECKLISTS_THRESHOLD = 10   # Minimum checklists to include hotspot
HIGH_CONFIDENCE_MIN = 100       # Checklists for "high" confidence
MEDIUM_CONFIDENCE_MIN = 30      # Checklists for "medium" confidence

# Seasonal definitions (month numbers)
SEASONS = {
    'spring': [3, 4, 5],
    'summer': [6, 7],
    'fall': [8, 9, 10, 11],
    'winter': [12, 1, 2]
}

# Output formatting
JSON_INDENT = 2
RATE_DECIMAL_PLACES = 4

# Columns to read from sampling file
SAMPLING_COLS = [
    'LOCALITY ID',
    'LOCALITY',
    'LOCALITY TYPE',
    'LATITUDE',
    'LONGITUDE',
    'OBSERVATION DATE',
    'SAMPLING EVENT IDENTIFIER',
    'ALL SPECIES REPORTED',
]

# Columns to read from main file
MAIN_COLS = [
    'COMMON NAME',
    'SCIENTIFIC NAME',
    'CATEGORY',
    'LOCALITY ID',
    'LOCALITY TYPE',
    'SAMPLING EVENT IDENTIFIER',
    'ALL SPECIES REPORTED',
    'OBSERVATION DATE',
    'OBSERVATION COUNT',
]


def init_config(
    data_dir: Path,
    output_dir: Optional[Path] = None,
    min_checklists_threshold: Optional[int] = None,
    high_confidence_min: Optional[int] = None,
    medium_confidence_min: Optional[int] = None,
    seasons: Optional[dict] = None,
) -> None:
    """
    Initialize configuration from external settings.

    This must be called before using the pipeline processors.

    Args:
        data_dir: Directory containing eBird Basic Dataset files
        output_dir: Directory for output files (default: data_dir parent / hotspot_guide_output)
        min_checklists_threshold: Minimum checklists to include a hotspot
        high_confidence_min: Checklists needed for "high" confidence
        medium_confidence_min: Checklists needed for "medium" confidence
        seasons: Dictionary mapping season names to month lists
    """
    global _initialized
    global DATA_DIR, OUTPUT_DIR, MAIN_FILE, SAMPLING_FILE
    global MIN_CHECKLISTS_THRESHOLD, HIGH_CONFIDENCE_MIN, MEDIUM_CONFIDENCE_MIN
    global SEASONS

    DATA_DIR = Path(data_dir)
    OUTPUT_DIR = Path(output_dir) if output_dir else (DATA_DIR.parent / "hotspot_guide_output")

    # Auto-detect data files
    MAIN_FILE, SAMPLING_FILE = find_ebird_files(DATA_DIR)

    # Apply threshold overrides
    if min_checklists_threshold is not None:
        MIN_CHECKLISTS_THRESHOLD = min_checklists_threshold
    if high_confidence_min is not None:
        HIGH_CONFIDENCE_MIN = high_confidence_min
    if medium_confidence_min is not None:
        MEDIUM_CONFIDENCE_MIN = medium_confidence_min
    if seasons is not None:
        SEASONS = seasons

    _initialized = True


def ensure_initialized() -> None:
    """Raise an error if config has not been initialized."""
    if not _initialized:
        raise RuntimeError(
            "Hotspot guide config not initialized. Call init_config() first."
        )
