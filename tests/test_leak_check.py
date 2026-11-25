"""Tests for tools/leak_check.py: a check that a folder holds no private term."""

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from leak_check import main, scan  # noqa: E402


class LeakCheckTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        return p

    def terms_hit(self, text, terms):
        self.write("f.md", text)
        hits, _ = scan(self.root, terms)
        return {h[2] for h in hits}

    def test_name_with_any_separator(self):
        for text in ["Jane Doe", "jane-doe", "JANE_DOE", "JaneDoe"]:
            self.assertEqual(self.terms_hit(text, ["Jane Doe"]), {"Jane Doe"}, text)

    def test_phone_in_any_grouping(self):
        self.assertEqual(self.terms_hit("call +1 555 123 4567", ["+15551234567"]), {"+15551234567"})

    def test_score_with_slash(self):
        self.assertEqual(self.terms_hit("scored 7 / 10", ["7/10"]), {"7/10"})

    def test_no_match_inside_a_longer_word(self):
        self.assertEqual(self.terms_hit("Annual report", ["Ann"]), set())
        self.assertEqual(self.terms_hit("Ann_report", ["Ann"]), {"Ann"})

    def test_non_latin_term(self):
        self.assertEqual(self.terms_hit("συγγραφέας: Μαρία", ["Μαρία"]), {"Μαρία"})

    def test_path_is_searched(self):
        self.write("cv/Jane-Doe_CV.tex", "clean")
        hits, _ = scan(self.root, ["Jane Doe"])
        self.assertEqual(hits[0][1], 0)

    def test_allowlist_masks_a_kept_credit(self):
        self.write("README.md", "Adapted by jane-doe.\nWritten by Jane Doe.\n")
        hits, _ = scan(self.root, ["jane-doe"], allowed=["adapted by jane-doe"])
        self.assertEqual([h[1] for h in hits], [2])

    def test_binary_file_fails_as_unscanned(self):
        (self.root / "x.pdf").write_bytes(b"%PDF\0\0data")
        blacklist = Path(self._tmp.name + "_bl.txt")
        blacklist.write_text("# comment\nnothing\n", encoding="utf-8")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(self.root), str(blacklist)])
            self.assertEqual(code, 1)
        finally:
            blacklist.unlink()

    def test_empty_folder_passes(self):
        blacklist = Path(self._tmp.name + "_bl.txt")
        blacklist.write_text("Jane Doe\n", encoding="utf-8")
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                code = main([str(self.root), str(blacklist)])
            self.assertEqual(code, 0)
        finally:
            blacklist.unlink()


if __name__ == "__main__":
    unittest.main()
