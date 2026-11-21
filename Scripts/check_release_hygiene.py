#!/usr/bin/env python3
"""Named invariant: every published release is hygienic on every host.

Read-only; requires gh and glab authenticated. Checks (PASS/FAIL by name, any
failure exits 1):
  pair-count     both hosts report the same set of tags
  title-format   "<tag> — <description>", tag exactly once, prefix only on older
  body-structure EN then TR, each with version heading and required sections
  no-garbage     no bare #N, embedded changelog TOC, or other version's heading
  cross-host     title and body byte-identical after LF normalization
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GH_REPO = "bayraktarozcan/Agent-Skills-Project"
GL_PROJECT = "86516633"

EN = {"Summary", "Added", "Changed", "Removed", "Fixed", "Files", "Documentation"}
TR = {"Özet", "Eklenenler", "Değiştirilenler", "Kaldırılanlar", "Düzeltilenler",
      "Dosyalar", "Belgelendirme"}


def norm(s: str) -> str:
    return s.replace("\r\n", "\n").strip()


def current_version() -> str:
    text = (ROOT / "skills.py").read_text(encoding="utf-8")
    m = re.search(r'"version_str"\s*:\s*"AgentSynapse v([0-9.]+)"', text)
    if m is None:
        raise SystemExit("current version not found in skills.py")
    return m.group(1)


def releases() -> tuple[dict, dict]:
    gh = json.loads(subprocess.check_output([
        "gh", "api", "--paginate", f"repos/{GH_REPO}/releases"
    ]).decode())
    # GitLab: CI runners do not ship glab, so use REST when a token is injected;
    # locally fall back to glab's keyring-backed CLI.
    if os.environ.get("GITLAB_TOKEN"):
        url = f"https://gitlab.com/api/v4/projects/{GL_PROJECT}/releases?per_page=100"
        req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": os.environ["GITLAB_TOKEN"]})
        with urllib.request.urlopen(req, timeout=30) as response:
            gl = json.load(response)
    else:
        gl = json.loads(subprocess.check_output([
            "glab", "api", f"projects/{GL_PROJECT}/releases?per_page=100"
        ]).decode())
    return ({r["tag_name"]: r for r in gh}, {r["tag_name"]: r for r in gl})


def check() -> list[str]:
    failures: list[str] = []
    gh, gl = releases()
    latest = "v" + current_version()
    if set(gh) != set(gl):
        failures.append(f"pair-count: GH {sorted(gh)} vs GL {sorted(gl)}")
    else:
        print(f"PASS pair-count: {len(gh)} releases on both hosts")

    bad_titles = []
    for tag, r in gh.items():
        title = r["name"]
        prefix = "[DEPRECATED] " if tag != latest else ""
        if not re.fullmatch(r"(?:\[DEPRECATED\] )?" + re.escape(tag) + r" — \S.*", title):
            bad_titles.append(f"{tag}: {title}")
        elif tag != latest and not title.startswith(prefix):
            bad_titles.append(f"{tag}: missing prefix")
        elif tag == latest and "[DEPRECATED]" in title:
            bad_titles.append(f"{tag}: current marked deprecated")
        elif title.count(tag) != 1:
            bad_titles.append(f"{tag}: tag appears {title.count(tag)} times")
    if bad_titles:
        failures.append("title-format: " + ", ".join(bad_titles))
    else:
        print("PASS title-format: all titles canonical")

    bad_bodies = []
    for tag, r in gh.items():
        body = r["body"].replace("\r\n", "\n")
        halves = re.split(r"(?m)^## v", body)
        if len(halves) < 3:
            bad_bodies.append(f"{tag}: missing bilingual halves")
            continue
        heads_en = set(re.findall(r"(?m)^### (.+)$", halves[1]))
        heads_tr = set(re.findall(r"(?m)^### (.+)$", "## v" + halves[2]))
        core_en = {"Summary", "Files", "Documentation"}
        core_tr = {"Özet", "Dosyalar", "Belgelendirme"}
        content_en = heads_en & {"Added", "Changed", "Removed", "Fixed"}
        content_tr = heads_tr & {"Eklenenler", "Değiştirilenler", "Kaldırılanlar", "Düzeltilenler"}
        if not core_en.issubset(heads_en) or not core_tr.issubset(heads_tr):
            bad_bodies.append(f"{tag}: missing core sections")
        elif not content_en or not content_tr:
            bad_bodies.append(f"{tag}: no content section")
        elif len(content_en) != len(content_tr):
            bad_bodies.append(f"{tag}: EN/TR content scope differs")
    if bad_bodies:
        failures.append("body-structure: " + ", ".join(bad_bodies))
    else:
        print("PASS body-structure: bilingual sections present")

    garbage = []
    for tag, r in gh.items():
        body = r["body"]
        if re.search(r"(?m)^\s*\|\s*#\d+", body) or re.search(r"(?<!\w)#\d+\b", body):
            garbage.append(f"{tag}: bare #N")
        if "<details" in body or "<a id=" in body or "Table of Contents" in body or "İçindekiler" in body:
            garbage.append(f"{tag}: embedded TOC")
        for other in gh:
            if other != tag and f"## {other} —" in body:
                garbage.append(f"{tag}: other version {other}")
    if garbage:
        failures.append("no-garbage: " + ", ".join(garbage))
    else:
        print("PASS no-garbage: no bare numbers, TOC or foreign rows")

    mismatch = []
    for tag in set(gh) & set(gl):
        if norm(gh[tag]["name"]) != norm(gl[tag]["name"]):
            mismatch.append(f"{tag}: title")
        if norm(gh[tag]["body"]) != norm(gl[tag]["description"]):
            mismatch.append(f"{tag}: body")
    if mismatch:
        failures.append("cross-host: " + ", ".join(mismatch))
    else:
        print("PASS cross-host: title and body byte-identical after LF normalization")
    return failures


def main() -> int:
    failures = check()
    for failure in failures:
        print("FAIL", failure)
    if failures:
        return 1
    print("OK: release hygiene holds on every host")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
