#!/usr/bin/env python3
"""Tests for pull request checks."""

import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

from scripts import check_pr, validate_proposal


class CheckPullRequestTests(unittest.TestCase):
    EVENT = json.dumps(
        {
            "pull_request": {
                "base": {"sha": "base-sha"},
                "head": {"sha": "head-sha"},
                "user": {"login": "octocat"},
            }
        }
    )

    def run_check(
        self, added_paths: list[str], changed_proposals: list[str] | None = None
    ) -> tuple[int, str, str]:
        with (
            mock.patch.dict(os.environ, {"GITHUB_EVENT_PATH": "event.json"}),
            mock.patch("builtins.open", mock.mock_open(read_data=self.EVENT)),
            mock.patch("scripts.check_pr.get_added_paths", return_value=added_paths),
            mock.patch(
                "scripts.check_pr.get_changed_proposal_paths",
                return_value=changed_proposals or [],
            ),
            redirect_stdout(stdout := io.StringIO()),
            redirect_stderr(stderr := io.StringIO()),
        ):
            result = check_pr.main()

        return result, stdout.getvalue(), stderr.getvalue()

    def test_accepts_valid_added_paths(self) -> None:
        result, stdout, stderr = self.run_check(
            ["proposals/0020-feature.md", "docs/NNNN-notes.md"]
        )

        self.assertEqual(result, 0)
        self.assertEqual(stdout, "## Pull request checks\n\nNo problems found.\n")
        self.assertEqual(stderr, "")

    def test_rejects_placeholder_file_and_directory(self) -> None:
        result, stdout, stderr = self.run_check(
            ["proposals/NNNN-feature.md", "proposals/NNNN-assets/image.png"]
        )

        self.assertEqual(result, 1)
        self.assertIn("### Placeholder proposal paths", stdout)
        self.assertIn("proposals/NNNN-feature.md", stdout)
        self.assertIn("proposals/NNNN-assets/image.png", stdout)
        self.assertIn(
            "A proposal number must be assigned by the committee, not the author.",
            stdout,
        )
        self.assertEqual(stderr, "")

    def test_writes_markdown_report_to_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            report_path = Path(directory, "report.md")
            with mock.patch.dict(
                os.environ, {"CHECK_PR_REPORT_PATH": report_path.as_posix()}
            ):
                result, stdout, stderr = self.run_check([])

            report = report_path.read_text(encoding="utf-8")

        self.assertEqual(result, 0)
        self.assertEqual(report, stdout)
        self.assertEqual(stderr, "")

    def test_escapes_untrusted_markdown_in_report(self) -> None:
        report = validate_proposal.format_markdown_report(
            [("Proposal: [bad](url)", ["Notify @reviewers about author's change."])]
        )

        self.assertIn(r"Proposal: \[bad\]\(url\)", report)
        self.assertIn("Notify &#64;reviewers about author's change.", report)

    def test_requires_pr_author_only_for_added_proposals(self) -> None:
        path = "proposals/0020-feature.md"
        with mock.patch("scripts.check_pr.validate_proposal", return_value=[]) as validate:
            self.run_check([path], [path])
            validate.assert_called_once_with(path, "octocat")

        with mock.patch("scripts.check_pr.validate_proposal", return_value=[]) as validate:
            self.run_check([], [path])
            validate.assert_called_once_with(path, None)


