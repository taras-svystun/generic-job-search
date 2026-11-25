"""Build reports/pipeline.html from the tracker, the outcome files and highlights.md.

No tokens: run `python3 tools/stats.py` after any tracker or outcome change.

Sources, each with one job:
- job_search_tracker.csv: one row per application; `status` is the only status.
- documents/applications/*/outcome.md: the stage checkboxes, `Note:` and `Next:` of one
  application. Matched to its row by the header `# Outcome: <Company> — <Role>`, not by
  folder name (a folder made by hand may not follow the naming rule).
- reports/highlights.md: hand-written banner and live-process cards.
"""
from __future__ import annotations

import csv
import html
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

STAGES = (
    "call booked",
    "call held",
    "technical held",
    "past technical",
    "rejected at CV",
    "rejected after HR",
)
# Group order on the page, with the row heading of each.
GROUPS = {
    "live": "In process",
    "won": "Offer stage reached",
    "withdrawn": "Withdrawn",
    "rej": "Rejected",
    "silent": "No reply yet",
}
HIGHLIGHT_SECTIONS = {"Banner": 2, "Live processes": 3, "Other tracks": 3}
ANALYSIS_HINT = "Ask your agent to analyse these numbers."


class FormatError(ValueError):
    """A source file breaks its format; the message names the file and the line."""


@dataclass
class Outcome:
    company: str
    role: str
    stages: dict = field(default_factory=dict)  # label -> detail ("" when no detail)
    note: str = ""
    next: str = ""


@dataclass
class App:
    row: dict
    outcome: Outcome

    def has(self, stage: str) -> bool:
        return stage in self.outcome.stages

    def detail(self, stage: str) -> str:
        return self.outcome.stages.get(stage, "")


def key(company: str, role: str) -> tuple:
    return (" ".join(company.split()).casefold(), " ".join(role.split()).casefold())


def parse_outcome(text: str, source: str = "outcome.md") -> Outcome:
    """Read the header and the `## Stages` block of one outcome.md."""
    lines = text.splitlines()
    head = re.match(r"# Outcome: (.+?) — (.+)$", lines[0].strip()) if lines else None
    if not head:
        raise FormatError(f"{source}: first line must be '# Outcome: <Company> — <Role>'")
    out = Outcome(head.group(1).strip(), head.group(2).strip())

    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == "## Stages")
    except StopIteration:
        raise FormatError(f"{source}: no '## Stages' section") from None
    seen = set()
    for n, ln in enumerate(lines[start + 1:], start + 2):
        ln = ln.strip()
        if ln.startswith("#"):
            break
        box = re.match(r"- \[([ xX])\] ([^:]+?)(?::\s*(.*))?$", ln)
        if box:
            label = box.group(2).strip()
            if label not in STAGES:
                raise FormatError(f"{source}:{n}: unknown stage {label!r}")
            seen.add(label)
            if box.group(1) != " ":
                out.stages[label] = (box.group(3) or "").strip()
        elif ln.startswith("Note:"):
            out.note = ln[5:].strip()
        elif ln.startswith("Next:"):
            out.next = ln[5:].strip()
        elif ln:
            raise FormatError(f"{source}:{n}: unexpected line in Stages: {ln!r}")
    missing = [s for s in STAGES if s not in seen]
    if missing:
        raise FormatError(f"{source}: Stages lacks {', '.join(missing)}")
    return out


def parse_highlights(text: str, source: str = "highlights.md") -> dict:
    """Sections of `- a | b | c` items. Other non-heading lines are comments."""
    out = {name: [] for name in HIGHLIGHT_SECTIONS}
    current = None
    for n, ln in enumerate(text.splitlines(), 1):
        if ln.startswith("## "):
            current = ln[3:].strip()
            if current not in HIGHLIGHT_SECTIONS:
                raise FormatError(f"{source}:{n}: unknown section {current!r}")
        elif ln.startswith("- ") and current:
            parts = [p.strip() for p in ln[2:].split(" | ")]
            if len(parts) != HIGHLIGHT_SECTIONS[current]:
                raise FormatError(
                    f"{source}:{n}: {current} items need "
                    f"{HIGHLIGHT_SECTIONS[current]} fields split by ' | '"
                )
            out[current].append(parts)
    return out


