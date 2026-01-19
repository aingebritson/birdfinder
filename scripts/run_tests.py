#!/usr/bin/env python3
"""
Unified Test Runner - Executes all test suites for the bird data pipeline

Runs all automated tests and provides a summary of results.
"""

import sys
import subprocess
from pathlib import Path


# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def run_test_suite(test_file, description):
    """
    Run a single test suite and return success status.

    Args:
        test_file: Path to test file
        description: Human-readable description of test suite

    Returns:
        True if all tests passed, False otherwise
    """
    print(f"\n{Colors.BLUE}{Colors.BOLD}Running: {description}{Colors.END}")
    print(f"File: {test_file}")
    print("─" * 60)

    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Print output
        if result.stdout:
            print(result.stdout)

        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ {description} - ALL TESTS PASSED{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}✗ {description} - TESTS FAILED{Colors.END}")
            if result.stderr:
                print(f"\n{Colors.RED}Error output:{Colors.END}")
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"{Colors.RED}✗ {description} - TIMEOUT{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.RED}✗ {description} - ERROR: {e}{Colors.END}")
        return False


def main():
    """Run all test suites and print summary."""
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("Bird Data Pipeline - Test Suite Runner")
    print(f"{'=' * 60}{Colors.END}\n")

    # Define all test suites
    test_suites = [
        {
            'file': 'test_species_code_generation.py',
            'description': 'Species Code Generation Tests'
        },
        {
            'file': 'utils/test_valley_detection.py',
            'description': 'Valley Detection Algorithm Tests'
        },
        {
            'file': 'test_migration_classification.py',
            'description': 'Migration Pattern Classification Tests'
        },
        {
            'file': 'test_arrival_departure.py',
            'description': 'Arrival/Departure Timing Tests'
        },
        {
            'file': 'utils/test_validation.py',
            'description': 'Input Validation Tests'
        },
        {
            'file': 'utils/test_region_config.py',
            'description': 'Region Configuration Tests'
        },
        {
            'file': 'utils/test_timing_helpers.py',
            'description': 'Timing Helper Functions Tests'
        }
    ]

    results = []
    scripts_dir = Path(__file__).parent

    # Run each test suite
    for suite in test_suites:
        test_path = scripts_dir / suite['file']

        # Check if test file exists
        if not test_path.exists():
            print(f"\n{Colors.YELLOW}⚠ Skipping: {suite['description']}{Colors.END}")
            print(f"File not found: {suite['file']}")
            results.append({
                'name': suite['description'],
                'status': 'skipped'
            })
            continue

        # Run the test
        passed = run_test_suite(test_path, suite['description'])
        results.append({
            'name': suite['description'],
            'status': 'passed' if passed else 'failed'
        })

    # Print summary
    print(f"\n{Colors.BOLD}{'=' * 60}")
    print("Test Summary")
    print(f"{'=' * 60}{Colors.END}\n")

    passed_count = sum(1 for r in results if r['status'] == 'passed')
    failed_count = sum(1 for r in results if r['status'] == 'failed')
    skipped_count = sum(1 for r in results if r['status'] == 'skipped')
    total_count = len(results)

    for result in results:
        status_symbol = {
            'passed': f"{Colors.GREEN}✓{Colors.END}",
            'failed': f"{Colors.RED}✗{Colors.END}",
            'skipped': f"{Colors.YELLOW}⚠{Colors.END}"
        }[result['status']]

        print(f"{status_symbol} {result['name']}")

    print(f"\n{Colors.BOLD}Total: {total_count} test suites{Colors.END}")
    print(f"{Colors.GREEN}Passed: {passed_count}{Colors.END}")
    if failed_count > 0:
        print(f"{Colors.RED}Failed: {failed_count}{Colors.END}")
    if skipped_count > 0:
        print(f"{Colors.YELLOW}Skipped: {skipped_count}{Colors.END}")

    # Exit with appropriate code
    if failed_count > 0:
        print(f"\n{Colors.RED}{Colors.BOLD}TESTS FAILED{Colors.END}")
        sys.exit(1)
    elif passed_count == total_count:
        print(f"\n{Colors.GREEN}{Colors.BOLD}ALL TESTS PASSED!{Colors.END}")
        sys.exit(0)
    else:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}TESTS COMPLETED WITH WARNINGS{Colors.END}")
        sys.exit(0)


if __name__ == "__main__":
    main()
