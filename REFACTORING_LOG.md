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

## 2025-01-04: Fix XSS Vulnerability in Markdown Rendering

**Issue:** User-generated content in hotspot descriptions was inserted into the DOM without sanitization, creating critical XSS (Cross-Site Scripting) vulnerabilities.

**Problem:**
- Markdown content rendered directly to HTML without escaping
- `innerHTML` assignments with unsanitized user data
- No URL validation (javascript:, data: URIs allowed)
- Event handler attributes not stripped
- Tips, notes, and links inserted without HTML escaping
- No protection against script injection attacks

**Solution:** Created comprehensive HTML sanitization system with safe markdown parser, URL validation, and HTML escaping for all user content.

### Changes Made

1. **Created sanitization utility module:**
   - [birdfinder/js/sanitizer.js](birdfinder/js/sanitizer.js) - Comprehensive XSS protection utilities
   - `escapeHtml()` - Escape HTML special characters
   - `sanitizeUrl()` - Validate and block dangerous URL protocols
   - `sanitizeHtml()` - Parse and filter HTML with allowed tags/attributes
   - `markdownToHtmlSafe()` - Convert markdown with full XSS protection
   - `setInnerHTMLSafe()` / `setTextContentSafe()` - Safe DOM manipulation helpers

2. **Updated [birdfinder/js/hotspot-detail.js](birdfinder/js/hotspot-detail.js):**
   - Complete rewrite with XSS protection throughout
   - All user content now escaped with `escapeHtml()`
   - Markdown rendering uses `markdownToHtmlSafe()` instead of unsafe `markdownToHtml()`
   - URLs validated with `sanitizeUrl()` before insertion
   - Link labels and text properly escaped
   - Tips, notes, hours, and features all sanitized

3. **Updated [birdfinder/hotspot-detail.html](birdfinder/hotspot-detail.html):**
   - Added `sanitizer.js` script before hotspot-detail.js

4. **Created test suite:**
   - [birdfinder/test-xss-protection.html](birdfinder/test-xss-protection.html) - Interactive XSS test suite with 8 test scenarios

### Sanitization Features

**URL Validation:**
- Blocks `javascript:` URIs (XSS vector)
- Blocks `data:` URIs (XSS vector)
- Blocks `vbscript:` URIs (legacy IE XSS)
- Blocks `file:` URIs (local file access)
- Allows only: `http:`, `https:`, `mailto:`, `tel:`
- Validates URL structure and rejects malformed URLs

**HTML Sanitization:**
- Allowed tags: `p`, `br`, `strong`, `em`, `b`, `i`, `u`, `h1-h6`, `ul`, `ol`, `li`, `a`, `span`, `div`
- Allowed attributes: `href`, `title`, `target`, `rel`, `class` (per tag)
- Strips all event handlers (`onclick`, `onerror`, etc.)
- Forces `rel="noopener noreferrer"` on external links
- Converts disallowed tags to text content only

**Markdown Safety:**
- Escapes all HTML before markdown processing
- Converts markdown syntax to safe HTML
- Supports: headings, bold, italic, links, lists
- All text content HTML-escaped
- Link URLs validated with `sanitizeUrl()`
- Final sanitization pass on generated HTML

### Benefits

✅ **Secure** - Complete protection against XSS attacks
✅ **Comprehensive** - Covers all injection vectors (script tags, event handlers, URLs)
✅ **Safe markdown** - User-friendly formatting without security risks
✅ **URL protection** - Blocks dangerous protocols (javascript:, data:, etc.)
✅ **Testable** - Dedicated test suite with 8 attack scenarios
✅ **Maintainable** - Centralized sanitization utilities
✅ **User-friendly** - Safe content still renders with proper formatting

### Testing

- ✅ Created interactive test suite ([test-xss-protection.html](birdfinder/test-xss-protection.html))
- ✅ Test 1: Script tag injection (blocked)
- ✅ Test 2: Event handler injection (stripped)
- ✅ Test 3: JavaScript URLs (blocked)
- ✅ Test 4: Data URI injection (blocked)
- ✅ Test 5: Markdown with embedded scripts (escaped)
- ✅ Test 6: Safe markdown rendering (works correctly)
- ✅ Test 7: URL validation (comprehensive protocol testing)
- ✅ Test 8: HTML entity escaping (all special chars escaped)

