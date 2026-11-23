#!/usr/bin/env python3
"""Network integration check for the real installer path.

The default run clones ONE small pinned source repo (expo/skills) with the
same code path the installer uses, verifies the checked-out commit equals the
recorded SHA, counts SKILL.md files and checks every skill name against the
specialization manifest. `--all` repeats this for every pinned repo and is
used by the weekly pin-refresh workflow to detect inventory drift.

--selftest is offline and plants a wrong commit plus a missing manifest name
to prove the detectors can fail.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import skills  # noqa: E402  (project module under test)

MANIFEST = ROOT / "SKILL-SPECIALIZATION.json"
DEFAULT_REPO = "expo/skills"
MIN_SKILLS = 20


def repo_subpath(repo: str) -> str:
    for category in skills.REPOS["categories"]:
        for entry in category["repos"]:
            if entry["repo"] == repo:
                return str(entry.get("subpath", ""))
    return ""


def manifest_names() -> set[str]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    return set(data["skills"].keys())


def commit_matches(actual: str, expected: str) -> bool:
    return bool(expected) and actual == expected


def missing_names(found: set[str], known: set[str]) -> list[str]:
    return sorted(found - known)


def check_repo(repo: str, known: set[str], minimum: int = 0) -> tuple[list[str], int]:
    problems: list[str] = []
    ref = skills._repo_ref(repo)
    if not ref:
        return ["missing commit pin"], 0
    tmpdir = Path(tempfile.mkdtemp(prefix="asp-integration-"))
    try:
        ok, detail = skills._clone_once(repo, repo_subpath(repo), tmpdir)
        if not ok:
            return [f"clone failed: {detail}"], 0
        actual = skills._repo_commit(tmpdir)
        if not commit_matches(actual, ref):
            problems.append(f"commit mismatch: expected {ref}, got {actual or '-'}")
        src = tmpdir / repo_subpath(repo) if repo_subpath(repo) else tmpdir
        count = 0
        missing: list[str] = []
        for mdfile in sorted(src.rglob("SKILL.md")):
            if skills._source_verdict(mdfile, src, tmpdir) is not None:
                problems.append(f"unsafe source: {mdfile.name}")
                continue
            raw = mdfile.read_bytes()
            name = skills.valid_name(
                skills._frontmatter_name(raw.decode("utf-8", "replace"))
                or mdfile.parent.name
            )
            if name not in known:
                missing.append(name)
            count += 1
        if count < max(1, minimum):
            problems.append(f"only {count} SKILL.md files found")
        if missing:
            problems.append("missing from manifest: " + ", ".join(missing[:8]))
        return problems, count
    finally:
        skills.cleanup(tmpdir)


def selftest() -> int:
    if commit_matches("b" * 40, "a" * 40):
        print("FAIL selftest: wrong commit not detected")
        return 1
    print("PASS selftest: wrong commit detected")
    found = missing_names({"present-skill", "new-skill"}, {"present-skill"})
    if found != ["new-skill"]:
        print("FAIL selftest: missing manifest name not detected")
        return 1
    print("PASS selftest: missing manifest name detected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()

    known = manifest_names()
    repos = [
        entry["repo"]
        for category in skills.REPOS["categories"]
        for entry in category["repos"]
    ] if args.all else [DEFAULT_REPO]
    failures = 0
    for repo in repos:
        problems, count = check_repo(repo, known, 0 if args.all else MIN_SKILLS)
        if problems:
            failures += 1
            print(f"FAIL {repo}: " + "; ".join(problems))
        else:
            print(f"PASS {repo}: commit={skills._repo_ref(repo)} skills={count}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
