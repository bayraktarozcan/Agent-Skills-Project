#!/usr/bin/env python3
"""Named invariant: declared line endings agree and working trees hold them.

The gate reads real repository state, not a hand-kept list: `git ls-files --eol`
for the working-tree/attribute columns, `.gitattributes` for declared `eol`, and
`.editorconfig` for declared `end_of_line`.

Checks (each prints PASS/FAIL by name; any failure exits 1):
  no-mixed        no tracked file reports w/mixed
  worktree-attr   where an eol attribute is declared, w/ agrees with it
  decl-agreement  .gitattributes eol and .editorconfig end_of_line agree per type

--selftest plants a mixed-ending file, a wrong-ending file and a declaration
drift in throwaway git repositories and proves each named check can fail, then
proves a clean repository passes. What this cannot see: eol drift in untracked
files (Git does not list them), or an upstream declaration nobody committed.
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LS_RE = re.compile(r"^i/(\S+)\s+w/(\S+)\s+(.*?)\t(.*)$")
EOL_RE = re.compile(r"\beol=([A-Za-z0-9]+)")
SECTION_RE = re.compile(r"^\[([^\]]+)\]\s*$")
KV_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*=\s*(.*?)\s*$")
GITATTR_RE = re.compile(r"^(\S+)\s+.*\beol=([A-Za-z0-9]+)")
BRACE_RE = re.compile(r"^(.+)\{([^}]+)\}(.*)$")


def _eol_rows(root: Path) -> list[dict[str, str]]:
    proc = subprocess.run(
        ["git", "ls-files", "--eol"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    rows: list[dict[str, str]] = []
    for line in proc.stdout.splitlines():
        match = LS_RE.match(line)
        if not match:
            continue
        index, work, meta, path = match.groups()
        declared = EOL_RE.search(meta)
        rows.append(
            {
                "i": index,
                "w": work,
                "eol": declared.group(1) if declared else "",
                "path": path,
            }
        )
    return rows


def _editor_sections(text: str) -> list[dict]:
    sections: list[dict] = []
    current = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        match = SECTION_RE.match(line)
        if match:
            current = {"pattern": match.group(1), "props": {}}
            sections.append(current)
            continue
        match = KV_RE.match(line)
        if match and current is not None:
            current["props"][match.group(1).lower()] = match.group(2).lower()
    return sections


def _pattern_matches(pattern: str, path: str) -> bool:
    patterns = [pattern]
    brace = BRACE_RE.match(pattern)
    if brace:
        patterns = [
            brace.group(1) + part + brace.group(3)
            for part in brace.group(2).split(",")
        ]
    name = path.rsplit("/", 1)[-1]
    for candidate in patterns:
        if candidate == "*":
            return True
        if candidate.startswith("*.") and name.endswith(candidate[1:]):
            return True
        if "/" not in candidate and candidate == name:
            return True
    return False


def _effective_editor_eol(sections: list[dict], path: str) -> str:
    value = ""
    for section in sections:
        if _pattern_matches(section["pattern"], path):
            value = section["props"].get("end_of_line", value)
    return value


def _git_declarations(text: str) -> dict[str, str]:
    declared: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = GITATTR_RE.match(line)
        if match:
            declared[match.group(1)] = match.group(2)
    return declared


def check(root: Path = ROOT, verbose: bool = True) -> list[str]:
    failures: list[str] = []
    rows = _eol_rows(root)

    mixed = [row["path"] for row in rows if row["w"] == "mixed"]
    if mixed:
        failures.append("no-mixed: " + ", ".join(mixed))
    elif verbose:
        print(f"PASS no-mixed: {len(rows)} tracked files have consistent endings")

    wrong = [
        row["path"]
        for row in rows
        if row["eol"] and row["w"] in ("lf", "crlf") and row["w"] != row["eol"]
    ]
    if wrong:
        failures.append("worktree-attr: " + ", ".join(wrong))
    elif verbose:
        print("PASS worktree-attr: working trees match declared eol where present")

    sections = _editor_sections((root / ".editorconfig").read_text(encoding="utf-8"))
    declared = _git_declarations((root / ".gitattributes").read_text(encoding="utf-8"))
    bad: list[str] = []
    for pattern, eol in declared.items():
        probe = "probe" if pattern == "*" else "probe" + pattern[1:]
        editor_eol = _effective_editor_eol(sections, probe)
        if editor_eol != eol:
            bad.append(f"{pattern}: git={eol} editor={editor_eol or 'unset'}")
    if bad:
        failures.append("decl-agreement: " + ", ".join(bad))
    elif verbose:
        print(f"PASS decl-agreement: {len(declared)} declared types agree")
    return failures


def _make_repo(path: Path, files: dict[str, bytes], attrs: str, editor: str) -> None:
    path.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-q"], cwd=path, check=True, capture_output=True
    )
    (path / ".gitattributes").write_bytes(attrs.encode("utf-8"))
    (path / ".editorconfig").write_bytes(editor.encode("utf-8"))
    for name, data in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    subprocess.run(
        ["git", "add", "-A"], cwd=path, check=True, capture_output=True
    )


def selftest() -> int:
    import shutil

    if shutil.which("git") is None:
        print("SKIP selftest: git is unavailable")
        return 0
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        clean = base / "clean"
        _make_repo(
            clean,
            {"a.py": b"print(1)\n"},
            "*.py text eol=lf\n",
            "[*]\nend_of_line = lf\n",
        )
        assert check(clean, verbose=False) == [], "clean repo must pass"
        mixed = base / "mixed"
        _make_repo(
            mixed,
            {"a.py": b"a\r\nb\nc\r\n"},
            "*.py text eol=lf\n",
            "[*]\nend_of_line = lf\n",
        )
        assert any(
            f.startswith("no-mixed:") for f in check(mixed, verbose=False)
        ), "mixed endings must fail no-mixed"
        wrong = base / "wrong"
        _make_repo(
            wrong,
            {"a.py": b"a\r\nb\r\n"},
            "*.py text eol=lf\n",
            "[*]\nend_of_line = lf\n",
        )
        assert any(
            f.startswith("worktree-attr:") for f in check(wrong, verbose=False)
        ), "wrong working-tree eol must fail worktree-attr"
        drift = base / "drift"
        _make_repo(
            drift,
            {"a.ps1": b"a\r\n"},
            "*.ps1 text eol=crlf\n",
            "[*]\nend_of_line = lf\n",
        )
        assert any(
            f.startswith("decl-agreement:") for f in check(drift, verbose=False)
        ), "declaration drift must fail decl-agreement"
    print("PASS selftest: every named line-ending check can fail")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL " + failure)
        return 1
    print("OK: line-ending declarations and working trees agree")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
