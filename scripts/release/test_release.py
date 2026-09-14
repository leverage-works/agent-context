# /// script
# requires-python = ">=3.11"
# dependencies = ["PyYAML==6.0.3"]
# ///
"""Release behaviour tests: isolated Git repositories and fake GitHub calls."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import release

ROOT = Path(__file__).resolve().parents[2]


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.previous = Path.cwd()
        os.chdir(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(os.chdir, self.previous)
        for args in (("init", "-q"), ("config", "user.name", "Test"),
                     ("config", "user.email", "test@example.invalid")):
            release.git(*args)
        for name in ("apm.yml", "packages/org-meta-bundle/apm.yml", ".claude-plugin/marketplace.json"):
            path = Path(name)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text((ROOT / name).read_text())
        release.sync("0.2.0")
        self.commit("chore: baseline")
        release.git("tag", "v0.2.0")

    def commit(self, subject, body=""):
        Path("change.txt").write_text(subject + body)
        release.git("add", ".")
        release.git("commit", "-q", "--allow-empty", "-m", subject, "-m", body)
        return release.git("rev-parse", "HEAD")

    def prepared(self):
        self.commit("feat: add a skill", "Consumers can now plan a release.\n\nRefs #123")
        release.prepare("0.3.0")
        sha = self.commit("chore(release): v0.3.0", "Synchronize release metadata.")
        Path("notes.md").write_text(release.plan()["notes"])
        return sha

    def test_highest_bump_and_bodyless_commit(self):
        self.commit("fix: correct guidance")
        self.assertEqual(release.plan()["version"], "0.2.1")
        self.commit("perf: accelerate script")
        self.commit("feat: introduce workflow")
        self.assertEqual(release.plan()["version"], "0.3.0")
        self.commit("fix!: remove old interface", "BREAKING CHANGE: use the replacement.")
        self.assertEqual(release.plan()["version"], "1.0.0")

    def test_breaking_footer_and_docs_only(self):
        self.commit("docs: explain a command")
        self.assertEqual(release.plan(), {})
        self.commit("refactor: replace interface", "BREAKING-CHANGE: migrate consumers.")
        self.assertEqual(release.plan()["version"], "1.0.0")

    def test_development_metadata_can_retain_published_index(self):
        old_index = release.INDEX.read_text()
        release.sync("0.2.1")
        release.INDEX.write_text(old_index)
        release.check()
        with self.assertRaises(ValueError):
            release.check(release_ready=True)

    def test_unreachable_tags_are_ignored(self):
        head = release.git("rev-parse", "HEAD")
        release.git("checkout", "-q", "-b", "other")
        self.commit("feat: unrelated")
        release.git("tag", "v99.0.0")
        release.git("checkout", "-q", "--detach", head)
        self.commit("fix: current branch")
        self.assertEqual(release.plan()["version"], "0.2.1")

    def test_pending_metadata_commit_resumes_before_new_work(self):
        sha = self.prepared()
        self.commit("feat: later work")
        result = release.plan()
        self.assertFalse(result["prepare"])
        self.assertEqual(result["commit"], sha)
        self.assertIn("Refs #123", result["notes"])
        self.assertNotIn("later work", result["notes"])
        release.check()
        self.assertEqual(json.loads(release.INDEX.read_text())["plugins"][0]["source"]["ref"], "v0.3.0")

    def test_rejects_wrong_preparation_version_and_metadata_drift(self):
        self.commit("fix: correct guidance")
        with self.assertRaises(ValueError):
            release.prepare("9.0.0")
        release.INDEX.write_text('{}')
        with self.assertRaises((ValueError, KeyError)):
            release.check()

    def test_tagged_release_recovery_with_newer_commits(self):
        sha = self.prepared()
        release.git("tag", "v0.3.0")
        self.commit("feat: newer work")
        with patch.object(release, "gh", return_value='[[]]'):
            result = release.plan("org/repo")
        self.assertEqual(result["commit"], sha)
        self.assertFalse(result["prepare"])
        with patch.object(release, "gh", return_value='[[{"tag_name":"v0.3.0","draft":false}]]'):
            self.assertEqual(release.plan("org/repo")["version"], "0.4.0")

    def test_completed_metadata_commit_does_not_release_again(self):
        self.prepared()
        release.git("tag", "v0.3.0")
        with patch.object(release, "gh", return_value='[[{"tag_name":"v0.3.0","draft":false}]]'):
            self.assertEqual(release.plan("org/repo"), {})

    def publish_with(self, refs, pages, actual=None):
        sha = release.git("rev-parse", "HEAD")
        def fake(*args):
            if "matching-refs" in " ".join(args):
                return json.dumps(refs)
            if f"repos/org/repo/commits/v0.3.0" in args:
                return json.dumps({"sha": actual or sha})
            if "--paginate" in args:
                return json.dumps(pages)
            return "{}"
        with patch.object(release, "gh", side_effect=fake) as calls:
            release.publish("org/repo", "0.3.0", sha, Path("notes.md"))
            return calls.call_args_list

    def test_new_release_is_draft_before_publication(self):
        self.prepared()
        calls = self.publish_with([], [[]])
        creation = next(i for i, c in enumerate(calls) if c.args[:2] == ("release", "create"))
        publication = next(i for i, c in enumerate(calls) if c.args[:2] == ("release", "edit"))
        self.assertLess(creation, publication)
        self.assertIn("--draft", calls[creation].args)

    def test_resume_draft_without_recreating_tag(self):
        self.prepared()
        calls = self.publish_with([{"ref": "refs/tags/v0.3.0"}], [[{"tag_name": "v0.3.0", "draft": True}]])
        self.assertFalse(any("POST" in c.args or "create" in c.args for c in calls))
        self.assertTrue(any("--draft=false" in c.args for c in calls))

    def test_completed_release_is_immutable(self):
        self.prepared()
        calls = self.publish_with([{"ref": "refs/tags/v0.3.0"}], [[{"tag_name": "v0.3.0", "draft": False}]])
        self.assertFalse(any(c.args[0] == "release" or "POST" in c.args for c in calls))

    def test_conflicting_tag_fails_without_publishing(self):
        self.prepared()
        with self.assertRaisesRegex(ValueError, "refusing to move"):
            self.publish_with([{"ref": "refs/tags/v0.3.0"}], [[]], actual="a" * 40)

    def test_network_failure_does_not_create_release(self):
        sha = self.prepared()
        with patch.object(release, "gh", side_effect=subprocess.CalledProcessError(1, "gh")) as calls:
            with self.assertRaises(subprocess.CalledProcessError):
                release.publish("org/repo", "0.3.0", sha, Path("notes.md"))
        self.assertEqual(calls.call_count, 1)


if __name__ == "__main__":
    unittest.main()
