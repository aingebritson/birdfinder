# Refactoring Log

This document tracks major refactoring changes made to improve code quality and maintainability.

---

## 2025-01-03: Extract Valley Detection to Shared Module

**Issue:** Valley detection algorithm was duplicated in two files:
- `scripts/classify_migration_patterns.py` (lines 17-77)
- `scripts/calculate_arrival_departure.py` (lines 643-701)

**Problem:** Code duplication creates maintenance burden. Any changes to the algorithm had to be manually synchronized across both files, increasing risk of bugs and inconsistencies.

**Solution:** Extracted the algorithm to a shared utility module.

### Changes Made

1. **Created shared utility module:**
   - `scripts/utils/__init__.py` - Package initialization
   - `scripts/utils/valley_detection.py` - Contains the `detect_valleys()` function
   - `scripts/utils/test_valley_detection.py` - Unit tests for the algorithm

2. **Updated `scripts/classify_migration_patterns.py`:**
   - Removed local `detect_valleys()` function definition (61 lines)
   - Added import: `from utils.valley_detection import detect_valleys`
   - Added path setup to ensure imports work when running from any directory

3. **Updated `scripts/calculate_arrival_departure.py`:**
   - Removed local `detect_valleys()` function definition (59 lines)
   - Added import: `from utils.valley_detection import detect_valleys`
   - Added path setup to ensure imports work when running from any directory

### Benefits

✅ **Single source of truth** - Algorithm now defined in exactly one place
✅ **Easier maintenance** - Changes only need to be made once
✅ **Better documentation** - Comprehensive docstring with examples
✅ **Testable** - Added unit tests to verify correctness
✅ **Less code** - Removed ~120 lines of duplicate code

### Testing

- ✅ Full pipeline runs successfully: `python3 scripts/run_pipeline.py washtenaw`
- ✅ Individual scripts work: `classify_migration_patterns.py` and `calculate_arrival_departure.py`
- ✅ Unit tests pass: `python3 scripts/utils/test_valley_detection.py`
- ✅ Output JSON matches expected format with 340 species

### Files Modified

- `scripts/classify_migration_patterns.py`
- `scripts/calculate_arrival_departure.py`

### Files Created

- `scripts/utils/__init__.py`
- `scripts/utils/valley_detection.py`
- `scripts/utils/test_valley_detection.py`

---

## 2025-01-03: Add Comprehensive Input Validation

**Issue:** The pipeline lacked input validation, allowing malformed or malicious data to propagate through the system, potentially causing cryptic errors or security issues.

**Problem:**
- No validation of frequency arrays (length, range)
- No validation of week indices
- No validation of species names, codes, categories
- No protection against path traversal in region names
- Missing file existence checks
- No validation of valley tuples or data structures

**Solution:** Created comprehensive validation utility module with reusable validation functions.

### Changes Made

1. **Created validation utility module:**
   - `scripts/utils/validation.py` - Comprehensive validation functions
   - `scripts/utils/test_validation.py` - Unit tests for all validators
   - Custom `ValidationError` exception for clear error messages

2. **Added validation to `scripts/parse_ebird_data.py`:**
   - Validate region name (prevent path traversal)
   - Validate input file exists
   - Validate species names and frequency arrays
   - Gracefully skip invalid species with warnings

3. **Added validation to `scripts/classify_migration_patterns.py`:**
   - Validate region name
   - Validate input file exists
   - Validate frequency arrays in `calculate_metrics()`
   - Validate valley tuples
   - Validate week indices

4. **Added validation to `scripts/merge_to_json.py`:**
   - Validate region name
   - Validate all input files exist before processing
   - Validate final species data structure
   - Gracefully skip invalid species with warnings

### Validation Functions Added

- `validate_frequency_array()` - Checks length (48), range [0.0, 1.0], and type
- `validate_week_index()` - Checks range [0, 47]
- `validate_species_name()` - Checks for empty, whitespace, invalid characters
- `validate_category()` - Checks against valid categories
- `validate_pattern_type()` - Checks against valid pattern types
- `validate_species_code()` - Checks length (6), lowercase, alphanumeric
- `validate_region_name()` - Prevents path traversal, checks format
- `validate_valley_tuple()` - Checks tuple format and week indices
- `validate_file_exists()` - Checks file exists and is not empty
- `validate_json_structure()` - Validates JSON structure
- `validate_species_data_structure()` - Validates complete species object

### Benefits

