#!/usr/bin/env python3
"""Compute canonical release metadata from CHANGELOG.md.

Parameters (CLI):
  <version>          bare version number, e.g. 1.2.1 (no leading v)
  [--current]        mark this version as current (no [DEPRECATED] prefix)

Prints two lines:
  1) canonical title: "[DEPRECATED] vX — Short Description" (prefix omitted
     for --current); the prefix is always at the START, never appended
  2) short description used in the title

Title case rules: coordinating conjunctions (and, or) stay lowercase;
acronyms stay uppercase (API, CI, ADMX); mixed-case brands are preserved
(IoC, PowerShell, GitHub). stdlib only.
"""
from __future__ import annotations

import sys

# Curated, factual one-line descriptions per published version.
DESCRIPTIONS = {
    "1.2.1": "Release Workflow and Documentation Fixes",
    "1.2.0": "Specialization, CI Currency and Security Release",
    "1.1.0": "Specialization Profiles Release",
    "1.0.2": "Compatibility and Documentation Update",
    "1.0.1": "Reliability Improvements",
    "1.0.0": "Functional Categories and Installer",
}


def title(version: str, current: bool) -> str:
    description = DESCRIPTIONS.get(version, "Release")
    base = f"v{version} — {description}"
    return base if current else f"[DEPRECATED] {base}"


def main() -> None:
    args = sys.argv[1:]
    if not args or len(args) > 2:
        raise SystemExit("usage: release_title.py <version> [--current]")
    version = args[0].lstrip("v")
    current = "--current" in args
    print(title(version, current))
    print(DESCRIPTIONS.get(version, "Release"))


if __name__ == "__main__":
    main()
