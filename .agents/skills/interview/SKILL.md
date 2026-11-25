---
name: interview
description: Build a stage-specific interview prep pack for one tracked application (likely questions, STAR answers, consistency brief, questions to ask) and offer a mock interview. Use when the user has an interview, screen, technical round or final round coming up on an application.
---

# /interview - Prepare for an Interview on a Tracked Application

You are preparing the user for a real, scheduled interview on one of their applications. The building blocks already exist - `07-interview-prep.md` (STAR examples, tough questions, questions to ask, roleplay rules) and the Company Research Checklist in `04-job-evaluation.md` - and the `/outcome` archive records which stage the user is at and what earlier stages showed. This skill joins them into a stage-specific prep pack and an optional mock interview.

STAR means Situation, Task, Action, Result: a short story told in that order.

`/apply` improves what the company reads; `/interview` improves what the company hears. The bridge between them is consistency: the interviewer has read the submitted CV and cover letter, so everything prepared here must match what those documents claim.

Paths: the skill files live in `.agents/skills/job-application-assistant/`.

Follow these steps **in order**.

---

## Step 0: Parse Input

`$ARGUMENTS` (or the user's message) may contain a company name (optionally with a role), e.g. `/interview acme`.

- **With an argument:** match against `job_search_tracker.csv` rows (case-insensitive on company, then role). One match → proceed. Several → list and ask. None → this application isn't tracked; suggest `/outcome <company>` to register it first, or accept the posting and role details directly if the user wants to prep anyway.
- **Without an argument:** list tracker rows whose status suggests a live process — an open status per the **Tracker status vocabulary** in `/outcome` (`interview`, `offer`, or recently `applied`; `drafted` is open but nothing was sent, so it never qualifies) — and ask which one. If the tracker is empty, ask for the company, role, and posting.

This skill preps for a **specific application**. General practice with no target is out of scope - if asked, prep against a real tracked application instead.

---

## Step 1: Load the Application Context

1. **The archive** (started by `/apply`, kept by `/outcome`): derive `<company>_<role>` by the **Subfolder naming** rule in `documents/README.md`, then use `documents/applications/<company>_<role>/`.
   - `job_posting.md` - the exact posting the user applied to
   - `cv_draft.tex` and `cover_letter.tex` - what was actually submitted. **These are what the interviewer read**; every talking point must be consistent with their claims.
   - `outcome.md` - the stage reached so far and any recorded feedback from earlier stages. Feedback from stage N is the most valuable input for stage N+1 prep.
2. **Fallbacks** (the application may predate `/outcome`): posting via a fetch of the tracker row's `source` URL, or ask the user to paste it; CV via `cv/main_<company>*.tex` and cover letter via `cover_letters/cover_<company>_*.tex`. State plainly which context is missing rather than guessing - and suggest `/outcome <company>` to build the archive for next time.
3. **Ask the user what this interview is** (skip anything `outcome.md` already records): stage (phone screen / technical / case / final round), date, format (phone, video, on-site), and who is interviewing (names and titles, if known).
4. **Read these files once** - do not re-read them in later steps:
   - `.agents/skills/job-application-assistant/07-interview-prep.md`
   - `.agents/skills/job-application-assistant/01-candidate-profile.md` (its Stories, Framing policy and Disclosure sections first)
   - `.agents/skills/job-application-assistant/02-behavioral-profile.md`
   - `.agents/skills/job-application-assistant/04-job-evaluation.md`

---

## Step 2: Research the Company (Interview-Focused)

**First, check the cache**: read `company_research/<normalized-company-name>.json` per the Company Research Cache section in `04-job-evaluation.md` (normalize the company name the same way). If it exists and is within the documented TTL (time to live: how many days a cached result stays fresh), start from it instead of researching from scratch — `/apply` may already have filled it for this same application. Verification still applies to a cache hit: the rule below holds whatever the source.

If the cache is missing or stale, run the Company Research Checklist that `04-job-evaluation.md` defines: company website (mission, values, recent news), review sites, LinkedIn (team size, recent hires), and media coverage (growth, restructuring, workplace issues). Afterward, write (or overwrite) the cache file with the fresh findings per the schema in `04-job-evaluation.md`, so a later `/apply` or `/interview` run for the same company can reuse them.

Additions for interview purposes:

- **Interviewer angle:** if interviewer names are known (from Step 1 or the tracker's `contact_person`), look up their public professional profile. A hiring manager probes team fit and motivation; a senior specialist probes technical depth; HR probes the CV timeline. Note the likely angle per interviewer - do not speculate beyond public information.
- **Conversation hooks:** 2-3 recent, checkable company facts (a product launch, a stated priority) the user can mention naturally in answers and in the "why this company" moment.

**Verify before using:** every company claim that will appear in the prep pack must be confirmed by you with a fetch or a search - the same rule the repo applies to cover-letter claims. An unverified "fact" said with confidence in an interview is worse than no fact. On a 403, follow the search fallback in `.agents/skills/job-application-assistant/09-web-research.md` rather than falling back to search snippets; a snippet is a lead, not a source.

---

## Step 3: Build the Prep Pack

Put together a prep document that fits the stage, with these sections:

### 1. Likely questions
Derive from four sources, in priority order:
1. **Recorded feedback from earlier stages** (`outcome.md`) - anything flagged, doubted, or left open will come back
2. **The fit evaluation's gaps** - the requirements where the profile is weakest are the likeliest probes. For each, prepare an honest bridge answer per `07`'s "You don't have [X]" pattern: admit it, connect adjacent experience, show how you would learn it. **Never prepare an answer that invents experience.**
3. **The posting's stated requirements** - one by one
4. **The stage type** - phone screens get motivation and timeline questions; technical rounds get the posting's tools and methods; final rounds get values, salary, and "any doubts about me" questions. For salary, use the pay bands in 01 (internal only): prepare the user's range, never write it into a document an employer reads.

### 2. STAR answer mapping
Match the ready-made STAR examples in `07-interview-prep.md` (and the Stories in 01) to the likely questions using their "Use for" tags. Then:
- For likely questions **no existing STAR example covers**, draft a new STAR answer grounded strictly in facts from `01-candidate-profile.md` - profile facts arranged into S/T/A/R, not embellished. Include these drafts in the prep pack; offer to append them to `07-interview-prep.md` only if the user explicitly approves.
- If `07-interview-prep.md` has unfinished STAR stubs relevant to this role, show them: the user should fill in the details before the interview.

### 3. Consistency brief
A short list of the specific claims the submitted CV and cover letter make (achievements, numbers, skills emphasized) that the interviewer is most likely to probe. The rule stated plainly: **no claim in the room that isn't on the paper, and every claim on the paper must be defensible in depth.** If 01's framing policy is `generous`, list each stretch the documents contain (from 01's "Stretches in use" list for this application, else by comparing the documents with 01) and how the user will answer a deep question on it honestly.

### 4. Tough questions, customized
The relevant entries from `07`'s tough-question list with answers for this application - "Why this company specifically?" must use the verified hooks from Step 2, never a generic line.

### 5. Questions to ask
Pick 4-6 from `07`'s categories, customized to the research and the stage: role and team questions at screens, tools and growth questions at technical rounds, culture and leadership questions by the final round (that is the last chance to spot a deal-breaker from 01 Fit rubric). Cut any question the research already answers publicly - asking it signals you didn't look.

### 6. Logistics
The phone/video tips from `07` when the format calls for them, plus date and interviewer names as a header.

Save the pack in the archive folder derived in Step 1 as `interview_prep_<stage>.md` (create the folder if this application predates `/outcome`). The folder holds personal data and stays out of any public repo; one file per stage, so earlier packs remain as history. Present the pack in chat as well - the file is the artifact, the conversation is the delivery.

---

## Step 4: Offer a Mock Interview

Ask if the user wants to practice. If yes, run the roleplay **in this conversation** following the Roleplay Guidelines in `07-interview-prep.md` exactly: warm-up first, then role-specific technical questions, 1-2 behavioural questions tied to the posting's requirements, and one tough question or surprise. After each answer, give brief feedback - what worked, what to sharpen, and which STAR example from the pack would have served better.

Calibrate feedback against `02-behavioral-profile.md`: coach toward the user's natural style, not a generic ideal - the same voice-consistency rule the `/apply` reviewer applies to cover letters.

---

## Step 5: Close the Loop

End with:

> Good luck. After the interview, run `/outcome <company>` to log the stage and any feedback - it sharpens the prep for the next round.

If Step 3 drafted new STAR answers the user approved for keeps, remind them those were appended to `07-interview-prep.md` (or offer again if they deferred).

---

## Important Rules

1. **Consistency with the submitted documents.** The interviewer read the archived CV and cover letter; prep must never contradict them or coach claims beyond them.
2. **Honesty on gaps.** Weak matches get bridge answers (admit → adjacent experience → how you would learn it), never invented experience. Same rule as everywhere else in this repo.
3. **Verified research only.** Company facts go in the pack only after you confirm them yourself. Interviewer notes stick to public professional information.
4. **Disclosure.** Names that 01 Disclosure forbids (for example clients under NDA) stay out of the pack and out of practice answers; describe them by sector and scale.
5. **Prep fits the stage.** A phone screen pack and a final-round pack are different documents; recorded feedback from earlier stages comes before generic question lists.
6. **Write only to the application archive** — with one exception. The prep pack lands in the archive folder derived in Step 1; skill files are not edited, except appending user-approved STAR examples to `07-interview-prep.md` on explicit request.

   **The exception is `01-candidate-profile.md`.** Interview prep is where new facts come up most often: the user recalls a metric, corrects a scope, or fills in a STAR stub. When that happens, write the fact into the profile, as well as putting it in the prep pack. A fact recorded only in prep material reads as unsupported to a later drafting session and gets stripped from CVs as a fabrication. Prep files are not a substitute for the profile.
