"""Tests for apt Packages index parsing."""

from pathlib import Path
import unittest

from src.apt_index import (
    AptIndexError,
    direct_dependencies,
    parse_depends,
    parse_stanzas,
)


FIXTURE = Path(__file__).parent / "fixtures" / "Packages"


class AptIndexTests(unittest.TestCase):
    """Apt index parsing tests."""

    def read_fixture(self) -> str:
        return FIXTURE.read_text(encoding="utf-8")

    def test_parse_depends(self) -> None:
        value = "liba (>= 1.0), libb | libc, libd:any"
        self.assertEqual(
            parse_depends(value),
            ["liba", "libb", "libd"],
        )

    def test_parse_empty_depends(self) -> None:
        self.assertEqual(parse_depends(""), [])

    def test_parse_stanzas(self) -> None:
        stanzas = parse_stanzas(self.read_fixture())
        self.assertEqual(len(stanzas), 4)
        self.assertEqual(stanzas[0]["Package"], "app")

    def test_direct_dependencies(self) -> None:
        deps = direct_dependencies(
            self.read_fixture(),
            "app",
            "1.0",
        )
        self.assertEqual(deps, ["liba", "libb", "libd"])

    def test_missing_package(self) -> None:
        with self.assertRaises(AptIndexError):
            direct_dependencies(
                self.read_fixture(),
                "missing",
                "1.0",
            )