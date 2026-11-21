#!/usr/bin/env python3
"""Resolve and bump the CI Python floor from the upstream PEP release calendar.

The canonical declaration is ``FLOOR`` in this file; every other declaration
(CI matrices and documentation, EN + local mirror) must match it. Upstream truth
is the Python core team's calendar at https://peps.python.org/api/release-cycle.json.

Usage::

    python Scripts/python_floor.py check [--offline]
    python Scripts/python_floor.py apply 3.12
    python Scripts/python_floor.py selftest

No minimum Python 3 runtime is advertised to users; the current release is the
only recommended runtime. stdlib only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLOOR = "3.11"  # canonical CI floor; every declaration below must match

PEPS_URL = "https://peps.python.org/api/release-cycle.json"
VERSION_RE = r"[0-9]+\.[0-9]+"
PLACEHOLDER = "\u00a7"
MARKER_RE = re.compile(r"<!-- mirror-sync: sync-sha=[0-9a-fA-F]+ -->")
OPTIONAL_FILES = frozenset({"AGENTS-TR.md"})

# (file, template containing {old}) — each must carry exactly the declared floor.
FLOOR_DECLARATIONS: dict[str, tuple[str, ...]] = {
    "Scripts/python_floor.py": ('FLOOR = "{old}"',),
    ".github/workflows/CI.yml": ('python-version: ["{old}", "3.x"]',),
    ".github/workflows/Mojibake.yml": ('python-version: ["{old}", "3.x"]',),
    ".github/workflows/Release.yml": ('python-version: ["{old}", "3.x"]',),
    ".gitlab-ci.yml": ('- PYTHON_VERSION: ["{old}", "latest"]',),
    "AGENTS.md": ("matrix of `{old}` plus the current line",),
    "AGENTS-TR.md": ("`{old}` ile güncel hattı",),
}


def version_key(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split("."))


def read_floor(root: Path = ROOT) -> str:
    """Read the canonical floor from this script's source."""
    text = (root / "Scripts" / "python_floor.py").read_text(encoding="utf-8")
    m = re.search(rf'^FLOOR = "({VERSION_RE})"', text, re.M)
    if m is None:
        raise ValueError("canonical FLOOR declaration not found")
    return m.group(1)


def fetch_cycles(attempts: int = 3) -> dict:
    """Fetch the trusted release calendar with bounded retries."""
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            # Fixed, trusted HTTPS URL from the Python core team; no caller input.
            with urllib.request.urlopen(PEPS_URL, timeout=30) as response:  # nosec B310
                data = json.load(response)
            if not isinstance(data, dict) or len(data) < 10:
                raise ValueError("release calendar looks incomplete")
            return data
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last = exc
            if attempt < attempts:
                time.sleep(2**attempt)
    raise RuntimeError(f"could not fetch {PEPS_URL} after {attempts} attempts") from last


def resolve_floor(cycles: dict, today: date | None = None) -> str:
    """Oldest minor that is still supported upstream.

    A version is unsupported when the core team marks it end-of-life or when its
    scheduled EOL date has passed, whichever comes first.
    """
    today = today or date.today()
    supported = []
    for version, detail in cycles.items():
        if re.fullmatch(VERSION_RE, version) is None:
            continue
        if detail.get("status") == "end-of-life":
            continue
        raw = detail.get("end_of_life", "")
        m = re.match(r"(\d{4})-(\d{2})", raw)
        if m:
            year, month = int(m.group(1)), int(m.group(2))
            eol = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
            if eol <= today:
                continue
        supported.append(version)
    if not supported:
        raise ValueError("no supported Python version in the release calendar")
    return min(supported, key=version_key)


def _pattern(template: str) -> re.Pattern[str]:
    escaped = re.escape(template.replace("{old}", PLACEHOLDER))
    return re.compile(escaped.replace(re.escape(PLACEHOLDER), f"({VERSION_RE})"))


def _render(template: str, version: str) -> str:
    return template.replace("{old}", version)


def find_drift(root: Path = ROOT) -> list[str]:
    """Mismatches between the canonical floor and its declarations."""
    floor = read_floor(root)
    problems: list[str] = []
    for name, templates in FLOOR_DECLARATIONS.items():
        path = root / name
        if not path.exists():
            if name not in OPTIONAL_FILES:
                problems.append(f"{name}: missing file")
            continue
        text = path.read_bytes().decode("utf-8")
        for template in templates:
            matches = _pattern(template).findall(text)
            if not matches:
                problems.append(f"{name}: missing declaration {_render(template, floor)!r}")
            elif any(v != floor for v in matches):
                problems.append(f"{name}: {template!r} uses {sorted(set(matches))}, expected {floor}")
    return problems


