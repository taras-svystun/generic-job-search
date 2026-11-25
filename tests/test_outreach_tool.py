"""Tests for tools/outreach.py.

Fictional fixtures only: no real person or company from the trackers appears
here, so the file is safe to commit whatever the repo's visibility.
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import outreach  # noqa: E402

LEGACY_HEADER = ",".join(outreach.LEGACY_COLUMNS)
LEGACY_TRACKER = (
    LEGACY_HEADER + "\n"
    "2030-04-01,Acme Corp,mid,,Head of Operations,founder,teardown,"
    "2030-04-03,,,,,,,https://example.com/job/1,"
    "\"Asked about travel, \"\"maybe\"\"\nsecond line\"\n"
    "2030-04-02,Example Labs,small,Jane Example,CTO,founder,teardown,,,,,,,,,\n"
)


def full_row(**over):
    row = {c: "" for c in outreach.LEGACY_COLUMNS + outreach.NEW_COLUMNS}
    row.update(company="Example Labs", person_name="Jane Example",
               contact_role="decision_maker", channel="email", status="queued")
    row.update(over)
    return row


class TempRoot(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)
        (self.root / "company_research").mkdir()

    def write(self, rel, text, bom=False):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes((b"\xef\xbb\xbf" if bom else b"") + text.encode("utf-8"))
        return p

    def tracker_rows(self):
        return outreach.read_csv(self.root / outreach.TRACKER)[1]


class MigrateTests(TempRoot):
    def test_idempotent(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        outreach.migrate(self.root)
        first = (self.root / outreach.TRACKER).read_bytes()
        self.assertEqual(outreach.migrate(self.root), 0)
        self.assertEqual((self.root / outreach.TRACKER).read_bytes(), first)

    def test_connect_sent_becomes_status_with_that_date(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        outreach.migrate(self.root)
        acme, jane = self.tracker_rows()
        self.assertEqual((acme["status"], acme["status_date"], acme["channel"]),
                         ("connect_sent", "2030-04-03", "linkedin"))
        self.assertEqual(acme["contact_role"], "decision_maker")
        self.assertEqual((jane["status"], jane["status_date"]), ("queued", ""))

    def test_legacy_columns_unchanged(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        _, before, _ = outreach.read_csv(self.root / outreach.TRACKER)
        outreach.migrate(self.root)
        header, after, _ = outreach.read_csv(self.root / outreach.TRACKER)
        self.assertEqual(header[:len(outreach.LEGACY_COLUMNS)], outreach.LEGACY_COLUMNS)
        for b, a in zip(before, after):
            self.assertEqual({k: a[k] for k in outreach.LEGACY_COLUMNS}, b)

    def test_migrated_legacy_tracker_validates(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        outreach.migrate(self.root)
        # Jane has no channel yet: the only expected error, and it names the fix.
        errors = outreach.validate(self.root)
        self.assertEqual(len(errors), 1, errors)
        self.assertIn("channel", errors[0])


class RoundTripTests(TempRoot):
    def test_bom_and_tricky_notes_survive(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER, bom=True)
        header, rows, term = outreach.read_csv(self.root / outreach.TRACKER)
        outreach.write_csv(self.root / outreach.TRACKER, header, rows, term)
        raw = (self.root / outreach.TRACKER).read_bytes()
        self.assertFalse(raw.startswith(b"\xef\xbb\xbf"), "writes must not carry a BOM")
        self.assertEqual(outreach.read_csv(self.root / outreach.TRACKER)[1], rows)
        self.assertEqual(rows[0]["notes"], 'Asked about travel, "maybe"\nsecond line')

    def test_crlf_preserved(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER.replace("\n", "\r\n").replace(
            "maybe\"\"\r\nsecond", "maybe\"\"\nsecond"))
        outreach.migrate(self.root)
        self.assertIn(b"\r\n", (self.root / outreach.TRACKER).read_bytes())

    def test_semicolon_file_fails_loudly(self):
        self.write(outreach.TRACKER, LEGACY_HEADER.replace(",", ";") + "\n")
        with self.assertRaises(outreach.OutreachError):
            outreach.read_csv(self.root / outreach.TRACKER)

    def test_write_leaves_bak(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        outreach.migrate(self.root)
        bak = self.root / (outreach.TRACKER + ".bak")
        self.assertEqual(bak.read_text(encoding="utf-8"), LEGACY_TRACKER)


class ValidateTests(unittest.TestCase):
    def assertRejects(self, rows, fragment, previous=None):
        errors = outreach.validate_rows(rows, previous)
        self.assertTrue(any(fragment in e for e in errors), errors)

    def test_good_row_passes(self):
        self.assertEqual(outreach.validate_rows([full_row()]), [])

    def test_bad_status(self):
        self.assertRejects([full_row(status="ghosted")], "status 'ghosted'")

    def test_status_not_on_channel(self):
        self.assertRejects([full_row(status="connect_sent", status_date="2030-05-01")],
                           "does not exist on channel")

    def test_bad_date(self):
        self.assertRejects([full_row(status="messaged", status_date="04/05/2030")],
                           "not an ISO date")

    def test_status_date_required(self):
        self.assertRejects([full_row(status="messaged")], "status_date is required")

    def test_hook_tier(self):
        self.assertRejects([full_row(hook_tier="7")], "hook_tier")

    def test_vocabularies(self):
        self.assertRejects([full_row(channel="fax")], "channel 'fax'")
        self.assertRejects([full_row(contact_role="boss")], "contact_role 'boss'")
        self.assertRejects([full_row(email_source="hunch")], "email_source")

    def test_duplicate_person(self):
        self.assertRejects([full_row(), full_row(company="Example Labs Ltd")],
                           "duplicate person")

    def test_illegal_transition(self):
        old = [full_row(status="no_reply", status_date="2030-05-01")]
        new = [full_row(status="messaged", status_date="2030-05-02")]
        self.assertRejects(new, "illegal transition no_reply -> messaged", previous=old)

    def test_legal_transitions(self):
        self.assertTrue(outreach.is_legal("linkedin", "connect_sent", "replied"))
        self.assertTrue(outreach.is_legal("email", "queued", "dropped"))
        self.assertFalse(outreach.is_legal("email", "converted", "declined"))
        self.assertFalse(outreach.is_legal("email", "queued", "replied"))

    def test_documented_reopen_allowed(self):
        old = [full_row(status="no_reply", status_date="2030-05-01")]
        new = [full_row(status="messaged", status_date="2030-05-02",
                        notes="Reopened: she wrote back via a colleague")]
        self.assertEqual(outreach.validate_rows(new, old), [])


class SlugifyTests(unittest.TestCase):
    def test_cases(self):
        self.assertEqual(outreach.slugify("Example Labs"), "example-labs")
        self.assertEqual(outreach.slugify("Globex GmbH"), "globex")
        self.assertEqual(outreach.slugify("Zoë Müller Design"), "zoe-muller-design")
        self.assertEqual(outreach.slugify("Acme, Inc."), "acme")
        self.assertEqual(outreach.slugify("SA"), "sa")  # never strips to nothing

    def test_digits_and_spaces(self):
        for name, slug in [("Initech", "initech"), ("Umbrella  Group", "umbrella-group"),
                           ("Area 51 Labs", "area-51-labs"), ("42data", "42data")]:
            self.assertEqual(outreach.slugify(name), slug)


class ExcludedTests(TempRoot):
    def test_collects_all_sources(self):
        self.write(outreach.JOB_TRACKER, "date,company,status\n2030-03-20,Acme Corp GmbH,applied\n")
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        self.write("company_research/vetoed-co.json", json.dumps({"outreach": {"stage": "vetoed"}}))
        self.write("company_research/fresh-co.json", json.dumps({"outreach": {"stage": "shortlisted"}}))
        self.write("company_research/plain-cache.json", json.dumps({"company": "Plain Cache"}))
        ex = outreach.excluded(self.root)
        self.assertIn("acme-corp", ex)
        self.assertIn("example-labs", ex)
        self.assertIn("vetoed-co", ex)
        self.assertNotIn("fresh-co", ex)
        self.assertNotIn("plain-cache", ex)


class CompanySetTests(TempRoot):
    def test_preserves_unrelated_keys(self):
        original = {"company": "Acme", "fetched_date": "2030-05-01",
                    "sources": {"website": {"url": "https://example.com"}}}
        p = self.write("company_research/acme.json", json.dumps(original))
        outreach.company_set(self.root, "acme", "shortlisted", segment="warm",
                             scores={"fit": 4, "hook_ability": 3}, date="2030-05-04")
        data = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual({k: data[k] for k in original}, original)
        self.assertEqual(data["outreach"]["stage"], "shortlisted")
        self.assertEqual(data["outreach"]["total"], 7)
        self.assertTrue((self.root / "company_research/acme.json.bak").exists())

    def test_vetoed_requires_reason(self):
        with self.assertRaises(outreach.OutreachError):
            outreach.company_set(self.root, "acme", "vetoed")
        self.assertFalse((self.root / "company_research/acme.json").exists())

    def test_veto_appends_to_preferences(self):
        outreach.company_set(self.root, "acme", "vetoed", reason="crypto", date="2030-05-04")
        outreach.company_set(self.root, "beta", "vetoed", reason="hybrid", date="2030-05-04")
        text = (self.root / outreach.PREFERENCES).read_text(encoding="utf-8")
        log, taste = text.split("## Taste rules")
        self.assertIn("- 2030-05-04 — acme — crypto", log)
        self.assertLess(log.index("acme"), log.index("beta"))
        self.assertNotIn("acme", taste)

    def test_rejects_bad_input(self):
        for kwargs in ({"slug": "Acme Inc", "stage": "candidate"},
                       {"slug": "acme", "stage": "maybe"},
                       {"slug": "acme", "stage": "candidate", "scores": {"fit": 6}},
                       {"slug": "acme", "stage": "candidate", "scores": {"vibes": 3}}):
            with self.subTest(**{k: str(v) for k, v in kwargs.items()}):
                with self.assertRaises(outreach.OutreachError):
                    outreach.company_set(self.root, **kwargs)

    def test_refuses_to_overwrite_corrupt_json(self):
        self.write("company_research/acme.json", "{not json")
        with self.assertRaises(outreach.OutreachError):
            outreach.company_set(self.root, "acme", "candidate")


class AddTests(TempRoot):
    def setUp(self):
        super().setUp()
        outreach.company_set(self.root, "example-labs", "shortlisted", name="Example Labs")
        outreach.migrate(self.root)

    def add(self, **kw):
        args = dict(company="Example Labs", person="Jane Example", contact_role="decision_maker",
                    person_role="CTO", email="jane@example.com", email_source="pattern_seen")
        args.update(kw)
        return outreach.add(self.root, **args)

    def test_writes_valid_queued_row(self):
        row = self.add()
        self.assertEqual((row["status"], row["channel"]), ("queued", "email"))
        self.assertEqual(outreach.validate(self.root), [])
        self.assertEqual(len(self.tracker_rows()), 1)

    def test_peer_defaults_to_linkedin_without_email(self):
        row = self.add(person="John Sample", contact_role="peer", email="", email_source="")
        self.assertEqual(row["channel"], "linkedin")

    def test_refuses_duplicate(self):
        self.add()
        with self.assertRaisesRegex(outreach.OutreachError, "already in the tracker"):
            self.add(company="Example Labs Ltd")

    def test_refuses_declined_person_even_at_another_company(self):
        self.add()
        header, rows, term = outreach.read_csv(self.root / outreach.TRACKER)
        rows[0].update(status="declined", status_date="2030-05-01")
        outreach.write_csv(self.root / outreach.TRACKER, header, rows, term)
        outreach.company_set(self.root, "other-co", "shortlisted", name="Other Co")
        with self.assertRaisesRegex(outreach.OutreachError, "do not contact"):
            self.add(company="Other Co", person="J. Example", email="jane@example.com")

    def test_refuses_company_not_shortlisted(self):
        outreach.company_set(self.root, "cand-co", "candidate")
        for company in ("Cand Co", "Unknown Co"):
            with self.subTest(company=company):
                with self.assertRaisesRegex(outreach.OutreachError, "company stage"):
                    self.add(company=company)

    def test_email_rules(self):
        for kw, msg in (({"email": "", "email_source": ""}, "needs --email"),
                        ({"email_source": ""}, "go together"),
                        ({"email": "not-an-email"}, "does not look like"),
                        ({"email_source": "hunch"}, "email_source")):
            with self.subTest(**kw):
                with self.assertRaisesRegex(outreach.OutreachError, msg):
                    self.add(**kw)
        self.assertEqual(self.tracker_rows(), [])

    def test_cli_add(self):
        r = subprocess.run([sys.executable, str(REPO_ROOT / "tools/outreach.py"), "--root",
                            str(self.root), "add", "--company", "Example Labs", "--person",
                            "John Sample", "--contact-role", "peer", "--role-title",
                            "Senior Accountant"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("(peer, linkedin, queued)", r.stdout)


GOOD_EMAIL = """Subject: Your mobile checkout - three findings

