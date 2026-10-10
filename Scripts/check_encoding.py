#!/usr/bin/env python3
"""Detect encoding damage (mojibake) across the repository and commit metadata.

Scans three surfaces:
  1. Every tracked text file (via `git ls-files`) for:
       - invalid UTF-8 byte sequences (strict decode failure)
       - double-encoded UTF-8 signatures produced when UTF-8 bytes were read as
         a single-byte encoding (latin-1 / windows-1252 / windows-1254).
  2. Branch and tag names (`git for-each-ref`) for the same two classes.
  3. Commit messages, plus author and committer names, in a given range
     (`--commits BEFORE..AFTER`) for the same two classes.

The double-encoding signature is purely byte-structural and ASCII-safe:

  * a 2-byte UTF-8 char (C2-DF 80-BF) misread as latin-1 leaves the literal
    characters U+00C2..U+00DF followed by U+0080..U+00BF
  * a 3-byte UTF-8 char (E0-EF 80-BF 80-BF) misread as latin-1 leaves
    U+00E0..U+00EF followed by two chars in U+0080..U+00BF

Only these exact structural pairs are flagged (e.g. the text "{escaped}" -- literally
U+00C3 U+00A7 -- which is the double-encoded form of "c"). Genuine text that
merely contains a latin-1 letter such as "C" or "e" is not affected. To avoid
false positives from various spellings, only decoded text that already is valid
UTF-8 is inspected.

No false confidence: a clean run prints "OK" per surface and exits 0; any
finding prints the file/ref/commit, the offending context and exits non-zero.

Usage:
  python Scripts/check_encoding.py                       # files + refs only
  python Scripts/check_encoding.py --commits A..B        # + commit metadata
  python Scripts/check_encoding.py --commits 0000..B     # root push: scan B only
  python Scripts/check_encoding.py --selftest            # verify the detectors
  python Scripts/check_encoding.py --no-files            # refs/commits only
"""

import io
import re
import subprocess
import sys

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

PROBE_BYTES = 8192

# Structural double-encoded signatures (see module docstring).
_SIG_2 = re.compile("[\u00c2-\u00df][\u0080-\u00bf]")
_SIG_3 = re.compile("[\u00e0-\u00ef][\u0080-\u00bf][\u0080-\u00bf]")


def is_binary(head: bytes) -> bool:
    return b"\x00" in head


def format_pos(text: str, char_col: int) -> str:
    line = text.count("\n", 0, char_col) + 1
    col = char_col - (text.rfind("\n", 0, char_col) + 1)
    snippet = text[char_col:char_col + 60].replace("\n", " ")
    return f"line {line}, col {col + 1}: {snippet!r}"


def inspect_text(raw: bytes, failures: list, where: str):
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        failures.append(f"{where}: invalid UTF-8 at byte {exc.start} "
                        f"(reason: {exc.reason})")
        return
    for pat, label in ((_SIG_2, "2-byte double-encoding"),
                       (_SIG_3, "3-byte double-encoding")):
        for m in pat.finditer(text):
            snippet = text[m.start():m.start() + 20].replace("\n", " ")
            failures.append(
                f"{where}: {label} signature {m.group(0)!r} at "
                f"{format_pos(text, m.start())} "
                f"(context: ...{snippet}...)")
            if len(failures) >= 50:
                return


def scan_files() -> int:
    failures = []
    try:
        out = subprocess.run(["git", "ls-files", "-z"], check=True,
                             capture_output=True).stdout
    except subprocess.CalledProcessError as exc:
        print("ERROR: git ls-files failed: "
              + exc.stderr.decode("utf-8", "replace").strip())
        return EXIT_FINDINGS
    paths = [p for p in out.split(b"\x00") if p]
    text_count = 0
    for raw_path in paths:
        path = raw_path.decode("utf-8", errors="replace")
        try:
            with open(path, "rb") as fh:
                raw = fh.read()
        except OSError as exc:
            failures.append(f"{path}: unreadable ({exc})")
            continue
        if is_binary(raw[:PROBE_BYTES]):
            continue
        text_count += 1
        inspect_text(raw, failures, path)
    print(f"tracked files scanned: {len(paths)} "
          f"({text_count} text, {len(paths) - text_count} binary)")
    return report("tracked files", failures)


def scan_refs() -> int:
    failures = []
    try:
        out = subprocess.run(
            ["git", "for-each-ref", "--format=%(refname:short)"],
            check=True, capture_output=True).stdout
    except subprocess.CalledProcessError as exc:
        print("ERROR: git for-each-ref failed: "
              + exc.stderr.decode("utf-8", "replace").strip())
        return EXIT_FINDINGS
    refs = [r for r in out.split(b"\n") if r]
    for raw_ref in refs:
        ref = raw_ref.decode("utf-8", errors="replace")
        try:
            text = raw_ref.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            failures.append(f"ref {ref!r}: invalid UTF-8 at byte {exc.start}")
            continue
        for pat, label in ((_SIG_2, "2-byte double-encoding"),
                           (_SIG_3, "3-byte double-encoding")):
            for m in pat.finditer(text):
                failures.append(f"ref {ref!r}: {label} signature "
                                f"{m.group(0)!r}")
    print(f"refs scanned: {len(refs)}")
    return report("branch/tag refs", failures)


