#!/usr/bin/env python3
"""Create a Git-ignored private player profile from the public template."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TEMPLATE = SKILL_ROOT / "assets" / "player-profile-template.md"
DEFAULT_DESTINATION = SKILL_ROOT / "references" / "player-profile.md"


def initialize_profile(template: Path, destination: Path, force: bool = False) -> Path:
    if not template.is_file():
        raise FileNotFoundError(f"profile template not found: {template}")
    if destination.exists() and not force:
        raise FileExistsError(f"private profile already exists: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(template, destination)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--force", action="store_true", help="overwrite an existing profile")
    args = parser.parse_args()
    try:
        destination = initialize_profile(args.template, args.destination, args.force)
    except (FileNotFoundError, FileExistsError) as exc:
        parser.error(str(exc))
    print(f"Created private profile: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
