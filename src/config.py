from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse
import re


MIN_DEPTH = 1
PACKAGE_RE = re.compile(r"^[a-z0-9][a-z0-9+.-]*$")
ALLOWED_SCHEMES = {"http", "https"}


class ConfigError(ValueError):
    """Raised when a CLI option is invalid."""


@dataclass(frozen=True)
class Config:
    """Validated configuration for the tool."""

    package: str
    repo: str
    test_mode: bool
    version: str
    max_depth: int


def validate_config(config: Config) -> None:
    """Validate all user-configurable parameters."""
    _validate_package(config.package)
    _validate_version(config.version)
    _validate_depth(config.max_depth)
    _validate_repo(config.repo, config.test_mode)


def _validate_package(package: str) -> None:
    if not PACKAGE_RE.fullmatch(package):
        raise ConfigError(
            "package must match Debian package name format"
        )


def _validate_version(version: str) -> None:
    if not version or any(ch.isspace() for ch in version):
        raise ConfigError(
            "version must be non-empty and contain no spaces"
        )


def _validate_depth(depth: int) -> None:
    if depth < MIN_DEPTH:
        raise ConfigError("max-depth must be a positive integer")


def _validate_repo(repo: str, test_mode: bool) -> None:
    if not repo:
        raise ConfigError("repo must not be empty")
    if test_mode:
        if not Path(repo).is_file():
            raise ConfigError("test repository file not found")
        return
    parsed = urlparse(repo)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ConfigError(
            "repo must be an http(s) URL or a test file path"
        )