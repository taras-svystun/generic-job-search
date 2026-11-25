#!/usr/bin/env python3
"""State tool for the direct-outreach track.

The /find-companies and /outreach skills make the judgement calls;
every deterministic write goes through this module so it is validated and
tested. Specs never hand-edit outreach_tracker.csv or the `outreach` key of a
company_research/<slug>.json file.

Stdlib only. Subcommands:

  migrate                  append the new columns, derive status from legacy ones
  validate [--previous F]  check vocabularies, dates, duplicates, transitions
  slugify NAME             print the canonical company slug
  excluded                 print every company slug that must not be proposed
  company set SLUG --stage S [--segment warm|cold] [--reason R]
                           [--scores-json JSON] [--name NAME]
  add --company C --person P --contact-role decision_maker|peer [--role-title T]
      [--channel email|linkedin] [--email E --email-source public|pattern_seen|guess]
      [--linkedin-url U] [--hook-tier N] [--notes N]
                           append a `queued` person (refuses duplicates and
                           anyone who ever declined)
  hook COMPANY --tier N [--url URL]
                           record the hook tier/URL on the company's open rows
  check-message FILE --max-words N
                           fail on length, short links, placeholders, a missing
                           role ask, or a denylisted name

Common option: --root DIR (default: the repo root) - every path resolves
against it, which is how the tests run on temp directories.

Per-company working files live in outreach/<slug>/ (see OUTREACH_FILES).

Exit codes: 0 ok, 1 validation failed, 2 bad input (unreadable file, refused
write, usage error).
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TRACKER = "outreach_tracker.csv"
JOB_TRACKER = "job_search_tracker.csv"
RESEARCH_DIR = "company_research"
PREFERENCES = "company_research/_preferences.md"
OUTREACH_DIR = "outreach"
OUTREACH_FILES = ("teardown.md", "test-script.md", "email.md", "linkedin.md",
                  "brief-tier3-4.md")

# Frozen after `migrate`: read once to derive status, never written again.
LEGACY_COLUMNS = ["date", "company", "company_size", "person_name", "person_role",
                  "segment", "hook_type", "connect_sent", "connect_accepted",
                  "message_sent", "reply", "followup_date", "outcome",
                  "linkedin_url", "job_url", "notes"]
NEW_COLUMNS = ["contact_role", "channel", "email", "email_source", "hook_tier",
               "hook_url", "status", "status_date", "followups_sent",
               "next_action_date"]
DATE_COLUMNS = ["date", "connect_sent", "connect_accepted", "message_sent",
                "status_date", "next_action_date"]

CHANNELS = {"email", "linkedin"}
CONTACT_ROLES = {"decision_maker", "peer"}
EMAIL_SOURCES = {"public", "pattern_seen", "guess"}

# Status machine: one table shared by every subcommand.
FINAL = {"converted", "declined", "no_reply", "dropped"}
CLOSING = {"declined", "no_reply", "dropped"}
_PATHS = {
    "email": ["queued", "messaged", "replied", "call", "converted"],
    "linkedin": ["queued", "connect_sent", "connected", "messaged", "replied",
                 "call", "converted"],
}
SENT = {"connect_sent", "connected", "messaged"}  # people reply to bare connects


def _transitions():
    table = {}
    for channel, path in _PATHS.items():
        moves = {s: set() for s in path}
        for a, b in zip(path, path[1:]):
            moves[a].add(b)
        for s in path:
            if s in SENT:
                moves[s].add("replied")
            if s not in FINAL:
                moves[s] |= CLOSING
        for s in CLOSING:
            moves[s] = set()
        table[channel] = moves
    return table


TRANSITIONS = _transitions()
STATUSES = set().union(*(set(m) for m in TRANSITIONS.values()))

COMPANY_STAGES = {"candidate", "shortlisted", "vetoed", "in_outreach", "closed"}
SEGMENTS = {"warm", "cold"}
SCORE_CRITERIA = ["fit", "hiring_signal", "hook_ability", "work_mode", "language",
                  "people_reachable", "long_term"]

LEGAL_SUFFIXES = {"inc", "ltd", "llc", "plc", "gmbh", "ag", "bv", "nv", "sa", "sas",
                  "srl", "ab", "oy", "pty"}

PREFERENCES_TEMPLATE = (
    "# Company preferences (outreach track)\n\n"
    "## Veto log\n\n"
    "<!-- Written by tools/outreach.py `company set --stage vetoed`. -->\n\n"
    "## Taste rules\n\n"
    "<!-- Prose rules distilled from the veto log; Claude updates these in chat. -->\n"
)


class OutreachError(Exception):
    """Bad input that the caller must fix; never guessed around."""


def today():
    return dt.date.today().isoformat()


# ── slugs ────────────────────────────────────────────────────────────────────

def slugify(name):
    """Canonical company slug: ASCII-folded, lowercase, legal suffix dropped."""
    folded = unicodedata.normalize("NFKD", name)
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = folded.encode("ascii", "ignore").decode().lower()
    tokens = [t for t in re.split(r"[^a-z0-9]+", folded.replace(".", "")) if t]
    while len(tokens) > 1 and tokens[-1] in LEGAL_SUFFIXES:
        tokens.pop()
    return "-".join(tokens)


# ── safe file I/O ────────────────────────────────────────────────────────────

def _atomic_write(path, text):
    """Temp file + os.replace, leaving the previous version at <path>.bak."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        shutil.copy2(path, str(path) + ".bak")
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def read_csv(path):
    """-> (header, rows, line_terminator). BOM-tolerant; refuses `;` files."""
    raw = Path(path).read_bytes()
    text = raw.decode("utf-8-sig")
    if not text.strip():
        raise OutreachError(f"{path}: file is empty (expected at least a header)")
    first = text.splitlines()[0]
    if ";" in first and "," not in first:
        raise OutreachError(
            f"{path}: header is ';'-delimited (likely re-saved by Excel). "
            "Re-export as comma-separated UTF-8 CSV; refusing to guess.")
    terminator = "\r\n" if "\r\n" in text else "\n"
    reader = csv.DictReader(io.StringIO(text, newline=""))
    header = list(reader.fieldnames or [])
    if "company" not in header:
        raise OutreachError(f"{path}: no 'company' column in header {header}")
    rows = []
    for n, row in enumerate(reader, start=2):
        if None in row:
            raise OutreachError(f"{path}: row {n} has more fields than the header")
        rows.append({k: (v if v is not None else "") for k, v in row.items()})
    return header, rows, terminator


