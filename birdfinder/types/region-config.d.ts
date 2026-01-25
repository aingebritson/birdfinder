/**
 * TypeScript definitions for region configuration
 * Generated from: schemas/region-config.schema.json
 */

/**
 * File path configuration for pipeline input/output
 */
export interface Paths {
  /** Glob pattern for eBird input files (e.g., 'ebird_*.txt') */
  input_pattern?: string;
  /** Output filename pattern, supports {region_id} placeholder */
  output_file?: string;
  /** Directory for intermediate processing files */
  intermediate_dir?: string;
  /** Directory for hotspot data files */
  hotspots_dir?: string;
}

/**
 * Algorithm threshold overrides (keys match constants.py)
 */
export interface Thresholds {
  /** Valley detection threshold as ratio of peak (default: 0.15) */
  VALLEY_THRESHOLD_PEAK_RATIO?: number;
  /** Valley detection absolute minimum threshold (default: 0.005) */
  VALLEY_THRESHOLD_ABSOLUTE?: number;
  /** Minimum weeks for valley detection (default: 4) */
  VALLEY_MIN_LENGTH_WEEKS?: number;
  /** Minimum weeks present to not be vagrant (default: 10) */
  MIN_WEEKS_PRESENCE?: number;
  /** Minimum peak frequency to not be vagrant (default: 0.005) */
  MIN_PEAK_FREQUENCY?: number;
  /** Arrival/departure threshold as ratio of peak (default: 0.10) */
  ARRIVAL_THRESHOLD_PEAK_RATIO?: number;
  /** Arrival/departure absolute minimum (default: 0.001) */
  ARRIVAL_THRESHOLD_ABSOLUTE?: number;
  /** Min/max ratio for resident classification (default: 0.20) */
  RESIDENT_MIN_MAX_RATIO_THRESHOLD?: number;
}

/**
 * Week range that may wrap around year boundary
 */
export interface WeekRange {
  /** Start week index (0-47) */
  start: number;
  /** End week index (0-47), may be less than start for wraparound */
  end: number;
}

/**
 * Week range definitions for seasons (can adapt to different latitudes)
 */
export interface SeasonalWeeks {
  winter?: WeekRange;
  spring?: WeekRange;
  summer?: WeekRange;
  fall?: WeekRange;
}

/**
 * UI display configuration
 */
export interface DisplaySettings {
  /** Year to display in copyright notice */
  copyright_year?: number;
  /** Theme or mascot name for the region */
  theme_name?: string;
  /** About/intro text for the region */
  about_text?: string;
}

/**
 * Hotspot guide feature configuration
 */
export interface HotspotGuide {
  /** Whether to generate hotspot guide data */
  enabled?: boolean;
  /** Minimum complete checklists to include a hotspot */
  min_checklists_threshold?: number;
  /** Minimum checklists for high confidence rating */
  high_confidence_min?: number;
  /** Minimum checklists for medium confidence rating */
  medium_confidence_min?: number;
}

/**
 * Configuration for a BirdFinder region
 */
export interface RegionConfig {
  /** Unique identifier for the region, used in file paths (e.g., 'washtenaw') */
  region_id: string;
  /** Human-readable name for the region (e.g., 'Washtenaw County, Michigan') */
  display_name: string;
  /** Longer description of the region for display in the UI */
  description?: string;
  /** eBird region code for API queries (e.g., 'US-MI-161') */
  ebird_region_code?: string;
  /** IANA timezone identifier (e.g., 'America/Detroit') */
  timezone?: string;
  /** File path configuration */
  paths?: Paths;
  /** Algorithm threshold overrides */
  thresholds?: Thresholds;
  /** Week range definitions for seasons */
  seasonal_weeks?: SeasonalWeeks;
  /** UI display configuration */
  display_settings?: DisplaySettings;
  /** Hotspot guide feature configuration */
  hotspot_guide?: HotspotGuide;
}
