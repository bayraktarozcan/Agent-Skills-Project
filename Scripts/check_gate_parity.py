#!/usr/bin/env python3
"""Named invariant: the documented local gate covers the checks CI declares.

The two lists are read from the artifacts that own them, not from a copy kept
beside them: the fenced command block in AGENTS.md (local) and every `run:` /
`script:` line in the GitHub workflows and .gitlab-ci.yml (CI). Interpreter
spellings (`python`, `python3`, `py -3`) and redirection noise are normalized.

Checks (each prints PASS/FAIL by name; any failure exits 1):
  ci-covered       every core CI check (skills.py / py_compile) is in the gate
  local-covered    every core gate check is in CI
  ci-scripts       every non-exempt CI Scripts/ check is in the gate
  local-scripts    every non-exempt gate Scripts/ check is in CI

Declared asymmetries (the gate cannot run them the way CI does):
  CI_ONLY    network-bound release audit, commit-range encoding audit, lychee
  LOCAL_ONLY offline doc/manifest and mirror checks, all --selftest runs
What this cannot see: a check hidden behind a script CI never calls, or a
renamed workflow step that stops containing the command text.
"""

from __future__ import annotations

import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CI_ONLY = (
    "Scripts/check_release_hygiene.py",
    "Scripts/check_encoding.py --commits",
    "lychee",
)
LOCAL_ONLY = (
    "Scripts/check_version_parity.py",
    "Scripts/verify_mirror.py",
)
SELFTEST_TOKENS = ("--selftest", " selftest")
CHECK_MARKERS = (
    "skills.py",
    "py_compile",
    "Scripts/check_",
    "Scripts/python_floor.py",
    "Scripts/verify_mirror.py",
)

FENCE_RE = re.compile(r"```[^\n]*\n(.*?)```", re.S)
GATE_HEADER = "Single local gate command"
RUN_RE = re.compile(r"^\s*(?:-\s*)?(?:run|script):\s*(.*)$")
LIST_RE = re.compile(r"^\s+-\s+(.*)$")
PY_RE = re.compile(r"^(?:python3|python|py\s+-3)\s+")


def normalize(command: str) -> str:
    command = command.strip()
    command = PY_RE.sub("py ", command)
    command = re.sub(r"\s*>/dev/null\s*", " ", command)
    command = re.sub(r"\s*>\s*\$null\s*", " ", command)
    command = re.sub(r"\s*2>&1\s*", " ", command)
    command = re.sub(r"\s+--offline\b", "", command)
    return " ".join(command.split())


def local_commands(root: Path) -> list[str]:
    text = (root / "AGENTS.md").read_text(encoding="utf-8")
    start = text.find(GATE_HEADER)
    if start < 0:
        return []
    match = FENCE_RE.search(text[start:])
    if not match:
        return []
    return [normalize(part) for part in match.group(1).split("&&")]


def ci_commands(root: Path) -> list[str]:
    files = sorted((root / ".github" / "workflows").glob("*.yml"))
    files.append(root / ".gitlab-ci.yml")
    commands: list[str] = []
    for path in files:
        if not path.exists():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            match = RUN_RE.match(line)
            if match:
                candidate = match.group(1)
            else:
                item = LIST_RE.match(line)
                candidate = item.group(1) if item else ""
            normalized = normalize(candidate)
            if normalized.startswith("py ") and any(
                token in normalized for token in CHECK_MARKERS
            ):
                commands.append(normalized)
    return commands


def _exempt(command: str) -> bool:
    return any(
        token in command
        for token in CI_ONLY + LOCAL_ONLY + SELFTEST_TOKENS
    )


def _core(commands: list[str]) -> list[str]:
    return [
        c
        for c in commands
        if any(token in c for token in ("skills.py", "py_compile")) and not _exempt(c)
    ]


def _scripts(commands: list[str]) -> list[str]:
    return [c for c in commands if "Scripts/" in c and not _exempt(c)]


def check(root: Path = ROOT, verbose: bool = True) -> list[str]:
    failures: list[str] = []
    local, ci = local_commands(root), ci_commands(root)
    if not local or not ci:
        return ["gate-inventory: missing gate block or CI commands"]

    ci_core, local_core = _core(ci), _core(local)
    ci_scripts, local_scripts = _scripts(ci), _scripts(local)

    pairs = (
        ("ci-covered", ci_core, local_core),
        ("local-covered", local_core, ci_core),
        ("ci-scripts", ci_scripts, local_scripts),
        ("local-scripts", local_scripts, ci_scripts),
    )
    for name, source, target in pairs:
        missing = [command for command in source if command not in target]
        if missing:
            failures.append(name + ": " + ", ".join(missing))
        elif verbose:
            print(f"PASS {name}: {len(source)} commands mirrored")
    return failures


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temp:
        base = Path(temp)
        workflows = base / ".github" / "workflows"
        workflows.mkdir(parents=True)
        (base / ".gitlab-ci.yml").write_text("", encoding="utf-8")

        def write_gate(commands: list[str]) -> None:
            block = " && ".join(commands)
            (base / "AGENTS.md").write_text(
                "## Commands\n\n" + GATE_HEADER + " (x):\n\n```text\n"
                + block + "\n```\n",
                encoding="utf-8",
            )

        def write_ci(commands: list[str]) -> None:
            steps = "".join(
                "      - run: " + command + "\n" for command in commands
            )
            (workflows / "CI.yml").write_text(
                "jobs:\n  t:\n    steps:\n" + steps, encoding="utf-8"
            )

        core = [
            "python -m py_compile skills.py",
            "python skills.py --version",
            "python skills.py --list",
        ]
        write_gate(core)
        write_ci(core)
        assert check(base, verbose=False) == [], "matching gate and CI must pass"

        write_ci(core + ["python skills.py --dry-run"])
        assert any(
            f.startswith("ci-covered:") for f in check(base, verbose=False)
        ), "CI-only command must fail ci-covered"

        write_gate(core + ["py skills.py --local-only"])
        write_ci(core)
        assert any(
            f.startswith("local-covered:") for f in check(base, verbose=False)
        ), "gate-only command must fail local-covered"

        write_gate(core)
        write_ci(core + ["python Scripts/check_repo_conventions.py"])
        assert any(
            f.startswith("ci-scripts:") for f in check(base, verbose=False)
        ), "CI-only script check must fail ci-scripts"

        write_gate(core + ["py Scripts/check_action_refs.py"])
        write_ci(core)
        assert any(
            f.startswith("local-scripts:") for f in check(base, verbose=False)
        ), "gate-only script check must fail local-scripts"
    print("PASS selftest: every named parity check can fail")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    failures = check()
    if failures:
        for failure in failures:
            print("FAIL " + failure)
        return 1
    print("OK: local gate and CI declare the same core checks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