def write_csv(path, header, rows, terminator="\n"):
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=header, lineterminator=terminator,
                       extrasaction="raise")
    w.writeheader()
    for row in rows:
        w.writerow({k: row.get(k, "") for k in header})
    _atomic_write(path, buf.getvalue())


# ── tracker ──────────────────────────────────────────────────────────────────

def person_key(row):
    """(company slug, person) identity used for duplicate and transition checks."""
    who = (row.get("person_name") or row.get("email") or row.get("linkedin_url")
           or row.get("person_role") or "").strip().lower()
    return slugify(row.get("company", "")), who


def _derive(row):
    """Fill new columns of one legacy row; never touches a non-empty value."""
    out = {}
    if not row.get("channel"):
        if row.get("connect_sent") or row.get("connect_accepted"):
            out["channel"] = "linkedin"
    if not row.get("contact_role"):
        seg = (row.get("segment") or "").lower()
        if seg in {"hiring-manager", "decision-maker", "founder", "cto"}:
            out["contact_role"] = "decision_maker"
        elif seg == "peer":
            out["contact_role"] = "peer"
    if not row.get("status"):
        if row.get("message_sent"):
            out["status"], out["status_date"] = "messaged", row["message_sent"]
        elif row.get("connect_accepted"):
            out["status"], out["status_date"] = "connected", row["connect_accepted"]
        elif row.get("connect_sent"):
            out["status"], out["status_date"] = "connect_sent", row["connect_sent"]
        else:
            out["status"] = "queued"
    if not row.get("followups_sent") and (row.get("status") or out.get("status")) != "queued":
        out["followups_sent"] = "0"
    return out


def migrate(root):
    """Append NEW_COLUMNS and derive status. Idempotent. Returns change count."""
    path = Path(root) / TRACKER
    if not path.exists():
        write_csv(path, LEGACY_COLUMNS + NEW_COLUMNS, [])
        return 0
    header, rows, term = read_csv(path)
    new_header = header + [c for c in NEW_COLUMNS if c not in header]
    changed = 0
    for row in rows:
        for c in NEW_COLUMNS:
            row.setdefault(c, "")
        derived = _derive(row)
        if derived:
            row.update(derived)
            changed += 1
    if changed or new_header != header:
        write_csv(path, new_header, rows, term)
    return changed


def _is_date(value):
    try:
        dt.date.fromisoformat(value)
        return re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is not None
    except ValueError:
        return False