def load(csv_path: Path, applications: Path, warn=None) -> list:
    """Join tracker rows with their outcome files. Drafted rows were never sent: skipped."""
    warn = warn or (lambda msg: print(f"warning: {msg}", file=sys.stderr))
    csv_path = Path(csv_path)
    if not csv_path.exists():  # fresh clone: the tracker is git-ignored and made by /apply
        rows = []
    else:
        with open(csv_path, encoding="utf-8", newline="") as f:
            rows = [r for r in csv.DictReader(f) if status(r) != "drafted"]
    outcomes = {}
    for path in sorted(applications.glob("*/outcome.md")):
        o = parse_outcome(path.read_text(encoding="utf-8"), str(path))
        k = key(o.company, o.role)
        if k in outcomes:
            raise FormatError(f"{path}: a second outcome file for {o.company} — {o.role}")
        outcomes[k] = o
    apps = []
    for r in rows:
        o = outcomes.pop(key(r["company"], r["role"]), None)
        apps.append(App(r, o or Outcome(r["company"], r["role"])))
    for o in outcomes.values():
        warn(f"outcome file with no tracker row: {o.company} — {o.role}")
    for a in apps:
        rejected_box = a.has("rejected at CV") or a.has("rejected after HR")
        if rejected_box and status(a.row) != "rejected":
            warn(f"{a.row['company']} — {a.row['role']}: rejected box, tracker says "
                 f"{a.row['status']!r}")
    return apps


def status(row: dict) -> str:
    """Tracker status, legacy space spellings read as the underscore forms."""
    return row.get("status", "").strip().lower().replace(" ", "_")


def group(a: App) -> str:
    s = status(a.row)
    if s == "rejected":
        return "rej"
    if s in ("hired", "offer_declined") or (s == "withdrawn" and a.has("past technical")):
        return "won"
    if s == "withdrawn":
        return "withdrawn"
    if s in ("interview", "offer"):
        return "live"
    if any(a.has(x) for x in ("call booked", "call held", "technical held")):
        return "live"
    # applied, no_response and any unknown value: shown, never dropped.
    return "silent"


def counts(apps: list) -> dict:
    g = [group(a) for a in apps]
    rej = [a for a in apps if group(a) == "rej"]
    past = [a for a in apps if a.has("past technical")]
    return {
        "applied": len(apps),
        **{name: g.count(name) for name in GROUPS},
        "rej-cv": sum(a.has("rejected at CV") for a in rej),
        "rej-hr": sum(a.has("rejected after HR") for a in rej),
        "rej-tech": sum(a.has("technical held") and not a.has("past technical") for a in rej),
        "call-held": sum(a.has("call held") for a in apps),
        "call-booked": sum(a.has("call booked") and not a.has("call held") for a in apps),
        "tech": sum(a.has("technical held") for a in apps),
        "past": len(past),
        "past-names": ", ".join(a.row["company"] for a in past),
    }


# ---------------------------------------------------------------- rendering

def e(text: str) -> str:
    return html.escape(text, quote=True)


def day(iso: str) -> str:
    try:
        d = date.fromisoformat(iso)
    except ValueError:
        return iso
    return f"{d.day} {d:%b}"


def pill(cls: str, text: str) -> str:
    return f'<span class="pill {cls}">{e(text)}</span>'


NONE = '<span class="no">·</span>'


def cells(a: App, grp: str) -> list:
    def joined(*parts):
        return " ".join(p for p in parts if p)

    if a.has("rejected at CV"):
        cv = pill("p-bad", "✕")
    elif grp == "silent":
        cv = pill("p-idle", "silent")
    else:
        cv = pill("p-ok", "✓")

    if a.has("rejected after HR"):
        call = pill("p-bad", "✕ after HR")
    elif a.has("call held"):
        call = pill("p-ok", joined("✓", a.detail("call held")))
    elif a.has("call booked"):
        call = pill("p-acc", joined("booked", a.detail("call booked")))
    else:
        call = NONE

    if a.has("past technical"):
        tech = pill("p-ok", joined("✓", a.detail("technical held")))
    elif a.has("technical held") and grp == "rej":
        tech = pill("p-bad", "✕")
    elif a.has("technical held"):
        tech = pill("p-wait", "waiting")
    else:
        tech = NONE

    nxt = a.outcome.next
    nxt = pill("p-ok" if nxt.startswith("✓") else "p-acc", nxt) if nxt else NONE
    return [cv, call, tech, nxt]


def render_table(apps: list) -> str:
    out = []
    for name, title in GROUPS.items():
        members = sorted((a for a in apps if group(a) == name), key=lambda a: a.row["date"])
        if not members:
            continue
        win = " win" if name == "won" else ""
        out.append(f'      <tr class="grp{win}"><td colspan="8">{e(title)} · {len(members)}</td></tr>')
        for a in members:
            tds = "".join(f'<td class="c">{c}</td>' for c in cells(a, name))
            row_cls = ' class="win"' if name == "won" else ""
            out.append(
                f'      <tr{row_cls}><td class="co">{e(a.row["company"])}</td>'
                f'<td class="role">{e(a.row["role"])}</td>'
                f'<td class="mono">{e(day(a.row["date"]))}</td>{tds}'
                f'<td class="note">{e(a.outcome.note)}</td></tr>'
            )
    return "\n".join(out)