✅ **Fail fast** - Errors caught immediately with clear messages
✅ **Security** - Path traversal prevention, input sanitization
✅ **Data integrity** - Ensures all data meets expectations
✅ **Better debugging** - Validation errors show exactly what's wrong
✅ **Testable** - All validation logic in one place with comprehensive tests
✅ **Reusable** - Validation functions can be used throughout the codebase

### Testing

- ✅ All validation unit tests pass (24 tests)
- ✅ Full pipeline runs successfully with valid data
- ✅ Invalid region names properly rejected (e.g., `../etc`)
- ✅ Malformed data gracefully handled with warnings
- ✅ Output JSON validated for correct structure

### Example Error Messages

```
Error: Invalid region name (contains path separators): ../etc
Error: Frequency array must have exactly 48 values (one per week) for species: American Robin, got 47 values
Error: Week index must be in range [0, 47] (valley start for Snow Goose), got 50
Error: eBird data JSON file not found: /path/to/missing/file.json
```

### Files Modified

- `scripts/parse_ebird_data.py`
- `scripts/classify_migration_patterns.py`
- `scripts/merge_to_json.py`

### Files Created

- `scripts/utils/validation.py`
- `scripts/utils/test_validation.py`

### Bug Found and Fixed

**Bonus:** The validation caught a **bug** in the original `generate_species_code()` function!

**Issue:** Single-word species names shorter than 6 characters (e.g., "Ruff", "Sora", "Veery") generated invalid codes:
- `"Ruff"` → `"ruff"` (4 chars, should be 6)
- `"Sora"` → `"sora"` (4 chars, should be 6)
- `"Veery"` → `"veery"` (5 chars, should be 6)

**Fix:** Modified `generate_species_code()` to pad short single-word names by repeating the word:
- `"Ruff"` → `"ruffru"` ✓
- `"Sora"` → `"soraso"` ✓
- `"Veery"` → `"veeryv"` ✓

**Result:** All 340 species now successfully included (previously 337 due to filtering).

**Test coverage added:** [scripts/test_species_code_generation.py](scripts/test_species_code_generation.py)

---

## 2025-01-03: Create Constants Module for Magic Numbers

**Issue:** Magic numbers and threshold values were scattered throughout the codebase, making them difficult to understand, maintain, and adjust.

**Problem:**
- Hardcoded thresholds (0.15, 0.005, 0.10, 0.001, etc.) with no context
- Week ranges (40-47, 0-11, 16-35) repeated multiple times
- Category and pattern type strings duplicated across files
- No single source of truth for configuration values

**Solution:** Created centralized constants module with well-documented, named constants.

### Changes Made

1. **Created constants module:**
   - [scripts/utils/constants.py](scripts/utils/constants.py) - Centralized constants with comprehensive documentation
   - Organized into logical sections: week structure, seasonal ranges, thresholds, categories, flags

2. **Updated [scripts/classify_migration_patterns.py](scripts/classify_migration_patterns.py):**
   - Replaced magic numbers with named constants
   - Used `MIN_WEEKS_PRESENCE` instead of `10`
   - Used `MIN_PEAK_FREQUENCY` instead of `0.005`
   - Used `VALLEY_TYPE_WINTER`/`VALLEY_TYPE_SUMMER` instead of string literals
   - Used category/pattern type constants

3. **Updated [scripts/calculate_arrival_departure.py](scripts/calculate_arrival_departure.py):**
   - Used `ARRIVAL_THRESHOLD_PEAK_RATIO` instead of `0.10`
   - Used `ARRIVAL_THRESHOLD_ABSOLUTE` instead of `0.001`
   - Used `WEEKS_PER_YEAR` instead of hardcoded `48`

4. **Updated [scripts/utils/validation.py](scripts/utils/validation.py):**
   - Used `WEEKS_PER_YEAR` instead of `48`
   - Used `WEEK_INDEX_MIN`/`WEEK_INDEX_MAX` instead of `0`/`47`
   - Used `FREQUENCY_MIN`/`FREQUENCY_MAX` instead of `0.0`/`1.0`
   - Used `SPECIES_CODE_LENGTH` instead of `6`
   - Used `VALID_CATEGORIES` and `VALID_PATTERN_TYPES` sets

### Constants Defined

**Week Structure:**
- `WEEKS_PER_YEAR = 48`
- `WEEK_INDEX_MIN = 0`, `WEEK_INDEX_MAX = 47`
- `WINTER_WEEKS_START = 44`, `WINTER_WEEKS_END = 7`
- `SUMMER_WEEKS_START = 16`, `SUMMER_WEEKS_END = 35`

