#!/usr/bin/env python3
"""Refresh the immutable commit pins recorded in skills.py from upstream HEAD.

The registry pins every source repo to a reviewed commit SHA. This script is
the currency mechanism: a weekly workflow opens an auto-merge PR when upstream
HEAD advances, so pinning never freezes the catalog permanently.

Usage::

    python Scripts/update_pin_refs.py --check    # exit 1 when any pin is stale
    python Scripts/update_pin_refs.py            # rewrite skills.py in place
    python Scripts/update_pin_refs.py --selftest # prove drift/rewrite can be detected

Only HTTPS `git ls-remote` is used; no credentials and no shell interpolation.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "skills.py"
REF_RE = re.compile(r'(\{"repo": "([^"]+)", "ref": ")([0-9a-f]{40})(")')


def collect_refs(text: str) -> dict[str, str]:
    return {match.group(2): match.group(3) for match in REF_RE.finditer(text)}


def resolve_head(repo: str, attempts: int = 3) -> str:
    url = f"https://github.com/{repo}.git"
    for _ in range(attempts):
        try:
            result = subprocess.run(
                ["git", "ls-remote", "--exit-code", url, "HEAD"],
                capture_output=True, text=True, timeout=45,
            )
            sha = result.stdout.split()[0] if result.returncode == 0 and result.stdout.strip() else ""
            if re.fullmatch(r"[0-9a-f]{40}", sha):
                return sha
        except (OSError, subprocess.TimeoutExpired, IndexError):
            pass
    return ""


def apply_refs(text: str, desired: dict[str, str]) -> tuple[str, int]:
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        sha = desired.get(match.group(2), match.group(3))
        if sha != match.group(3):
            changed += 1
        return match.group(1) + sha + match.group(4)

    return REF_RE.sub(replace, text), changed


def selftest() -> int:
    fake = (
        '{"repo": "acme/one", "ref": "' + "a" * 40 + '"},\n'
        '{"repo": "acme/two", "ref": "' + "b" * 40 + '"},\n'
    )
    current = collect_refs(fake)
    if current != {"acme/one": "a" * 40, "acme/two": "b" * 40}:
        print("FAIL selftest: refs were not collected")
        return 1
    desired = {"acme/one": "c" * 40, "acme/two": "b" * 40}
    updated, changed = apply_refs(fake, desired)
    if changed != 1 or collect_refs(updated) != desired:
        print("FAIL selftest: stale pin was not detected and rewritten")
        return 1
    print("PASS selftest: stale pin detected and rewritten by name")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    text = TARGET.read_text(encoding="utf-8")
    current = collect_refs(text)
    if not current:
        print("FAIL: no commit pins found in skills.py")
        return 1
    desired: dict[str, str] = {}
    unresolved: list[str] = []
    for repo in current:
        sha = resolve_head(repo)
        if sha:
            desired[repo] = sha
        else:
            unresolved.append(repo)
    if unresolved:
        print("FAIL: could not resolve upstream HEAD for " + ", ".join(unresolved))
        return 1

    if args.check:
        stale = [repo for repo, sha in current.items() if sha != desired[repo]]
        if stale:
            print(f"FAIL pin-refs: {len(stale)} stale pins: " + ", ".join(stale[:8]))
            return 1
        print(f"PASS pin-refs: {len(current)} repos at current upstream HEAD")
        return 0

    updated, changed = apply_refs(text, desired)
    if changed:
        TARGET.write_text(updated, encoding="utf-8", newline="\n")
    print(f"OK: updated {changed} of {len(current)} commit pins")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
