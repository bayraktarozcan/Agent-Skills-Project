#!/usr/bin/env python3
"""Runtime-built unit tests for installer path safety and provenance.

No fixture files are committed: every sample is assembled in a throwaway
temporary directory at run time, so an integrity scan cannot read its own
fixtures. stdlib only.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import skills  # noqa: E402  (project module under test)


class PathSafetyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.root = self.base / "clone"
        self.root.mkdir()
        self.file = self.root / "SKILL.md"
        self.file.write_text("---\nname: demo\n---\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_regular_file_accepted(self) -> None:
        self.assertIsNone(skills._source_verdict(self.file, self.root, self.root))

    def test_outside_path_rejected(self) -> None:
        outside = self.base / "outside.md"
        outside.write_text("secret", encoding="utf-8")
        self.assertIsNotNone(skills._source_verdict(outside, self.root, self.root))

    def test_dotdot_path_rejected(self) -> None:
        outside = self.base / "outside.md"
        outside.write_text("secret", encoding="utf-8")
        candidate = self.root / ".." / "outside.md"
        self.assertIsNotNone(skills._source_verdict(candidate, self.root, self.root))

    def test_symlink_file_rejected(self) -> None:
        link = self.root / "linked.md"
        try:
            link.symlink_to(self.file)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertIsNotNone(skills._source_verdict(link, self.root, self.root))

    def test_symlink_parent_rejected(self) -> None:
        real = self.base / "elsewhere"
        real.mkdir()
        (real / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
        link_dir = self.root / "linked"
        try:
            link_dir.symlink_to(real, target_is_directory=True)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        candidate = link_dir / "SKILL.md"
        self.assertIsNotNone(skills._source_verdict(candidate, self.root, self.root))

    def test_destination_symlink_rejected(self) -> None:
        dest = self.root / "skill"
        dest_file = dest / "SKILL.md"
        dest.mkdir()
        target = self.base / "victim.txt"
        target.write_text("do not overwrite", encoding="utf-8")
        try:
            dest_file.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertIsNotNone(skills._dest_verdict(dest, dest_file, self.root))

    def test_clean_destination_accepted(self) -> None:
        dest = self.root / "skill"
        self.assertIsNone(skills._dest_verdict(dest, dest / "SKILL.md", self.root))

    def test_trusted_install_root_is_not_rejected(self) -> None:
        saved = skills._is_link_or_junction
        skills._is_link_or_junction = lambda path: path == self.root
        try:
            dest = self.root / "skill"
            self.assertIsNone(skills._dest_verdict(dest, dest / "SKILL.md", self.root))
        finally:
            skills._is_link_or_junction = saved


class FrontmatterTests(unittest.TestCase):
    def test_name_is_case_insensitive(self) -> None:
        text = "---\nName: Bad Name\ndescription: x\n---\n"
        self.assertEqual(skills._frontmatter_name(text), "Bad Name")

    def test_rewrite_stays_inside_frontmatter(self) -> None:
        text = "---\nName: Bad Name\ndescription: x\n---\nname: body trap\n"
        out = skills._rewrite_frontmatter_name(text, "good-name")
        self.assertIn("Name: good-name", out)
        self.assertIn("name: body trap", out)

    def test_rewrite_preserves_key_and_spacing(self) -> None:
        text = "---\nname  :   Bad Name\n---\n"
        out = skills._rewrite_frontmatter_name(text, "good-name")
        self.assertIn("name  : good-name", out)

    def test_body_without_frontmatter_untouched(self) -> None:
        text = "name: only in body\n"
        self.assertEqual(skills._rewrite_frontmatter_name(text, "x"), text)

    def test_name_beyond_old_2000_char_limit(self) -> None:
        text = "---\ndescription: " + "x" * 2500 + "\nname: Real Name\n---\n"
        self.assertEqual(skills._frontmatter_name(text), "Real Name")

    def test_bom_frontmatter_is_rewritten(self) -> None:
        text = "\ufeff---\nname: Bad Name\n---\n"
        out = skills._rewrite_frontmatter_name(text, "good-name")
        self.assertTrue(out.startswith("\ufeff"))
        self.assertIn("name: good-name", out)

    def test_valid_name_sanitizes(self) -> None:
        self.assertEqual(skills.valid_name("../Bad Name_!!"), "bad-name")


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.saved = json.loads(json.dumps(skills.REPOS))

    def tearDown(self) -> None:
        skills.REPOS.clear()
        skills.REPOS.update(self.saved)

    def test_ref_and_trust_are_read_from_data_layer(self) -> None:
        repo = skills.REPOS["categories"][0]["repos"][0]["repo"]
        entry = next(
            r for c in skills.REPOS["categories"] for r in c["repos"]
            if r["repo"] == repo
        )
        entry["ref"] = "a" * 40
        entry["trust"] = "verified-review"
        self.assertEqual(skills._repo_ref(repo), "a" * 40)
        self.assertEqual(skills._repo_trust(repo), "verified-review")

    def test_targets_deduplicated_and_aliased(self) -> None:
        self.assertEqual(
            skills._resolve_targets(["K2", "k2", "onerilen", "tumu"]),
            ["K2", "recommended", "all"],
        )


class ProvenanceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.saved_path = skills.PROVENANCE_PATH
        self.saved_dir = skills.SKILLS_DIR
        skills.PROVENANCE_PATH = self.base / "provenance.jsonl"
        skills.SKILLS_DIR = self.base / "skills"

    def tearDown(self) -> None:
        skills.PROVENANCE_PATH = self.saved_path
        skills.SKILLS_DIR = self.saved_dir
        self.tmp.cleanup()

    def test_drift_detected_after_content_change(self) -> None:
        target = skills.SKILLS_DIR / "demo"
        target.mkdir(parents=True)
        skill_file = target / "SKILL.md"
        skill_file.write_text("original", encoding="utf-8")
        record = {
            "skill": "demo",
            "source": "SKILL.md",
            "sha256": skills.hashlib.sha256(b"original").hexdigest(),
        }
        skills.PROVENANCE_PATH.write_text(
            json.dumps(record, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assertEqual(skills._provenance_drift(), (1, 0))
        skill_file.write_text("tampered", encoding="utf-8")
        self.assertEqual(skills._provenance_drift(), (1, 1))

    def test_missing_file_counts_as_drift(self) -> None:
        record = {"skill": "gone", "source": "SKILL.md", "sha256": "0" * 64}
        skills.PROVENANCE_PATH.write_text(
            json.dumps(record, sort_keys=True) + "\n", encoding="utf-8"
        )
        self.assertEqual(skills._provenance_drift(), (1, 1))


class RetryTests(unittest.TestCase):
    def test_process_repo_retries_after_failed_attempt(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name)
        clone = base / "clone"
        saved_clone = skills._clone_once
        saved_mkdtemp = skills.tempfile.mkdtemp
        saved_sleep = skills.time.sleep
        saved_commit = skills._repo_commit
        saved_skills_dir = skills.SKILLS_DIR
        saved_provenance = skills.PROVENANCE_PATH
        calls: list[str] = []

        def sample_dir(prefix: str = "") -> str:
            clone.mkdir(parents=True, exist_ok=True)
            (clone / "SKILL.md").write_text(
                "---\nname: retry-skill\n---\n", encoding="utf-8"
            )
            return str(clone)

        def fake_clone(repo: str, subpath: str, target: Path) -> tuple[bool, str]:
            calls.append(repo)
            return len(calls) > 1, "planted failure"

        skills._clone_once = fake_clone
        skills.tempfile.mkdtemp = sample_dir
        skills.time.sleep = lambda _seconds: None
        skills._repo_commit = lambda _dir: "deadbeef"
        skills.SKILLS_DIR = base / "skills"
        skills.PROVENANCE_PATH = base / "provenance.jsonl"
        try:
            count, fixes = skills.process_repo("acme/demo", "", "en")
        finally:
            skills._clone_once = saved_clone
            skills.tempfile.mkdtemp = saved_mkdtemp
            skills.time.sleep = saved_sleep
            skills._repo_commit = saved_commit
            skills.SKILLS_DIR = saved_skills_dir
            skills.PROVENANCE_PATH = saved_provenance
            tmp.cleanup()
        self.assertEqual(count, 1)
        self.assertEqual(len(calls), 2)
        self.assertEqual(fixes, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
