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