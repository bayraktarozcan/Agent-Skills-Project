#!/usr/bin/env python3
"""Named invariant checks: version/count parity plus marker presence.

Each check reports PASS or FAIL by name; any failure exits 1. Run from
the repository root before push. stdlib only.

Checks:
  manifest-internal  skill map length, class counts, and profile counts
                     agree inside SKILL-SPECIALIZATION.json
  registry-repos     recommended/trusted/all repo counts from skills.py
  readme/docs/wiki   hand-maintained counts match the manifest
  cli-text           profile description strings match the manifest
  markers            hidden-layer markers exist where declared
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
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
            for p in ("Logs/._dont_migrate_", "Scratch/._dont_migrate_")
            if not (ROOT / p).is_file()]


def check_repo_count_tables(paths: list[Path], expected: dict[str, str]) -> list[str]:
    """Read repo-count cells from Markdown tables; a substring check cannot drift by one.

    A row qualifies only when a cell is exactly the backticked marker (or ends
    with it, for a command cell such as ``python skills.py trusted``). The
    first purely numeric cell after the marker is the repo count. Descriptive
    prose mentioning "all" cannot be mistaken for the profile row.
    """
    problems: list[str] = []
    for path in paths:
        rows = [
            line for line in path.read_text(encoding="utf-8").splitlines()
            if line.startswith("|")
        ]
        cells_by_row = [
            [cell.strip() for cell in row.strip().strip("|").split("|")]
            for row in rows
        ]
        for marker, count in expected.items():
            found: str | None = None
            for cells in cells_by_row:
                marker_index = next(
                    (i for i, cell in enumerate(cells)
                     if cell.startswith("`") and cell.endswith("`")
                     and (cell.strip("`") == marker
                          or cell.strip("`").endswith(" " + marker))),
                    None,
                )
                if marker_index is None:
                    continue
                found = next(
                    (cell for cell in cells[marker_index + 1:]
                     if re.fullmatch(r"\d+", cell)),
                    None,
                )
                if found is not None:
                    break
            if found is None:
                problems.append(f"{path.name} missing repo-count row for {marker}")
            elif found != count:
                problems.append(
                    f"{path.name} {marker} reports {found}, expected {count}"
                )
    return problems


def check_docs_stat(path: Path, recommended: int) -> list[str]:
    needle = f'<div class="stat-value">{recommended}</div>'
    return [f"{path.name} stat value is not {recommended}"] if needle not in path.read_text(encoding="utf-8") else []


def check_pin_refs(categories: list[dict]) -> list[str]:
    """Every source repo must carry a full 40-hex commit pin, never a branch."""
    return [
        f"{entry['repo']} has no immutable SHA pin"
        for category in categories for entry in category["repos"]
        if not re.fullmatch(r"[0-9a-f]{40}", str(entry.get("ref", "")))
    ]


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        doc = base / "index.html"
        doc.write_text('<div class="stat-value">34</div>\n', encoding="utf-8")
        if not check_docs_stat(doc, 35):
            print("FAIL selftest: stale docs stat was not detected")
            return 1
        doc.write_text('<div class="stat-value">35</div>\n', encoding="utf-8")
        if check_docs_stat(doc, 35):
            print("FAIL selftest: correct docs stat was rejected")
            return 1
        page = base / "Home.md"
        page.write_text("| `trusted` | 40 | ~645 |\n| `all` | 49 | ~1000 |\n", encoding="utf-8")
        expected = {"trusted": "41", "all": "50"}
        if not check_repo_count_tables([page], expected):
            print("FAIL selftest: stale wiki counts were not detected")
            return 1
        page.write_text("| `trusted` | 41 | ~645 |\n| `all` | 50 | ~1000 |\n", encoding="utf-8")
        if check_repo_count_tables([page], expected):
            print("FAIL selftest: corrected wiki counts were rejected")
            return 1
        noisy = base / "Noisy.md"
        noisy.write_text(
            "| prose | all sorts of text | 7 | x |\n"
            "| row | Everything including all | 7 | x |\n"
            "| row | `all` | 50 | ~1000 |\n",
            encoding="utf-8",
        )
        if check_repo_count_tables([noisy], {"all": "50"}):
            print("FAIL selftest: descriptive prose was mistaken for a repo row")
            return 1
        if check_pin_refs([{"repos": [{"repo": "acme/x", "ref": "main"}]}]):
            if not check_pin_refs([{"repos": [{"repo": "acme/x"}]}]):
                print("FAIL selftest: missing pin was not detected")
                return 1
        else:
            print("FAIL selftest: branch name accepted as an immutable pin")
            return 1
    print("PASS selftest: docs stat and wiki count drift both fail by name")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    manifest = json.loads((ROOT / "SKILL-SPECIALIZATION.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    tam = manifest["profiles"]["tam"]["count"]
    temel = manifest["profiles"]["temel"]["count"]
    dengeli = manifest["profiles"]["dengeli"]["count"]
    recommended = len(skills.list_repos("recommended", "en"))
    trusted = len(skills.list_repos("trusted", "en"))
    all_repos = len(skills.list_repos("all", "en"))
    suites = [
        ("manifest-internal", check_manifest_internal(manifest)),
        ("registry-repos", check_registry_repos(
            {"recommended": 35, "trusted": 41, "all": 50})),
        ("docs-counts", check_docs_stat(ROOT / "docs" / "index.html", recommended)),
        ("wiki-counts", check_repo_count_tables(
            [ROOT / "Wiki" / "Home.md", ROOT / "Wiki" / "Installation.md",
             ROOT / "Wiki" / "Command-Reference.md"],
            {"trusted": str(trusted), "all": str(all_repos),
             "guvenli": str(trusted), "tumu": str(all_repos)})),
        ("readme", check_text_contains(ROOT / "README.md",
                                       [str(tam), str(temel), str(dengeli), "35", "41", "50"])),
        ("docs", check_text_contains(ROOT / "docs" / "index.html",
                                     [str(tam), "35", "41"])),
        ("wiki", check_text_contains(ROOT / "Wiki" / "Home.md", [str(tam), "35"])
         + check_text_contains(ROOT / "Wiki" / "Installation.md", [str(tam), "35"])),
        ("cli-text", check_cli_text(manifest, readme)),
        ("pin-refs", check_pin_refs(skills.REPOS["categories"])),
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