class ProposalValidationTests(unittest.TestCase):
    def validate(
        self,
        frontmatter: str,
        filename: str = "0020-feature.md",
        required_author: str | None = "octocat",
    ) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, filename)
            path.write_text(f"---\n{frontmatter}\n---\n\nProposal body.\n", encoding="utf-8")
            return validate_proposal.validate_proposal(path.as_posix(), required_author)

    def valid_frontmatter(self, status: str = "Under Consideration") -> str:
        return f"""title: 0020 - Feature
slug: "0020"
params:
  authors:
    - octocat: Octo Cat
  status: {status}"""

    def test_accepts_each_valid_status(self) -> None:
        for status in validate_proposal.VALID_PROPOSAL_STATUSES:
            with self.subTest(status=status):
                self.assertEqual(self.validate(self.valid_frontmatter(status)), [])

    def test_accepts_valid_proposal_without_required_author(self) -> None:
        frontmatter = self.valid_frontmatter().replace("octocat", "another-author")

        self.assertEqual(self.validate(frontmatter, required_author=None), [])

    def test_requires_numbered_title_matching_filename(self) -> None:
        missing_title = self.valid_frontmatter().replace("title: 0020 - Feature\n", "")
        mismatched_title = self.valid_frontmatter().replace("0020 - Feature", "0021 - Feature")

        self.assertIn(
            "title must start with a four-digit proposal number",
            self.validate(missing_title),
        )
        self.assertIn(
            "title proposal number 0021 does not match filename proposal number 0020",
            self.validate(mismatched_title),
        )

    def test_requires_slug_matching_filename(self) -> None:
        missing_slug = self.valid_frontmatter().replace('slug: "0020"\n', "")
        mismatched_slug = self.valid_frontmatter().replace('slug: "0020"', 'slug: "0021"')

        self.assertIn(
            "slug must be a four-digit proposal number",
            self.validate(missing_slug),
        )
        self.assertIn(
            "slug proposal number 0021 does not match filename proposal number 0020",
            self.validate(mismatched_slug),
        )

    def test_rejects_draft_true(self) -> None:
        frontmatter = f"draft: true\n{self.valid_frontmatter()}"

        self.assertIn("must not contain 'draft: true'", self.validate(frontmatter))

    def test_requires_pr_author(self) -> None:
        frontmatter = self.valid_frontmatter().replace("octocat", "other-author")

        self.assertIn(
            "authors must contain the PR author's GitHub username 'octocat'",
            self.validate(frontmatter),
        )

    def test_rejects_invalid_status(self) -> None:
        errors = self.validate(self.valid_frontmatter("Draft"))

        self.assertTrue(any(error.startswith("status must be one of:") for error in errors))

    def test_finds_duplicate_proposal_numbers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            proposals = Path(directory)
            Path(proposals, "0020-first.md").touch()
            Path(proposals, "0020-second.md").touch()
            Path(proposals, "0021-unique.md").touch()

            duplicates = validate_proposal.find_duplicate_proposal_numbers(proposals)

        self.assertEqual(set(duplicates), {"0020"})
        self.assertEqual(len(duplicates["0020"]), 2)

    def test_cli_outputs_markdown_report(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "0020-feature.md")
            path.write_text(
                f"---\n{self.valid_frontmatter()}\n---\n\nProposal body.\n",
                encoding="utf-8",
            )
            with (
                mock.patch("sys.argv", ["validate_proposal.py", path.as_posix()]),
                redirect_stdout(stdout := io.StringIO()),
            ):
                result = validate_proposal.main()

        self.assertEqual(result, 0)
        self.assertEqual(stdout.getvalue(), "## Proposal validation\n\nNo problems found.\n")

    def test_cli_validates_proposal_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            proposals = Path(directory)
            Path(proposals, "0020-valid.md").write_text(
                f"---\n{self.valid_frontmatter()}\n---\n",
                encoding="utf-8",
            )
            Path(proposals, "0021-invalid.md").write_text(
                f"---\ndraft: true\n{self.valid_frontmatter().replace('0020', '0021')}\n---\n",
                encoding="utf-8",
            )
            with (
                mock.patch("sys.argv", ["validate_proposal.py", proposals.as_posix()]),
                redirect_stdout(stdout := io.StringIO()),
            ):
                result = validate_proposal.main()

        self.assertEqual(result, 1)
        heading = validate_proposal.escape_markdown(
            "Proposal: " + Path(directory, "0021-invalid.md").as_posix()
        )
        self.assertIn(f"### {heading}", stdout.getvalue())
        self.assertIn("must not contain 'draft: true'", stdout.getvalue())
        self.assertNotIn("0020-valid.md", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
