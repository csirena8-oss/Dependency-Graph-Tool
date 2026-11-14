"""Tests for configuration validation."""

from pathlib import Path
import unittest

from src.config import Config, ConfigError, validate_config


class ConfigTests(unittest.TestCase):
    """Configuration validation tests."""

    def make_config(self, **overrides) -> Config:
        data = {
            "package": "app",
            "repo": "https://example.com/Packages.gz",
            "test_mode": False,
            "version": "1.0",
            "max_depth": 3,
        }
        data.update(overrides)
        return Config(**data)

    def test_valid_remote_config(self) -> None:
        validate_config(self.make_config())

    def test_invalid_package_name(self) -> None:
        with self.assertRaises(ConfigError):
            validate_config(self.make_config(package="Bad Name"))

    def test_invalid_version(self) -> None:
        with self.assertRaises(ConfigError):
            validate_config(self.make_config(version="1.0 beta"))

    def test_invalid_depth(self) -> None:
        with self.assertRaises(ConfigError):
            validate_config(self.make_config(max_depth=0))

    def test_invalid_remote_url(self) -> None:
        with self.assertRaises(ConfigError):
            validate_config(self.make_config(repo="ftp://example.com"))

    def test_missing_test_file(self) -> None:
        with self.assertRaises(ConfigError):
            validate_config(
                self.make_config(
                    repo="missing.file",
                    test_mode=True,
                )
            )

    def test_existing_test_file(self) -> None:
        target = Path(__file__).parent.parent / "README.md"
        validate_config(
            self.make_config(
                repo=str(target),
                test_mode=True,
            )
        )