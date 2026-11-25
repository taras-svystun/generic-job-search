---
framework_version: 2.0.0
---

# CV Template and Tailoring Guide

## Pick the template

| Template | Folder | Use for | Pages |
|---|---|---|---|
| Classic (FAANGPath) | `templates/cv/classic/` | industry roles in any field | exactly 1 (2 only if 01 or the posting asks for it) |
| Academic | `templates/cv/academic/` | PhD, postdoc, faculty, research lab and grant applications | no fixed limit; follow the posting |

If 01 names a preferred template, use it. Before drafting, read `templates/TEMPLATE.md`: it
says how to compile, which extra files each template needs, the page size and the licence.
Where its tips disagree with this file, this file wins.

- **Skeleton:** `templates/cv/<classic|academic>/template.tex`. Copy it; never edit the
  template itself for one application.
- **Facts** come only from `01-candidate-profile.md`. Old tailored CVs in `cv/` give structure
  and phrasing, never facts.
- **Output:** `cv/main_<company>_<role>.tex`. Copy every other file from the template folder
  (for example a `.cls` class file) into `cv/` beside it.
- **Compile:** `cd cv && pdflatex -interaction=nonstopmode main_<company>_<role>.tex`, or the
  `xelatex` for a non-Latin script (see "LaTeX special characters" below). Run it twice if
  hyperref reports a changed `.out` file.
- **Page count:** the limit in the table above. Any other page count is a failure to fix before
  showing the candidate.

## Layout

Section headings come only from the template's `template.tex` (the `rSection` blocks in the
classic CV, the `\section` lines in the academic CV). Delete a section that 01 cannot fill;
never invent a heading. Keep the template's order, except: move Education below Experience
when the candidate has more than a few years of work. A typical industry order:

```
OBJECTIVE / SUMMARY   3-4 lines; role first, present tense, proof, no wish at the end
EXPERIENCE            most bullets on the most recent and most relevant role (4-6)
                      older relevant roles: 2-3 bullets with real tool or method names
                      other roles: one compact "Other roles:" line
PROJECTS              1-2 items, bold project name as the link text (if 01 has projects)
EDUCATION             degree, awards, relevant coursework
SKILLS                labelled lines
```

An academic CV usually adds: research interests, publications, talks, grants and funding,
teaching, supervision, service, references. Follow the academic template's order.

## Section-by-section tailoring

### Objective (or summary)
- The most important section to tailor. Short, plain, business thinking first.
- It opens with the role and what the candidate does, in the present tense; then proof (a
  number, a live product, a result from 01); it ends on what they bring the employer, never on
  what they want.
- When the role is outside the candidate's home field, open with the one sentence that links
  their work to the employer's problem.
- Objectives in old drafts are phrasing references, never fact sources.

### Skills
- Reorder for the role. Use the posting's own core term in a label where it is true: ATS and
  quick human readers match words literally.

### Experience
- Rewrite bullets toward the role; most bullets on the most recent and most relevant roles.
- **Labelled bullets.** On the main role, each bullet may open with a short label: a sector
  ("Healthcare:", "Retail:") or the posting's term ("Delivery ownership:", "Budgeting:"). Either
  way the bullet tells one real case from 01 Stories or Experience: what was done, why, and the
  result. The label names the skill; the case proves it. A label over a list of steps or tools
  is a slogan: give it a case or cut it. Clients marked in 01 Disclosure are named by sector and
  scale only.
- **A must-have gets its own bullet**, labelled with the posting's word, with named tools or
  methods ("CI/CD with GitHub Actions", "IFRS 16 lease accounting", not only "CI/CD" or
  "accounting"). If 01 Disclosure bars the proof from paid work, the bullet goes in PROJECTS.
- **Every bullet has a result:** a number, a named outcome or a named reaction from a client or
  manager. A bullet with none is the first to cut.
- **An older relevant role keeps at least 2 bullets that name its tools or methods.** Pick the
  two that fit the posting.
- **Other roles line.** A role the page has no room for goes on the "Other roles:" line (title,
  employer, dates, a few words in brackets), never out of the CV.
- **Numbers:** measured, or an estimate the candidate can explain. Anything else only as a
  stretch, only under a `generous` Framing policy, and listed in the truth report.
- **Tenure vs visible output:** a long role shown by one project reads as low output. Fixes, in
  order: show more real work from 01; make phases inside the role clear; name what made the
  cycle long. Never invent projects, never shorten dates. If the gap remains, put the answer in
  interview prep.
