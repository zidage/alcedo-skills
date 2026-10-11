#!/usr/bin/env python3
"""Sets the version of the alcedo plugin to an Alcedo Studio version.

    python scripts/set_version.py <x.y.z>

Writes the version of `.claude-plugin/plugin.json` and of its entry in
`.claude-plugin/marketplace.json`. Use the Alcedo Studio version of the release.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PLUGIN_JSON = REPO_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_JSON = REPO_ROOT / ".claude-plugin" / "marketplace.json"
VERSION = re.compile(r"^\d+\.\d+\.\d+$")


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("version", help="The Alcedo Studio version, for example 0.3.2.")
    arguments = parser.parse_args()
    if not VERSION.match(arguments.version):
        raise SystemExit(f"the version must be x.y.z, not '{arguments.version}'")

    plugin = json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))
    plugin["version"] = arguments.version
    write_json(PLUGIN_JSON, plugin)
    marketplace = json.loads(MARKETPLACE_JSON.read_text(encoding="utf-8"))
    for entry in marketplace.get("plugins", []):
        if entry.get("name") == plugin["name"]:
            entry["version"] = arguments.version
    write_json(MARKETPLACE_JSON, marketplace)
    print(f"version {arguments.version}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
