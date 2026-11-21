#!/usr/bin/env python3
"""Compute canonical release titles from the canonical CHANGELOG.md.

Parameters (CLI):
  <version>          bare version number, e.g. 1.2.1 (no leading v)
  [--current]        mark this version as current (no [DEPRECATED] prefix)

Prints two lines:
  1) canonical title: "[DEPRECATED] vX — Short Description" (prefix omitted
     for --current); the prefix is always at the START, never appended
  2) short description used in the title

The description is derived at call time from the first bullet of that version's
CHANGELOG section (an explicit `### Summary` first sentence takes precedence),
so a new release cannot drift from the changelog. Title case: coordinating
conjunctions stay lowercase, acronyms stay uppercase, established mixed-case
names are preserved. stdlib only.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINOR = {"a", "an", "the", "and", "or", "nor", "but", "for", "of", "on", "per",
         "to", "via", "with", "as", "at", "by", "in", "if"}
ACRONYMS = {"api": "API", "ci": "CI", "cd": "CD", "dns": "DNS", "html": "HTML",
            "json": "JSON", "yaml": "YAML", "pdf": "PDF", "sha256": "SHA256",
            "tls": "TLS", "url": "URL", "utf8": "UTF8", "guid": "GUID", "lts": "LTS"}
MIXED = {"github": "GitHub", "gitlab": "GitLab", "dependabot": "Dependabot",
         "ioc": "IoC", "powershell": "PowerShell", "codeql": "CodeQL",
         "python": "Python", "windows": "Windows", "linux": "Linux",
         "macos": "macOS", "javascript": "JavaScript", "lychee": "Lychee",
         "semver": "SemVer"}


def title_case(text: str) -> str:
    words = []
    for token in text.split():
        comma = "," if token.endswith(",") else ""
        word = token.strip("-/.;:|()[]{}*\"',")
        if not word or re.fullmatch(r"v?\d+(\.\d+){1,3}", word, re.I):
            continue
        low = word.lower()
        if low in ACRONYMS:
            words.append(ACRONYMS[low] + comma)
            continue
        if low in MIXED:
            words.append(MIXED[low] + comma)
            continue
        if low in MINOR and words:
            words.append(low + comma)
            continue
        parts = []
        for part in (p for p in re.split(r"[-/]", word) if p):
            pl = part.lower()
            if pl in ACRONYMS:
                parts.append(ACRONYMS[pl])
            elif pl in MIXED:
                parts.append(MIXED[pl])
            elif pl in MINOR and parts:
                parts.append(pl)
            else:
                parts.append(part[:1].upper() + part[1:])
        words.append("-".join(parts) + comma)
    return " ".join(words)


def description(version: str) -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    en = text.split('<a id="en"></a>', 1)[1].split('<a id="tr"></a>', 1)[0]
    lines = en.splitlines()
    start = next((i for i, l in enumerate(lines) if l.startswith(f"## [{version}]")), None)
    if start is None:
        raise SystemExit(f"version {version} not found in CHANGELOG.md")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## [")), len(lines))
    section = lines[start + 1:end]
    # Explicit Summary sentence wins; otherwise the first bullet's bold lead-in.
    summary = next((i for i, l in enumerate(section) if l.strip() == "### Summary"), None)
    if summary is not None:
        for line in section[summary + 1:]:
            if line.startswith("### ") or not line.strip():
                continue
            prose = re.sub(r"\*\*", "", line.strip())
            return title_case(prose.rstrip(" .:"))
    for line in section:
        if not line.startswith("- "):
            continue
        bold = re.match(r"^- \*\*(.+?)\*\*", line)
        prose = bold.group(1) if bold else re.sub(r"\*\*", "", line[2:]).split(".")[0]
        return title_case(prose.rstrip(" .:"))
    raise SystemExit(f"no description found for version {version}")


def title(version: str, current: bool) -> tuple[str, str]:
    desc = description(version)
    base = f"v{version} — {desc}"
    return (base if current else f"[DEPRECATED] {base}"), desc


def main() -> None:
    args = sys.argv[1:]
    if not args or len(args) > 2:
        raise SystemExit("usage: release_title.py <version> [--current]")
    version = args[0].lstrip("v")
    current = "--current" in args
    full, desc = title(version, current)
    print(full)
    print(desc)


if __name__ == "__main__":
    main()