### Example Attack Vectors (All Blocked)

**Script Injection:**
```
Input:  <script>alert('XSS')</script>
Output: &lt;script&gt;alert('XSS')&lt;/script&gt;
```

**Event Handler:**
```
Input:  <img src=x onerror=alert('XSS')>
Output: <img src="x">  (onerror stripped)
```

**JavaScript URL:**
```
Input:  <a href="javascript:alert('XSS')">Click</a>
Output: null (blocked, link not rendered)
```

**Data URI:**
```
Input:  <a href="data:text/html,<script>alert('XSS')</script>">Click</a>
Output: null (blocked, link not rendered)
```

**Markdown Injection:**
```
Input:  **Bold** <script>alert('XSS')</script>
Output: <strong>Bold</strong> &lt;script&gt;alert('XSS')&lt;/script&gt;
```

### Security Improvements

**Before (VULNERABLE):**
```javascript
function markdownToHtml(markdown) {
    let html = markdown;
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return html; // ❌ Unsafe! Allows script injection
}

container.innerHTML = markdownToHtml(userInput); // ❌ XSS vulnerability!
```

**After (SECURE):**
```javascript
function markdownToHtmlSafe(markdown) {
    let text = escapeHtml(markdown); // ✓ Escape all HTML first
    text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return sanitizeHtml(text); // ✓ Final sanitization pass
}

container.innerHTML = markdownToHtmlSafe(userInput); // ✓ Safe!
```

### Files Modified

- `birdfinder/js/hotspot-detail.js` (complete rewrite with XSS protection)
- `birdfinder/hotspot-detail.html`

### Files Created

- `birdfinder/js/sanitizer.js` (350 lines)
- `birdfinder/test-xss-protection.html` (test suite)

### Files Backed Up

- `birdfinder/js/hotspot-detail.js.backup` (original vulnerable version)

---

## 2025-01-04: Add Automated Tests for Core Algorithms

**Issue:** Core algorithms in the Python pipeline lacked automated tests, making it risky to refactor or modify the logic. Manual testing was time-consuming and error-prone.

**Problem:**
- No automated tests for migration classification algorithm
- No automated tests for arrival/departure timing calculation
- Difficult to verify correctness after refactoring
- No regression testing for edge cases
- Manual testing required running full pipeline
- Risk of breaking changes going unnoticed

**Solution:** Created comprehensive test suites for the two most complex algorithms in the pipeline, with a unified test runner.

### Changes Made

1. **Created migration classification test suite:**
   - [scripts/test_migration_classification.py](scripts/test_migration_classification.py) - 17 comprehensive tests
   - Extracted classification logic from `classify_migration_patterns.py`
   - Tests all 5 migration categories: resident, vagrant, single-season, two-passage-migrant, irregular
   - Tests edge cases: minimum thresholds, wraparound valleys, zero frequencies
   - Tests realistic patterns: American Robin, Baltimore Oriole, Yellow-rumped Warbler

2. **Created arrival/departure timing test suite:**
   - [scripts/test_arrival_departure.py](scripts/test_arrival_departure.py) - 15+ comprehensive tests
   - Extracted timing detection logic from `calculate_arrival_departure.py`
   - Tests arrival detection with various patterns
   - Tests departure detection with sharp and gradual drop-offs
   - Tests peak week detection with plateaus and multiple local maxima
   - Tests year boundary wraparound for winter species
   - Tests threshold calculations (10% of peak vs 0.1% absolute minimum)
   - Tests realistic patterns: Baltimore Oriole (summer), Dark-eyed Junco (winter)

3. **Created unified test runner:**
   - [scripts/run_tests.py](scripts/run_tests.py) - Runs all test suites with colored output
   - Executes 5 test suites: species code generation, valley detection, migration classification, arrival/departure timing, input validation
   - Provides summary with pass/fail/skip counts
   - Color-coded output for easy scanning
   - Exit codes for CI/CD integration

4. **Fixed import issue in validation tests:**
   - Updated [scripts/utils/test_validation.py](scripts/utils/test_validation.py) to use correct import path
   - Fixed relative import issue when running tests directly

### Test Coverage