def render_highlights(h: dict) -> str:
    out = []
    for title, text in h["Banner"]:
        out.append(
            '<section aria-label="Win">\n'
            f'  <div class="cheer"><b>{e(title)}</b><span>{e(text)}</span></div>\n'
            "</section>"
        )

    def card(when, what, how):
        return (f'<div class="ev"><div class="when">{e(when)}</div>'
                f'<div class="what">{e(what)}</div><div class="how">{e(how)}</div></div>')

    if h["Live processes"] or h["Other tracks"]:
        body = ["<section>", "  <h2>Live processes, in date order</h2>"]
        if h["Live processes"]:
            body.append('  <div class="week">')
            body += ["    " + card(*c) for c in h["Live processes"]]
            body.append("  </div>")
        body += ["  " + card(*c) for c in h["Other tracks"]]
        body.append("</section>")
        out.append("\n".join(body))
    return "\n\n".join(out)


def silent_line(apps: list, today: date) -> str:
    ages = []
    for a in apps:
        if group(a) == "silent":
            try:
                ages.append((today - date.fromisoformat(a.row["date"])).days // 7)
            except ValueError:
                pass
    n = sum(group(a) == "silent" for a in apps)
    span = f" They are {min(ages)} to {max(ages)} weeks old." if ages else ""
    return f"{n} applications have had no reply at all.{span}"


def render(apps: list, highlights: dict, today: date) -> str:
    c = counts(apps)
    dates = sorted(a.row["date"] for a in apps if a.row["date"])
    span = f" from {day(dates[0])} to {day(dates[-1])}" if dates else ""
    past = f'past technical: {e(c["past-names"])}' if c["past-names"] else "past technical"
    return f"""<title>Job Pipeline</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Instrument+Sans:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{CSS}</style>

<div class="wrap">
<header>
  <div class="eyebrow">Snapshot · {today.day} {today:%B %Y}</div>
  <h1>Job pipeline</h1>
  <p class="sub">{c["applied"]} applications{span}. Source: <span class="mono">job_search_tracker.csv</span>, the <span class="mono">outcome.md</span> files and <span class="mono">reports/highlights.md</span>.</p>
</header>

<section aria-label="Funnel">
  <div class="funnel">
    <div class="step acc"><b>{c["applied"]}</b><span>applied</span></div>
    <div class="step bad"><b>{c["rej"]}</b><span>rejected ({c["rej-cv"]} at CV, {c["rej-hr"]} after HR, {c["rej-tech"]} after technical)</span></div>
    <div class="step ok"><b>{c["live"]}</b><span>in process now</span></div>
    <div class="step"><b>{c["call-held"]} + {c["call-booked"]}</b><span>first call held + booked</span></div>
    <div class="step"><b>{c["tech"]}</b><span>technical interview held</span></div>
    <div class="step ok"><b>{c["past"]}</b><span>{past}</span></div>
  </div>
  <p class="sub">{e(silent_line(apps, today))}</p>
</section>

{render_highlights(highlights)}

<section>
  <h2>Every application by stage</h2>
  <div class="legend">
    <span><span class="pill p-ok">✓</span> stage passed</span>
    <span><span class="pill p-acc">booked</span> invited, not yet held</span>
    <span><span class="pill p-wait">waiting</span> done, no answer yet</span>
    <span><span class="pill p-bad">✕</span> rejected at this stage</span>
    <span><span class="no">·</span> not reached</span>
  </div>
  <div class="tbl">
  <table>
    <thead><tr><th>Company</th><th>Role</th><th>Applied</th><th>CV stage</th><th>First call</th><th>Technical</th><th>Next stage</th><th>Where it stands</th></tr></thead>
    <tbody>
{render_table(apps)}
    </tbody>
  </table>
  </div>
</section>

<footer>Built by <span class="mono">tools/stats.py</span>. {ANALYSIS_HINT}</footer>
</div>
"""


CSS = """
:root{
  --bg:#f5f7f9; --surface:#ffffff; --fg:#17212b; --muted:#5b6b7a; --line:#dde3ea;
  --accent:#1f5f8b; --accent-soft:#e3eef6;
  --ok:#1e7a4c; --ok-soft:#e1f2e8; --wait:#9a6a00; --wait-soft:#fbf0d6;
  --bad:#b23a3a; --bad-soft:#f8e3e3; --idle:#7c8896; --idle-soft:#eef1f4;
  --f-display:"Bricolage Grotesque", "Segoe UI", system-ui, sans-serif;
  --f-body:"Instrument Sans", "Segoe UI", system-ui, sans-serif;
  --f-mono:"JetBrains Mono", ui-monospace, Menlo, monospace;
}
@media (prefers-color-scheme: dark){ :root:not([data-theme="light"]){
  --bg:#0f151b; --surface:#16202a; --fg:#e4eaf0; --muted:#94a3b2; --line:#2a3744;
  --accent:#7cb8e4; --accent-soft:#1b3346;
  --ok:#5fcf93; --ok-soft:#163626; --wait:#e6b84c; --wait-soft:#3a2f12;
  --bad:#f08484; --bad-soft:#3e1c1c; --idle:#8795a3; --idle-soft:#1f2a35; color-scheme:dark }}
:root[data-theme="dark"]{
  --bg:#0f151b; --surface:#16202a; --fg:#e4eaf0; --muted:#94a3b2; --line:#2a3744;
  --accent:#7cb8e4; --accent-soft:#1b3346;
  --ok:#5fcf93; --ok-soft:#163626; --wait:#e6b84c; --wait-soft:#3a2f12;
  --bad:#f08484; --bad-soft:#3e1c1c; --idle:#8795a3; --idle-soft:#1f2a35; color-scheme:dark }
body{background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:15px;line-height:1.5}
.wrap{max-width:1180px;margin:0 auto;padding-block:32px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:40px}
h1,h2{font-family:var(--f-display);text-wrap:balance;margin:0;letter-spacing:-.01em}
h1{font-size:2rem;line-height:1.15}
h2{font-size:1.3rem}
.sub{color:var(--muted);margin:6px 0 0}
.mono{font-family:var(--f-mono);font-variant-numeric:tabular-nums;font-size:.86em}
section{display:grid;gap:14px;min-width:0}
.eyebrow{text-transform:uppercase;letter-spacing:.08em;font-size:.72rem;color:var(--muted);font-weight:600}
.funnel{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px}
.step{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:2px;min-width:0}
.step b{font-family:var(--f-display);font-size:2rem;line-height:1;font-variant-numeric:tabular-nums}
.step span{color:var(--muted);font-size:.85rem}
.step.bad b{color:var(--bad)} .step.ok b{color:var(--ok)} .step.acc b{color:var(--accent)}
@media (max-width:760px){.funnel{grid-template-columns:repeat(2,minmax(0,1fr))}}
.week{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:10px}
.ev{background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:14px 16px;display:grid;gap:4px;min-width:0}
.ev .when{font-family:var(--f-mono);font-size:.8rem;color:var(--accent);font-weight:500}
.ev .what{font-weight:600}
.ev .how{color:var(--muted);font-size:.9rem}
.tbl{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:10px}
table{border-collapse:collapse;width:100%;min-width:900px}
th,td{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}
th{font-size:.72rem;text-transform:uppercase;letter-spacing:.07em;color:var(--muted);font-weight:600;background:var(--surface);position:sticky;top:0}
tr.grp td{background:var(--idle-soft);font-weight:600;font-size:.82rem;letter-spacing:.03em;padding:7px 12px}
td.co{font-weight:600;white-space:nowrap}
td.role{color:var(--muted);min-width:180px}
td.note{color:var(--muted);font-size:.88rem;min-width:220px}
.c{white-space:nowrap;font-size:.85rem}
.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:.78rem;font-weight:600;white-space:nowrap}
.p-ok{background:var(--ok-soft);color:var(--ok)}
.p-wait{background:var(--wait-soft);color:var(--wait)}
.p-bad{background:var(--bad-soft);color:var(--bad)}
.p-idle{background:var(--idle-soft);color:var(--idle)}
.p-acc{background:var(--accent-soft);color:var(--accent)}
.no{color:var(--line)}
tr.grp.win td{background:var(--ok-soft);color:var(--ok)}
tr.win td{background:color-mix(in srgb,var(--ok-soft) 45%,transparent)}
.cheer{background:var(--ok-soft);border:1px solid var(--ok);border-radius:12px;padding:16px 20px;display:grid;gap:4px}
.cheer b{font-family:var(--f-display);font-size:1.15rem;color:var(--ok)}
.cheer span{color:var(--fg);font-size:.92rem}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;color:var(--muted);font-size:.85rem}
footer{color:var(--muted);font-size:.82rem}
"""


def main(argv=None) -> int:
    try:
        apps = load(REPO / "job_search_tracker.csv", REPO / "documents" / "applications")
        hl_path = REPO / "reports" / "highlights.md"
        highlights = parse_highlights(
            hl_path.read_text(encoding="utf-8") if hl_path.exists() else "", str(hl_path)
        )
    except FormatError as err:
        print(f"error: {err}", file=sys.stderr)
        return 1
    out = REPO / "reports" / "pipeline.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(render(apps, highlights, date.today()), encoding="utf-8")
    c = counts(apps)
    print(f"wrote {out.relative_to(REPO)}")
    print(", ".join(f"{k} {v}" for k, v in c.items() if v != ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
