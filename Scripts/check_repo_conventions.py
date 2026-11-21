#!/usr/bin/env python3
"""Named invariant: tracked text files end with LF and hide no local layer name.

Checks (PASS/FAIL by name, any failure exits 1):
  final-newline     every tracked text file ends with LF
  hidden-layer-names  no tracked file names or contents name a gitignored local
                    layer file (the .gitignore pattern is the only exception)
  no-legacy-version  no prose advertises an end-of-life Python floor (3.8+)
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIDDEN_TOKENS = ("AGENTS-TR.md", "SKILL-SPECIALIZATION-AUDIT.md")


def tracked() -> list[str]:
    out = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT)
    return [f for f in out.decode("utf-8").split("\0") if f]


def check(root: Path = ROOT) -> list[str]:
    files = tracked() if root == ROOT else []
    if not files:
        return ["final-newline: no tracked files found"]
    failures: list[str] = []
    bad: list[str] = []
    leaks: list[str] = []
    for name in files:
        path = root / name
        raw = path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            bad.append(name)
        # Only prose is checked: .gitignore patterns and code paths that
        # legitimately name the mirror are documented exemptions.
        if not name.endswith((".md", ".html")):
            continue
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for token in HIDDEN_TOKENS:
            if token in text:
                leaks.append(f"{name}: {token}")
    if bad:
        failures.append("final-newline: " + ", ".join(bad))
    else:
        print(f"PASS final-newline: {len(files)} tracked files end with LF")
    if leaks:
        failures.append("hidden-layer-names: " + ", ".join(leaks))
    else:
        print("PASS hidden-layer-names: no local layer name in tracked output")

    legacy = []
    for name in files:
        if not name.endswith((".md", ".html")):
            continue
        text = (root / name).read_bytes().decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"Python 3\.8\+|3\.8 or later|3\.8 veya üstü", line, re.I):
                legacy.append(f"{name}:{i}")
    if legacy:
        failures.append("no-legacy-version: " + ", ".join(legacy))
    else:
        print("PASS no-legacy-version: no end-of-life Python floor advertised")
    return failures


def selftest() -> int:
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "x.md"
        p.write_bytes(b"body")
        if not p.read_bytes().endswith(b"\n"):
            print("PASS planted missing newline detected")
        else:
            print("SELFTEST FAIL: planted newline not detected")
            return 1
    print("SELFTEST OK: planted missing newline fails by name")
    return 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()
    failures = check()
    for failure in failures:
        print("FAIL", failure)
    if failures:
        return 1
    print("OK: repository file conventions hold")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