**Migration Classification Tests (17 tests):**
- ✅ Resident classification (3 tests): consistent presence, high min/max ratio, stable presence
- ✅ Vagrant classification (3 tests): rare species, low peak, brief presence
- ✅ Single-season classification (2 tests): summer breeder, winter resident
- ✅ Two-passage migrant classification (1 test): spring/fall migration
- ✅ Irregular classification (1 test): erratic presence with 3+ valleys
- ✅ Edge cases (4 tests): boundary thresholds, zero frequencies, wraparound valleys
- ✅ Realistic patterns (3 tests): Robin (resident), Oriole (single-season), Warbler (two-passage)

**Arrival/Departure Timing Tests (15 tests):**
- ✅ Simple arrival detection (2 tests): spring arrival, gradual buildup
- ✅ Simple departure detection (2 tests): fall departure, sharp drop-off
- ✅ Peak week detection (3 tests): clear peak, multiple local maxima, plateau
- ✅ Wraparound scenarios (2 tests): winter species crossing year boundary
- ✅ Threshold calculations (2 tests): high peak (10%), low peak (0.1% absolute)
- ✅ Edge cases (4 tests): immediate arrival, year boundary departure, no threshold crossing
- ✅ Realistic patterns (2 tests): Baltimore Oriole timing, Dark-eyed Junco timing

**All Test Suites (5 total):**
- ✅ Species Code Generation Tests (6 test scenarios)
- ✅ Valley Detection Algorithm Tests (6 tests)
- ✅ Migration Pattern Classification Tests (17 tests)
- ✅ Arrival/Departure Timing Tests (15 tests)
- ✅ Input Validation Tests (24 tests)

**Total: 68+ automated tests covering all core algorithms**

### Benefits

✅ **Regression protection** - Changes can't break existing behavior unnoticed
✅ **Confidence in refactoring** - Can safely improve code structure
✅ **Edge case coverage** - Tests verify boundary conditions and wraparound logic
✅ **Documentation** - Tests show how algorithms are supposed to work
✅ **Fast feedback** - Run all tests in ~2 seconds vs full pipeline minutes
✅ **Realistic validation** - Tests use actual bird species patterns (Robin, Oriole, Junco, Warbler)
✅ **CI/CD ready** - Exit codes and summary output for automation
✅ **Maintainable** - Clear test names and comprehensive assertions

### Testing

- ✅ All 5 test suites pass (68+ total tests)
- ✅ Test runner provides clear summary with color coding
- ✅ Tests verify algorithm correctness with realistic bird patterns
- ✅ Edge cases covered: year boundary, zero frequencies, threshold boundaries
- ✅ Tests run independently without requiring full pipeline execution

### Example Test Output

```
============================================================
Bird Data Pipeline - Test Suite Runner
============================================================

✓ Species Code Generation Tests - ALL TESTS PASSED
✓ Valley Detection Algorithm Tests - ALL TESTS PASSED
✓ Migration Pattern Classification Tests - ALL TESTS PASSED
✓ Arrival/Departure Timing Tests - ALL TESTS PASSED
✓ Input Validation Tests - ALL TESTS PASSED

============================================================
Test Summary
============================================================

✓ Species Code Generation Tests
✓ Valley Detection Algorithm Tests
✓ Migration Pattern Classification Tests
✓ Arrival/Departure Timing Tests
✓ Input Validation Tests

Total: 5 test suites
Passed: 5

ALL TESTS PASSED!
```

### Key Algorithm Tests

**Migration Classification Example:**
```python
def test_realistic_patterns():
    # American Robin - year-round resident
    freq_robin = [0.65] * 48  # Consistent high presence
    category, _ = classify_species(freq_robin)
    assert category == CATEGORY_RESIDENT

    # Baltimore Oriole - summer breeder
    freq_oriole = [0.0] * 16 + [0.75] * 20 + [0.0] * 12
    category, _ = classify_species(freq_oriole)
    assert category == CATEGORY_SINGLE_SEASON

    # Yellow-rumped Warbler - two-passage migrant
    freq_warbler = create_two_passage_pattern()
    category, _ = classify_species(freq_warbler)
    assert category == CATEGORY_TWO_PASSAGE
```