def refresh_mirror_marker(root: Path = ROOT) -> None:
    """Recompute sync-sha after a source-side edit; never copy one side to the other."""
    sys.path.insert(0, str(root / "Scripts"))
    from verify_mirror import marker_value, sync_sha

    source = root / "AGENTS.md"
    mirror = root / "AGENTS-TR.md"
    if not (source.exists() and mirror.exists()):
        return
    sha = sync_sha(source)
    for path in (source, mirror):
        text = path.read_bytes().decode("utf-8")
        if marker_value(path) == sha:
            continue
        updated = MARKER_RE.sub(f"<!-- mirror-sync: sync-sha={sha} -->", text)
        if updated != text:
            path.write_bytes(updated.encode("utf-8"))


def apply_bump(root: Path, old: str, new: str) -> list[str]:
    """Apply the floor change everywhere; return changed paths."""
    changed: list[str] = []
    for name, templates in FLOOR_DECLARATIONS.items():
        path = root / name
        if not path.exists():
            continue
        original = path.read_bytes().decode("utf-8")
        updated = original
        for template in templates:
            updated = updated.replace(_render(template, old), _render(template, new))
        if updated != original:
            path.write_bytes(updated.encode("utf-8"))
            changed.append(name)
    if any(n in changed for n in ("AGENTS.md", "AGENTS-TR.md", "Scripts/python_floor.py")):
        refresh_mirror_marker(root)
    return changed


def _check(root: Path, offline: bool) -> int:
    current = read_floor(root)
    desired = current
    if not offline:
        desired = resolve_floor(fetch_cycles())
        if version_key(desired) < version_key(current):
            print(f"upstream floor {desired} is below declared {current}; refusing to downgrade",
                  file=sys.stderr)
            desired = current
    outputs = {
        "desired": desired,
        "current": current,
        "changed": "true" if desired != current else "false",
    }
    for key, value in outputs.items():
        print(f"{key}={value}")
    out_file = os.environ.get("GITHUB_OUTPUT")
    if out_file:
        with Path(out_file).open("a", encoding="utf-8") as handle:
            for key, value in outputs.items():
                handle.write(f"{key}={value}\n")
    problems = find_drift(root)
    if problems:
        print("floor parity problems:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 2
    return 0


def selftest() -> int:
    cycles = {
        "3.15": {"status": "bugfix", "end_of_life": "2031-10"},
        "3.12": {"status": "security", "end_of_life": "2028-10"},
        "3.11": {"status": "security", "end_of_life": "2027-10"},
        "3.10": {"status": "end-of-life", "end_of_life": "2026-10-01"},
    }
    assert resolve_floor(cycles, date(2026, 11, 21)) == "3.11"
    assert resolve_floor(cycles, date(2027, 11, 1)) == "3.12"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        for name in FLOOR_DECLARATIONS:
            src = ROOT / name
            dst = root / name
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
        assert find_drift(root) == [], "clean tree must have no drift"
        path = root / ".github" / "workflows" / "CI.yml"
        path.write_bytes(path.read_bytes().replace(b'"3.11"', b'"3.12"', 1))
        assert find_drift(root), "planted drift must be detected"
    assert version_key("3.11") < version_key("3.12")
    assert version_key("3.12") > version_key("3.11")
    print("selftest OK: resolution, downgrade guard, parity and planted drift")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="compare declared floor with upstream calendar")
    check.add_argument("--offline", action="store_true", help="parity only, no network")
    apply_parser = sub.add_parser("apply", help="bump the declared floor everywhere")
    apply_parser.add_argument("version", help="new floor, e.g. 3.12")
    sub.add_parser("selftest", help="prove the guards can fail")
    args = parser.parse_args()
    if args.command == "check":
        return _check(ROOT, args.offline)
    if args.command == "selftest":
        return selftest()
    if re.fullmatch(VERSION_RE, args.version) is None:
        parser.error("version must look like 3.12")
    old = read_floor(ROOT)
    if version_key(args.version) < version_key(old):
        parser.error(f"refusing to downgrade from {old} to {args.version}")
    changed = apply_bump(ROOT, old, args.version)
    print(f"Python floor {old} -> {args.version}: {len(changed)} files updated")
    for name in changed:
        print(f"  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
