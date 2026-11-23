#!/usr/bin/env python3
"""Runtime-built unit tests for installer path safety and provenance.

No fixture files are committed: every sample is assembled in a throwaway
temporary directory at run time, so an integrity scan cannot read its own
fixtures. stdlib only.
"""

from __future__ import annotations

import json
import os
import subprocess
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

    def test_junction_parent_rejected(self) -> None:
        if os.name != "nt":
            self.skipTest("junctions are Windows-only")
        real = self.base / "elsewhere"
        real.mkdir()
        (real / "SKILL.md").write_text("---\nname: x\n---\n", encoding="utf-8")
        junction = self.root / "linked"
        result = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(junction), str(real)],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            self.skipTest(f"junction creation unavailable: {result.stderr.strip()}")
        candidate = junction / "SKILL.md"
        self.assertIsNotNone(skills._source_verdict(candidate, self.root, self.root))
        self.assertTrue(skills._is_link_or_junction(junction))

    def test_quarantine_chain_link_rejected(self) -> None:
        qdir = self.root / "_quarantine_temel_2026-01-01"
        saved = skills._is_link_or_junction
        skills._is_link_or_junction = lambda path: path == qdir
        try:
            self.assertIsNotNone(
                skills._quarantine_verdict(qdir, self.root, qdir / "demo")
            )
        finally:
            skills._is_link_or_junction = saved

    def test_quarantine_entry_link_rejected(self) -> None:
        qdir = self.root / "quarantine"
        qdir.mkdir()
        dst = qdir / "demo"
        victim = self.base / "victim.txt"
        victim.write_text("do not overwrite", encoding="utf-8")
        try:
            dst.symlink_to(victim)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertIsNotNone(skills._quarantine_verdict(qdir, self.root, dst))

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


