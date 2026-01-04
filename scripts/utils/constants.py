#!/usr/bin/env python3
"""
Constants for BirdFinder data processing pipeline.

This module centralizes all magic numbers and threshold values used throughout
the pipeline, making them easier to understand, maintain, and adjust.
"""

# ==============================================================================
# WEEK STRUCTURE
# ==============================================================================

# eBird uses a 48-week calendar system (4 weeks per month)
WEEKS_PER_YEAR = 48
WEEKS_PER_MONTH = 4
MONTHS_PER_YEAR = 12

# Week index range (zero-indexed)
WEEK_INDEX_MIN = 0
WEEK_INDEX_MAX = 47

# Month names for display
MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
]

# Abbreviated month names for week labels
MONTH_ABBREV = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

# ==============================================================================
# SEASONAL WEEK RANGES
# ==============================================================================

# Winter weeks: December through February (weeks 44-47, 0-7)
# Note: This wraps around the year boundary
WINTER_WEEKS_START = 44  # Early December
WINTER_WEEKS_END = 7     # Late February

# Summer weeks: May through August (weeks 16-35)
SUMMER_WEEKS_START = 16  # Early May
SUMMER_WEEKS_END = 35    # Late August

# Spring migration window: March through May (weeks 8-19)
SPRING_WEEKS_START = 8
SPRING_WEEKS_END = 19

# Fall migration window: August through November (weeks 28-43)
FALL_WEEKS_START = 28
FALL_WEEKS_END = 43

# Helper function to check if a week is in winter
def is_winter_week(week):
    """Check if a week falls in winter (wraps around year boundary)."""
    return week >= WINTER_WEEKS_START or week <= WINTER_WEEKS_END

# Helper function to check if a week is in summer
def is_summer_week(week):
    """Check if a week falls in summer."""
    return SUMMER_WEEKS_START <= week <= SUMMER_WEEKS_END


# ==============================================================================
# VALLEY DETECTION THRESHOLDS
# ==============================================================================

# A valley is a period of low or zero detection frequency, indicating absence

# Minimum length for a valley (consecutive weeks)
VALLEY_MIN_LENGTH_WEEKS = 4

# Valley threshold as ratio of peak frequency
# Weeks below 15% of peak are considered "low"
VALLEY_THRESHOLD_PEAK_RATIO = 0.15

# Absolute valley threshold
# Weeks below 0.5% are always considered "low" regardless of peak
VALLEY_THRESHOLD_ABSOLUTE = 0.005  # 0.5%


# ==============================================================================
# ARRIVAL/DEPARTURE DETECTION THRESHOLDS
# ==============================================================================

# Threshold for detecting arrival/departure as ratio of peak frequency
ARRIVAL_THRESHOLD_PEAK_RATIO = 0.10  # 10% of peak

# Absolute threshold for arrival/departure
ARRIVAL_THRESHOLD_ABSOLUTE = 0.001  # 0.1%

# Minimum peak frequency to be considered "present"
# Species with peak < 0.5% are considered vagrants
MIN_PEAK_FREQUENCY = 0.005  # 0.5%


# ==============================================================================
# SPECIES CLASSIFICATION THRESHOLDS
# ==============================================================================

# Minimum weeks of presence to avoid "vagrant" classification
MIN_WEEKS_PRESENCE = 10

# Minimum frequency ratio (min/max) for resident classification
# If min frequency is > 20% of max, species is likely year-round
RESIDENT_MIN_MAX_RATIO_THRESHOLD = 0.20

# Seasonal variation threshold for residents
# If max/min ratio > 5x, species has strong seasonal variation even if resident
RESIDENT_SEASONAL_VARIATION_THRESHOLD = 5.0

# Overwintering detection threshold
# Need 8+ consecutive weeks in winter above 5% of peak
OVERWINTERING_MIN_WEEKS = 8
OVERWINTERING_FREQUENCY_THRESHOLD = 0.05  # 5% of peak


# ==============================================================================
# DATA VALIDATION CONSTANTS
# ==============================================================================

# Frequency values must be in range [0.0, 1.0] (represents 0% to 100%)
FREQUENCY_MIN = 0.0
FREQUENCY_MAX = 1.0

# Species codes must be exactly 6 characters (eBird standard)
SPECIES_CODE_LENGTH = 6


# ==============================================================================
# MIGRATION CATEGORIES
# ==============================================================================

# Valid migration category values
CATEGORY_RESIDENT = 'resident'
CATEGORY_SINGLE_SEASON = 'single-season'
CATEGORY_TWO_PASSAGE = 'two-passage-migrant'
CATEGORY_VAGRANT = 'vagrant'
CATEGORY_IRREGULAR = 'irregular'

VALID_CATEGORIES = {
    CATEGORY_RESIDENT,
    CATEGORY_SINGLE_SEASON,
    CATEGORY_TWO_PASSAGE,
    CATEGORY_VAGRANT,
    CATEGORY_IRREGULAR
}


# ==============================================================================
# PATTERN TYPES
# ==============================================================================

# Valid pattern type values
PATTERN_YEAR_ROUND = 'year-round'
PATTERN_IRREGULAR = 'irregular'
PATTERN_TWO_PASSAGE = 'two-passage'
PATTERN_SUMMER = 'summer'
PATTERN_WINTER = 'winter'

VALID_PATTERN_TYPES = {
    PATTERN_YEAR_ROUND,
    PATTERN_IRREGULAR,
    PATTERN_TWO_PASSAGE,
    PATTERN_SUMMER,
    PATTERN_WINTER
}


# ==============================================================================
# VALLEY TIMING CLASSIFICATIONS
# ==============================================================================

VALLEY_TYPE_WINTER = 'winter'
VALLEY_TYPE_SUMMER = 'summer'
VALLEY_TYPE_SPRING = 'spring'
VALLEY_TYPE_FALL = 'fall'


# ==============================================================================
# DIAGNOSTIC FLAGS
# ==============================================================================

# Flags added to species data for edge cases and special conditions
FLAG_LOW_PEAK_FREQUENCY = 'low_peak_frequency'
FLAG_SEASONAL_VARIATION = 'seasonal_variation'
FLAG_MIN_MAX_NEAR_BOUNDARY = 'min_max_near_boundary'
FLAG_CLASSIC_BIMODAL = 'classic_bimodal'
FLAG_OVERWINTERING = 'overwintering'
FLAG_THREE_VALLEYS_IRREGULAR = 'three_valleys_irregular'
FLAG_CLOSE_VALLEYS = 'close_valleys'
FLAG_WINTER_BREEDING = 'winter_breeding'


# ==============================================================================
# DISPLAY FORMATTING
# ==============================================================================

# Day ranges for each week in a month
WEEK_DAY_RANGES = [
    (1, 7),    # Week 1: 1st-7th
    (8, 14),   # Week 2: 8th-14th
    (15, 21),  # Week 3: 15th-21st
    (22, 31),  # Week 4: 22nd-31st (or 28/29/30 depending on month)
]
