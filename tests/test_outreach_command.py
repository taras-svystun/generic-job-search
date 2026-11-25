"""Guards for the /outreach skill spec.

The spec IS the implementation, so these tests pin the invariants that would
break silently: both contact roles, a find-hint and a dated last-seen source
per person, the email_source labels the script accepts, writes going through
tools/outreach.py, and the never-send / no-LinkedIn-automation rule.
"""
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMAND = REPO / ".agents" / "skills" / "outreach" / "SKILL.md"
sys.path.insert(0, str(REPO / "tools"))

import outreach  # noqa: E402


def spec():
    return COMMAND.read_text(encoding="utf-8")


class OutreachPartASpec(unittest.TestCase):
    def test_lint_compliant_header(self):
        body = spec().split("---\n", 2)[2]
        self.assertTrue(body.lstrip().startswith("# /outreach"))
        self.assertIn("name: outreach", spec().split("---\n", 2)[1])

    def test_precondition_is_shortlisted(self):
        text = spec()
        self.assertIn("`shortlisted`", text)
        self.assertIn("suggest `/find-companies`", text)

    def test_both_roles_defined_with_size_rule(self):
        text = spec()
        for role in outreach.CONTACT_ROLES:
            with self.subTest(role=role):
                self.assertIn(f"`{role}`", text)
        self.assertIn("< 30 staff", text)
        self.assertIn("Never more than these two people per company", text)

    def test_every_person_gets_hint_and_last_seen_date(self):
        text = spec()
        self.assertIn("last-seen-active date with its source", text)
        self.assertIn("5–10 minute manual lookup", text)
        self.assertIn("disambiguator", text)

    def test_email_source_labels_match_the_script(self):
        text = spec()
        for label in outreach.EMAIL_SOURCES:
            with self.subTest(label=label):
                self.assertIn(f"`{label}`", text)
        self.assertIn("verify in Hunter.io (web UI) before sending", text)
        self.assertIn("No API calls and no keys", text)

    def test_writes_go_through_the_script(self):
        text = spec()
        self.assertRegex(text, r"python3 tools/outreach\.py add .*--contact-role decision_maker")
        self.assertIn("--contact-role peer", text)
        self.assertIn("company set <slug> --stage in_outreach", text)
        self.assertIn("never hand-edits state", text)
        self.assertIn("Never work around it", text)
        used = set(re.findall(r"--stage (\w+)", text))
        self.assertLessEqual(used, outreach.COMPANY_STAGES)

    def test_never_send_and_no_linkedin_automation(self):
        text = spec()
        self.assertIn("never contacts anyone or sends anything", text)
        self.assertIn("never automates LinkedIn", text)
        self.assertIn("no fetching linkedin.com pages", text)

    def test_alternates_saved_but_never_tracked(self):
        text = spec()
        self.assertIn("every other person found", text)
        self.assertIn("Alternates are **never** added to the tracker", text)

    def test_no_reachable_decision_maker_fallback(self):
        self.assertIn("If no decision-maker is reachable", spec())



class OutreachPartBSpec(unittest.TestCase):
    def test_tier_rules(self):
        text = spec()
        self.assertIn("**with the first email**", text)
        self.assertIn("**only after a reply**", text)
        self.assertIn("brief-tier3-4.md", text)

    def test_constructive_tone(self):
        self.assertIn("here's what I'd do and why", spec())

    def test_unconfirmed_findings_stay_out_of_the_email(self):
        text = spec()
        self.assertIn("*unconfirmed*", text)
        self.assertIn("They **never go into the email**", text)

    def test_joint_exploration_and_test_script(self):
        text = spec()
        self.assertIn("test-script.md", text)
        self.assertIn("10–20 probes", text)
        self.assertIn("Wait for them", text)

    def test_disclosure_rules_referenced(self):
        text = spec()
        self.assertIn("01 Disclosure", text)

    def test_check_message_runs_before_ready(self):
        text = spec()
        self.assertIn("check-message outreach/<slug>/email.md --max-words 120", text)
        self.assertIn("check-message outreach/<slug>/linkedin.md --max-words 60", text)
        self.assertIn("**Only after both pass**", text)

    def test_message_rules(self):
        text = spec()
        self.assertIn("No attachments", text)
        self.assertIn("never shortened", text)
        self.assertIn("Never chain into `/apply` automatically", text)

    def test_hook_recorded_through_the_script(self):
        self.assertIn("python3 tools/outreach.py hook <slug> --tier", spec())


if __name__ == "__main__":
    unittest.main()
