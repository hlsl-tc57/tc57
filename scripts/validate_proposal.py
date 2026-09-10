#!/usr/bin/env python3
"""Validate a proposal document and report problems as Markdown."""

import argparse
import re
from collections import defaultdict
from html import escape
from pathlib import Path, PurePosixPath

import yaml


VALID_PROPOSAL_STATUSES = {
    "Under Consideration",
    "Refinement",
    "Accepted",
    "Completed",
    "Rejected",
    "Deferred",
}
PROPOSAL_FILENAME_PATTERN = re.compile(r"^(\d{4})-")
PROPOSAL_TITLE_PATTERN = re.compile(r"^(\d{4})\b")
MARKDOWN_SPECIAL_CHARACTER_PATTERN = re.compile(r"([\\`*_{}\[\]()#+|])")


def escape_markdown(value: str) -> str:
    """Escape untrusted text for inclusion in a Markdown report."""
    value = MARKDOWN_SPECIAL_CHARACTER_PATTERN.sub(
        r"\\\1", escape(value, quote=False)
    )
    return value.replace("@", "&#64;")


def format_markdown_report(
    problems: list[tuple[str, list[str]]], title: str = "Proposal validation"
) -> str:
    """Format validation results as Markdown."""
    lines = [f"## {escape_markdown(title)}", ""]
    if not problems:
        lines.append("No problems found.")
        return "\n".join(lines)

    lines.extend(["The following problems must be fixed:", ""])
    for heading, errors in problems:
        lines.append(f"### {escape_markdown(heading)}")
        lines.extend(f"- {escape_markdown(error)}" for error in errors)
        lines.append("")
    return "\n".join(lines).rstrip()


def read_frontmatter(path: str) -> dict:
    """Parse and return a proposal's YAML frontmatter."""
    contents = Path(path).read_text(encoding="utf-8")
    lines = contents.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("frontmatter must begin with '---'")

    try:
        closing_delimiter = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("frontmatter must end with '---'") from error

    frontmatter = yaml.safe_load("\n".join(lines[1:closing_delimiter]))
    if not isinstance(frontmatter, dict):
        raise ValueError("frontmatter must be a YAML mapping")
    return frontmatter


def find_duplicate_proposal_numbers(proposal_directory: Path) -> dict[str, list[str]]:
    """Return proposal numbers used by more than one proposal filename."""
    paths_by_number = defaultdict(list)
    for path in proposal_directory.glob("*.md"):
        match = PROPOSAL_FILENAME_PATTERN.match(path.name)
        if match:
            paths_by_number[match.group(1)].append(path.as_posix())
    return {
        number: paths
        for number, paths in paths_by_number.items()
        if len(paths) > 1
    }


def validate_proposal(path: str, required_author: str | None = None) -> list[str]:
    """Return validation errors for a proposal document."""
    errors = []
    proposal_path = PurePosixPath(path)
    filename_match = PROPOSAL_FILENAME_PATTERN.match(proposal_path.name)
    filename_number = filename_match.group(1) if filename_match else None
    if filename_number is None:
        errors.append("filename must start with a four-digit proposal number followed by '-'")

    try:
        frontmatter = read_frontmatter(path)
    except (OSError, ValueError, yaml.YAMLError) as error:
        errors.append(f"invalid frontmatter: {error}")
    else:
        title = frontmatter.get("title")
        title_match = PROPOSAL_TITLE_PATTERN.match(title) if isinstance(title, str) else None
        if title_match is None:
            errors.append("title must start with a four-digit proposal number")
        elif filename_number is not None and title_match.group(1) != filename_number:
            errors.append(
                f"title proposal number {title_match.group(1)} does not match "
                f"filename proposal number {filename_number}"
            )

        slug = frontmatter.get("slug")
        if not isinstance(slug, str) or re.fullmatch(r"\d{4}", slug) is None:
            errors.append("slug must be a four-digit proposal number")
        elif filename_number is not None and slug != filename_number:
            errors.append(
                f"slug proposal number {slug} does not match "
                f"filename proposal number {filename_number}"
            )

        if frontmatter.get("draft") is True:
            errors.append("must not contain 'draft: true'")

        params = frontmatter.get("params")
        if not isinstance(params, dict):
            errors.append("params must be a mapping")
        else:
            authors = params.get("authors")
            if not isinstance(authors, list) or not authors or not all(
                isinstance(author, dict) for author in authors
            ):
                errors.append("authors must be a non-empty list of mappings")
            elif required_author is not None and not any(
                required_author in author for author in authors
            ):
                errors.append(
                    "authors must contain the PR author's GitHub username "
                    f"'{required_author}'"
                )

            status = params.get("status")
            if status not in VALID_PROPOSAL_STATUSES:
                valid_statuses = ", ".join(sorted(VALID_PROPOSAL_STATUSES))
                errors.append(f"status must be one of: {valid_statuses}")

    if filename_number is not None:
        duplicate_numbers = find_duplicate_proposal_numbers(Path(path).parent)
        if filename_number in duplicate_numbers:
            duplicates = ", ".join(duplicate_numbers[filename_number])
            errors.append(f"proposal number {filename_number} is not unique: {duplicates}")

    return errors


def validate_path(
    path: str, required_author: str | None = None
) -> list[tuple[str, list[str]]]:
    """Return Markdown report entries for a proposal file or directory."""
    input_path = Path(path)
    proposal_paths = (
        sorted(input_path.glob("*.md")) if input_path.is_dir() else [input_path]
    )
    problems = []
    for proposal_path in proposal_paths:
        proposal_path_string = proposal_path.as_posix()
        errors = validate_proposal(proposal_path_string, required_author)
        if errors:
            problems.append((f"Proposal: {proposal_path_string}", errors))
    return problems


def main() -> int:
    """Validate a proposal path provided on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="path to a proposal Markdown file or directory")
    parser.add_argument(
        "--author",
        help="require this GitHub username to be listed as a proposal author",
    )
    arguments = parser.parse_args()

    problems = validate_path(arguments.path, arguments.author)
    print(format_markdown_report(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
