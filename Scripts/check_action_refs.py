#!/usr/bin/env python3
"""Named invariant: CI references follow the always-latest policy.

The map below is a deliberately local, deterministic record of each upstream
action's default branch, verified from GitHub on 2026-11-21. It keeps the gate
offline; refreshing it is a reviewed code change. What this check cannot see:
a future upstream default-branch rename not reflected in the map, or a
compromise of a tracked branch (the accepted risk in SECURITY.md).

Checks (each reports PASS/FAIL by name; any failure exits 1):
  ref-count        at least one action reference is actually inspected
  no-sha           no full-commit SHA pin
  no-version-pin   no == version pin or @sha256: digest in any CI file
  known-repo       every action is in the verified map
  default-branch   every ref equals its upstream default branch
  exception-doc    each @master use has a nearby "master, not main" comment
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DEFAULT_BRANCH = {
    "actions/checkout": "main",
    "actions/configure-pages": "main",
    "actions/deploy-pages": "main",
    "actions/setup-python": "main",
    "actions/upload-pages-artifact": "main",
    "gitleaks/gitleaks-action": "master",
    "lycheeverse/lychee-action": "master",
    "rhysd/actionlint": "main",
    "softprops/action-gh-release": "master",
}

USE_RE = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)@([^\s#]+)")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
PIN_RE = re.compile(r"==\d|@sha256:[0-9a-f]{64}|RequiredVersion\s+\S")


def ci_files(root: Path = ROOT) -> list[Path]:
    return sorted((root / ".github" / "workflows").glob("*.yml")) + [root / ".gitlab-ci.yml"]


def references(root: Path = ROOT) -> list[tuple[str, str, str]]:
    found = []
    for path in ci_files(root):
        text = path.read_text(encoding="utf-8")
        for m in USE_RE.finditer(text):
            found.append((path.name, m.group(1), m.group(2)))
    return found


def check(root: Path = ROOT) -> list[str]:
    refs = references(root)
    failures: list[str] = []
    if not refs:
        failures.append("ref-count: no action references found")
    else:
        print(f"PASS ref-count: {len(refs)} references")
    shas = [f"{f}: {repo}@{ref}" for f, repo, ref in refs if SHA_RE.match(ref)]
    if shas:
        failures.append("no-sha: " + ", ".join(shas))
    else:
        print("PASS no-sha: no full-commit SHA pins")
    pins = []
    for path in ci_files(root):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if PIN_RE.search(line):
                pins.append(f"{path.name}:{i}: {line.strip()[:80]}")
    if pins:
        failures.append("no-version-pin: " + ", ".join(pins))
    else:
        print("PASS no-version-pin: no == pins or @sha256 digests")
    unknown = [f"{f}: {repo}@{ref}" for f, repo, ref in refs if repo not in DEFAULT_BRANCH]
    if unknown:
        failures.append("known-repo: " + ", ".join(unknown))
    else:
        print("PASS known-repo: every action has a verified default branch")
    wrong = [f"{f}: {repo}@{ref}" for f, repo, ref in refs
             if repo in DEFAULT_BRANCH and ref != DEFAULT_BRANCH[repo]]
    if wrong:
        failures.append("default-branch: " + ", ".join(wrong))
    else:
        print("PASS default-branch: every ref matches the verified default branch")
    undocumented = []
    for name, repo, ref in refs:
        if ref != "master":
            continue
        text = (root / ".github" / "workflows" / name).read_text(encoding="utf-8")
        lines = text.splitlines()
        idx = next((i for i, l in enumerate(lines) if f"{repo}@master" in l), None)
        nearby = " ".join(lines[max(0, idx - 2):idx + 1]) if idx is not None else ""
        if "master, not main" not in nearby:
            undocumented.append(f"{name}: {repo}@master")
    if undocumented:
        failures.append("exception-doc: " + ", ".join(undocumented))
    else:
        print("PASS exception-doc: every @master use is documented next to its line")
    return failures


def selftest() -> int:
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "Scripts").mkdir()
        shutil.copyfile(ROOT / "Scripts" / "check_action_refs.py",
                        root / "Scripts" / "check_action_refs.py")
        wf = root / ".github" / "workflows"
        wf.mkdir(parents=True)
        for source in sorted((ROOT / ".github" / "workflows").glob("*.yml")):
            shutil.copyfile(source, wf / source.name)
        src = (wf / "CI.yml").read_text(encoding="utf-8")
        (root / ".gitlab-ci.yml").write_bytes((ROOT / ".gitlab-ci.yml").read_bytes())
        if check(root):
            print("SELFTEST FAIL: clean tree reported as drift")
            return 1
        (wf / "CI.yml").write_text(
            src.replace("actions/checkout@main", "actions/checkout@" + "a" * 40), encoding="utf-8")
        failures = check(root)
        if not any(f.startswith("no-sha:") for f in failures):
            print("SELFTEST FAIL: planted SHA pin not caught")
            return 1
    print("SELFTEST OK: clean tree passes, planted SHA pin fails by name")
    return 0


def main() -> int:
    if "--selftest" in sys.argv[1:]:
        return selftest()
    failures = check()
    for failure in failures:
        print("FAIL", failure)
    if failures:
        return 1
    print("OK: action references are unpinned and match upstream default branches")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
