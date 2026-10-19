"""Exercise the SDK admission boundary without credentials or network access."""

from __future__ import annotations

import copy
import time
import unittest

from sdk_admission import CONSUMERS, app, validate
from typer.testing import CliRunner


class AdmissionTests(unittest.TestCase):
    """Keep source review and trusted workflow authorization independent."""

    def setUp(self) -> None:
        """Create synthetic identities without external API or credential access."""
        self.env = {
            "GITHUB_REPOSITORY": "pokerlost/authService",
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_ACTOR": "serrja",
            "GITHUB_TRIGGERING_ACTOR": "serrja",
            "GITHUB_REF": "refs/heads/main",
            "GITHUB_SHA": "a" * 40,
            "REVIEWED_SHA": "b" * 40,
            "ADMITTED_WORKFLOW_SHA": "a" * 40,
            "ADMITTED_SHA": "b" * 40,
        }
        self.reviewed_at = int(time.time())
        self.env["OWNER_WRITER_REVIEW"] = self.owner_review()
        self.repository = {
            "full_name": "pokerlost/authService",
            "private": True,
            "default_branch": "main",
        }
        self.default = {"sha": "a" * 40}
        self.pull = {
            "state": "open",
            "head": {
                "sha": "b" * 40,
                "repo": {"full_name": "pokerlost/authService"},
            },
        }
        self.source = {"sha": "b" * 40}
        self.comparison = {"status": "diverged", "merge_base_commit": {"sha": "c" * 40}}
        self.writers = [
            {"login": "serrja", "role_name": "admin", "permissions": {"push": True}},
        ]

    def owner_review(self, reviewed_at: int | None = None) -> str:
        """Bind a synthetic owner audit to the fixture repository and both commits."""
        return "|".join(
            [
                self.env["GITHUB_REPOSITORY"],
                "serrja",
                self.env["REVIEWED_SHA"],
                self.env["GITHUB_SHA"],
                str(self.reviewed_at if reviewed_at is None else reviewed_at),
            ]
        )

    def admit(self) -> None:
        """Evaluate the current synthetic admission fixture."""
        validate(
            self.env,
            self.repository,
            self.default,
            self.source,
            self.comparison,
            [self.pull],
            self.writers,
        )

    def test_reviewed_source_is_distinct_from_default_workflow(self) -> None:
        """Allow a reviewed source that differs from the trusted workflow commit."""
        self.admit()

    def test_every_identity_and_admission_field_is_required(self) -> None:
        """Reject every independently changed identity or authorization field."""
        for key in self.env:
            with self.subTest(key=key):
                original = copy.deepcopy(self.env)
                self.env[key] = "invalid"
                with self.assertRaises(ValueError):
                    self.admit()
                self.env = original

    def test_exact_six_consumers_share_the_same_boundary(self) -> None:
        """Admit each named consumer without broadening the repository set."""
        for name in CONSUMERS:
            with self.subTest(name=name):
                self.env["GITHUB_REPOSITORY"] = name
                self.env["OWNER_WRITER_REVIEW"] = self.owner_review()
                self.repository["full_name"] = name
                self.pull["head"]["repo"]["full_name"] = name
                self.admit()

    def test_changed_source_head_is_rejected(self) -> None:
        """Do not transfer admission to an updated source PR."""
        self.pull["head"]["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "neither integrated"):
            self.admit()

    def test_changed_default_head_is_rejected(self) -> None:
        """Require another review after the default workflow head changes."""
        self.default["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "Default HEAD changed"):
            self.admit()

    def test_fork_source_is_rejected(self) -> None:
        """Do not admit a foreign repository through a same-named source PR."""
        self.pull["head"]["repo"]["full_name"] = "fork/authService"
        with self.assertRaisesRegex(ValueError, "neither integrated"):
            self.admit()

    def test_public_repository_is_rejected(self) -> None:
        """Keep the SDK CI consumers private."""
        self.repository["private"] = False
        with self.assertRaisesRegex(ValueError, "Private"):
            self.admit()

    def test_repository_identity_is_checked(self) -> None:
        """Reject inconsistent repository API metadata."""
        self.repository["full_name"] = "pokerlost/anotherService"
        with self.assertRaisesRegex(ValueError, "identity"):
            self.admit()

    def test_second_writer_is_rejected(self) -> None:
        """Fail closed when the sole-writer assumption changes."""
        self.writers.append(
            {"login": "another", "role_name": "write", "permissions": {"push": True}}
        )
        with self.assertRaisesRegex(ValueError, "Sole-writer"):
            self.admit()

    def test_read_only_collaborator_does_not_gain_admission(self) -> None:
        """Permit readers without treating them as workflow writers."""
        self.writers.append(
            {"login": "reader", "role_name": "read", "permissions": {"push": False}}
        )
        self.admit()

    def test_closed_unintegrated_pr_is_rejected(self) -> None:
        """Keep this entry point bound to an open candidate PR."""
        self.pull["state"] = "closed"
        with self.assertRaisesRegex(ValueError, "neither integrated"):
            self.admit()

    def test_post_merge_source_needs_no_open_pr(self) -> None:
        """An exact integrated source remains admissible after its PR is merged."""
        self.pull["state"] = "closed"
        self.comparison = {
            "status": "ahead",
            "merge_base_commit": {"sha": self.env["REVIEWED_SHA"]},
        }
        self.admit()
        self.comparison["merge_base_commit"]["sha"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "neither integrated"):
            self.admit()

    def test_source_repository_commit_is_exact(self) -> None:
        """Reject a response belonging to a different source commit."""
        self.source["sha"] = "d" * 40
        with self.assertRaisesRegex(ValueError, "commit identity"):
            self.admit()

    def test_cli_help_and_invalid_arguments_need_no_credentials(self) -> None:
        """Keep CLI help lazy and parser errors free of environment values."""
        result = CliRunner().invoke(
            app,
            ["--help"],
            env={"GH_TOKEN": "synthetic-do-not-print"},
        )
        self.assertEqual(result.exit_code, 0)
        self.assertNotIn("synthetic-do-not-print", result.output)
        result = CliRunner().invoke(app, ["--unknown"])
        self.assertEqual(result.exit_code, 2)
        self.assertTrue(result.stderr)

    def test_incomplete_collaborator_page_is_rejected(self) -> None:
        """Avoid assuming that an incomplete page proves sole ownership."""
        self.writers *= 100
        with self.assertRaisesRegex(ValueError, "pagination"):
            self.admit()

    def test_organization_admin_keeps_effective_write_with_read_base(self) -> None:
        """Recognize organization access rather than only base permissions."""
        self.writers[0]["permissions"]["push"] = False
        self.admit()

    def test_second_inherited_writer_is_rejected_even_with_read_base(self) -> None:
        """Never miss an additional effective writer whose base grant is read."""
        self.writers.append(
            {"login": "another", "role_name": "write", "permissions": {"push": False}}
        )
        with self.assertRaisesRegex(ValueError, "Sole-writer"):
            self.admit()

    def test_unknown_custom_role_requires_review(self) -> None:
        """Do not assume unfamiliar custom roles are readers."""
        self.writers.append(
            {"login": "another", "role_name": "custom", "permissions": {"push": False}}
        )
        with self.assertRaisesRegex(ValueError, "Unknown collaborator role"):
            self.admit()

    def test_contradictory_role_permissions_fail_closed(self) -> None:
        """Reject inconsistent API metadata rather than ignoring a possible writer."""
        self.writers.append(
            {"login": "another", "role_name": "read", "permissions": {"push": True}}
        )
        with self.assertRaisesRegex(ValueError, "Inconsistent collaborator role"):
            self.admit()

    def test_missing_owner_writer_review_fails_closed(self) -> None:
        """Owner dispatch and source pins alone cannot replace the writer audit."""
        del self.env["OWNER_WRITER_REVIEW"]
        with self.assertRaisesRegex(ValueError, "Owner writer review"):
            self.admit()

    def test_owner_review_binds_every_identity_and_both_commits(self) -> None:
        """Do not reuse a writer audit across repositories, owners or commit pairs."""
        for position in range(5):
            with self.subTest(position=position):
                fields = self.owner_review().split("|")
                fields[position] = "invalid"
                self.env["OWNER_WRITER_REVIEW"] = "|".join(fields)
                with self.assertRaisesRegex(ValueError, "Owner writer review"):
                    self.admit()

    def test_owner_review_must_be_fresh(self) -> None:
        """Reject expired or future-dated owner attestations."""
        for offset in [-3601, 120]:
            with self.subTest(offset=offset):
                self.env["OWNER_WRITER_REVIEW"] = self.owner_review(
                    self.reviewed_at + offset,
                )
                with self.assertRaisesRegex(ValueError, "Owner writer review"):
                    self.admit()

    def test_empty_visible_list_is_never_owner_review(self) -> None:
        """Accept a partial API only with a separate fresh full owner audit."""
        self.source = {"sha": "b" * 40}
        self.comparison = {"status": "diverged", "merge_base_commit": {"sha": "c" * 40}}
        self.writers = []
        self.admit()
        self.env["OWNER_WRITER_REVIEW"] = ""
        with self.assertRaisesRegex(ValueError, "Owner writer review"):
            self.admit()


if __name__ == "__main__":
    unittest.main()
