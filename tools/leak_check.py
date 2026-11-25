"""Fail if a folder holds any term from a blacklist.

Usage: python3 tools/leak_check.py FOLDER BLACKLIST [--allow ALLOWLIST]

Use it before you make a copy of your job-search folder public: every file's
text AND its path are searched for every blacklist term (your name, employers,
clients, contacts).

Blacklist format: one term per line; blank lines and lines starting with # are
skipped. Matching ignores case, and the parts of a term may be joined by any
punctuation or none, so "Jane Doe" also catches "jane-doe", "Jane_Doe" and
"JaneDoe". A term made of digits also matches with up to three punctuation or
space characters between any two digits, so "+15551234567" catches
"+1 555 123 4567" and "7/10" catches "7 / 10". A term never matches inside a longer word: "Ann" does not
hit "Annual".

Allowlist (optional): one exact string per line. Each occurrence is blanked out
before the search, for traces kept on purpose (an author credit).

Files the tool cannot read as text (a NUL byte in the first 8 KB) are reported
as unscanned and also fail the check: a PDF can hide a name the grep never sees.
Only .git, .venv, venv and node_modules are skipped. __pycache__ is scanned: its
.pyc files hold absolute paths (often a user name), so delete them before a copy.

Exit code: 0 when clean, 1 on any hit or unscanned file, 2 on bad usage.
"""

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {".git", ".venv", "venv", "node_modules"}
DIGIT_SEP = r"[\W_]{0,3}"
# A letter or digit; "_" is a separator here, unlike in \w.
EDGE_BEFORE = r"(?<![^\W_])"
EDGE_AFTER = r"(?![^\W_])"


def read_lines(path):
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.strip().startswith("#")]


def term_pattern(term):
    """Regex for one blacklist term, or None if it holds no letter or digit."""
    parts = re.findall(r"[^\W_]+", term)
    if not parts:
        return None
    if "".join(parts).isdigit():
        body = DIGIT_SEP.join(re.escape(d) for d in "".join(parts))
    else:
        body = r"[\W_]*".join(re.escape(p) for p in parts)
    return re.compile(EDGE_BEFORE + body + EDGE_AFTER, re.IGNORECASE)


def is_binary(path):
    with open(path, "rb") as f:
        return b"\0" in f.read(8192)


def mask(text, allowed):
    for a in allowed:
        text = re.sub(re.escape(a), " ", text, flags=re.IGNORECASE)
    return text


def scan(folder, terms, allowed=(), skip=()):
    """Return (hits, unscanned). A hit is (relative path, line no, term, line text)."""
    folder = Path(folder)
    skip = {Path(s).resolve() for s in skip}
    patterns = [(t, p) for t in terms if (p := term_pattern(t))]
    hits, unscanned = [], []
    for path in sorted(folder.rglob("*")):
        rel = path.relative_to(folder)
        if any(part in SKIP_DIRS for part in rel.parts) or path.resolve() in skip:
            continue
        name = mask(str(rel), allowed)
        for term, pat in patterns:
            if pat.search(name):
                hits.append((str(rel), 0, term, "(path)"))
        if not path.is_file():
            continue
        if is_binary(path):
            unscanned.append(str(rel))
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for no, line in enumerate(text.splitlines(), 1):
            clean = mask(line, allowed)
            for term, pat in patterns:
                if pat.search(clean):
                    hits.append((str(rel), no, term, line.strip()[:120]))
    return hits, unscanned


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("folder")
    ap.add_argument("blacklist")
    ap.add_argument("--allow", help="file of exact strings that may appear")
    args = ap.parse_args(argv)
    if not Path(args.folder).is_dir():
        print(f"not a folder: {args.folder}", file=sys.stderr)
        return 2
    terms = read_lines(args.blacklist)
    allowed = read_lines(args.allow) if args.allow else []
    skip = [args.blacklist] + ([args.allow] if args.allow else [])
    hits, unscanned = scan(args.folder, terms, allowed, skip)
    for rel, no, term, line in hits:
        print(f"{rel}:{no}: [{term}] {line}")
    for rel in unscanned:
        print(f"{rel}: unscanned binary file, review it by hand")
    print(f"{len(hits)} hits, {len(unscanned)} unscanned, {len(terms)} terms")
    return 1 if hits or unscanned else 0


if __name__ == "__main__":
    sys.exit(main())
