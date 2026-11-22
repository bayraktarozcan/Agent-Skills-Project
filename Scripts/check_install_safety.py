#!/usr/bin/env python3
"""Named invariant: installer safety unit tests pass.

Runs the runtime-built unit tests under Tests/ with stdlib unittest. The
suite exercises linked files, linked parents, escaped paths, destination
links, frontmatter rewrites, provenance drift, target dedup and clone retry.

--selftest plants a deliberately failing test and proves the runner reports
it; a green suite alone proves only that the runner was never allowed to fail.
"""

from __future__ import annotations

import argparse
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _run(extra: unittest.TestSuite | None = None, verbosity: int = 1) -> int:
    loader = unittest.TestLoader()
    suite = loader.discover(str(ROOT / "Tests"), pattern="test_*.py")
    if extra is not None:
        suite.addTests(extra)
    result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
    return 0 if result.wasSuccessful() else 1


def selftest() -> int:
    class Planted(unittest.TestCase):
        def test_planted_failure(self) -> None:
            self.fail("planted failure must be detected")

    planted = unittest.TestSuite([Planted("test_planted_failure")])
    if _run(planted, verbosity=0) == 0:
        print("FAIL selftest: planted failure was not detected")
        return 1
    print("PASS selftest: planted failure detected")
    return _run()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return _run()


if __name__ == "__main__":
    raise SystemExit(main())
