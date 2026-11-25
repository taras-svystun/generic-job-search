---
name: outcome
description: Record news on a job application (reply, interview, rejection, offer, silence) in the tracker and the application archive, and draft polite follow-ups for quiet applications. Use when the user reports any news on an application, asks which applications are open, or wants to chase one that went quiet.
---

# /outcome - Record the Result of an Application

You are recording what happened to a job application: progress updates (interview invitations, stages completed, offers) and final resolutions (hired, rejected, no response). The data lands in two places:

- `job_search_tracker.csv` - one row per application, with its status
- `documents/applications/<company>_<role>/` - the per-application archive (posting, submitted drafts, `outcome.md`)

This skill never edits the profile or the other skill files itself.

It also owns the stretch *before* there is an outcome to record: the **follow-up branch** (Step 2b) finds open applications that have gone quiet, drafts a short follow-up note in the user's voice, and logs it. So the chase and the result it leads to live in one flow.

Paths: the skill files live in `.agents/skills/job-application-assistant/`.

Follow these steps **in order**.

---

## Step 0: Parse Input

`$ARGUMENTS` (or the user's message) may contain:

- Nothing → list open applications and ask which one to update
- A company name (optionally with a role), e.g. `/outcome acme` or `/outcome acme data analyst` → target that application
- `followup` → enter the follow-up branch (Step 2b) over every quiet open application, using the default threshold of **10 days**
- `followup <N>`, e.g. `/outcome followup 14` → follow-up branch with an N-day threshold
- `followup <company>`, e.g. `/outcome followup acme` → draft a follow-up for that application now, regardless of threshold

---

## Step 1: Load State and Identify the Application

1. Read `job_search_tracker.csv`. If it does not exist, create it with the standard header:
   ```
   date,company,sector,role,role_type,channel,status,contact_person,fit_rating,notes,cv_file,cover_letter_file,source,deadline
   ```
   **If the file exists and its header does not end in `,deadline`, append `,deadline` to the header line only** - no data row is touched. Legacy rows then read as an empty deadline. This is the one edit to an existing tracker this skill may make outside a matched row, and Step 4's "never restructure the CSV" governs that row, not this header line.
2. **With an argument:** match rows case-insensitively on company (and role, if given). One match → proceed. Several → list them and ask. None → the application was made outside the workflow; collect company, role, date applied, channel, and posting URL from the user and add a tracker row.
3. **Without an argument:** list all rows whose status is not final (see **Tracker status vocabulary** below) as a numbered table (company, role, date applied, current status, deadline, days quiet, follow-ups sent) and ask which to update. The two derived columns come straight from existing data: **days quiet** counts from the row's `date` or the latest dated entry in `notes`, whichever is more recent; **follow-ups sent** counts the `followed up YYYY-MM-DD` markers in `notes`. If any open row is 10+ days quiet with fewer than two follow-ups sent, add one line under the table: "Some of these have gone quiet - want a follow-up draft? (Step 2b)". If every row is resolved, say so and stop.

   **`drafted` rows are listed but never counted as quiet** - nothing was sent, so nobody is late replying. List them under their own heading ("Drafted, not yet submitted"), leave **days quiet** and **follow-ups sent** blank, and keep them out of the follow-up offer above.

   **Deadline urgency is the one clock that does apply to a drafted row.** Show the `deadline` column when the row has one and leave it blank otherwise. Mark a deadline within 7 days with 🔥 and one that has already passed with ⚠. A passed deadline on a `drafted` row is the failure this column exists to catch - documents written, never sent, and now too late to send - so name it in one line under the table rather than leaving the user to compare dates. This changes nothing about the follow-up offer: a drafted row is still never chased, because nobody is late replying to something that was never sent.

4. Derive the archive folder name. First look for an existing `outcome.md` whose header is `# Outcome: <Company> — <Role>` of this row, and use its folder (a folder made by hand may not follow the naming rule; `tools/stats.py` matches by this header too). If none exists, derive `documents/applications/<company>_<role>/` by the **Subfolder naming** rule in `documents/README.md`. An existing `outcome.md` means you are updating, not creating.

---

## Tracker status vocabulary

Canonical spellings for the tracker CSV `status` column (underscores, never spaces):

`drafted` | `applied` | `interview` | `offer` | `hired` | `rejected` | `no_response` | `offer_declined` | `withdrawn`

- **Final** (application closed): `hired`, `rejected`, `no_response`, `offer_declined`, `withdrawn`
- **Open**: everything else, `drafted` included — a row is active until its status is one of the **Final** values.
- **`drafted`** is open but distinct — nothing was sent, so no follow-up is ever due.
- Readers must also accept the legacy space spellings `no response` and `offer declined` on read, so that existing trackers keep working without a migration. Never write them — they are the same values as `no_response` and `offer_declined`, not separate statuses, equally **Final**, and every rule that names one applies to the other.

This column is the only status of an application: `outcome.md` holds its stages and notes, never a status.

---

## Step 2: Collect What Happened

Ask the user what happened, then classify:

**Progress updates** (application still open):
- Interview invitation / stage scheduled or completed (phone screen, technical, case, final round)
- Offer received (not yet accepted or declined)

**Resolutions** (application closed) — these map to the tracker statuses in **Tracker status vocabulary** above:
- `hired` - accepted an offer
- `offer_declined` - received an offer, turned it down
- `rejected` - explicit rejection at any stage
- `no_response` - no reply; if the user is unsure whether to call it, note how long it has been since the last contact and let them decide - do not impose a cutoff
- `no_response` also covers a process that stalled after interviews with no explicit rejection; say so in `Notes`
- `withdrawn` - the user stopped the process

Also collect, without interrogating - one or two open questions are enough:
- Dates for the stages reached
- Any feedback received, word for word where the user remembers it
- What they'd do differently, and any signal about what the company valued (concrete beats polished: these notes sharpen later interview prep)

---

## Step 2b: Follow-Up Branch (chase a quiet application)

Enter this branch from the `followup` argument (Step 0) or from the offer under the open-pipeline table (Step 1.3). Standard practice is a short, polite follow-up one to two weeks after applying, at most twice; this branch puts that into practice.

**Candidates.** An application qualifies when its status is neither final nor `drafted`, the threshold has passed since its `date` (or since the last `followed up` marker in `notes`, if any), and it has fewer than **two** logged follow-ups. Parse dates with care - skip rows whose dates do not parse and say so rather than guessing. Present qualifying applications as a table (company, role, days quiet, follow-ups sent, channel, contact person) and draft only for the ones the user picks.

**Threshold.** 10 days by default: a nudge while a reply is still likely.

**Drafting.** For each selected application:

1. Read the archive folder: the `job_posting.md`, `cv_draft.tex`, and `cover_letter.tex` that Step 3 keeps are the source of **every claim** the note may make - this is Rule 3 (never fabricate) widened to "no new claims": a follow-up that adds skills or experience the submitted materials don't contain is a way to fabricate.
2. Apply the writing style rules from `03-writing-style.md` (no clichés, no em-dashes, warm but direct), and match the application's language - take the register from the archived cover letter.
3. Write roughly **60 to 120 words**: address the `contact_person` from the tracker if present (otherwise the team, in the application's language); one sentence restating interest in the specific role; one concrete reminder of value drawn from the submitted materials; one polite question about the timeline. No pressure, no "just checking in" filler.
4. Shape it for the `channel` column: email (with a subject line reusing the application's headline), LinkedIn message (shorter, no subject), or portal message (plain text).
5. Present the draft and iterate until the user is happy.

**Logging.** Once the user confirms they will send it (or have sent it), log it in the same turn - an unlogged follow-up breaks the next run's quiet-days count:

- Append `followed up YYYY-MM-DD` to the row's `notes` column (Step 4's rule applies: append a dated note, never restructure the CSV).
- Save the final note as `followup_YYYY-MM-DD.md` in the application's archive folder. Extra files sit safely beside the four named archive files, like `/interview`'s prep files.

If the user decides not to send, log nothing.

**Ending.** When an application hits two follow-ups and stays silent, do not offer a third. This is the moment to continue in this same skill's Step 2: note how long it has been since last contact and let the user decide whether to record `no_response` - as ever, no imposed cutoff. And if the user mentions an actual response while in this branch (an interview invitation, a rejection), leave the branch and record it through the normal Step 2 flow.

---

## Step 3: Archive the Application Materials

Create or update `documents/applications/<company>_<role>/`. All content here is personal data. Make sure `.gitignore` keeps `documents/applications/**` out of any public repo; nothing needs redacting inside the folder.

1. **`cv_draft.tex` and `cover_letter.tex`** - copy (never move) the submitted files. Find them via the tracker row's `cv_file`/`cover_letter_file` columns; if those are empty, look for `cv/main_<company>*.tex` and `cover_letters/cover_<company>_*.tex`. If a file already exists in the archive, leave it - the archived version is what was actually submitted. If no draft files exist (application made outside `/apply`), skip with a note.
2. **`job_posting.md`** - if it already exists, leave it. Otherwise fetch the tracker row's `source` URL and save the posting text; on a 403, follow the search fallback in `.agents/skills/job-application-assistant/09-web-research.md`. If the URL is dead (postings expire fast - this is exactly why the archive matters), ask the user to paste the posting, or write a stub noting the posting is unavailable. **Never reconstruct a posting from memory.**
3. **`outcome.md`** - write or update it in exactly the format documented in `documents/README.md`:

```markdown
# Outcome: <Company> — <Role>

## Stages
- [x] call booked: <short detail, for example a date>
- [ ] call held
- [ ] technical held
- [ ] past technical
- [ ] rejected at CV
- [ ] rejected after HR

Note: <one line for the page: where it stands>
Next: <one line: the next stage, if known; start with ✓ when it is already passed>

## Notes
<feedback received, what to do differently, signals about what they valued -
appended per update with a date, never overwritten>
```

The header uses the tracker row's `company` and `role` exactly. All six boxes stay, in this order; `tools/stats.py` refuses a file that lacks one or adds another. What each box means:
- `call booked`: a first call (recruiter, HR or intro) is set; stays ticked once held.
- `call held`: that first call took place.
- `technical held`: a technical or skills interview, case, or graded test task took place.
- `past technical`: they moved the candidate on after that stage.
- `rejected at CV`: rejected before any call.
- `rejected after HR`: rejected after the first call, before a technical stage.

Update rules: tick boxes as stages are reached, with a short detail after a colon (`call held: recruiter, <date>`); rewrite the `Note:` and `Next:` lines to the current state (they are the page's summary, the only lines you may overwrite); append dated entries to `## Notes`. Re-running `/outcome` on the same application is idempotent - it appends new information, never duplicates or rewrites history.

**Thank-you note trigger:** when this step ticks a newly completed interview stage, offer in the same turn: "Want a short thank-you note for the interviewer? A prompt one is standard practice." If accepted, draft it under Step 2b's drafting and logging rules (same voice, same no-new-claims boundary, same `followup_YYYY-MM-DD.md` archive file). Recording the stage is the trigger - no scanning for recent stages is ever needed.

---

## Step 4: Update the Tracker

Update the matched row's `status` column using the canonical spellings from **Tracker status vocabulary** above (e.g. `drafted` → `applied` → `interview` → `offer` → `hired` / `rejected` / `no_response` / `offer_declined` / `withdrawn`) and append a short dated note to the `notes` column. Never restructure the CSV, reorder rows, or touch other rows. The rewrite touches only the `status` and `notes` columns: preserve every other field of the row, parsed or not, so a value the row carries - the `deadline` written by `/apply` Step 6b, or any column added in the future - is never blanked by a status update.

**Moving a row off `drafted`:** a `drafted` row carries the date the documents were drafted, not the date they were sent. Whenever this step advances such a row to any other status - `applied`, or straight to `interview` or `rejected` when the user reports an outcome for something they submitted without recording it - overwrite its `date` column with the actual submission date. The `date` column is read as "applied on" and drives `tools/stats.py`'s page and this skill's own days-quiet count, so leaving the draft date in place would misreport the application.

---

## Step 5: Confirm

Run `python3 tools/stats.py` to rebuild `reports/pipeline.html` (no tokens; publish or share it only if the user asks). If it prints an error or a warning, fix the file it names. Then summarize what was recorded:

> **Outcome recorded for <Role> at <Company>.**
>
> - `documents/applications/<company>_<role>/outcome.md` - <boxes ticked, Note/Next changed>
> - Archived: <which of cv_draft.tex / cover_letter.tex / job_posting.md were copied or fetched, and which were skipped and why>
> - Tracker: status → <new status>

If the update recorded an upcoming or newly scheduled interview stage, also suggest:

> "Interview coming up? `/interview <company>` builds a prep pack for that stage from this application's archive - the posting, the documents you submitted, and any feedback recorded from earlier rounds."

If the recorded status is `hired`, congratulate the user warmly first - this is the moment the whole workflow exists for.

---

## Important Rules

1. **Write data, don't interpret it.** The archive and tracker are the outputs. This skill never edits profile or other skill files.
2. **The archived version is the submitted version.** Existing files in the application folder are never overwritten by fresher drafts.
3. **Never fabricate.** A dead posting URL gets a user-pasted copy or an explicit "unavailable" stub, not a reconstruction. Feedback is recorded as the user reports it.
4. **Stay schema-compatible.** `outcome.md` follows the Step 3 format exactly, because `tools/stats.py` parses it; the tracker keeps its columns.
5. **Idempotent updates.** Re-running on the same application appends new stages and notes; it never duplicates folders, rows, or history.
6. **Follow-ups: draft only, never send.** The follow-up branch produces text for the user to send themselves. It never emails, messages, or submits anything, and it must not be wired to tools that do.
7. **Follow-ups: no new claims.** Every claim in a follow-up or thank-you note comes from the archived submitted materials. Rule 3 applies with no exceptions.
8. **Maximum two follow-ups per application.** After the second silent follow-up, the honest move is recording the result, not more chasing.