**Valley Detection:**
- `VALLEY_MIN_LENGTH_WEEKS = 4`
- `VALLEY_THRESHOLD_PEAK_RATIO = 0.15` (15% of peak)
- `VALLEY_THRESHOLD_ABSOLUTE = 0.005` (0.5%)

**Arrival/Departure:**
- `ARRIVAL_THRESHOLD_PEAK_RATIO = 0.10` (10% of peak)
- `ARRIVAL_THRESHOLD_ABSOLUTE = 0.001` (0.1%)
- `MIN_PEAK_FREQUENCY = 0.005` (0.5%)

**Species Classification:**
- `MIN_WEEKS_PRESENCE = 10`
- `RESIDENT_MIN_MAX_RATIO_THRESHOLD = 0.20` (20%)
- `OVERWINTERING_MIN_WEEKS = 8`

**Data Validation:**
- `FREQUENCY_MIN = 0.0`, `FREQUENCY_MAX = 1.0`
- `SPECIES_CODE_LENGTH = 6`

**Categories & Types:**
- `VALID_CATEGORIES = {resident, single-season, two-passage-migrant, vagrant, irregular}`
- `VALID_PATTERN_TYPES = {year-round, irregular, two-passage, summer, winter}`

### Benefits

✅ **Self-documenting** - Constant names explain their purpose
✅ **Single source of truth** - Change once, applies everywhere
✅ **Type safety** - Using sets for valid values prevents typos
✅ **Easier tuning** - All thresholds in one place for experimentation
✅ **Better IDE support** - Auto-completion for constant names
✅ **Comprehensible** - Comments explain what each threshold means

### Testing

- ✅ Full pipeline runs successfully
- ✅ All validation tests pass
- ✅ Output identical to before refactoring (340 species)
- ✅ Constants properly imported across all modules

### Example Improvements

**Before:**
```python
if metrics['weeks_with_presence'] < 10 or metrics['peak_frequency'] < 0.005:
    category = 'vagrant'
```

**After:**
```python
if metrics['weeks_with_presence'] < MIN_WEEKS_PRESENCE or metrics['peak_frequency'] < MIN_PEAK_FREQUENCY:
    category = CATEGORY_VAGRANT
```

Much more readable and maintainable!

### Files Modified

- `scripts/classify_migration_patterns.py`
- `scripts/calculate_arrival_departure.py`
- `scripts/utils/validation.py`

### Files Created

- `scripts/utils/constants.py` (180 lines)

---

## 2025-01-04: Add Error Recovery in JavaScript Data Loading

**Issue:** JavaScript data loading had no error recovery mechanism, resulting in silent failures that left users with blank pages and no way to retry.

**Problem:**
- `fetch()` errors only logged to console with no user feedback
- No retry logic for transient network failures
- No distinction between retryable (network issues) and permanent errors (404)
- No HTTP status code validation
- No loading states or progress indicators
- Pages would fail silently, leaving users confused

**Solution:** Created comprehensive error recovery system with automatic retry, exponential backoff, user-visible error messages, and retry UI.

### Changes Made

1. **Created error recovery utility module:**
   - [birdfinder/js/data-loader.js](birdfinder/js/data-loader.js) - Robust data fetching with retry logic
   - `fetchWithRetry()` function with automatic retry and exponential backoff
   - Custom `DataLoadError` class with error type classification
   - User-friendly error message formatting
   - Loading and error UI components

2. **Updated [birdfinder/js/data.js](birdfinder/js/data.js):**
   - Replaced simple `fetch()` with `fetchWithRetry()`
   - Added caching to prevent redundant loads
   - Added concurrent load prevention
   - Added data structure validation
   - Added `getLoadError()` and `clearCache()` functions
   - Progress and error callbacks for UI updates

3. **Updated [birdfinder/js/browse.js](birdfinder/js/browse.js):**
   - Added loading state display
   - Added error handling with retry button
   - Shows detailed error messages to users
   - Gracefully handles empty data

4. **Updated [birdfinder/js/species-detail.js](birdfinder/js/species-detail.js):**
   - Added progress updates during loading
   - Shows error UI with retry capability
   - Updates loading message during retries

5. **Updated [birdfinder/js/this-week.js](birdfinder/js/this-week.js):**
   - Shows errors in all three list containers
   - Provides retry functionality

