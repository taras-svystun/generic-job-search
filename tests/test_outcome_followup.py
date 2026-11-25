"""Guards for /outcome's follow-up branch (Step 2b).

The branch is part of the /outcome markdown spec (the spec IS the
implementation), so these tests pin the invariants that would break
silently: the draft-only rule (the branch must never send anything on the
user's behalf), the no-new-claims rule that keeps follow-ups inside the
framework's never-fabricate boundary, the two-follow-up cap that terminates
into /outcome's own no_response flow.
"""
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMAND = REPO / ".agents" / "skills" / "outcome" / "SKILL.md"


class OutcomeFollowupBranchSpec(unittest.TestCase):
    def test_followup_branch_exists(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn(
            "## Step 2b: Follow-Up Branch",
            text,
            "outcome.md lost its follow-up branch section",
        )

    def test_followup_argument_documented(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn(
            "`followup <N>`",
            text,
            "spec lost the /outcome followup argument forms",
        )

    def test_draft_only_rule_present(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn(
            "draft only, never send",
            text,
            "spec lost the rule that the follow-up branch never sends anything on the user's behalf",
        )

    def test_no_new_claims_rule_present(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn(
            "no new claims",
            text,
            "spec lost the rule that follow-ups only reuse claims from the archived submitted materials",
        )

    def test_two_followup_cap_present(self):
        text = COMMAND.read_text(encoding="utf-8")
        self.assertIn(
            "Maximum two follow-ups per application",
            text,
            "spec lost the cap that stops the follow-up branch from nagging indefinitely",
        )


if __name__ == "__main__":
    unittest.main()