def is_legal(channel, old, new):
    return old == new or new in TRANSITIONS.get(channel, {}).get(old, set())


def validate_rows(rows, previous=None):
    """-> list of error strings. `previous` = rows of the last written version."""
    errors, seen = [], {}
    for n, row in enumerate(rows, start=2):
        where = f"row {n} ({row.get('company', '')}/{person_key(row)[1] or '?'})"
        channel, status = row.get("channel", ""), row.get("status", "")
        if channel not in CHANNELS:
            errors.append(f"{where}: channel {channel!r} not in {sorted(CHANNELS)}")
        if row.get("contact_role", "") not in CONTACT_ROLES:
            errors.append(f"{where}: contact_role {row.get('contact_role', '')!r} "
                          f"not in {sorted(CONTACT_ROLES)}")
        if status not in STATUSES:
            errors.append(f"{where}: status {status!r} not in {sorted(STATUSES)}")
        elif channel in CHANNELS and status not in TRANSITIONS[channel]:
            errors.append(f"{where}: status {status!r} does not exist on channel {channel!r}")
        for col in DATE_COLUMNS:
            if row.get(col) and not _is_date(row[col]):
                errors.append(f"{where}: {col} {row[col]!r} is not an ISO date (YYYY-MM-DD)")
        if status and status != "queued" and not row.get("status_date"):
            errors.append(f"{where}: status_date is required once status leaves 'queued'")
        if row.get("hook_tier") and row["hook_tier"] not in {"1", "2", "3", "4"}:
            errors.append(f"{where}: hook_tier {row['hook_tier']!r} must be 1-4 or empty")
        if row.get("email_source") and row["email_source"] not in EMAIL_SOURCES:
            errors.append(f"{where}: email_source {row['email_source']!r} "
                          f"not in {sorted(EMAIL_SOURCES)}")
        if row.get("followups_sent") and not row["followups_sent"].isdigit():
            errors.append(f"{where}: followups_sent {row['followups_sent']!r} "
                          "must be a whole number")
        key = person_key(row)
        if key in seen:
            errors.append(f"{where}: duplicate person, same as row {seen[key]}")
        seen.setdefault(key, n)
    for old in previous or []:
        new = next((r for r in rows if person_key(r) == person_key(old)), None)
        if new is None:
            continue
        a, b = old.get("status", ""), new.get("status", "")
        channel = new.get("channel", "")
        if a in STATUSES and b in STATUSES and not is_legal(channel, a, b):
            if a in FINAL and "reopened" in new.get("notes", "").lower():
                continue  # manual re-open, documented in notes
            errors.append(
                f"{new.get('company', '')}/{person_key(new)[1]}: illegal transition "
                f"{a} -> {b} on {channel or '?'}"
                + (" (re-opening a final state needs 'reopened' in notes)" if a in FINAL else ""))
    return errors


def validate(root, previous=None):
    path = Path(root) / TRACKER
    if not path.exists():
        migrate(root)
    header, rows, _ = read_csv(path)
    missing = [c for c in NEW_COLUMNS if c not in header]
    if missing:
        return [f"{path}: missing columns {missing} - run `migrate` first"]
    prev_path = Path(previous) if previous else Path(str(path) + ".bak")
    prev_rows = read_csv(prev_path)[1] if prev_path.exists() else None
    return validate_rows(rows, prev_rows)


PERSON_DEFAULT_CHANNEL = {"decision_maker": "email", "peer": "linkedin"}
OPEN_COMPANY_STAGES = {"shortlisted", "in_outreach"}


def _same_human(row, name, email, linkedin_url):
    """Identity across companies: any one matching identifier is the same person."""
    pairs = ((row.get("person_name", ""), name), (row.get("email", ""), email),
             (row.get("linkedin_url", ""), linkedin_url))
    return any(a.strip() and b and a.strip().lower() == b.strip().lower() for a, b in pairs)


