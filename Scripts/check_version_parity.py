#!/usr/bin/env python3
"""Named invariant checks: version/count parity plus marker presence.

Each check reports PASS or FAIL by name; any failure exits 1. Run from
the repository root before push. stdlib only.

Checks:
  manifest-internal  skill map length, class counts, and profile counts
                     agree inside skill-specialization.json
  registry-repos     recommended/trusted/all repo counts from skills.py
  readme/docs/wiki   hand-maintained counts match the manifest
  cli-text           profile description strings match the manifest
  markers            hidden-layer markers exist where declared
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import skills  # noqa: E402  (project data layer, guarded import)


def check_manifest_internal(manifest: dict) -> list[str]:
    failures: list[str] = []
    given = manifest["skills"]
    if len(given) != manifest["profiles"]["tam"]["count"]:
        failures.append("tam {0} != map length {1}".format(
            manifest["profiles"]["tam"]["count"], len(given)))
    actual: dict[str, int] = {}
    for cls in given.values():
        actual[cls] = actual.get(cls, 0) + 1
    for cls, info in manifest["classes"].items():
        if actual.get(cls, 0) != info["count"]:
            failures.append("{0} declares {1} but map has {2}".format(
                cls, info["count"], actual.get(cls, 0)))
    expect_temel = actual.get("C1", 0) + actual.get("C2", 0)
    if manifest["profiles"]["temel"]["count"] != expect_temel:
        failures.append("temel {0} != C1+C2 {1}".format(
            manifest["profiles"]["temel"]["count"], expect_temel))
    partial = manifest["profiles"]["dengeli"].get("partial", {}).get("count", 0)
    expect_dengeli = (actual.get("C1", 0) + actual.get("C2", 0)
                      + actual.get("C3", 0) + partial)
    if manifest["profiles"]["dengeli"]["count"] != expect_dengeli:
        failures.append("dengeli {0} != C1+C2+C3+partial {1}".format(
            manifest["profiles"]["dengeli"]["count"], expect_dengeli))
    return failures


def check_registry_repos(expected: dict[str, int]) -> list[str]:
    failures: list[str] = []
    for target, count in expected.items():
        actual = len(skills.list_repos(target, "en"))
        if actual != count:
            failures.append("{0} has {1} repos, expected {2}".format(
                target, actual, count))
    return failures


def check_text_contains(path: Path, needles: list[str]) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return ["{0} unreadable: {1}".format(path, exc)]
    return ["{0} missing {1!r}".format(path.name, n)
            for n in needles if n not in text]


def check_cli_text(manifest: dict, readme: str) -> list[str]:
    import re
    failures: list[str] = []
    tam = str(manifest["profiles"]["tam"]["count"])
    for lang in ("en", "tr"):
        descs = skills.S[lang]
        if tam not in descs["profile_recommended_desc"]:
            failures.append("cli {0}.recommended lacks {1}".format(lang, tam))
        for key in ("profile_trusted_desc", "profile_all_desc"):
            match = re.search(r"~(\d+)", descs[key])
            if not match:
                failures.append("cli {0}.{1} states no count".format(lang, key))
            elif match.group(1) not in readme:
                failures.append("cli {0}.{1} count {2} not in README".format(
                    lang, key, match.group(1)))
    return failures


def check_markers() -> list[str]:
    return ["marker missing: {0}".format(p)
            for p in ("Logs/._dont_migrate_", "Temp/._dont_migrate_")
            if not (ROOT / p).is_file()]


def main() -> int:
    manifest = json.loads((ROOT / "skill-specialization.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    tam = manifest["profiles"]["tam"]["count"]
    temel = manifest["profiles"]["temel"]["count"]
    dengeli = manifest["profiles"]["dengeli"]["count"]
    suites = [
        ("manifest-internal", check_manifest_internal(manifest)),
        ("registry-repos", check_registry_repos(
            {"recommended": 35, "trusted": 40, "all": 49})),
        ("readme", check_text_contains(ROOT / "README.md",
                                       [str(tam), str(temel), str(dengeli), "35", "40", "49"])),
        ("docs", check_text_contains(ROOT / "Docs" / "index.html",
                                     [str(tam), "35", "40"])),
        ("wiki", check_text_contains(ROOT / "Wiki" / "Home.md", [str(tam), "35"])
         + check_text_contains(ROOT / "Wiki" / "Installation.md", [str(tam), "35"])),
        ("cli-text", check_cli_text(manifest, readme)),
        ("markers", check_markers()),
    ]
    failed = False
    for name, problems in suites:
        if problems:
            failed = True
            for problem in problems:
                print("FAIL [{0}] {1}".format(name, problem))
        else:
            print("PASS [{0}]".format(name))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
