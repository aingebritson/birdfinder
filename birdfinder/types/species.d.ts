/**
 * TypeScript definitions for species data
 * Generated from: schemas/species-data.schema.json
 */

/**
 * Migration category based on presence pattern analysis
 */
export type Category =
  | 'resident'
  | 'single-season'
  | 'two-passage-migrant'
  | 'vagrant'
  | 'irregular';

/**
 * Edge case flag indicating special classification conditions
 */
export type Flag =
  | 'low_peak_frequency'
  | 'seasonal_variation'
  | 'overwintering'
  | 'min_max_near_boundary'
  | 'classic_bimodal'
  | 'separated_valleys'
  | 'three_valley_migrant'
  | 'mixed_valley_winter_lean'
  | 'mixed_valley_summer_lean'
  | 'low_presence'
  | 'many_valleys';

/**
 * Date range in 'Month Day-Day' format (e.g., 'May 8-14')
 */
export type DateRange = string;

/**
 * 48 frequency values (one per week), representing occurrence rate from 0.0 to 1.0
 */
export type WeeklyFrequency = [
  number, number, number, number, number, number, number, number,
  number, number, number, number, number, number, number, number,
  number, number, number, number, number, number, number, number,
  number, number, number, number, number, number, number, number,
  number, number, number, number, number, number, number, number,
  number, number, number, number, number, number, number, number
];

/**
 * Timing for year-round resident species
 */
export interface TimingYearRound {
  status: 'year-round';
}

/**
 * Timing for summer breeding species (single-season)
 */
export interface TimingSummer {
  arrival?: DateRange;
  peak: DateRange;
  departure?: DateRange;
}

/**
 * Timing for winter resident species (single-season, overwintering)
 */
export interface TimingWinter {
  winter_arrival?: DateRange;
  winter_peak: DateRange;
  winter_departure?: DateRange;
}

/**
 * Timing for two-passage migrants with spring and fall migrations
 */
export interface TimingTwoPassage {
  spring_arrival?: DateRange;
  spring_peak: DateRange;
  spring_departure?: DateRange;
  fall_arrival?: DateRange;
  fall_peak: DateRange;
  fall_departure?: DateRange;
}

/**
 * Timing for vagrant or irregular species
 */
export interface TimingIrregular {
  status: 'irregular';
  first_appears?: DateRange;
  peak: DateRange;
  last_appears?: DateRange;
}

/**
 * Timing information varies by migration pattern type
 */
export type Timing =
  | TimingYearRound
  | TimingSummer
  | TimingWinter
  | TimingTwoPassage
  | TimingIrregular;

/**
 * A single bird species with all occurrence and timing data
 */
export interface Species {
  /** Common name of the species (e.g., 'American Robin') */
  name: string;
  /** 6-character species code, lowercase alphabetic */
  code: string;
  /** Migration category based on presence pattern analysis */
  category: Category;
  /** Edge case indicators and additional classification details */
  flags: Flag[];
  /** Timing information varies by migration pattern type */
  timing: Timing;
  /** 48 frequency values (one per week), representing occurrence rate from 0.0 to 1.0 */
  weekly_frequency: WeeklyFrequency;
}

/**
 * Array of bird species with occurrence data, migration patterns, and timing information
 */
export type SpeciesData = Species[];

// Type guards for timing patterns

export function isYearRound(timing: Timing): timing is TimingYearRound {
  return 'status' in timing && timing.status === 'year-round';
}

export function isIrregular(timing: Timing): timing is TimingIrregular {
  return 'status' in timing && timing.status === 'irregular';
}

export function isSummer(timing: Timing): timing is TimingSummer {
  return 'peak' in timing && !('status' in timing) && !('spring_peak' in timing) && !('winter_peak' in timing);
}

export function isWinter(timing: Timing): timing is TimingWinter {
  return 'winter_peak' in timing;
}

export function isTwoPassage(timing: Timing): timing is TimingTwoPassage {
  return 'spring_peak' in timing && 'fall_peak' in timing;
}
