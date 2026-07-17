"""Tests for the GitHub issue discovery helper."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "packages/org-meta-bundle/.apm/skills/work-on-gh-issues/scripts/list_issues.py"
)
SPEC = importlib.util.spec_from_file_location("list_issues", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
list_issues = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(list_issues)


class RenovateDependencyDashboardTests(unittest.TestCase):
    def test_identifies_renovate_dependency_dashboard_label(self) -> None:
        issue = {"labels": [{"name": "renovate-dependency-dashboard"}]}

        self.assertTrue(list_issues.has_renovate_dependency_dashboard_label(issue))

    def test_keeps_issue_without_renovate_dependency_dashboard_label(self) -> None:
        issue = {"labels": [{"name": "dependencies"}]}

        self.assertFalse(list_issues.has_renovate_dependency_dashboard_label(issue))

    def test_list_results_exclude_only_renovates_dashboard(self) -> None:
        response = [
            {"number": 1, "labels": [{"name": "renovate-dependency-dashboard"}]},
            {"number": 2, "labels": [{"name": "dependencies"}]},
            {"number": 3, "labels": []},
        ]

        with patch.object(list_issues, "run_command", return_value=json.dumps(response)):
            issues = list_issues.fetch_issues("owner/repository", None, "open", 30)

        self.assertEqual([issue["number"] for issue in issues], [2, 3])
