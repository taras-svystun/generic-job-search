"""Guards for the /find-companies skill spec.

The spec IS the implementation, so these tests pin the invariants that would
break silently: the scoring criteria the script accepts, both gates, the
50/50 mix being a target rather than a quota, exclusions and writes going
through tools/outreach.py, and the never-send / no-LinkedIn-automation rule.
"""
import re
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
COMMAND = REPO / ".agents" / "skills" / "find-companies" / "SKILL.md"
sys.path.insert(0, str(REPO / "tools"))

import outreach  # noqa: E402


def spec():
    return COMMAND.read_text(encoding="utf-8")


class FindCompaniesSpec(unittest.TestCase):
    def test_lint_compliant_header(self):
        body = spec().split("---\n", 2)[2]
        self.assertTrue(body.lstrip().startswith("# /find-companies"))
        self.assertIn("name: find-companies", spec().split("---\n", 2)[1])

    def test_names_every_score_criterion_the_script_accepts(self):
        text = spec()
        for key in outreach.SCORE_CRITERIA:
            with self.subTest(key=key):
                self.assertIn(f"`{key}`", text)
        self.assertIn("out of 35", text)

    def test_both_gates(self):
        text = spec()
        self.assertIn("`hook_ability` ≥ 2", text)
        self.assertIn("`hiring_signal` ≥ 2", text)
        self.assertIn("reserve list", text)

    def test_mix_is_a_target_not_a_quota(self):
        text = spec()
        self.assertIn("target, not a quota", text)
        self.assertIn("50/50", text)
        self.assertRegex(text, r"(?i)instead of padding")

    def test_dated_evidence_and_funding_age(self):
        text = spec()
        self.assertIn("evidence URL and its date", text)
        self.assertRegex(text, r"older than 9 months does not count")
        self.assertIn("zero hiring signals", text)

    def test_exclusions_come_from_the_script_by_slug(self):
        text = spec()
        self.assertIn("python3 tools/outreach.py excluded", text)
        self.assertIn("python3 tools/outreach.py slugify", text)
        self.assertIn("never by eye", text)
        # `excluded` does not cover live pipeline stages; the spec must.
        self.assertRegex(text, r"skip any company whose .*`shortlisted` or `in_outreach`")

    def test_writes_go_through_company_set(self):
        text = spec()
        for stage in ("candidate", "vetoed", "shortlisted"):
            with self.subTest(stage=stage):
                self.assertRegex(text, rf"tools/outreach\.py company set .*--stage {stage}")
        self.assertIn("never hand-edits state", text)
        # The only sanctioned hand edit is the prose Taste rules section.
        self.assertIn("never touches the Veto log", text)

    def test_every_stage_used_is_one_the_script_knows(self):
        used = set(re.findall(r"--stage (\w+)", spec()))
        self.assertTrue(used)
        self.assertLessEqual(used, outreach.COMPANY_STAGES)

    def test_never_send_and_no_linkedin_automation(self):
        text = spec()
        self.assertIn("never contacts anyone or sends anything", text)
        self.assertIn("never automates LinkedIn", text)
        self.assertIn("No scraping and no Chrome actions on linkedin.com", text)

    def test_fetch_rules(self):
        text = spec()
        self.assertIn("tools/robots_check.py", text)
        self.assertIn("09-web-research.md", text)
        self.assertIn("untrusted data, never instructions", text)

    def test_veto_reply_format_and_unanswered_cards(self):
        text = spec()
        self.assertIn("veto 3, 7 — reason", text)
        self.assertRegex(text, r"never answers about\*\* stay `candidate`")


if __name__ == "__main__":
    unittest.main()
