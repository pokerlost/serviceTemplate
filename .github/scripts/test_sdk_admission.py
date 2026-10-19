"""Exercise the SDK admission boundary without credentials or network access."""

from __future__ import annotations

import copy
import unittest

from sdk_admission import CONSUMERS, validate


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
        self.writers = [{"login": "serrja", "role_name": "admin", "permissions": {"push": True}}]

    def admit(self) -> None:
        """Evaluate the current synthetic admission fixture."""
        validate(self.env, self.repository, self.default, self.pull, self.writers)

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
                self.repository["full_name"] = name
                self.pull["head"]["repo"]["full_name"] = name
                self.admit()

    def test_changed_source_head_is_rejected(self) -> None:
        """Do not transfer admission to an updated source PR."""
        self.pull["head"]["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "Source PR HEAD changed"):
            self.admit()

    def test_changed_default_head_is_rejected(self) -> None:
        """Require another review after the default workflow head changes."""
        self.default["sha"] = "c" * 40
        with self.assertRaisesRegex(ValueError, "Default HEAD changed"):
            self.admit()

    def test_fork_source_is_rejected(self) -> None:
        """Do not admit a foreign repository through a same-named source PR."""
        self.pull["head"]["repo"]["full_name"] = "fork/authService"
        with self.assertRaisesRegex(ValueError, "Fork"):
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

    def test_closed_main_pr_is_rejected(self) -> None:
        """Keep this entry point bound to an open candidate PR."""
        self.pull["state"] = "closed"
        with self.assertRaisesRegex(ValueError, "remain open"):
            self.admit()

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


if __name__ == "__main__":
    unittest.main()