Hi Jane,

I'm a UX researcher who runs usability tests for online shops. I tested your mobile
checkout with five people and timed each step:

- four of five missed the promo-code field
- the address form loses its data after a failed card payment

Full write-up: https://docs.google.com/document/d/1AbCdEfGhIjKlMnOp/edit

I'm looking for a UX research role and would love to talk about joining Example.

--
Your Name
https://www.linkedin.com/in/your-name
"""


class CheckMessageTests(unittest.TestCase):
    def check(self, text, max_words=120, denylist=()):
        return outreach.check_message(text, max_words, list(denylist))

    def test_good_message_passes(self):
        errors, warnings = self.check(GOOD_EMAIL)
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])

    def test_signature_and_subject_not_counted(self):
        body_only = GOOD_EMAIL.split("--")[0]
        self.assertEqual(outreach.count_words(GOOD_EMAIL), outreach.count_words(body_only))
        self.assertNotIn("Your", " ".join(outreach._message_body(GOOD_EMAIL).split()[:1]))

    def test_too_long(self):
        long = GOOD_EMAIL.replace("Hi Jane,", "Hi Jane, " + "word " * 130)
        self.assertTrue(any("words in the body" in e for e in self.check(long)[0]))

    def test_shortened_link(self):
        bad = GOOD_EMAIL.replace("https://docs.google.com/document/d/1AbCdEfGhIjKlMnOp/edit",
                                 "https://bit.ly/3xYz")
        self.assertTrue(any("shortened URL" in e for e in self.check(bad)[0]))

    def test_missing_role_ask(self):
        bad = GOOD_EMAIL.replace(
            "I'm looking for a UX research role and would love to talk about joining Example.",
            "Happy to chat if useful.")
        self.assertTrue(any("no role ask" in e for e in self.check(bad)[0]))

    def test_leftover_placeholder(self):
        for ph in ("[Name]", "{{doc_url}}", "TODO"):
            with self.subTest(ph=ph):
                bad = GOOD_EMAIL.replace("Hi Jane,", f"Hi {ph},")
                self.assertTrue(any("placeholder" in e for e in self.check(bad)[0]))

    def test_markdown_link_is_not_a_placeholder(self):
        ok = GOOD_EMAIL.replace("Full write-up: ", "[Full write-up](https://example.com/doc) ")
        self.assertFalse(any("placeholder" in e for e in self.check(ok)[0]))

    def test_denylist_hit(self):
        bad = GOOD_EMAIL.replace("for online shops", "for Initech")
        errors, _ = self.check(bad, denylist=["Initech"])
        self.assertTrue(any("denylisted" in e for e in errors))

    def test_missing_denylist_warns(self):
        errors, warnings = outreach.check_message(GOOD_EMAIL, 120, None)
        self.assertEqual(errors, [])
        self.assertTrue(any("not found" in w for w in warnings))

    def test_cli(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        (root / "outreach").mkdir()
        (root / "outreach/_denylist.txt").write_text("# protected names\nInitech\n", encoding="utf-8")
        msg = root / "email.md"
        msg.write_text(GOOD_EMAIL, encoding="utf-8")
        cmd = [sys.executable, str(REPO_ROOT / "tools/outreach.py"), "--root", str(root),
               "check-message", str(msg), "--max-words", "120"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        msg.write_text(GOOD_EMAIL.replace("for online shops", "for Initech"), encoding="utf-8")
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        self.assertIn("denylisted", r.stderr)


class HookTests(TempRoot):
    def test_sets_open_rows_only(self):
        outreach.company_set(self.root, "example-labs", "shortlisted")
        outreach.migrate(self.root)
        outreach.add(self.root, "Example Labs", "Jane Example", "decision_maker",
                     email="jane@example.com", email_source="guess")
        outreach.add(self.root, "Example Labs", "John Sample", "peer")
        header, rows, term = outreach.read_csv(self.root / outreach.TRACKER)
        rows[1].update(status="dropped", status_date="2030-05-04")
        outreach.write_csv(self.root / outreach.TRACKER, header, rows, term)
        self.assertEqual(outreach.set_hook(self.root, "Example Labs", 1,
                                           "https://docs.google.com/document/d/x/edit"), 1)
        jane, john = self.tracker_rows()
        self.assertEqual((jane["hook_tier"], john["hook_tier"]), ("1", ""))
        with self.assertRaises(outreach.OutreachError):
            outreach.set_hook(self.root, "Example Labs", 1, "https://bit.ly/x")
        with self.assertRaises(outreach.OutreachError):
            outreach.set_hook(self.root, "Nobody Co", 1)


class CliSmokeTest(TempRoot):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(REPO_ROOT / "tools/outreach.py"),
                               "--root", str(self.root), *args],
                              capture_output=True, text=True)

    def test_cli(self):
        self.write(outreach.TRACKER, LEGACY_TRACKER)
        r = self.run_cli("migrate")
        self.assertEqual(r.returncode, 1, r.stderr)  # Jane lacks a channel
        self.assertIn("migrate: 2 row(s) updated", r.stdout)
        self.assertEqual(self.run_cli("slugify", "Globex GmbH").stdout.strip(), "globex")
        r = self.run_cli("company", "set", "acme", "--stage", "vetoed")
        self.assertEqual(r.returncode, 2)
        self.assertIn("requires --reason", r.stderr)
        r = self.run_cli("company", "set", "acme", "--stage", "vetoed", "--reason", "x")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("acme", self.run_cli("excluded").stdout.split())


class GitignoreTests(unittest.TestCase):
    """Real check-ignore semantics on a copy of the shipped .gitignore."""

    def test_outreach_paths(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
        base = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
        marker = "# PRIVATE-REPO OVERRIDES"
        self.assertIn(marker, base)
        # The optional private-repo block ships commented out ("#> " lines);
        # switch it on to test what it does.
        text = "\n".join(ln[3:] if ln.startswith("#> ") else ln
                         for ln in base.splitlines()) + "\n"

        def ignored(gitignore, path):
            (root / ".gitignore").write_text(gitignore, encoding="utf-8")
            return subprocess.run(["git", "-C", str(root), "check-ignore", "-q", path],
                                  capture_output=True).returncode == 0

        for path in ("outreach_tracker.csv", "outreach/acme/email.md",
                     "outreach_tracker.csv.bak", "outreach/_denylist.txt"):
            with self.subTest(section="base", path=path):
                self.assertTrue(ignored(base, path))
        for path, expect in (("outreach_tracker.csv", False),
                             ("outreach/acme/email.md", False),
                             ("outreach_tracker.csv.bak", True),
                             ("company_research/acme.json.bak", True),
                             ("outreach/_denylist.txt", True)):
            with self.subTest(section="override", path=path):
                self.assertEqual(ignored(text, path), expect)


if __name__ == "__main__":
    unittest.main()