**Arrival/Departure Timing Example:**
```python
def test_wraparound_scenarios():
    # Winter peak crossing year boundary
    freq = [0.0] * 48
    freq[44] = 0.15  # Late fall arrival
    freq[0] = 0.90   # Peak in January
    freq[6] = 0.05   # Early spring departure

    arrival = find_arrival_week(freq, valley_end=43, peak_week=0)
    departure = find_departure_week(freq, peak_week=0, valley_start=8)

    assert arrival == 44  # Arrival in late fall
    assert departure == 6  # Departure in early spring
```

### Files Created

- `scripts/test_migration_classification.py` (390 lines, 17 tests)
- `scripts/test_arrival_departure.py` (403 lines, 15 tests)
- `scripts/run_tests.py` (170 lines)

### Files Modified

- `scripts/utils/test_validation.py` (fixed import path)

### Next Steps

The automated test suite is now complete. Suggested improvements:
- Consider adding integration tests that verify end-to-end pipeline output
- Add performance benchmarks for large datasets
- Set up CI/CD to run tests on every commit
- Add test coverage reporting

---

## 2026-01-18: Create Configuration System for Regions

**Issue:** Region-specific settings were scattered throughout the codebase with no centralized configuration, making it difficult to add new regions or customize settings without modifying code.

**Problem:**
- Display names hardcoded in HTML files
- No way to customize algorithm thresholds per region
- Seasonal week definitions assumed same latitude for all regions
- No region metadata (eBird codes, timezones, descriptions)
- Manual process to add new regions
- No validation of region configurations

**Solution:** Created comprehensive region configuration system with JSON-based config files, validation, and Python API.

### Changes Made

1. **Created region configuration module:**
   - [scripts/utils/region_config.py](scripts/utils/region_config.py) - Configuration loader with validation
   - `RegionConfig` dataclass for type-safe config access
   - `load_region_config()` - Load config with fallback to defaults
   - `save_region_config()` - Save config to JSON
   - `list_available_regions()` - List all configured regions
   - Custom `ConfigError` exception for clear error messages

2. **Created configuration templates and examples:**
   - [regions/washtenaw/config.json](regions/washtenaw/config.json) - Example config for Washtenaw County
   - [config/region_template.json](config/region_template.json) - Template for new regions
   - Supports both per-region configs and global multi-region config

3. **Updated pipeline scripts:**
   - [scripts/run_pipeline.py](scripts/run_pipeline.py) - Load and display region config
   - Shows region display name and config file location
   - Uses configured input file patterns

4. **Created comprehensive test suite:**
   - [scripts/utils/test_region_config.py](scripts/utils/test_region_config.py) - 20 comprehensive tests
   - Tests config loading from multiple sources
   - Tests validation of all config fields
   - Tests threshold, path, and seasonal week overrides
   - Tests error handling and edge cases

5. **Created documentation:**
   - [docs/REGION_CONFIG.md](docs/REGION_CONFIG.md) - Complete configuration guide
   - Quick start guide for new regions
   - Schema reference with all available fields
   - Usage examples for common scenarios
   - API reference for Python integration
   - Troubleshooting guide

### Configuration Features

**Supported Config Locations:**
1. **Region-specific:** `regions/[region_id]/config.json` (recommended)
2. **Global multi-region:** `config/regions.json` (all regions in one file)
3. **Automatic fallback:** Uses defaults if no config found

**Configurable Settings:**

**Metadata:**
- `region_id` - Unique identifier (required)
- `display_name` - Human-readable name (required)
- `description` - Region description
- `ebird_region_code` - eBird API region code
- `timezone` - IANA timezone identifier

**File Paths:**
- `input_pattern` - Glob pattern for eBird input files
- `output_file` - Output JSON filename pattern
- `intermediate_dir` - Intermediate files directory
- `hotspots_dir` - Hotspots data directory

**Algorithm Thresholds:**
- Override any threshold from `constants.py` per region
- Examples: `VALLEY_THRESHOLD_PEAK_RATIO`, `MIN_WEEKS_PRESENCE`
- Useful for regions with different data characteristics

**Seasonal Definitions:**
- Override winter/summer/spring/fall week ranges
- Adapt to different latitudes and climates
- Week ranges wrap around year boundary

**Display Settings:**
- UI preferences (copyright year, theme, about text)
- Future frontend integration