def add(root, company, person, contact_role, person_role="", channel=None, email="",
        email_source="", linkedin_url="", hook_tier="", notes="", date=None):
    """Append one `queued` person row. Refuses duplicates and do-not-contact people."""
    date = date or today()
    if not person.strip():
        raise OutreachError("person name is required")
    if contact_role not in CONTACT_ROLES:
        raise OutreachError(f"contact_role {contact_role!r} not in {sorted(CONTACT_ROLES)}")
    channel = channel or PERSON_DEFAULT_CHANNEL[contact_role]
    if channel == "email" and not email:
        raise OutreachError("channel email needs --email; with no address, use --channel linkedin")
    if bool(email) != bool(email_source):
        raise OutreachError("--email and --email-source go together "
                            f"(sources: {sorted(EMAIL_SOURCES)})")
    if email and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise OutreachError(f"{email!r} does not look like an email address")
    if linkedin_url and "linkedin.com/" not in linkedin_url:
        raise OutreachError(f"{linkedin_url!r} is not a linkedin.com URL")

    slug = slugify(company)
    research = Path(root) / RESEARCH_DIR / f"{slug}.json"
    stage = None
    if research.exists():
        stage = (json.loads(research.read_text(encoding="utf-8-sig")).get("outreach") or {}).get("stage")
    if stage not in OPEN_COMPANY_STAGES:
        raise OutreachError(f"{slug}: company stage is {stage or 'missing'}; add people only to "
                            f"{sorted(OPEN_COMPANY_STAGES)} companies (run /find-companies first)")

    path = Path(root) / TRACKER
    if not path.exists():
        migrate(root)
    header, rows, term = read_csv(path)
    missing = [c for c in NEW_COLUMNS if c not in header]
    if missing:
        raise OutreachError(f"{path}: missing columns {missing} - run `migrate` first")
    for r in rows:
        if r.get("status") == "declined" and _same_human(r, person, email, linkedin_url):
            raise OutreachError(f"{person}: declined on {r.get('status_date') or '?'} "
                                f"({r.get('company')}) - do not contact again")
    new = {c: "" for c in header}
    new.update(date=date, company=company, person_name=person.strip(), person_role=person_role,
               linkedin_url=linkedin_url, notes=notes, contact_role=contact_role,
               channel=channel, email=email, email_source=email_source,
               hook_tier=str(hook_tier or ""), status="queued")
    key = person_key(new)
    if any(person_key(r) == key for r in rows):
        raise OutreachError(f"{company}/{person}: already in the tracker")
    errors = validate_rows([new])
    if errors:
        raise OutreachError("; ".join(errors))
    write_csv(path, header, rows + [new], term)
    return new


def set_hook(root, company, tier, url=""):
    """Record the hook on every open row of one company. Returns rows changed."""
    if str(tier) not in {"1", "2", "3", "4"}:
        raise OutreachError(f"hook tier {tier!r} must be 1-4")
    if url and not re.match(r"https?://", url):
        raise OutreachError(f"hook url {url!r} must be a full http(s) URL")
    if url and _shortener(url):
        raise OutreachError(f"hook url {url!r} is a shortened link; use the full URL")
    path = Path(root) / TRACKER
    if not path.exists():
        migrate(root)
    header, rows, term = read_csv(path)
    slug, changed = slugify(company), 0
    for r in rows:
        if slugify(r.get("company", "")) == slug and r.get("status") not in FINAL:
            r["hook_tier"], r["hook_url"] = str(tier), url or r.get("hook_url", "")
            changed += 1
    if not changed:
        raise OutreachError(f"{slug}: no open rows in the tracker")
    write_csv(path, header, rows, term)
    return changed


# ── message checks ───────────────────────────────────────────────────────────

DENYLIST = "outreach/_denylist.txt"
SHORTENERS = {"bit.ly", "t.co", "lnkd.in", "tinyurl.com", "goo.gl", "ow.ly", "buff.ly",
              "rebrand.ly", "is.gd", "cutt.ly", "shorturl.at", "rb.gy", "t.ly", "tiny.cc",
              "s.id", "bl.ink"}
# Any one of these reads as "I am asking for a job with you". "hiring" alone is
# not on the list: "I saw you're hiring" observes, it does not ask.
ROLE_ASK = re.compile(r"\brole\b|\bposition\b|\bjoin(ing)? (you|your team|the team)\b"
                      r"|\bjoin(ing)? (?-i:[A-Z])|\bwork with you\b|\bpart of your team\b",
                      re.I)
PLACEHOLDER = re.compile(r"\[[A-Za-z][^\]\n]*\](?!\()|\{\{|\bTODO\b|\bTBD\b|\bXXX\b|<[A-Z_ ]{3,}>")
URL = re.compile(r"https?://[^\s)>\]]+")


def _shortener(url):
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    host = host[4:] if host.startswith("www.") else host
    return host in SHORTENERS


def _message_body(text):
    """Text that counts toward the word limit: no comments, Subject:, or signature."""
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    lines = []
    for line in text.splitlines():
        if line.strip() in {"--", "-- "}:
            break
        if re.match(r"\s*subject\s*:", line, re.I):
            continue
        lines.append(line)
    return "\n".join(lines)