def scan_commits(commit_range: str) -> int:
    parts = commit_range.split("..")
    if len(parts) not in (1, 2) or any(not p for p in parts):
        print(f"ERROR: invalid commit range {commit_range!r} "
              f"(expected BEFORE..AFTER)")
        return EXIT_USAGE
    if len(parts) == 2:
        before, after = parts
        spec = after if before.strip("0") == "" else f"{before}..{after}"
    else:
        spec = parts[0]
    fmt = "%H%x00%an%x00%cn%x00%B%x00"
    try:
        out = subprocess.run(["git", "log", f"--format={fmt}", spec],
                             check=True, capture_output=True).stdout
    except subprocess.CalledProcessError as exc:
        print(f"ERROR: git log failed for range {spec!r}: "
              + exc.stderr.decode("utf-8", "replace").strip())
        return EXIT_FINDINGS
    failures = []
    commits = []
    for rec in out.split(b"\x00"):
        if rec:
            commits.append(rec)
    count = 0
    for i in range(0, len(commits), 4):
        if i + 3 >= len(commits):
            break
        sha, author, committer, body = commits[i:i + 4]
        short = sha.decode("utf-8", errors="replace")[:12]
        count += 1
        inspect_commit_part(author, f"commit {short} author", failures)
        inspect_commit_part(committer, f"commit {short} committer", failures)
        inspect_commit_part(body, f"commit {short} message", failures)
    print(f"commits scanned: {count} (range {spec!r})")
    return report("commit metadata", failures)


def inspect_commit_part(raw: bytes, where: str, failures: list):
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        failures.append(f"{where}: invalid UTF-8 at byte {exc.start}")
        return
    for pat, label in ((_SIG_2, "2-byte double-encoding"),
                       (_SIG_3, "3-byte double-encoding")):
        for m in pat.finditer(text):
            failures.append(f"{where}: {label} signature {m.group(0)!r}"
                            f" in {text[m.start():m.start() + 40]!r}")


def report(surface: str, failures: list) -> int:
    if failures:
        print(f"FAIL {surface} ({len(failures)} finding(s)):")
        for f in failures[:20]:
            print("  - " + f)
        if len(failures) > 20:
            print(f"  ... and {len(failures) - 20} more")
        return EXIT_FINDINGS
    print(f"OK   {surface}")
    return EXIT_OK


def selftest() -> int:
    cases = [
        # (bytes, expected_clean)
        (b"plain ascii text\n", True),
        (b"T\xc3\xbcrk\xc3\xa7e \xc3\xb6z\xc3\xbcr\n", True),   # valid utf-8
        (b"caf\xc3\xa9 menu\n", True),                            # valid utf-8
        ("\u00c3\u00a7\u00c3\u00b6".encode("utf-8"), False),      # U+00C3 U+00A7 U+00C3 U+00B6 = mojibake
        ("d\u00c3\u00bcnya".encode("utf-8"), False),               # d U+00C3 U+00BC nya = mojibake
        ("\u00e2\u0080\u0099ti".encode("utf-8"), False),          # 3-byte sig
        (b"\xff\xfe\x00\xd8junk", False),                         # invalid utf-8
    ]
    ok = 0
    for raw, want_clean in cases:
        failures = []
        inspect_text(raw, failures, "selftest")
        got_clean = not failures
        if got_clean == want_clean:
            ok += 1
            print(f"  selftest {raw!r}: {'clean' if want_clean else 'flagged'} -> OK")
        else:
            print(f"  selftest {raw!r}: expected "
                  f"{'clean' if want_clean else 'flagged'} but got "
                  f"{'clean' if got_clean else 'flagged'} -> MISMATCH")
    return EXIT_OK if ok == len(cases) else EXIT_FINDINGS


def main(argv) -> int:
    commit_range = None
    do_files = True
    do_refs = True
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--commits":
            i += 1
            if i >= len(argv):
                print("ERROR: --commits needs BEFORE..AFTER")
                return EXIT_USAGE
            commit_range = argv[i]
        elif arg == "--no-files":
            do_files = False
        elif arg == "--no-refs":
            do_refs = False
        elif arg == "--selftest":
            return selftest()
        elif arg in ("-h", "--help"):
            print(__doc__)
            return EXIT_OK
        else:
            print(f"ERROR: unknown argument {arg!r}")
            return EXIT_USAGE
        i += 1

    rc = EXIT_OK
    if do_files and scan_files() != EXIT_OK:
        rc = EXIT_FINDINGS
    if do_refs and scan_refs() != EXIT_OK:
        rc = EXIT_FINDINGS
    if commit_range and scan_commits(commit_range) != EXIT_OK:
        rc = EXIT_FINDINGS

    print("check_encoding: " + ("CLEAN" if rc == EXIT_OK else "FINDINGS"))
    return rc


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")
    sys.exit(main(sys.argv[1:]))