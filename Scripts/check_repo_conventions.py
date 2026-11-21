#!/usr/bin/env python3
"""Named invariant: tracked text files end with LF and hide no local layer name.

Checks (PASS/FAIL by name, any failure exits 1):
  final-newline     every tracked text file ends with LF
  hidden-layer-names  no tracked file names or contents name a gitignored local
                    layer file (the .gitignore pattern is the only exception)
  no-legacy-version  no prose advertises an end-of-life Python floor (3.8+)
  heading-case     documentation headings follow the title-case rule in AGENTS.md
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HIDDEN_TOKENS = ("AGENTS-TR.md", "SKILL-SPECIALIZATION-AUDIT.md")

MINOR = {"a", "an", "the", "and", "or", "but", "nor", "for", "of", "on", "per",
         "to", "via", "with", "as", "at", "by", "in", "if", "is", "are", "was",
         "were", "be", "been", "am", "ve", "veya", "ya", "ile", "için", "bir",
         "göre", "den", "dan", "gibi", "kadar", "olarak", "mı", "mi", "mu", "mü"}
ACRONYMS = {"ADMX", "API", "ASCII", "BOM", "CD", "CI", "DNS", "GUID", "HTML",
            "HTTP", "HTTPS", "ID", "JSON", "JS", "LTS", "OS", "PDF", "SHA",
            "SHA1", "SHA256", "TLS", "UTC", "URL", "UTF8", "XML", "YAML", "CSS",
            "IO", "UI", "UX", "AI", "CLI", "CDN"}
MIXED = {"ioc", "powershell", "github", "gitlab", "dependabot", "pester", "lychee",
         "gitleaks", "actionlint", "markdown", "javascript", "i18n", "changelog",
         "readme", "wiki", "windows", "linux", "macos", "git", "codeql", "python",
         "semver"}
SKILL_NAME = "git-remote-credential-hygiene"


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
        # CHANGELOG is a historical record: it may describe the removal of an
        # old claim without advertising it. See AGENTS.md Historical records.
        if name == "CHANGELOG.md" or not name.endswith((".md", ".html")):
            continue
        text = (root / name).read_bytes().decode("utf-8", errors="replace")
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(r"Python 3\.8\+|3\.8 or later|3\.8 veya üstü", line, re.I):
                legacy.append(f"{name}:{i}")
    if legacy:
        failures.append("no-legacy-version: " + ", ".join(legacy))
    else:
        print("PASS no-legacy-version: no end-of-life Python floor advertised")

    bad_headings: list[str] = []
    for name in files:
        if not name.endswith(".md"):
            continue
        in_fence = False
        for i, line in enumerate((root / name).read_text(encoding="utf-8").splitlines(), 1):
            if re.match(r"^\s*(```|~~~)", line):
                in_fence = not in_fence
                continue
            m = re.match(r"^#{1,6}\s+(.+)$", line)
            if in_fence or m is None:
                continue
            text = re.sub(r"`[^`]*`", "", m.group(1))
            if re.search(r"\b(?:İs|İn|İf|İnto|İtself)\b", text):
                bad_headings.append(f"{name}:{i}: Turkish dotted I in English word")
            if re.match(r"^\[?v?\d|^\[?V\d|^vX", text):
                continue
            words = [w for w in text.split() if w]
            for wi, word in enumerate(words):
                if "`" in word or "[" in word or "<" in word or "://" in word:
                    continue
                core = re.sub(r"^[^A-Za-zÇĞİÖŞÜçğıöşü0-9]+", "", word)
                core = re.sub(r"[^A-Za-zÇĞİÖŞÜçğıöşü0-9]+$", "", core)
                if not core:
                    continue
                low = core.lower()
                if low in MIXED or core.upper() in ACRONYMS:
                    continue
                if low in MINOR and wi > 0:
                    continue
                if low.startswith(SKILL_NAME):
                    continue
                parts = [p for p in re.split(r"[-/]", core) if p]
                for sub in parts:
                    sl = sub.lower()
                    if sl in MIXED or sub.upper() in ACRONYMS:
                        continue
                    if sl in MINOR and sub != parts[0]:
                        continue
                    if sub[0] != sub[0].upper():
                        bad_headings.append(f"{name}:{i}: {sub}")
    if bad_headings:
        failures.append("heading-case: " + ", ".join(bad_headings[:10]))
    else:
        print("PASS heading-case: documentation headings follow title case")
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
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "x.md"
        p.write_text("# A Good Heading\n\n## a bad heading\n\n### What İs This\n",
                     encoding="utf-8")
        text = p.read_text(encoding="utf-8")
        if not any(re.search(r"^## [a-z]", l) for l in text.splitlines()):
            print("SELFTEST FAIL: planted lowercase heading not detected")
            return 1
    print("SELFTEST OK: planted missing newline and lowercase heading fail by name")
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
