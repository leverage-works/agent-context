#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""List GitHub issues for the repository containing the current checkout."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


ISSUE_FIELDS = "number,title,author,createdAt,labels,url"
GITHUB_REMOTE = re.compile(
    r"(?:github\.com[:/])(?P<owner>[^/\s]+)/(?P<repository>[^/\s]+?)(?:\.git)?/?$"
)


def positive_issue_number(value: str) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("issue number must be an integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("issue number must be positive")
    return number


def run_command(command: list[str]) -> str:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        raise RuntimeError(f"{' '.join(command[:3])} failed: {detail}")
    return completed.stdout


def current_repository() -> str:
    remote = run_command(["git", "config", "--get", "remote.origin.url"]).strip()
    matched = GITHUB_REMOTE.search(remote)
    if not matched:
        raise RuntimeError(
            "The current checkout's origin remote is not a GitHub repository. "
            "Set origin to a GitHub owner/repository before listing issues."
        )
    return f"{matched.group('owner')}/{matched.group('repository')}"


def fetch_issues(repository: str, issue_number: int | None, state: str, limit: int) -> list[dict[str, Any]]:
    if issue_number is not None:
        output = run_command(
            [
                "gh",
                "issue",
                "view",
                str(issue_number),
                "--repo",
                repository,
                "--json",
                ISSUE_FIELDS,
            ]
        )
        return [json.loads(output)]

    output = run_command(
        [
            "gh",
            "issue",
            "list",
            "--repo",
            repository,
            "--state",
            state,
            "--limit",
            str(limit),
            "--json",
            ISSUE_FIELDS,
        ]
    )
    result = json.loads(output)
    if not isinstance(result, list):
        raise RuntimeError("GitHub returned an unexpected issue-list response")
    return result


def one_line(value: object) -> str:
    return " ".join(str(value or "").split())


def shorten(value: str, width: int) -> str:
    value = one_line(value)
    return value if len(value) <= width else f"{value[: width - 1]}…"


def opened_date(value: object) -> str:
    timestamp = one_line(value)
    try:
        return datetime.fromisoformat(timestamp.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return timestamp or "—"


def labels(issue: dict[str, Any]) -> str:
    values = issue.get("labels", [])
    if not isinstance(values, list):
        return "—"
    names = [one_line(label.get("name")) for label in values if isinstance(label, dict)]
    return ", ".join(name for name in names if name) or "—"


def render_table(issues: list[dict[str, Any]]) -> str:
    headers = ("#", "Title", "Author", "Opened", "Labels", "URL")
    rows: list[tuple[str, ...]] = []
    for issue in issues:
        author = issue.get("author")
        author_name = author.get("login") if isinstance(author, dict) else "—"
        rows.append(
            (
                str(issue.get("number", "—")),
                shorten(one_line(issue.get("title")), 56),
                shorten(one_line(author_name), 18),
                opened_date(issue.get("createdAt")),
                shorten(labels(issue), 28),
                one_line(issue.get("url")),
            )
        )

    widths = [len(header) for header in headers]
    for row in rows:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]

    def border(left: str, middle: str, right: str, fill: str = "─") -> str:
        return left + middle.join(fill * (width + 2) for width in widths) + right

    def line(row: tuple[str, ...]) -> str:
        return "│" + "│".join(f" {cell.ljust(width)} " for cell, width in zip(row, widths)) + "│"

    return "\n".join(
        [
            border("┌", "┬", "┐"),
            line(headers),
            border("├", "┼", "┤"),
            *(line(row) for row in rows),
            border("└", "┴", "┘"),
        ]
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="List GitHub issues raised against the current repository."
    )
    parser.add_argument("issue", nargs="?", type=positive_issue_number, help="exact issue number")
    parser.add_argument("-i", "--issue", dest="issue_option", type=positive_issue_number, help="exact issue number")
    parser.add_argument("--state", choices=("open", "closed", "all"), default="open")
    parser.add_argument("--limit", type=positive_issue_number, default=30)
    arguments = parser.parse_args()
    if arguments.issue is not None and arguments.issue_option is not None:
        parser.error("provide an issue number either positionally or with --issue, not both")
    arguments.issue = arguments.issue if arguments.issue is not None else arguments.issue_option
    return arguments


def main() -> int:
    arguments = parse_arguments()
    try:
        repository = current_repository()
        issues = fetch_issues(repository, arguments.issue, arguments.state, arguments.limit)
    except (RuntimeError, json.JSONDecodeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    if not issues:
        print(f"No {arguments.state} issues found for {repository}.")
        return 0

    print(f"GitHub issues for {repository}")
    print(render_table(issues))
    return 0



if __name__ == "__main__":
    raise SystemExit(main())
