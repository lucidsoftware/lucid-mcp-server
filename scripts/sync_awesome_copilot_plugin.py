#!/usr/bin/env python3
"""Generate the awesome-copilot plugin directory (awesome-copilot/) from lucid/.

awesome-copilot rejects plugins whose manifest lists more than 10 keywords, while
the other marketplaces benefit from the full list. lucid/ stays the source of truth:
this script mirrors it into awesome-copilot/ and trims "keywords" to the first
MAX_KEYWORDS entries, so put the most important tags first in lucid/plugin.json.

Usage:
    python scripts/sync_awesome_copilot_plugin.py sync    # rewrite awesome-copilot/
    python scripts/sync_awesome_copilot_plugin.py check   # exit 1 if awesome-copilot/ is out of date
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_DIR = REPO_ROOT / "lucid"
TARGET_DIR = REPO_ROOT / "awesome-copilot"
MANIFEST = "plugin.json"
MAX_KEYWORDS = 10
MAX_KEYWORD_LENGTH = 30
KEYWORD_PATTERN = re.compile(r"^[a-z0-9-]+$")


class SyncError(Exception):
    pass


def awesome_copilot_manifest(source_manifest: Path) -> str:
    """Return the manifest text for awesome-copilot/, with keywords trimmed."""
    data = json.loads(source_manifest.read_text(encoding="utf-8"))
    keywords = data.get("keywords", [])[:MAX_KEYWORDS]
    for keyword in keywords:
        if not KEYWORD_PATTERN.fullmatch(keyword) or len(keyword) > MAX_KEYWORD_LENGTH:
            raise SyncError(
                f"keyword {keyword!r} is not valid for awesome-copilot "
                f"(lowercase letters, numbers, hyphens; max {MAX_KEYWORD_LENGTH} chars)"
            )
    data["keywords"] = keywords
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def expected_files(source: Path) -> dict[str, bytes]:
    """Map relative path -> expected bytes for everything awesome-copilot/ should contain."""
    files = {
        str(path.relative_to(source)): path.read_bytes()
        for path in sorted(source.rglob("*"))
        if path.is_file()
    }
    files[MANIFEST] = awesome_copilot_manifest(source / MANIFEST).encode("utf-8")
    return files


def actual_files(target: Path) -> dict[str, bytes]:
    if not target.exists():
        return {}
    return {
        str(path.relative_to(target)): path.read_bytes()
        for path in sorted(target.rglob("*"))
        if path.is_file()
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=["sync", "check"])
    args = parser.parse_args(argv)

    try:
        expected = expected_files(SOURCE_DIR)
    except (OSError, json.JSONDecodeError, SyncError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    actual = actual_files(TARGET_DIR)
    drift = sorted(
        path for path in expected.keys() | actual.keys() if expected.get(path) != actual.get(path)
    )

    if args.mode == "check":
        if drift:
            print(f"awesome-copilot/ is out of date ({len(drift)} file(s)):", file=sys.stderr)
            for path in drift:
                print(f"  {path}", file=sys.stderr)
            print("Run: python3 scripts/sync_awesome_copilot_plugin.py sync", file=sys.stderr)
            return 1
        return 0

    if not drift:
        print("awesome-copilot/ is already up to date")
        return 0
    shutil.rmtree(TARGET_DIR, ignore_errors=True)
    for relative, content in expected.items():
        destination = TARGET_DIR / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    print(f"synced awesome-copilot/ ({len(drift)} file(s) changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
