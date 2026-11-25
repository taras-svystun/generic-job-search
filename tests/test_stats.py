"""Tests for tools/stats.py: the outcome.md and highlights.md parsers, the join with the
tracker, grouping and counts. The page is built from these, so a parser slip is a wrong
number on the page."""
import csv
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import stats  # noqa: E402

HEADER = ("date,company,sector,role,role_type,channel,status,contact_person,"
          "fit_rating,notes,cv_file,cover_letter_file,source,deadline").split(",")


def outcome_text(company="Acme", role="Data Analyst", ticked=(), note="", nxt="",
                 details=None):
    details = details or {}
    lines = [f"# Outcome: {company} — {role}", "", "## Stages"]
    for s in stats.STAGES:
        mark = "x" if s in ticked else " "
        lines.append(f"- [{mark}] {s}" + (f": {details[s]}" if s in details else ""))
    lines += ["", f"Note: {note}", f"Next: {nxt}", "", "## Notes", "- [x] not a stage"]
    return "\n".join(lines) + "\n"


class ParseOutcome(unittest.TestCase):
    def test_reads_header_boxes_details_note_next(self):
        o = stats.parse_outcome(outcome_text(
            ticked=("call booked", "call held"), details={"call held": "recruiter, 3 Mar"},
            note="Liked the portfolio.", nxt="invited"))
        self.assertEqual((o.company, o.role), ("Acme", "Data Analyst"))
        self.assertEqual(o.stages, {"call booked": "", "call held": "recruiter, 3 Mar"})
        self.assertEqual((o.note, o.next), ("Liked the portfolio.", "invited"))

    def test_checkboxes_outside_stages_are_ignored(self):
        o = stats.parse_outcome(outcome_text())
        self.assertEqual(o.stages, {})

    def test_role_with_colon_and_slash(self):
        o = stats.parse_outcome(outcome_text(role="Project Manager (Region: North / South)"))
        self.assertEqual(o.role, "Project Manager (Region: North / South)")

    def test_errors_name_the_problem(self):
        bad = {
            "unknown stage": outcome_text().replace("call held", "call hled"),
            "lacks": outcome_text().replace("- [ ] rejected after HR\n", ""),
            "first line": outcome_text().replace("# Outcome: ", "# "),
            "no '## Stages'": outcome_text().replace("## Stages", "## Interview stages"),
            "unexpected line": outcome_text().replace("Note:", "Notes:"),
        }
        for needle, text in bad.items():
            with self.subTest(needle):
                with self.assertRaisesRegex(stats.FormatError, needle):
                    stats.parse_outcome(text)


class ParseHighlights(unittest.TestCase):
    def test_sections_and_fields(self):
        h = stats.parse_highlights(
            "# Highlights\nfree text\n## Banner\n- Win | text\n"
            "## Live processes\n- Fri | Acme · call | prep\n## Other tracks\n")
        self.assertEqual(h["Banner"], [["Win", "text"]])
        self.assertEqual(h["Live processes"], [["Fri", "Acme · call", "prep"]])
        self.assertEqual(h["Other tracks"], [])

    def test_wrong_field_count_and_unknown_section_fail(self):
        with self.assertRaisesRegex(stats.FormatError, "3 fields"):
            stats.parse_highlights("## Live processes\n- Fri | only two\n")
        with self.assertRaisesRegex(stats.FormatError, "unknown section"):
            stats.parse_highlights("## Banners\n- a | b\n")


