#!/usr/bin/env python3
"""
Unit tests for region configuration system.

Run with:
    python3 test_region_config.py
"""

import unittest
import json
import tempfile
from pathlib import Path
from region_config import (
    load_region_config,
    save_region_config,
    list_available_regions,
    RegionConfig,
    ConfigError,
    _validate_config
)


class TestRegionConfig(unittest.TestCase):
    """Test cases for region configuration loading and validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_root = Path(self.temp_dir.name)
        self.regions_dir = self.project_root / "regions"
        self.regions_dir.mkdir()

    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()

    def test_load_region_specific_config(self):
        """Test loading a region-specific config.json file."""
        # Create a region directory with config
        region_dir = self.regions_dir / "test_region"
        region_dir.mkdir()

        config_data = {
            "region_id": "test_region",
            "display_name": "Test Region",
            "description": "A test region",
            "ebird_region_code": "US-XX-123"
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        # Load the config
        config = load_region_config("test_region", self.project_root)

        # Verify
        self.assertEqual(config.region_id, "test_region")
        self.assertEqual(config.display_name, "Test Region")
        self.assertEqual(config.description, "A test region")
        self.assertEqual(config.ebird_region_code, "US-XX-123")

    def test_load_global_config(self):
        """Test loading from a global regions.json file."""
        # Create config directory
        config_dir = self.project_root / "config"
        config_dir.mkdir()

        # Create global config
        global_config = {
            "regions": {
                "region1": {
                    "display_name": "Region One",
                    "ebird_region_code": "US-AA-001"
                },
                "region2": {
                    "display_name": "Region Two",
                    "ebird_region_code": "US-BB-002"
                }
            }
        }

        config_path = config_dir / "regions.json"
        with open(config_path, 'w') as f:
            json.dump(global_config, f)

        # Load region1
        config = load_region_config("region1", self.project_root)
        self.assertEqual(config.region_id, "region1")
        self.assertEqual(config.display_name, "Region One")
        self.assertEqual(config.ebird_region_code, "US-AA-001")

        # Load region2
        config = load_region_config("region2", self.project_root)
        self.assertEqual(config.region_id, "region2")
        self.assertEqual(config.display_name, "Region Two")

    def test_load_fallback_to_defaults(self):
        """Test fallback to default config when no config file exists."""
        # Create region directory but no config
        region_dir = self.regions_dir / "no_config"
        region_dir.mkdir()

        # Load should succeed with defaults
        config = load_region_config("no_config", self.project_root)
        self.assertEqual(config.region_id, "no_config")
        self.assertEqual(config.display_name, "No Config")  # Titlecased

    def test_thresholds_override(self):
        """Test that region-specific thresholds can override defaults."""
        region_dir = self.regions_dir / "custom_thresholds"
        region_dir.mkdir()

        config_data = {
            "region_id": "custom_thresholds",
            "display_name": "Custom Thresholds Region",
            "thresholds": {
                "VALLEY_THRESHOLD_PEAK_RATIO": 0.20,
                "ARRIVAL_THRESHOLD_PEAK_RATIO": 0.15
            }
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = load_region_config("custom_thresholds", self.project_root)
        self.assertEqual(config.get_threshold("VALLEY_THRESHOLD_PEAK_RATIO"), 0.20)
        self.assertEqual(config.get_threshold("ARRIVAL_THRESHOLD_PEAK_RATIO"), 0.15)

    def test_seasonal_weeks_override(self):
        """Test that region-specific seasonal weeks can be configured."""
        region_dir = self.regions_dir / "custom_seasons"
        region_dir.mkdir()

        config_data = {
            "region_id": "custom_seasons",
            "display_name": "Custom Seasons Region",
            "seasonal_weeks": {
                "winter": {"start": 40, "end": 11},
                "summer": {"start": 20, "end": 32}
            }
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = load_region_config("custom_seasons", self.project_root)
        winter = config.get_seasonal_weeks("winter")
        self.assertEqual(winter["start"], 40)
        self.assertEqual(winter["end"], 11)

    def test_paths_configuration(self):
        """Test path pattern configuration."""
        region_dir = self.regions_dir / "custom_paths"
        region_dir.mkdir()

        config_data = {
            "region_id": "custom_paths",
            "display_name": "Custom Paths Region",
            "paths": {
                "input_pattern": "bird_data_*.txt",
                "output_file": "{region_id}_output.json"
            }
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = load_region_config("custom_paths", self.project_root)
        self.assertEqual(config.get_path("input_pattern"), "bird_data_*.txt")
        self.assertEqual(config.get_path("output_file"), "{region_id}_output.json")

    def test_display_settings(self):
        """Test display settings configuration."""
        region_dir = self.regions_dir / "display_settings"
        region_dir.mkdir()

        config_data = {
            "region_id": "display_settings",
            "display_name": "Display Settings Region",
            "display_settings": {
                "copyright_year": 2025,
                "theme_name": "Custom Theme"
            }
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        config = load_region_config("display_settings", self.project_root)
        self.assertEqual(config.get_display_setting("copyright_year"), 2025)
        self.assertEqual(config.get_display_setting("theme_name"), "Custom Theme")

    def test_save_region_config(self):
        """Test saving a region configuration."""
        region_dir = self.regions_dir / "save_test"
        region_dir.mkdir()

        config = RegionConfig(
            region_id="save_test",
            display_name="Save Test Region",
            description="Testing save functionality",
            ebird_region_code="US-TEST-999"
        )

        config_path = region_dir / "config.json"
        save_region_config(config, config_path)

        # Verify file was created
        self.assertTrue(config_path.exists())

        # Load it back
        loaded_config = load_region_config("save_test", self.project_root)
        self.assertEqual(loaded_config.region_id, "save_test")
        self.assertEqual(loaded_config.display_name, "Save Test Region")

    def test_list_available_regions(self):
        """Test listing available regions."""
        # Create several region directories
        (self.regions_dir / "region1").mkdir()
        (self.regions_dir / "region2").mkdir()
        (self.regions_dir / "region3").mkdir()

        regions = list_available_regions(self.project_root)
        self.assertEqual(set(regions), {"region1", "region2", "region3"})

    def test_validation_invalid_region_id(self):
        """Test that invalid region IDs are rejected."""
        config = RegionConfig(
            region_id="../etc/passwd",  # Path traversal attempt
            display_name="Evil Region"
        )
        with self.assertRaises(ConfigError):
            _validate_config(config)

    def test_validation_empty_display_name(self):
        """Test that empty display names are rejected."""
        config = RegionConfig(
            region_id="valid_id",
            display_name=""  # Empty
        )
        with self.assertRaises(ConfigError):
            _validate_config(config)

    def test_validation_negative_threshold(self):
        """Test that negative thresholds are rejected."""
        config = RegionConfig(
            region_id="test",
            display_name="Test",
            thresholds={"SOME_THRESHOLD": -0.1}
        )
        with self.assertRaises(ConfigError):
            _validate_config(config)

    def test_validation_invalid_seasonal_weeks(self):
        """Test that invalid seasonal week ranges are rejected."""
        config = RegionConfig(
            region_id="test",
            display_name="Test",
            seasonal_weeks={"winter": {"start": 50, "end": 5}}  # start > 47
        )
        with self.assertRaises(ConfigError):
            _validate_config(config)

    def test_missing_display_name_in_config(self):
        """Test that configs without display_name are rejected."""
        region_dir = self.regions_dir / "missing_name"
        region_dir.mkdir()

        config_data = {
            "region_id": "missing_name"
            # Missing display_name
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        with self.assertRaises(ConfigError):
            load_region_config("missing_name", self.project_root)

    def test_invalid_json(self):
        """Test that invalid JSON files raise ConfigError."""
        region_dir = self.regions_dir / "invalid_json"
        region_dir.mkdir()

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            f.write("{ invalid json }")

        with self.assertRaises(ConfigError):
            load_region_config("invalid_json", self.project_root)

    def test_region_id_mismatch(self):
        """Test that mismatched region IDs are caught."""
        region_dir = self.regions_dir / "mismatch"
        region_dir.mkdir()

        config_data = {
            "region_id": "different_id",  # Doesn't match directory name
            "display_name": "Mismatch Test"
        }

        config_path = region_dir / "config.json"
        with open(config_path, 'w') as f:
            json.dump(config_data, f)

        with self.assertRaises(ConfigError):
            load_region_config("mismatch", self.project_root)


class TestRegionConfigGetters(unittest.TestCase):
    """Test RegionConfig getter methods with defaults."""

    def test_get_threshold_with_default(self):
        """Test getting threshold with default value."""
        config = RegionConfig(
            region_id="test",
            display_name="Test"
        )
        # Threshold not set, should return default
        self.assertEqual(config.get_threshold("NONEXISTENT", 0.5), 0.5)

    def test_get_path_with_default(self):
        """Test getting path with default value."""
        config = RegionConfig(
            region_id="test",
            display_name="Test"
        )
        self.assertEqual(config.get_path("input_pattern", "default.txt"), "default.txt")

    def test_get_seasonal_weeks_nonexistent(self):
        """Test getting nonexistent seasonal week range."""
        config = RegionConfig(
            region_id="test",
            display_name="Test"
        )
        self.assertIsNone(config.get_seasonal_weeks("winter"))

    def test_get_display_setting_with_default(self):
        """Test getting display setting with default."""
        config = RegionConfig(
            region_id="test",
            display_name="Test"
        )
        self.assertEqual(config.get_display_setting("theme", "default"), "default")


def run_tests():
    """Run all tests and print results."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestRegionConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestRegionConfigGetters))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "="*70)
    print("Region Configuration Tests - Summary")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED")
        return 0
    else:
        print("\n✗ SOME TESTS FAILED")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_tests())
