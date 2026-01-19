#!/usr/bin/env python3
"""
Region configuration system for BirdFinder data processing pipeline.

This module provides centralized configuration management for region-specific
settings, including display names, file paths, thresholds, and seasonal definitions.

Usage:
    from utils.region_config import load_region_config

    config = load_region_config('washtenaw')
    print(config.display_name)  # "Washtenaw County, Michigan"
    print(config.get_threshold('VALLEY_THRESHOLD_PEAK_RATIO'))  # 0.15
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


class ConfigError(Exception):
    """Raised when there's an error loading or validating region configuration."""
    pass


@dataclass
class RegionConfig:
    """
    Configuration for a specific region.

    Attributes:
        region_id: Unique identifier for the region (e.g., 'washtenaw')
        display_name: Human-readable region name (e.g., 'Washtenaw County, Michigan')
        description: Optional description of the region
        ebird_region_code: eBird API region code (e.g., 'US-MI-161')
        timezone: Timezone identifier (e.g., 'America/Detroit')

        paths: Dictionary of file path patterns and overrides
        thresholds: Dictionary of algorithm thresholds (overrides constants.py defaults)
        seasonal_weeks: Dictionary of seasonal week range definitions
        display_settings: Dictionary of UI/display preferences

        config_path: Path to the config file (set automatically)
    """

    region_id: str
    display_name: str
    description: str = ""
    ebird_region_code: str = ""
    timezone: str = "America/New_York"

    paths: Dict[str, str] = field(default_factory=dict)
    thresholds: Dict[str, float] = field(default_factory=dict)
    seasonal_weeks: Dict[str, Any] = field(default_factory=dict)
    display_settings: Dict[str, Any] = field(default_factory=dict)

    config_path: Optional[Path] = None

    def get_threshold(self, name: str, default: Optional[float] = None) -> Optional[float]:
        """
        Get a threshold value, falling back to default if not set.

        Args:
            name: Threshold name (e.g., 'VALLEY_THRESHOLD_PEAK_RATIO')
            default: Default value to return if threshold not configured

        Returns:
            Threshold value or default
        """
        return self.thresholds.get(name, default)

    def get_path(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get a path pattern, falling back to default if not set.

        Args:
            name: Path name (e.g., 'input_pattern', 'output_file')
            default: Default value to return if path not configured

        Returns:
            Path pattern or default
        """
        return self.paths.get(name, default)

    def get_seasonal_weeks(self, season: str) -> Optional[Dict[str, int]]:
        """
        Get week range for a season.

        Args:
            season: Season name ('winter', 'summer', 'spring', 'fall')

        Returns:
            Dictionary with 'start' and 'end' week indices, or None
        """
        return self.seasonal_weeks.get(season)

    def get_display_setting(self, name: str, default: Any = None) -> Any:
        """
        Get a display setting.

        Args:
            name: Setting name (e.g., 'copyright_year', 'theme_color')
            default: Default value to return if setting not configured

        Returns:
            Setting value or default
        """
        return self.display_settings.get(name, default)


def load_region_config(region_id: str, project_root: Optional[Path] = None) -> RegionConfig:
    """
    Load configuration for a region.

    This function looks for configuration in the following order:
    1. regions/[region_id]/config.json (region-specific config)
    2. config/regions.json (multi-region config file)
    3. Falls back to defaults with region_id and display_name only

    Args:
        region_id: Unique identifier for the region (e.g., 'washtenaw')
        project_root: Optional project root path. If not provided, auto-detected.

    Returns:
        RegionConfig object with loaded settings

    Raises:
        ConfigError: If configuration cannot be loaded or is invalid
    """
    # Auto-detect project root if not provided
    if project_root is None:
        if Path.cwd().name == 'scripts':
            project_root = Path.cwd().parent
        else:
            project_root = Path.cwd()

    # Try region-specific config first
    region_config_path = project_root / "regions" / region_id / "config.json"
    if region_config_path.exists():
        return _load_config_from_file(region_config_path, region_id)

    # Try multi-region config file
    global_config_path = project_root / "config" / "regions.json"
    if global_config_path.exists():
        return _load_from_global_config(global_config_path, region_id)

    # Fall back to minimal config with just region_id
    return _create_default_config(region_id)


def _load_config_from_file(config_path: Path, region_id: str) -> RegionConfig:
    """Load configuration from a JSON file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file {config_path}: {e}")
    except IOError as e:
        raise ConfigError(f"Error reading config file {config_path}: {e}")

    # Validate required fields
    if 'region_id' not in data:
        data['region_id'] = region_id
    elif data['region_id'] != region_id:
        raise ConfigError(
            f"Region ID mismatch: config says '{data['region_id']}' "
            f"but loading for '{region_id}'"
        )

    if 'display_name' not in data:
        raise ConfigError(f"Config file {config_path} missing required field 'display_name'")

    # Create config object
    config = RegionConfig(
        region_id=data['region_id'],
        display_name=data['display_name'],
        description=data.get('description', ''),
        ebird_region_code=data.get('ebird_region_code', ''),
        timezone=data.get('timezone', 'America/New_York'),
        paths=data.get('paths', {}),
        thresholds=data.get('thresholds', {}),
        seasonal_weeks=data.get('seasonal_weeks', {}),
        display_settings=data.get('display_settings', {}),
        config_path=config_path
    )

    # Validate the loaded config
    _validate_config(config)

    return config


def _load_from_global_config(config_path: Path, region_id: str) -> RegionConfig:
    """Load configuration from a global regions.json file."""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in config file {config_path}: {e}")
    except IOError as e:
        raise ConfigError(f"Error reading config file {config_path}: {e}")

    # Find the region in the global config
    if 'regions' not in data:
        raise ConfigError(f"Global config file {config_path} missing 'regions' key")

    regions = data['regions']
    if region_id not in regions:
        raise ConfigError(
            f"Region '{region_id}' not found in {config_path}. "
            f"Available regions: {', '.join(regions.keys())}"
        )

    region_data = regions[region_id]
    region_data['region_id'] = region_id

    if 'display_name' not in region_data:
        raise ConfigError(
            f"Region '{region_id}' in {config_path} missing required field 'display_name'"
        )

    # Create config object
    config = RegionConfig(
        region_id=region_data['region_id'],
        display_name=region_data['display_name'],
        description=region_data.get('description', ''),
        ebird_region_code=region_data.get('ebird_region_code', ''),
        timezone=region_data.get('timezone', 'America/New_York'),
        paths=region_data.get('paths', {}),
        thresholds=region_data.get('thresholds', {}),
        seasonal_weeks=region_data.get('seasonal_weeks', {}),
        display_settings=region_data.get('display_settings', {}),
        config_path=config_path
    )

    # Validate the loaded config
    _validate_config(config)

    return config


def _create_default_config(region_id: str) -> RegionConfig:
    """Create a minimal default configuration."""
    # Create a display name from region_id (e.g., 'washtenaw' -> 'Washtenaw')
    display_name = region_id.replace('_', ' ').replace('-', ' ').title()

    return RegionConfig(
        region_id=region_id,
        display_name=display_name,
        description=f"Default configuration for {display_name}",
        ebird_region_code="",
        timezone="America/New_York"
    )


def _validate_config(config: RegionConfig) -> None:
    """
    Validate a loaded configuration.

    Raises:
        ConfigError: If configuration is invalid
    """
    # Validate region_id format
    if not config.region_id:
        raise ConfigError("region_id cannot be empty")

    if not config.region_id.replace('_', '').replace('-', '').isalnum():
        raise ConfigError(
            f"region_id must contain only alphanumeric characters, "
            f"hyphens, and underscores: '{config.region_id}'"
        )

    # Validate display_name
    if not config.display_name:
        raise ConfigError("display_name cannot be empty")

    # Validate threshold values
    for name, value in config.thresholds.items():
        if not isinstance(value, (int, float)):
            raise ConfigError(
                f"Threshold '{name}' must be numeric, got {type(value).__name__}"
            )
        if value < 0:
            raise ConfigError(f"Threshold '{name}' cannot be negative: {value}")

    # Validate seasonal_weeks structure
    for season, weeks in config.seasonal_weeks.items():
        if not isinstance(weeks, dict):
            raise ConfigError(
                f"Seasonal weeks for '{season}' must be a dictionary with "
                f"'start' and 'end' keys"
            )
        if 'start' not in weeks or 'end' not in weeks:
            raise ConfigError(
                f"Seasonal weeks for '{season}' must have 'start' and 'end' keys"
            )
        if not isinstance(weeks['start'], int) or not isinstance(weeks['end'], int):
            raise ConfigError(
                f"Seasonal week indices for '{season}' must be integers"
            )
        if not (0 <= weeks['start'] <= 47):
            raise ConfigError(
                f"Seasonal week start for '{season}' must be in range [0, 47]: "
                f"{weeks['start']}"
            )
        if not (0 <= weeks['end'] <= 47):
            raise ConfigError(
                f"Seasonal week end for '{season}' must be in range [0, 47]: "
                f"{weeks['end']}"
            )


def list_available_regions(project_root: Optional[Path] = None) -> list:
    """
    List all available regions (regions with config files or directories).

    Args:
        project_root: Optional project root path. If not provided, auto-detected.

    Returns:
        List of region IDs
    """
    # Auto-detect project root if not provided
    if project_root is None:
        if Path.cwd().name == 'scripts':
            project_root = Path.cwd().parent
        else:
            project_root = Path.cwd()

    regions = set()

    # Check for regions with directories
    regions_dir = project_root / "regions"
    if regions_dir.exists():
        for item in regions_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                regions.add(item.name)

    # Check global config file
    global_config_path = project_root / "config" / "regions.json"
    if global_config_path.exists():
        try:
            with open(global_config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if 'regions' in data:
                    regions.update(data['regions'].keys())
        except (json.JSONDecodeError, IOError):
            pass  # Ignore errors, just skip this source

    return sorted(list(regions))


def save_region_config(config: RegionConfig, config_path: Optional[Path] = None) -> None:
    """
    Save a region configuration to a JSON file.

    Args:
        config: RegionConfig object to save
        config_path: Optional path to save to. If not provided, uses config.config_path

    Raises:
        ConfigError: If save fails
    """
    if config_path is None:
        if config.config_path is None:
            raise ConfigError("No config_path specified and config has no existing path")
        config_path = config.config_path

    # Create config directory if needed
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Build config dictionary
    data = {
        'region_id': config.region_id,
        'display_name': config.display_name,
    }

    if config.description:
        data['description'] = config.description
    if config.ebird_region_code:
        data['ebird_region_code'] = config.ebird_region_code
    if config.timezone != 'America/New_York':
        data['timezone'] = config.timezone

    if config.paths:
        data['paths'] = config.paths
    if config.thresholds:
        data['thresholds'] = config.thresholds
    if config.seasonal_weeks:
        data['seasonal_weeks'] = config.seasonal_weeks
    if config.display_settings:
        data['display_settings'] = config.display_settings

    # Write to file
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        raise ConfigError(f"Error writing config file {config_path}: {e}")

    config.config_path = config_path
