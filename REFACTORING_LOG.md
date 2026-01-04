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

## Future Refactoring Tasks

Based on code review, the following improvements are recommended (in priority order):

### High Priority

1. ✅ **Extract duplicate valley detection code** to shared module (COMPLETED)
2. ✅ **Add input validation** throughout Python pipeline (COMPLETED)
3. ⬜ **Create constants module** for magic numbers (thresholds, week ranges)
4. ⬜ **Add error recovery** in JavaScript data loading
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