class LoadAndCount(unittest.TestCase):
    def build(self, rows, outcomes):
        tmp = Path(tempfile.mkdtemp())
        with open(tmp / "t.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, HEADER)
            w.writeheader()
            for company, role, status, day in rows:
                w.writerow({"date": day, "company": company, "role": role, "status": status})
        for i, text in enumerate(outcomes):
            (tmp / "apps" / f"f{i}").mkdir(parents=True)
            (tmp / "apps" / f"f{i}" / "outcome.md").write_text(text, encoding="utf-8")
        (tmp / "apps").mkdir(exist_ok=True)
        warnings = []
        apps = stats.load(tmp / "t.csv", tmp / "apps", warn=warnings.append)
        return apps, warnings

    def test_missing_tracker_is_an_empty_pipeline(self):
        # A fresh clone has no tracker: it is git-ignored and /apply creates it.
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d)
            (tmp / "apps").mkdir()
            self.assertEqual(stats.load(tmp / "none.csv", tmp / "apps", warn=print), [])

    def test_join_by_header_ignores_case_and_spaces(self):
        apps, warnings = self.build(
            [("Acme", "Data  Analyst", "interview", "2030-03-01")],
            [outcome_text("ACME", "data analyst", ticked=("call booked",))])
        self.assertTrue(apps[0].has("call booked"))
        self.assertEqual(warnings, [])

    def test_row_without_outcome_has_no_stages_and_orphan_file_warns(self):
        apps, warnings = self.build(
            [("Acme", "Data Analyst", "applied", "2030-03-01")],
            [outcome_text("Other", "Role")])
        self.assertEqual(apps[0].outcome.stages, {})
        self.assertIn("no tracker row", warnings[0])

    def test_two_files_for_one_application_fail(self):
        with self.assertRaisesRegex(stats.FormatError, "second outcome file"):
            self.build([], [outcome_text(), outcome_text()])

    def test_rejected_box_against_open_status_warns(self):
        _, warnings = self.build(
            [("Acme", "Data Analyst", "applied", "2030-03-01")],
            [outcome_text(ticked=("rejected at CV",))])
        self.assertIn("rejected box", warnings[0])

    def test_groups_cover_every_status_and_drafted_is_skipped(self):
        rows = [
            ("A", "r", "rejected", "2030-03-01"),
            ("B", "r", "offer declined", "2030-03-01"),   # legacy space spelling
            ("C", "r", "no response", "2030-03-01"),      # legacy space spelling
            ("D", "r", "withdrawn", "2030-03-01"),
            ("E", "r", "withdrawn", "2030-03-01"),
            ("F", "r", "interview", "2030-03-01"),
            ("G", "r", "applied", "2030-03-01"),
            ("H", "r", "something new", "2030-03-01"),    # unknown: shown, not dropped
            ("I", "r", "drafted", "2030-03-01"),          # never sent: not on the page
        ]
        apps, _ = self.build(rows, [outcome_text("E", "r", ticked=("past technical",)),
                                    outcome_text("G", "r", ticked=("call booked",))])
        got = {a.row["company"]: stats.group(a) for a in apps}
        self.assertEqual(got, {"A": "rej", "B": "won", "C": "silent", "D": "withdrawn",
                               "E": "won", "F": "live", "G": "live", "H": "silent"})

    def test_counts_follow_the_funnel_rules(self):
        rows = [("A", "r", "rejected", "2030-03-01"), ("B", "r", "rejected", "2030-03-01"),
                ("C", "r", "interview", "2030-03-01"), ("D", "r", "interview", "2030-03-01"),
                ("E", "r", "applied", "2030-03-01")]
        outs = [outcome_text("A", "r", ticked=("rejected at CV",)),
                outcome_text("B", "r", ticked=("call booked", "call held", "rejected after HR")),
                outcome_text("C", "r", ticked=("call booked", "call held", "technical held",
                                                 "past technical")),
                outcome_text("D", "r", ticked=("call booked",))]
        apps, _ = self.build(rows, outs)
        c = stats.counts(apps)
        self.assertEqual(
            {k: c[k] for k in ("applied", "rej", "rej-cv", "rej-hr", "live", "silent",
                               "call-held", "call-booked", "tech", "past", "past-names")},
            {"applied": 5, "rej": 2, "rej-cv": 1, "rej-hr": 1, "live": 2, "silent": 1,
             "call-held": 2, "call-booked": 1, "tech": 1, "past": 1, "past-names": "C"})

    def test_rejected_after_technical_is_counted_and_marked(self):
        rows = [("A", "r", "rejected", "2030-03-01")]
        apps, _ = self.build(rows, [outcome_text("A", "r", ticked=(
            "call booked", "call held", "technical held"))])
        self.assertEqual(stats.counts(apps)["rej-tech"], 1)
        tech_cell = stats.cells(apps[0], "rej")[2]
        self.assertIn("p-bad", tech_cell)


class Render(unittest.TestCase):
    def test_page_escapes_text_and_ends_with_the_analysis_hint(self):
        app = stats.App({"company": "A<b>", "role": "r", "status": "applied",
                         "date": "2030-03-01"}, stats.Outcome("A<b>", "r", note="x & y"))
        page = stats.render([app], stats.parse_highlights(""), date(2030, 3, 15))
        self.assertIn("A&lt;b&gt;", page)
        self.assertIn("x &amp; y", page)
        self.assertNotIn("<script", page)
        footer = page[page.index("<footer>"):]
        self.assertIn(stats.ANALYSIS_HINT, footer)


if __name__ == "__main__":
    unittest.main()
