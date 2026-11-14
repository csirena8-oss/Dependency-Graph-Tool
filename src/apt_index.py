"""Read Ubuntu apt Packages indexes without apt tools."""

import gzip
import lzma
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen


HTTP_TIMEOUT = 30
GZIP_MAGIC = b"\x1f\x8b"
XZ_MAGIC = b"\xfd7zXZ\x00"
INDEX_NAMES = ("Packages", "Packages.gz", "Packages.xz")


class AptIndexError(ValueError):
    """Raised when an apt index cannot be read or parsed."""


def read_index(location: str, test_mode: bool) -> str:
    """Read an apt Packages index from a file or URL."""
    if test_mode:
        data = Path(location).read_bytes()
        return decode_index(data, location)
    last_error = None
    for url in candidate_urls(location):
        try:
            with urlopen(url, timeout=HTTP_TIMEOUT) as response:
                data = response.read()
            return decode_index(data, url)
        except (URLError, OSError) as exc:
            last_error = exc
    raise AptIndexError(f"cannot read index: {last_error}")


def candidate_urls(url: str) -> list[str]:
    """Return candidate index URLs for a repository URL."""
    if url.endswith(INDEX_NAMES):
        return [url]
    base = url.rstrip("/") + "/"
    return [base + name for name in INDEX_NAMES]


def decode_index(data: bytes, name: str) -> str:
    """Decode plain, gzip or xz Packages index data."""
    try:
        if data.startswith(GZIP_MAGIC):
            data = gzip.decompress(data)
        elif data.startswith(XZ_MAGIC):
            data = lzma.decompress(data)
        return data.decode("utf-8")
    except (OSError, lzma.LZMAError, UnicodeDecodeError) as exc:
        raise AptIndexError(f"cannot decode {name}: {exc}") from exc

def parse_stanzas(text: str) -> list[dict[str, str]]:
    """Parse Packages index text into stanzas."""
    stanzas: list[dict[str, str]] = []
    current: dict[str, str] = {}
    last_key = None
    for line in text.splitlines():
        if not line.strip():
            if current:
                stanzas.append(current)
                current = {}
                last_key = None
            continue
        if line[0].isspace() and last_key:
            current[last_key] += "\n" + line.strip()
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise AptIndexError(f"invalid index line: {line}")
        last_key = key.strip()
        current[last_key] = value.strip()
    if current:
        stanzas.append(current)
    return stanzas


def parse_depends(value: str) -> list[str]:
    """Extract dependency names from an apt Depends field."""
    result: list[str] = []
    if not value.strip():
        return result
    for group in value.split(","):
        first = group.split("|", 1)[0].strip()
        name = first.split("(", 1)[0].strip()
        name = name.split(":", 1)[0].strip()
        if name and name not in result:
            result.append(name)
    return result


def find_package(
    stanzas: list[dict[str, str]],
    name: str,
    version: str,
) -> dict[str, str]:
    """Find a package stanza by name and version."""
    for stanza in stanzas:
        if (
            stanza.get("Package") == name
            and stanza.get("Version") == version
        ):
            return stanza
    raise AptIndexError(
        f"package {name} version {version} not found"
    )


def direct_dependencies(
    text: str,
    name: str,
    version: str,
) -> list[str]:
    """Return direct dependencies for a package."""
    stanzas = parse_stanzas(text)
    stanza = find_package(stanzas, name, version)
    return parse_depends(stanza.get("Depends", ""))