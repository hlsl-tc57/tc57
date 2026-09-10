#!/usr/bin/env python3
"""Check a pull request for common mistakes."""

import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath

if __package__:
    from .validate_proposal import format_markdown_report, validate_proposal
else:
    from validate_proposal import format_markdown_report, validate_proposal


def publish_report(
    problems: list[tuple[str, list[str]]], exit_code: int, report_path: str | None
) -> int:
    """Print a Markdown report and optionally save it to a file."""
    report = format_markdown_report(problems, "Pull request checks")
    print(report)
    if report_path is not None:
        try:
            output = Path(report_path)
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(f"{report}\n", encoding="utf-8")
        except OSError as error:
            print(f"error: unable to write Markdown report: {error}", file=sys.stderr)
            return 2
    return exit_code


def is_placeholder_proposal_path(path: str) -> bool:
    """Return whether a path contains an NNNN-prefixed part under proposals."""
    parts = PurePosixPath(path).parts
    return len(parts) > 1 and parts[0] == "proposals" and any(
        part.startswith("NNNN") for part in parts[1:]
    )


def get_pull_request_metadata(event_path: str) -> tuple[str, str, str]:
    """Read the base SHA, head SHA, and author from a GitHub event payload."""
    with open(event_path, encoding="utf-8") as event_file:
        event = json.load(event_file)

    pull_request = event["pull_request"]
    return (
        pull_request["base"]["sha"],
        pull_request["head"]["sha"],
        pull_request["user"]["login"],
    )


def get_added_paths(base_sha: str, head_sha: str) -> list[str]:
    """Return paths added between the pull request merge base and head."""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "-z",
            "--diff-filter=A",
            "--no-renames",
            f"{base_sha}...{head_sha}",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [path for path in result.stdout.split("\0") if path]


def get_changed_proposal_paths(base_sha: str, head_sha: str) -> list[str]:
    """Return added or modified proposal documents in a pull request."""
    result = subprocess.run(
        [
            "git",
            "diff",
            "--name-only",
            "-z",
            "--diff-filter=AM",
            "--no-renames",
            f"{base_sha}...{head_sha}",
            "--",
            "proposals/*.md",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return [
        path
        for path in result.stdout.split("\0")
        if path
        and PurePosixPath(path).parent == PurePosixPath("proposals")
        and PurePosixPath(path).suffix == ".md"
    ]


def main() -> int:
    """Run pull request checks."""
    report_path = os.environ.get("CHECK_PR_REPORT_PATH")
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if event_path is None:
        return publish_report(
            [("Checker error", ["GITHUB_EVENT_PATH is not set."])], 2, report_path
        )

    try:
        base_sha, head_sha, pr_author = get_pull_request_metadata(event_path)
        added_paths = get_added_paths(base_sha, head_sha)
        changed_proposals = get_changed_proposal_paths(base_sha, head_sha)
    except (OSError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as error:
        return publish_report(
            [("Checker error", [f"Unable to inspect pull request: {error}"])],
            2,
            report_path,
        )

    problems = []
    placeholder_paths = [path for path in added_paths if is_placeholder_proposal_path(path)]
    if placeholder_paths:
        problems.append(
            (
                "Placeholder proposal paths",
                [
                    f"{path} uses the placeholder proposal number NNNN. "
                    "A proposal number must be assigned by the committee, not the author."
                    for path in placeholder_paths
                ],
            )
        )

    added_path_set = set(added_paths)
    for path in changed_proposals:
        required_author = pr_author if path in added_path_set else None
        errors = validate_proposal(path, required_author)
        if errors:
            problems.append((f"Proposal: {path}", errors))

    return publish_report(problems, 1 if problems else 0, report_path)


if __name__ == "__main__":
    raise SystemExit(main())
