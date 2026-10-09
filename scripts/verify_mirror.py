#!/usr/bin/env python3
"""Mirror verifier for the AGENTS.md / human-language mirror pair.

Implements the `sync-sha` computation from the Local human-language
mirror rule (read bytes, drop a UTF-8 BOM if present, decode as UTF-8,
normalize every CRLF and lone CR to LF, remove the whole `mirror-sync`
marker line including its terminator, SHA1 the UTF-8 encoding of what
remains) and compares document structure (section count, heading depth
sequence, top-level rules per section, code fences, table blocks, and
ordered action-checklist token order).

Usage:
  python scripts/verify_mirror.py AGENTS.md AGENTS-TR.md
  python scripts/verify_mirror.py AGENTS.md --allow-missing-mirror
  python scripts/verify_mirror.py --selftest

Exit codes: 0 = in sync, 1 = drift or error.
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from pathlib import Path

MARKER = "<!-- mirror-sync:"


def sync_sha(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    text = raw.decode("utf-8")
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    kept = [ln for ln in text.split("\n") if MARKER not in ln]
    return hashlib.sha1("\n".join(kept).encode("utf-8")).hexdigest()


def marker_value(path: Path) -> str | None:
    for line in path.read_bytes().decode("utf-8", errors="replace").splitlines():
        if MARKER in line:
            match = re.search(r"sync-sha=([0-9a-fA-F]+)", line)
            if match:
                return match.group(1).lower()
    return None


def strip_fences(lines: list[str]) -> list[str]:
    out: list[str] = []
    in_fence = False
    for line in lines:
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return out


def structure(path: Path) -> dict:
    lines = path.read_bytes().decode("utf-8", errors="replace").split("\n")
    fences = sum(1 for ln in lines if ln.startswith("```"))
    body = strip_fences(lines)
    headings = [ln for ln in body if re.match(r"^#{1,6} ", ln)]
    depths = [len(ln.split(" ")[0]) for ln in headings]
    h2 = [ln for ln in headings if ln.startswith("## ")]
    rules: dict[str, int] = {}
    current = ""
    for ln in body:
        match = re.match(r"^(#{1,6}) (.*)$", ln)
        if match and len(match.group(1)) == 2:
            current = match.group(2)
            rules[current] = 0
        elif ln.startswith("- ") and current:
            rules[current] += 1
    tables = 0
    in_table = False
    for ln in body:
        if ln.startswith("|"):
            if not in_table:
                tables += 1
                in_table = True
        else:
            in_table = False
    checks: list[str] = []
    for ln in body:
        stripped = ln.strip()
        if re.match(r"^(- \[[ x]\]|(\d+)\.) ", stripped):
            tokens = re.findall(r"`([^`]+)`", stripped)
            if tokens:
                checks.append(tokens[0])
    return {
        "sections": len(h2),
        "depths": depths,
        "rules": rules,
        "fences": fences,
        "tables": tables,
        "checks": checks,
    }


def compare(source: Path, mirror: Path) -> list[str]:
    problems: list[str] = []
    a = structure(source)
    b = structure(mirror)
    if [a["sections"], a["depths"], a["fences"], a["tables"]] != [b["sections"], b["depths"], b["fences"], b["tables"]]:
        if a["sections"] != b["sections"]:
            problems.append("section count: {0} vs {1}".format(a["sections"], b["sections"]))
        if a["depths"] != b["depths"]:
            problems.append("heading depth sequence differs")
        if a["fences"] != b["fences"]:
            problems.append("code fence lines: {0} vs {1}".format(a["fences"], b["fences"]))
        if a["tables"] != b["tables"]:
            problems.append("table blocks: {0} vs {1}".format(a["tables"], b["tables"]))
    # Rule counts are compared by section position, not by heading text:
    # a translation legitimately renames headings.
    counts_a = [a["rules"][k] for k in a["rules"]]
    counts_b = [b["rules"][k] for k in b["rules"]]
    if counts_a != counts_b:
        problems.append("top-level rule counts differ by section position")
    if a["checks"] != b["checks"]:
        problems.append("action-checklist token order differs")
    return problems


def selftest() -> int:
    import tempfile

    en = "# T\n\n## A\n\n- one `git status` rule\n\n```\nx\n```\n\n| H |\n|---|\n| v |\n\n- [ ] `git status` first\n"
    ok_mirror = en.replace("one", "bir").replace("first", "ilk")
    drift_mirror = ok_mirror.replace("- [ ] `git status` ilk", "- [ ] `git diff` ilk")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        src = tmp_path / "EN.md"
        good = tmp_path / "TR.md"
        bad = tmp_path / "BAD.md"
        src.write_text(en + "<!-- mirror-sync: sync-sha=0 -->\n", encoding="utf-8")
        good.write_text(ok_mirror + "<!-- mirror-sync: sync-sha=0 -->\n", encoding="utf-8")
        bad.write_text(drift_mirror + "<!-- mirror-sync: sync-sha=0 -->\n", encoding="utf-8")
        if compare(src, good):
            print("SELFTEST FAIL: clean pair reported as drift")
            return 1
        if not compare(src, bad):
            print("SELFTEST FAIL: planted checklist drift not caught")
            return 1
    print("SELFTEST OK: clean pair passes, planted drift fails by name")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Verify the AGENTS.md mirror pair.")
    parser.add_argument("source", nargs="?", help="path to the source file")
    parser.add_argument("mirror", nargs="?", help="path to the mirror file")
    parser.add_argument("--allow-missing-mirror", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if not args.source:
        parser.print_usage(sys.stderr)
        return 2
    source = Path(args.source)
    value = sync_sha(source)
    print("sync-sha: {0}".format(value))
    if not args.mirror:
        if args.allow_missing_mirror:
            print("note: no mirror path given, allowed")
            return 0
        print("ERROR: no mirror path given")
        return 2
    mirror = Path(args.mirror)
    if not mirror.is_file():
        if args.allow_missing_mirror:
            print("note: mirror absent, allowed")
            return 0
        print("ERROR: mirror file missing: {0}".format(mirror))
        return 1
    declared = marker_value(mirror)
    source_declared = marker_value(source)
    failures = []
    if declared != value:
        failures.append("mirror marker {0} != computed {1}".format(declared, value))
    if source_declared != value:
        failures.append("source marker {0} != computed {1}".format(source_declared, value))
    failures.extend(compare(source, mirror))
    if failures:
        for failure in failures:
            print("DRIFT: {0}".format(failure))
        return 1
    print("IN SYNC: structure and markers agree (meaning still needs a human read)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
