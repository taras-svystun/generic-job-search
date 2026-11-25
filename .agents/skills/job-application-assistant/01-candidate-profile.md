# Candidate Profile

The one source of facts about the candidate, and the rules for how to present them. Every CV,
cover letter, LinkedIn text, form answer and interview answer is built from this file.

This file starts empty. Run the `onboard` skill to fill it. Each section says what goes there and
which skill reads it. Write "none" in a section that does not apply, so no agent guesses.

This file holds personal data. Keep your filled copy in a private repository.

## Framing rules (every document)

These rules read the **Framing policy** section below. If that section is empty, the policy is
`strict`.

**Goal.** Get the candidate past the screening software (ATS) and the recruiter to the real
interview. Show every true fact in its best light, so the role reads as a good match.

**Both policies:**
- Weak or awkward facts are reframed, not apologised for. A short job is a focused delivery. A
  learning project is hands-on experience. Working alone is full ownership, end to end.
- Use the posting's words where they are true. Lead with impact, scope, ownership and numbers.
- Do not volunteer limitations in employer documents. A gap is shown as the closest real
  strength, never listed as a gap.
- Honest caveats in this file are internal. They serve fit checks and interview prep, and never
  enter a document.
- Every claim must be one the candidate can explain in an interview. A claim that falls apart
  there costs the offer.
- A new fact the candidate confirms, corrects or adds goes back into this file in the same turn.

**Policy `strict`:** only true facts. No stretched number, scope, title or skill. A missing skill
is bridged with the closest real strength, or with a small project the candidate builds first.

**Policy `generous`:** small stretches are allowed, but only inside the limits written in the
Framing policy section. A stretch is, for example, a slightly generous number or scope, or a small
skill next to real work that the candidate can close before the interview. Most of the CV stays
real experience. Each stretch is listed in the truth report of the `apply` skill, and in the
"Stretches in use" list below, with the date it was first used.

**Allowed (both policies):**
- Numbers: measured, or an estimate the candidate can explain. Any other number: only as a
  stretch under `generous`.
- Tools used briefly, listed as skills. A tool never used: only as a stretch under `generous`.
- A key skill that postings keep asking for and the candidate lacks: suggest a small personal
  project to close it (one evening or one weekend). Once it exists, record it under Projects and
  list it short, for example "Kubernetes (personal project)" or "Bookkeeping software (basic)".
- Stronger scope words ("led", "designed", "owned") only where the role really was that.
- Job title written as "official title · function" when the function helps the reader, for
  example "Analyst · Client Delivery". The official title itself never changes.
- People: claim line management only if it is in Experience. Other leadership (volunteering,
  coordinating peers, teaching) is named as what it was, and only when the posting asks for
  people skills.

**Never changed (both policies): employers, official titles, dates, degrees.** No invented
employer, degree, certificate or reference.

