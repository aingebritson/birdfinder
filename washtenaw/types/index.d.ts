/**
 * BirdFinder TypeScript Type Definitions
 *
 * This module exports all type definitions for the BirdFinder data structures.
 * These types correspond to the JSON Schema files in /schemas/.
 *
 * Usage:
 *   import type { Species, HotspotDetail, RegionConfig } from './types';
 *
 * Or import from specific modules:
 *   import type { Species, Category, Timing } from './types/species';
 *   import type { HotspotRef, HotspotDetail } from './types/hotspot';
 */

// Species data types
export type {
  Category,
  Flag,
  DateRange,
  WeeklyFrequency,
  TimingYearRound,
  TimingSummer,
  TimingWinter,
  TimingTwoPassage,
  TimingIrregular,
  Timing,
  Species,
  SpeciesData,
} from './species';

// Re-export type guards
export {
  isYearRound,
  isIrregular,
  isSummer,
  isWinter,
  isTwoPassage,
} from './species';

// Hotspot data types
export type {
  HotspotRef,
  HotspotIndex,
  Coordinates,
  HotspotInfo,
  MonthlyChecklists,
  Effort,
  SeasonalRates,
  SpeciesOccurrence,
  HotspotMetadata,
  HotspotDetail,
} from './hotspot';

// Region configuration types
export type {
  Paths,
  Thresholds,
  WeekRange,
  SeasonalWeeks,
  DisplaySettings,
  HotspotGuide,
  RegionConfig,
} from './region-config';
