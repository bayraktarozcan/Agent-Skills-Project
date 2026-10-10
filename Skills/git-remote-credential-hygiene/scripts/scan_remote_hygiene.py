#!/usr/bin/env python3
"""Scan a git repo config for plaintext credential patterns (read-only).

Reports findings as file + line with masked values only. Never prints,
writes, or stores a secret value.

Exit codes: 0 = clean, 1 = findings, 2 = usage/config error.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PATTERNS = [
    ("gitlab-token", re.compile(r"glpat-[A-Za-z0-9_-]+")),
    ("github-token", re.compile(r"ghp_[A-Za-z0-9]+")),
    ("github-oauth", re.compile(r"gho_[A-Za-z0-9]+")),
    ("github-fine-grained", re.compile(r"github_pat_[A-Za-z0-9_]+")),
    ("access-token-marker", re.compile(r"x-access-token", re.IGNORECASE)),
    ("embedded-credentials", re.compile(r"://[^/\s@]+:[^/\s@]+@")),
]


def mask_host(line: str) -> str:
    return re.sub(r"://[^@\s/]+@", "://***@", line).strip()


def scan_file(path: Path) -> list[str]:
    findings: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return ["ERROR cannot read {0}: {1}".format(path, exc)]
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in PATTERNS:
            if rx.search(line):
                findings.append(
                    "{0}:{1} [{2}] {3}".format(path, lineno, label, mask_host(line))
                )
                break
    return findings


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Read-only credential hygiene scan.")
    ap.add_argument("repo", nargs="?", default=".", help="repo root (default: cwd)")
    args = ap.parse_args(argv)
    root = Path(args.repo)
    config = root / ".git" / "config"
    if not config.is_file():
        print("ERROR no .git/config under {0}".format(root))
        return 2
    findings = scan_file(config)
    creds = Path.home() / ".git-credentials"
    if creds.is_file():
        findings.extend(scan_file(creds))
    else:
        print("note: no ~/.git-credentials file present")
    errors = [f for f in findings if f.startswith("ERROR")]
    if errors:
        for f in findings:
            print(f)
        return 2
    if not findings:
        print("CLEAN: no plaintext credential pattern found")
        return 0
    for f in findings:
        print(f)
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