- Employment gap: matter-of-fact, framed as skill-building, only with what 01 supports.

### Education
- Highest degrees always; thesis when relevant; awards inside the education section, one line
  each, unless the template has an awards section.
- **An unfinished degree says so inside the entry** ("In progress, expected <Month Year>."). A
  closed year range reads as finished. The objective, the entry and any availability note give
  the same date.

### Projects, publications, links
- PROJECTS is a list right after EXPERIENCE: `\href{URL}{\textbf{name}}: description`. The bold
  name is the link, so a reader can check it in one click.
- One or two projects. A project with no public link is listed only if 01 says how a reader can
  check it.
- Publications: the 1-2 that match the posting on an industry CV; the full list on an academic
  CV.

### Lists
- No `\vspace` between `\item` entries: it makes one gap randomly larger. Use the list's own
  spacing.

## LaTeX special characters (important)

Postings and profile data are plain text; the CV is LaTeX. Escape these in body text:

| Character | Write | Typical trigger |
|---|---|---|
| `&` | `\&` | company names: H\&M |
| `%` | `\%` | numbers: "cut costs by 40\%" |
| `$` | `\$` | money |
| `#` | `\#` | "ranked \#1", C\# |
| `_` | `\_` | file names, code names |
| `~` | `\textasciitilde{}` | URLs |
| `^` | `\textasciicircum{}` | versions, maths |

- **`%` fails silently.** It starts a comment: the compile is clean and the rest of the line
  disappears from the PDF. Check every `%` in every bullet.
- **`&` fails loudly** (alignment errors). Escape employer names first.
- A bullet that starts with a literal `[` must be braced, `\item {[text]}`, or LaTeX reads the
  text as `\item`'s label and prints it off the page with a clean compile.
- **Non-Latin scripts** (Cyrillic, Greek, Chinese, Arabic...): check that the template's font
  has the glyphs. A missing glyph often compiles with no error and prints nothing. The fix:
  compile with `xelatex` instead of `pdflatex`; remove `\usepackage[utf8]{inputenc}` and
  `\usepackage[T1]{fontenc}` if the file has them; add `\usepackage{fontspec}` and
  `\setmainfont{<a font that covers the script, for example Noto Serif>}` after
  `\documentclass`. Search the log for `Missing character` after every compile.

## Relevance-weighted cutting (how to reach the page limit)

Cut by signal, not by section. Score each line on:
1. **Relevance** to this posting: a named tool, keyword or duty.
2. **Uniqueness**: is this the only place the claim appears?
3. **Narrative load**: does the cover letter lean on it?

Cut the lowest score first, wherever it sits. In practice the order is:
1. Repeats (a skill that a bullet already proves).
2. Filler in the objective.
3. The lowest-scoring bullet in any role, the main role included. A bullet with no result
   scores lowest. Keep at least 4 bullets on the main role.
4. Last resort: an older role down to 2 bullets; a role with no room moves to the "Other roles"
   line.

Never cut a whole structural section first.
- An older bullet that hits the posting beats a recent one that does not.
- Never cut the example the cover letter depends on.
- Never shrink margins, font size or `\vspace` to force a fit; cut instead.
- If the page ends early, put back the most relevant cut line.

## ATS parseability

An ATS (applicant tracking system) reads the PDF's text layer, not the page. After the layout
passes:

```bash
python3 tools/verify_pdf.py cv/main_<company>_<role>.pdf --dump-text cv/main_<company>_<role>.txt
```

It tries pypdf first, then Poppler. A `pdftotext -layout` fallback always adds `-enc UTF-8`,
or some builds output Latin-1 and a good CV shows replacement characters. With neither
extractor: warn, and check keywords from the visual read.

- **Contact details as literal text.** Email and phone print as text; a header link shows the
  literal handle or URL, never only a word like "github". A project link shows the project name.
- **No garbage:** `(cid:NNN)` or `�` means a font has no Unicode map.
- **Reading order** matches the page (both CV templates are single-column).
- **Dates are ASCII ranges.** Write `Mon YYYY - Mon YYYY` with one hyphen. `--` becomes an
  en-dash and many parsers then see no range. A short role gets a full range with months, never
  a bare year.
- **Keywords:** the posting's exact term where true; never a keyword 01 does not support.
