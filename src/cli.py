"""Command line interface for stages 1 and 2."""

import argparse
import sys

from .apt_index import AptIndexError, direct_dependencies, read_index
from .config import Config, ConfigError, validate_config


STAGE_ONE = 1
STAGE_TWO = 2


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Dependency graph tool, stages 1 and 2"
    )
    parser.add_argument("--package", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--max-depth", type=int, required=True)
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument(
        "--stage",
        type=int,
        choices=(STAGE_ONE, STAGE_TWO),
        default=STAGE_ONE,
    )
    return parser


def config_from_args(args: argparse.Namespace) -> Config:
    """Convert parsed CLI arguments into Config."""
    return Config(
        package=args.package,
        repo=args.repo,
        test_mode=args.test_mode,
        version=args.version,
        max_depth=args.max_depth,
    )


def print_config(config: Config) -> None:
    """Print all user-configurable parameters."""
    print(f"package={config.package}")
    print(f"repo={config.repo}")
    print(f"test_mode={str(config.test_mode).lower()}")
    print(f"version={config.version}")
    print(f"max_depth={config.max_depth}")


def run_stage_two(config: Config) -> None:
    """Print direct dependencies for the configured package."""
    text = read_index(config.repo, config.test_mode)
    deps = direct_dependencies(
        text,
        config.package,
        config.version,
    )
    for dep in deps:
        print(dep)


def main(argv: list[str] | None = None) -> int:
    """Run the CLI."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        config = config_from_args(args)
        validate_config(config)
        if args.stage == STAGE_ONE:
            print_config(config)
        else:
            run_stage_two(config)
    except (ConfigError, AptIndexError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())