def count_words(text):
    body = URL.sub(" URL ", _message_body(text))
    return len([t for t in body.split() if re.search(r"[\w]", t)])


def check_message(text, max_words, denylist=None):
    """-> (errors, warnings). `denylist` is a list of names, or None if the file is absent."""
    errors, warnings = [], []
    full = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    n = count_words(text)
    if n > max_words:
        errors.append(f"{n} words in the body, limit {max_words}")
    for url in URL.findall(full):
        if _shortener(url):
            errors.append(f"shortened URL {url}: use the full link")
    for m in PLACEHOLDER.finditer(full):
        errors.append(f"leftover placeholder {m.group(0)!r}")
    if not ROLE_ASK.search(_message_body(text)):
        errors.append("no role ask: say plainly that you are looking for a role with them")
    if denylist is None:
        warnings.append(f"{DENYLIST} not found: protected names (for example NDA clients) not checked")
    else:
        for name in denylist:
            if re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", full, re.I):
                errors.append(f"denylisted name {name!r} (protected names are never named)")
    return errors, warnings


def load_denylist(root):
    path = Path(root) / DENYLIST
    if not path.exists():
        return None
    return [l.strip() for l in path.read_text(encoding="utf-8-sig").splitlines()
            if l.strip() and not l.lstrip().startswith("#")]


# ── companies ────────────────────────────────────────────────────────────────

def _company_slugs_from_csv(path):
    if not Path(path).exists():
        return set()
    _, rows, _ = read_csv(path)
    return {slugify(r["company"]) for r in rows if r.get("company", "").strip()}


def excluded(root):
    root = Path(root)
    slugs = _company_slugs_from_csv(root / JOB_TRACKER)
    slugs |= _company_slugs_from_csv(root / TRACKER)
    for f in sorted((root / RESEARCH_DIR).glob("*.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8-sig"))
        except (ValueError, OSError) as e:
            raise OutreachError(f"{f}: unreadable JSON ({e})")
        stage = (data.get("outreach") or {}).get("stage") if isinstance(data, dict) else None
        if stage in {"vetoed", "closed"}:
            slugs.add(f.stem)
    return sorted(slugs)


def _append_veto(root, slug, reason, date):
    path = Path(root) / PREFERENCES
    text = path.read_text(encoding="utf-8-sig") if path.exists() else PREFERENCES_TEMPLATE
    line = f"- {date} — {slug} — {reason.strip()}\n"
    marker = "\n## Taste rules"
    if "## Veto log" not in text:
        text = text.rstrip("\n") + "\n\n## Veto log\n\n"
    i = text.find(marker, text.index("## Veto log"))
    if i == -1:
        text = text.rstrip("\n") + "\n" + line
    else:
        head = text[:i].rstrip("\n") + "\n"
        text = head + line + "\n" + text[i + 1:]
    _atomic_write(path, text)


def company_set(root, slug, stage, segment=None, reason=None, scores=None, name=None,
                date=None):
    """Read-modify-write of only the `outreach` key. Returns the new block."""
    date = date or today()
    if slug != slugify(slug):
        raise OutreachError(f"{slug!r} is not a slug; use {slugify(slug)!r}")
    if stage not in COMPANY_STAGES:
        raise OutreachError(f"stage {stage!r} not in {sorted(COMPANY_STAGES)}")
    if stage == "vetoed" and not (reason or "").strip():
        raise OutreachError("--stage vetoed requires --reason")
    if segment is not None and segment not in SEGMENTS:
        raise OutreachError(f"segment {segment!r} not in {sorted(SEGMENTS)}")
    if scores is not None:
        if not isinstance(scores, dict):
            raise OutreachError("scores must be a JSON object")
        unknown = set(scores) - set(SCORE_CRITERIA)
        if unknown:
            raise OutreachError(f"unknown score criteria {sorted(unknown)}; "
                                f"expected {SCORE_CRITERIA}")
        for k, v in scores.items():
            if not (isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 5):
                raise OutreachError(f"score {k}={v!r} must be an integer 1-5")
    path = Path(root) / RESEARCH_DIR / f"{slug}.json"
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8-sig"))
        except ValueError as e:
            raise OutreachError(f"{path}: unreadable JSON ({e}); refusing to overwrite")
        if not isinstance(data, dict):
            raise OutreachError(f"{path}: top level is not an object; refusing to overwrite")
    else:
        data = {"company": name or slug}
    block = dict(data.get("outreach") or {})
    block["stage"], block["stage_date"] = stage, date
    if segment is not None:
        block["segment"] = segment
    if reason:
        block["reason"] = reason.strip()
    if scores is not None:
        block["scores"] = dict(scores)
        block["total"] = sum(scores.values())
    history = list(block.get("history") or [])
    history.append({k: v for k, v in
                    {"date": date, "stage": stage, "reason": (reason or "").strip()}.items() if v})
    block["history"] = history
    data["outreach"] = block
    _atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    if stage == "vetoed":
        _append_veto(root, slug, reason, date)
    return block