**Style (defaults; the candidate may change them in `onboard`):**
- Plain, simple English (or the document's language): short sentences, a short objective, no
  argument that needs a second read. Say what the work changed for the employer before how it
  was done.
- Objective: confident. It opens with the role and what the candidate does, in the present
  tense, then gives proof (a result, a number), and ends on what the candidate brings the
  employer, never on what they want.
- No hedge words (words that weaken a claim): helped, assisted, tried to, fairly, somewhat, some, almost, usually, basic. Each one asks the reader to
  discount the claim. "Basic" is allowed only for a skill that really is basic.
- A partial score (for example "7 of 10") makes the reader ask about the missing part. Give the
  size of the work instead (how many cases, users or items). A full score is fine.
- A strength is shown by a short real case from Stories, never by a slogan.
- No hype words: spearheaded, leveraged, cutting-edge, seamless, robust, passionate,
  transformative, game-changer, synergy, delve, and similar.
- Extra style rules from the candidate: <none yet>

## Identity

What goes here: the facts for the CV header and forms. Read by the `apply` skill (CV header,
cover letter and form answers).

- **Name:**
- **Email:**
- **Phone:**
- **Links:** (LinkedIn, portfolio, GitHub, publications page; only the ones to show employers)
- **Location shown on the CV:** (the place the CV header shows, for example a city and country)
- **Current status:** (employed, studying, between roles; earliest start date)
- **CV language:** (the language every CV is written in; cover letters may follow the posting)
- **CV template:** (`classic` or `academic`; empty means the `apply` skill picks from the posting)
- **File-name prefix:** (starts every final PDF name, for example `J-Doe`; empty means first
  initial and surname)

## Constraints

What goes here: the hard limits on which jobs count. Read by `04-job-evaluation.md` as gates: a
posting that breaks one fails before scoring.

- **Work mode:** (remote only, hybrid, on-site, any; how many office days at most)
- **Locations:** (countries, cities or time zones that work; willing to relocate or not)
- **Working hours and time zones:** (hours of overlap that work; what to flag, not reject)
- **Contract types:** (employee, contractor, freelance, fixed-term, part-time; which come first)
- **Work authorisation:** (where the candidate may work without a visa; what to say on forms)
- **Company size, stage or sector limits:** (or "none")

### Languages

What goes here: one row per language. Read by `04-job-evaluation.md` (a posting that needs a
working level the candidate lacks fails) and by the CV and letter skills.

| Language | Level (native, C2-A1, or plain words) | Works in it? | Notes (for example, leave off the CV for some markets) |
|----------|---------------------------------------|--------------|--------------------------------------------------------|
|          |                                       |              |                                                        |

- **Translation tools for written-only languages:** (yes / no. "yes" means a posting that needs
  a language only for reading or writing is a FLAG, not a FAIL.)

## Pay bands (internal only)

What goes here: the target pay per market or contract type, and how to say it. Internal only:
never in a CV or letter unless the posting demands it. Read by `04-job-evaluation.md`,
`find-companies`, and the `apply` skill for form answers.

- **Bands:** (per market or contract type: amount, currency, gross or net, per year, month,
  day or hour)
- **Exact sentence to use when asked:**
- **Where the number goes:** (form, recruiter call, letter only when the posting asks)
- **Floor:** (the lowest pay worth a talk. A posting with no pay, or pay a little under the
  band, is flagged and the candidate decides. Reject on pay only when the posting publishes a
  range whose top is below this floor)

## Fit rubric

What goes here: what makes a job a good fit for this candidate. Read by `04-job-evaluation.md`
for scoring and by `find-companies` for ranking.

- **Must-haves:** (each one fails the posting if missing)
- **Deal-breakers:** (each one fails the posting if present)
- **Nice-to-haves:** (raise the score, never gate it)
- **Weights:** (how much each scoring area in `04-job-evaluation.md` counts: Skills,
  Experience, Behavioural, Career, in percent that add up to 100; leave empty to use 04's
  defaults)

## Framing policy

What goes here: how much the documents may stretch. Read by the Framing rules above and by every
skill that writes or reviews a document. Empty means `strict`.

- **Policy:** (strict | generous)
- **Chosen on:** (YYYY-MM-DD)
- **Stretch limits (generous only):** (what may stretch and how far, for example "numbers up to
  about 20% above the measured value"; "skills one step from real work, closed before the
  interview"; never the Never-changed list)
- **Never stretch:** (anything the candidate adds to the Never-changed list)

### Stretches in use

What goes here: every stretch used in a sent document, with the first date, the posting, and
how the candidate closes it before an interview. Empty under `strict`. Read by the interview
skill.

## Positioning

What goes here: the role tracks the candidate targets, in order, and the case for each. Read by
`04-job-evaluation.md`, the CV and letter skills, and `find-companies`.

- **Tracks, in order of interest:** (each with one line on why the evidence fits)
- **Roles to avoid:** (postings that compete on the candidate's weak points)
- **Target sectors:**
- **What excites the candidate about the work:** (in their own words)
- **What drains the candidate:** (tasks or settings that wear them down, in their own words)
- **Years framing:** (the line for "N+ years of X", and the strictest true reading behind it)

### Behavioral summary

What goes here: traits, strengths, growth areas (internal), the weakness answer, where the
candidate thrives, each backed by a source (a review, an evaluation, a story). Read by
`04-job-evaluation.md`, `02-behavioral-profile.md` and the interview skill.

## Experience

What goes here: one entry per job, newest first. Read by every skill that writes a CV, a letter
or an interview answer. Copy this block per job:

```
### <Official title> - <Employer> (<Mon YYYY> - <Mon YYYY or Present>)
<City or "remote">; <full-time / part-time / contract>
- What the team or company does (sector and scale; see Disclosure for what may be named).
- What the candidate owned, built or changed, with numbers and how each was measured.
- Tools and methods used.
- Internal caveats (never in a document).
```

## Education

What goes here: degrees, schools, dates, thesis or key topics, grades only if strong. Read by
the CV skill and `04-job-evaluation.md`.

| Degree | Period | Institution | Key topics or thesis |
|--------|--------|-------------|----------------------|
|        |        |             |                      |

- **Certifications:**
- **Publications:**
- **Awards:**

## Skills

What goes here: what the candidate can do, grouped as they want to show it. Read by the CV skill
(Skills line) and `04-job-evaluation.md` (skills score).

- **Strong:** (used often, can go deep in an interview)
- **Working:** (used on real work, can explain)
- **Basic:** (used briefly)
- **Not claimed:** (tools and skills with no real use; never on a document, except as a
  stretch under `generous`)

## Projects

What goes here: personal, open-source, study or side projects. Each with a link (if public),
the date, what it does, the result, and which postings it suits. Read by the CV and outreach
skills.

## Stories

What goes here: concrete cases (situation, task, action, result) that prove a strength. Each
with the Experience or Project entry it comes from. Read by the cover letter skill (one case per
strength) and by `07-interview-prep.md` (STAR answers).

### References

What goes here: who can vouch for the candidate (role and relation only), written letters or
public reviews in hand, and who was asked. Read by the `apply` skill (form answers) and the
`interview` skill.

## Current situation

What goes here: internal context that shapes letters and answers: notice period, why looking
now, what happens in parallel, anything that must not enter a document. Read by the cover
letter skill and the `apply` skill (form answers). Add the date to each fact, as it changes.

## Disclosure

What goes here: what may and may not be named in any document. Read by every skill that writes
for an employer.

- **May be named:** (employers, schools, products)
- **Never named or hinted at:** (for example clients under an NDA; describe them by sector and
  scale only, such as "a mid-size logistics company")
- **Other limits:** (anything else that must stay out of documents, or "none")
