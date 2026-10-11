#!/usr/bin/env python3
"""Copies the alcedo-cli documentation of an Alcedo Studio checkout into the alcedo skill.

    python scripts/sync_references.py <AlcedoStudio checkout> [--version <x.y.z>] [--check]

- Copies `docs/automation/` of the checkout to `skills/alcedo/references/`. A link that leaves
  `docs/automation/` becomes a link to the file on GitHub, because the skill does not have it.
- With `--version`, sets the version of the plugin (`.claude-plugin/plugin.json`) and of the
  marketplace entry. Use the Alcedo Studio version of the release.
- With `--check`, changes nothing and fails when the references differ from the checkout.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCES = REPO_ROOT / "skills" / "alcedo" / "references"
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
SOURCE_DIR = "docs/automation"
GITHUB_BLOB = "https://github.com/zidage/AlcedoStudio/blob/main/"
LINK = re.compile(r"\]\((?!https?://|#|mailto:)([^)#\s]+)(#[^)\s]*)?\)")
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def rewrite_links(text: str, page: str) -> str:
    """Points the links that leave docs/automation to GitHub. @p page is relative to the repo."""
    page_dir = posixpath.dirname(page)

    def replace(match: re.Match) -> str:
        target, anchor = match.group(1), match.group(2) or ""
        resolved = posixpath.normpath(posixpath.join(page_dir, target))
        if resolved == SOURCE_DIR or resolved.startswith(SOURCE_DIR + "/"):
            return match.group(0)
        return f"]({GITHUB_BLOB}{resolved}{anchor})"

    return LINK.sub(replace, text)


def expected_files(checkout: Path) -> dict[str, bytes]:
    source = checkout / SOURCE_DIR
    if not source.is_dir():
        raise SystemExit(f"{source} is not a directory; give the root of an AlcedoStudio checkout")
    files = {}
    for path in sorted(source.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(source).as_posix()
        data = path.read_bytes()
        if path.suffix == ".md":
            text = data.decode("utf-8").replace("\r\n", "\n")
            data = rewrite_links(text, f"{SOURCE_DIR}/{relative}").encode("utf-8")
        files[relative] = data
    return files


def current_files() -> dict[str, bytes]:
    if not REFERENCES.is_dir():
        return {}
    return {path.relative_to(REFERENCES).as_posix(): path.read_bytes()
            for path in sorted(REFERENCES.rglob("*")) if path.is_file()}


def set_version(version: str) -> None:
    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    plugin["version"] = version
    PLUGIN_JSON.write_text(json.dumps(plugin, indent=2) + "\n", encoding="utf-8", newline="\n")
    marketplace = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    for entry in marketplace.get("plugins", []):
        if entry.get("name") == plugin["name"]:
            entry["version"] = version
    MARKETPLACE_JSON.write_text(json.dumps(marketplace, indent=2) + "\n", encoding="utf-8",
                                newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("checkout", type=Path, help="Root of an AlcedoStudio checkout.")
    parser.add_argument("--version", help="Set the plugin version, for example 0.3.2.")
    parser.add_argument("--check", action="store_true", help="Check only; change no file.")
    arguments = parser.parse_args()

    expected = expected_files(arguments.checkout)
    current = current_files()
    changed = sorted(name for name in expected.keys() | current.keys()
                     if expected.get(name) != current.get(name))

    if arguments.check:
        for name in changed:
            print(f"references/{name} differs from {SOURCE_DIR}/{name}", file=sys.stderr)
        return 1 if changed else 0

    if arguments.version and not VERSION.match(arguments.version):
        raise SystemExit(f"--version must be x.y.z, not '{arguments.version}'")
    if REFERENCES.exists():
        shutil.rmtree(REFERENCES)
    for name, data in expected.items():
        target = REFERENCES / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    if arguments.version:
        set_version(arguments.version)
    print(f"{len(changed)} file(s) changed in skills/alcedo/references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