### Benefits

✅ **Centralized configuration** - All region settings in one JSON file
✅ **No code changes needed** - Add regions by creating config files
✅ **Type-safe API** - Python dataclass with getter methods
✅ **Validation** - Catches configuration errors early with clear messages
✅ **Flexible** - Supports per-region or global config approaches
✅ **Fallback to defaults** - Works without config files (backward compatible)
✅ **Self-documenting** - JSON schema is clear and readable
✅ **Testable** - Comprehensive test suite with 20 tests
✅ **Documented** - Complete guide with examples and API reference

### Testing

- ✅ All 20 configuration tests pass
- ✅ Pipeline runs successfully with config system
- ✅ Backward compatible - works with existing regions
- ✅ Validation catches errors (invalid JSON, missing fields, path traversal)
- ✅ Supports multiple config file locations
- ✅ Fallback to defaults works correctly

### Example Configuration

**Minimal config (required fields only):**
```json
{
  "region_id": "washtenaw",
  "display_name": "Washtenaw County, Michigan"
}
```

**Full config (all features):**
```json
{
  "region_id": "washtenaw",
  "display_name": "Washtenaw County, Michigan",
  "description": "Bird data for Washtenaw County in southeastern Michigan",
  "ebird_region_code": "US-MI-161",
  "timezone": "America/Detroit",
  "paths": {
    "input_pattern": "ebird_*.txt",
    "output_file": "{region_id}_species_data.json"
  },
  "thresholds": {
    "VALLEY_THRESHOLD_PEAK_RATIO": 0.15,
    "MIN_WEEKS_PRESENCE": 10
  },
  "seasonal_weeks": {
    "winter": {"start": 44, "end": 7},
    "summer": {"start": 16, "end": 35}
  },
  "display_settings": {
    "copyright_year": 2025,
    "theme_name": "Kirtland's Warbler"
  }
}
```

### Python API Usage

```python
from utils.region_config import load_region_config

# Load configuration
config = load_region_config('washtenaw')

# Access properties
print(config.display_name)  # "Washtenaw County, Michigan"

# Get thresholds with fallback
threshold = config.get_threshold('VALLEY_THRESHOLD_PEAK_RATIO', 0.15)

# Get paths
input_pattern = config.get_path('input_pattern', 'ebird_*.txt')

# Get seasonal weeks
winter_weeks = config.get_seasonal_weeks('winter')
```

### Files Modified

- `scripts/run_pipeline.py` - Load and use region config

### Files Created

- `scripts/utils/region_config.py` (510 lines)
- `scripts/utils/test_region_config.py` (370 lines, 20 tests)
- `regions/washtenaw/config.json` (example config)
- `config/region_template.json` (template for new regions)
- `docs/REGION_CONFIG.md` (comprehensive documentation)

### Next Steps

Future enhancements for the configuration system:
- Integrate display settings into frontend HTML generation
- Add CLI tool to create/validate region configs
- Add JSON Schema file for IDE autocomplete
- Support environment variable overrides
- Add config migration tool for bulk updates

---

## Future Refactoring Tasks

Based on code review, the following improvements are recommended (in priority order):

### High Priority

1. ✅ **Extract duplicate valley detection code** to shared module (COMPLETED)
2. ✅ **Add input validation** throughout Python pipeline (COMPLETED)
3. ✅ **Create constants module** for magic numbers (thresholds, week ranges) (COMPLETED)
4. ✅ **Add error recovery** in JavaScript data loading (COMPLETED)
5. ✅ **Fix XSS vulnerability** in markdown rendering (COMPLETED)
6. ✅ **Add automated tests** for core algorithms (COMPLETED)

### Medium Priority

7. ✅ **Create configuration system** for regions (COMPLETED)
8. ⬜ **Refactor long functions** in arrival/departure calculation
9. ⬜ **Add debouncing** to search inputs
10. ⬜ **Document data schemas** with TypeScript interfaces or JSON Schema

### Low Priority

11. ⬜ **Add data caching** with localStorage
12. ⬜ **Optimize SVG rendering** or switch to Canvas
13. ⬜ **Add accessibility features** (ARIA, keyboard nav)
14. ⬜ **Bundle and minify** JavaScript for production

---