6. **Updated [birdfinder/js/hotspots.js](birdfinder/js/hotspots.js):**
   - Complete rewrite of `loadHotspots()` function
   - Uses `fetchWithRetry()` with automatic retry
   - Shows loading and error states
   - Validates data structure

7. **Updated HTML files to include data-loader.js:**
   - [birdfinder/index.html](birdfinder/index.html)
   - [birdfinder/browse.html](birdfinder/browse.html)
   - [birdfinder/species.html](birdfinder/species.html)
   - [birdfinder/hotspots.html](birdfinder/hotspots.html)

8. **Created test suite:**
   - [birdfinder/test-error-recovery.html](birdfinder/test-error-recovery.html) - Interactive test page for error scenarios

### Error Recovery Features

**Retry Configuration:**
- Maximum 3 retry attempts for retryable errors
- Exponential backoff: 1s → 2s → 4s (capped at 5s)
- 10-second request timeout
- Automatic retry for network errors, server errors (5xx), and timeouts
- No retry for 404 Not Found or JSON parse errors

**Error Type Classification:**
- `NETWORK` - Network connectivity issues (retryable)
- `NOT_FOUND` - 404 errors (not retryable)
- `SERVER` - 5xx server errors (retryable)
- `TIMEOUT` - Request timeout (retryable)
- `PARSE` - JSON parsing errors (not retryable)

**User Experience Improvements:**
- Loading spinner with progress messages ("Loading...", "Retrying... (attempt 2/3)")
- Clear error messages explaining what went wrong
- "Try Again" button for retryable errors
- HTTP status codes shown when relevant
- Console logging for debugging

### Benefits

✅ **Resilient** - Automatic recovery from transient network failures
✅ **User-friendly** - Clear error messages and retry options
✅ **Transparent** - Loading states and progress indicators
✅ **Smart retry** - Exponential backoff prevents server overload
✅ **Type-safe** - Distinguishes between retryable and permanent errors
✅ **Debuggable** - Comprehensive console logging
✅ **Testable** - Dedicated test suite for error scenarios
✅ **Cached** - Prevents redundant data loads

### Testing

- ✅ Created interactive test suite ([test-error-recovery.html](birdfinder/test-error-recovery.html))
- ✅ Tested valid data load with retry capability
- ✅ Tested 404 Not Found (non-retryable error)
- ✅ Tested network timeout with exponential backoff
- ✅ Tested invalid JSON parsing error
- ✅ All error types display appropriate user messages
- ✅ Retry buttons work correctly

### Example Error Messages

**Network Error:**
```
⚠️ Network Error
Unable to load data due to a network problem.
Please check your internet connection and try again.
[Try Again]
```

**404 Not Found:**
```
⚠️ Data Not Found
The requested data file could not be found.
This may indicate a configuration issue.
```

**Server Error:**
```
⚠️ Server Error
The server encountered an error (503).
Please try again in a moment.
[Try Again]
```

### Files Modified

- `birdfinder/js/data.js`
- `birdfinder/js/browse.js`
- `birdfinder/js/species-detail.js`
- `birdfinder/js/this-week.js`
- `birdfinder/js/hotspots.js`
- `birdfinder/index.html`
- `birdfinder/browse.html`
- `birdfinder/species.html`
- `birdfinder/hotspots.html`

### Files Created

- `birdfinder/js/data-loader.js` (330 lines)
- `birdfinder/test-error-recovery.html` (test suite)

---

## Future Refactoring Tasks

Based on code review, the following improvements are recommended (in priority order):

### High Priority

1. ✅ **Extract duplicate valley detection code** to shared module (COMPLETED)
2. ✅ **Add input validation** throughout Python pipeline (COMPLETED)
3. ✅ **Create constants module** for magic numbers (thresholds, week ranges) (COMPLETED)
4. ✅ **Add error recovery** in JavaScript data loading (COMPLETED)
5. ⬜ **Fix XSS vulnerability** in markdown rendering
6. ⬜ **Add automated tests** for core algorithms

### Medium Priority

7. ⬜ **Create configuration system** for regions
8. ⬜ **Refactor long functions** in arrival/departure calculation
9. ⬜ **Add debouncing** to search inputs
10. ⬜ **Document data schemas** with TypeScript interfaces or JSON Schema

### Low Priority

11. ⬜ **Add data caching** with localStorage
12. ⬜ **Optimize SVG rendering** or switch to Canvas
13. ⬜ **Add accessibility features** (ARIA, keyboard nav)
14. ⬜ **Bundle and minify** JavaScript for production

---
