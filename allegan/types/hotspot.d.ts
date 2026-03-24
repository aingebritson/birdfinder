/**
 * TypeScript definitions for hotspot data
 * Generated from: schemas/hotspot-index.schema.json, schemas/hotspot-detail.schema.json
 */

/**
 * Reference to a birding hotspot location (used in index/listing)
 */
export interface HotspotRef {
  /** eBird locality ID (e.g., 'L320822') */
  locId: string;
  /** Hotspot name from eBird */
  name: string;
  /** Latitude in decimal degrees */
  lat: number;
  /** Longitude in decimal degrees */
  lng: number;
  /** Total number of species detected at this hotspot */
  numSpecies: number;
  /** Date/time of most recent observation (format: 'YYYY-MM-DD HH:MM') */
  latestObs: string | null;
  /** Reserved for future use (local knowledge, tips, etc.) */
  knowledge: object | null;
}

/**
 * Array of hotspot location references for quick listing and search
 */
export type HotspotIndex = HotspotRef[];

/**
 * Geographic coordinates
 */
export interface Coordinates {
  /** Latitude in decimal degrees */
  latitude: number;
  /** Longitude in decimal degrees */
  longitude: number;
}

/**
 * Basic hotspot identification and location
 */
export interface HotspotInfo {
  /** eBird locality ID (e.g., 'L320822') */
  locality_id: string;
  /** Hotspot name from eBird */
  name: string;
  /** Geographic coordinates */
  coordinates: Coordinates;
}

/**
 * Checklist counts by month (keys are '1' through '12')
 */
export interface MonthlyChecklists {
  '1': number;  // January
  '2': number;  // February
  '3': number;  // March
  '4': number;  // April
  '5': number;  // May
  '6': number;  // June
  '7': number;  // July
  '8': number;  // August
  '9': number;  // September
  '10': number; // October
  '11': number; // November
  '12': number; // December
}

/**
 * Birding effort statistics for a hotspot
 */
export interface Effort {
  /** Total number of complete checklists submitted */
  total_complete_checklists: number;
  /** Total unique species detected at this hotspot */
  total_species_detected: number;
  /** Checklist counts by month */
  monthly_checklists: MonthlyChecklists;
}

/**
 * Occurrence rates by season
 */
export interface SeasonalRates {
  /** Occurrence rate in spring (April-May), 0.0 to 1.0 */
  spring: number;
  /** Occurrence rate in summer (June-July), 0.0 to 1.0 */
  summer: number;
  /** Occurrence rate in fall (August-October), 0.0 to 1.0 */
  fall: number;
  /** Occurrence rate in winter (November-February), 0.0 to 1.0 */
  winter: number;
}

/**
 * Species occurrence data at a specific hotspot
 */
export interface SpeciesOccurrence {
  /** Rank by occurrence rate (1 = most frequently seen) */
  rank: number;
  /** Common name of the species */
  common_name: string;
  /** 6-character species code, lowercase alphabetic */
  code: string;
  /** Scientific (Latin) name of the species */
  scientific_name: string;
  /** Fraction of checklists where this species was detected (0.0 to 1.0) */
  occurrence_rate: number;
  /** Number of checklists where this species was detected */
  detection_count: number;
  /** Average count per checklist when detected */
  average_count: number;
  /** Maximum count ever recorded on a single checklist */
  max_count: number;
  /** Occurrence rates by season */
  seasonal: SeasonalRates;
}

/**
 * File generation metadata
 */
export interface HotspotMetadata {
  /** ISO 8601 timestamp when file was generated */
  generated_at: string;
  /** Version identifier for the source data (e.g., 'Dec-2025') */
  data_version: string;
}

/**
 * Detailed species occurrence data for a single birding hotspot
 */
export interface HotspotDetail {
  /** Basic hotspot identification and location */
  hotspot: HotspotInfo;
  /** Birding effort statistics */
  effort: Effort;
  /** Species detected at this hotspot, sorted by occurrence rate (descending) */
  species: SpeciesOccurrence[];
  /** File generation metadata */
  metadata: HotspotMetadata;
}