class TreeTests(unittest.TestCase):
    def test_linked_directory_is_not_traversed(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        base = Path(tmp.name)
        agents = base / "agents"
        agents.mkdir()
        normal = agents / "normal"
        normal.mkdir()
        (normal / "child.txt").write_text("ok", encoding="utf-8")
        linked = agents / "linked"
        linked.mkdir()
        (linked / "secret.txt").write_text("outside", encoding="utf-8")
        saved_agents = skills.AGENTS_DIR
        saved_tree = skills.TREE_DIR
        saved_link_check = skills._is_link_or_junction
        original = saved_link_check
        skills.AGENTS_DIR = agents
        skills.TREE_DIR = base / "logs"
        skills._is_link_or_junction = lambda path: original(path) or path == linked
        try:
            result = skills.save_tree("en")
            text = Path(result).read_text(encoding="utf-8") if result else ""
        finally:
            skills.AGENTS_DIR = saved_agents
            skills.TREE_DIR = saved_tree
            skills._is_link_or_junction = saved_link_check
            tmp.cleanup()
        self.assertIsNotNone(result)
        self.assertIn("linked", text)
        self.assertIn("[link", text)
        self.assertNotIn("secret.txt", text)
        self.assertIn("child.txt", text)

    def test_linked_root_is_skipped(self) -> None:
        saved_link_check = skills._is_link_or_junction
        skills._is_link_or_junction = lambda _path: True
        try:
            self.assertIsNone(skills.save_tree("en"))
        finally:
            skills._is_link_or_junction = saved_link_check


class RewriteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.clone = self.base / "clone"
        self.saved = {
            "clone_once": skills._clone_once,
            "mkdtemp": skills.tempfile.mkdtemp,
            "sleep": skills.time.sleep,
            "commit": skills._repo_commit,
            "skills_dir": skills.SKILLS_DIR,
            "provenance": skills._record_provenance,
        }
        self.entries: list[dict] = []
        self.sample = b"---\nname: Bad Name\ndesc: x\n---\n"

        def sample_dir(prefix: str = "") -> str:
            self.clone.mkdir(parents=True, exist_ok=True)
            (self.clone / "SKILL.md").write_bytes(self.sample)
            return str(self.clone)

        skills._clone_once = lambda repo, subpath, target: (True, "")
        skills.tempfile.mkdtemp = sample_dir
        skills.time.sleep = lambda _seconds: None
        skills._repo_commit = lambda _dir: "deadbeef"
        skills.SKILLS_DIR = self.base / "skills"
        skills._record_provenance = self.entries.append

    def tearDown(self) -> None:
        skills._clone_once = self.saved["clone_once"]
        skills.tempfile.mkdtemp = self.saved["mkdtemp"]
        skills.time.sleep = self.saved["sleep"]
        skills._repo_commit = self.saved["commit"]
        skills.SKILLS_DIR = self.saved["skills_dir"]
        skills._record_provenance = self.saved["provenance"]
        self.tmp.cleanup()

    def test_recorded_digest_matches_installed_file(self) -> None:
        count, fixes = skills.process_repo("acme/demo", "", "en")
        self.assertEqual((count, fixes), (1, 1))
        self.assertEqual(len(self.entries), 1)
        installed = skills.SKILLS_DIR / "bad-name" / "SKILL.md"
        self.assertEqual(
            self.entries[0]["sha256"],
            skills.hashlib.sha256(installed.read_bytes()).hexdigest(),
        )

    def test_invalid_utf8_does_not_crash_install(self) -> None:
        self.sample = b"---\nname: Bad Name\ndesc: \xff\xfe\n---\n"
        count, _fixes = skills.process_repo("acme/demo", "", "en")
        self.assertEqual(count, 1)


class CollisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp.name)
        self.clone = self.base / "clone"
        self.samples: list[bytes] = []
        self.calls: list[str] = []
        self.saved = {
            "clone_once": skills._clone_once,
            "mkdtemp": skills.tempfile.mkdtemp,
            "sleep": skills.time.sleep,
            "commit": skills._repo_commit,
            "trust": skills._repo_trust,
            "skills_dir": skills.SKILLS_DIR,
            "provenance": skills._record_provenance,
        }
        skills.SKILLS_DIR = self.base / "skills"
        self.entries: list[dict] = []
        skills._record_provenance = self.entries.append
        skills._repo_commit = lambda _dir: "deadbeef"
        skills.time.sleep = lambda _seconds: None
        skills._repo_trust = lambda repo: (
            "curated" if repo == "acme/trusted" else "risk"
        )

        def sample_dir(prefix: str = "") -> str:
            self.clone.mkdir(parents=True, exist_ok=True)
            index = min(len(self.calls), len(self.samples) - 1)
            (self.clone / "SKILL.md").write_bytes(self.samples[index])
            return str(self.clone)

        def fake_clone(repo: str, subpath: str, target: Path) -> tuple[bool, str]:
            self.calls.append(repo)
            return True, ""

        skills.tempfile.mkdtemp = sample_dir
        skills._clone_once = fake_clone

    def tearDown(self) -> None:
        skills._clone_once = self.saved["clone_once"]
        skills.tempfile.mkdtemp = self.saved["mkdtemp"]
        skills.time.sleep = self.saved["sleep"]
        skills._repo_commit = self.saved["commit"]
        skills._repo_trust = self.saved["trust"]
        skills.SKILLS_DIR = self.saved["skills_dir"]
        skills._record_provenance = self.saved["provenance"]
        self.tmp.cleanup()

    def run_repos(
        self, samples: list[bytes],
        repos: tuple[str, ...] = ("acme/trusted", "acme/risk"),
    ) -> dict:
        self.samples = samples
        claims: dict = {}
        for repo in repos:
            skills.process_repo(repo, "", "en", claims)
        return claims

    def test_lower_trust_copy_is_namespaced(self) -> None:
        claims = self.run_repos([
            b"---\nname: demo\n---\nA\n",
            b"---\nname: demo\n---\nB\n",
        ])
        canonical = (skills.SKILLS_DIR / "demo" / "SKILL.md").read_text(encoding="utf-8")
        other = (skills.SKILLS_DIR / "demo--acme-risk" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("\nA\n", canonical)
        self.assertIn("\nB\n", other)
        self.assertIn("name: demo--acme-risk", other)
        self.assertIn("demo", claims)
        self.assertIn("demo--acme-risk", claims)

    def test_higher_trust_copy_takes_canonical_name(self) -> None:
        claims = self.run_repos(
            [
                b"---\nname: demo\n---\nB\n",
                b"---\nname: demo\n---\nA\n",
            ],
            repos=("acme/risk", "acme/trusted"),
        )
        canonical = (skills.SKILLS_DIR / "demo" / "SKILL.md").read_text(encoding="utf-8")
        moved_bytes = (skills.SKILLS_DIR / "demo--acme-risk" / "SKILL.md").read_bytes()
        moved = moved_bytes.decode("utf-8")
        self.assertIn("\nA\n", canonical)
        self.assertIn("\nB\n", moved)
        self.assertIn("name: demo--acme-risk", moved)
        self.assertEqual(claims["demo"]["repo"], "acme/trusted")
        moved_records = [
            record for record in self.entries
            if record.get("skill") == "demo--acme-risk"
        ]
        self.assertTrue(moved_records)
        record = moved_records[-1]
        self.assertEqual(record.get("moved_from"), "demo")
        self.assertEqual(
            record.get("sha256"),
            skills.hashlib.sha256(moved_bytes).hexdigest(),
        )

    def test_identical_copy_is_deduplicated(self) -> None:
        self.run_repos([
            b"---\nname: demo\n---\nsame\n",
            b"---\nname: demo\n---\nsame\n",
        ])
        folders = sorted(p.name for p in skills.SKILLS_DIR.iterdir() if p.is_dir())
        self.assertEqual(folders, ["demo"])


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