# ── CLI ──────────────────────────────────────────────────────────────────────

def main(argv=None):
    p = argparse.ArgumentParser(prog="outreach.py", description=__doc__.split("\n")[0])
    p.add_argument("--root", default=str(REPO_ROOT))
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("migrate")
    v = sub.add_parser("validate")
    v.add_argument("--previous", help="earlier version to check transitions against "
                                      "(default: outreach_tracker.csv.bak)")
    s = sub.add_parser("slugify")
    s.add_argument("name")
    sub.add_parser("excluded")
    a = sub.add_parser("add")
    a.add_argument("--company", required=True)
    a.add_argument("--person", required=True)
    a.add_argument("--contact-role", required=True, choices=sorted(CONTACT_ROLES))
    a.add_argument("--role-title", default="")
    a.add_argument("--channel", choices=sorted(CHANNELS))
    a.add_argument("--email", default="")
    a.add_argument("--email-source", default="", choices=[""] + sorted(EMAIL_SOURCES))
    a.add_argument("--linkedin-url", default="")
    a.add_argument("--hook-tier", default="", choices=["", "1", "2", "3", "4"])
    a.add_argument("--notes", default="")
    h = sub.add_parser("hook")
    h.add_argument("company")
    h.add_argument("--tier", required=True, choices=["1", "2", "3", "4"])
    h.add_argument("--url", default="")
    m = sub.add_parser("check-message")
    m.add_argument("file")
    m.add_argument("--max-words", type=int, required=True)
    c = sub.add_parser("company")
    csub = c.add_subparsers(dest="action", required=True)
    cs = csub.add_parser("set")
    cs.add_argument("slug")
    cs.add_argument("--stage", required=True, choices=sorted(COMPANY_STAGES))
    cs.add_argument("--segment", choices=sorted(SEGMENTS))
    cs.add_argument("--reason")
    cs.add_argument("--scores-json")
    cs.add_argument("--name", help="display name when the JSON file is created")
    args = p.parse_args(argv)

    try:
        if args.cmd == "migrate":
            n = migrate(args.root)
            print(f"migrate: {n} row(s) updated")
            errors = validate(args.root)
        elif args.cmd == "validate":
            errors = validate(args.root, args.previous)
        elif args.cmd == "slugify":
            print(slugify(args.name))
            return 0
        elif args.cmd == "excluded":
            print("\n".join(excluded(args.root)))
            return 0
        elif args.cmd == "hook":
            n = set_hook(args.root, args.company, args.tier, args.url)
            print(f"hook: tier {args.tier} recorded on {n} row(s)")
            return 0
        elif args.cmd == "check-message":
            text = Path(args.file).read_text(encoding="utf-8-sig")
            errs, warns = check_message(text, args.max_words, load_denylist(args.root))
            for w in warns:
                print(f"warning: {w}", file=sys.stderr)
            for e in errs:
                print(f"fail: {e}", file=sys.stderr)
            if not errs:
                print(f"check-message: OK ({count_words(text)}/{args.max_words} words)")
            return 1 if errs else 0
        elif args.cmd == "add":
            row = add(args.root, args.company, args.person, args.contact_role,
                      args.role_title, args.channel, args.email, args.email_source,
                      args.linkedin_url, args.hook_tier, args.notes)
            print(f"added: {row['company']} / {row['person_name']} "
                  f"({row['contact_role']}, {row['channel']}, queued)")
            return 0
        else:
            scores = json.loads(args.scores_json) if args.scores_json else None
            block = company_set(args.root, args.slug, args.stage, args.segment,
                                args.reason, scores, args.name)
            print(json.dumps(block, ensure_ascii=False))
            return 0
    except (OutreachError, OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    for e in errors:
        print(f"invalid: {e}", file=sys.stderr)
    if not errors:
        print("validate: OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
