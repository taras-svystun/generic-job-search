---
framework_version: 2.0.0
---

# Application Form Fields

`/apply` makes two documents: a CV and a cover letter. Many applications need a **third**:
free-text fields typed straight into an application portal. Graduate programmes, large
employers' ATS portals and startup forms often ask for things neither document covers, under a
character or word limit, in a box with no formatting.

This file covers that third artifact. You do not compile it; the candidate pastes it.

## When this applies

Use it whenever a posting or portal asks for any of:

- A self-introduction, personal statement or "tell us about yourself" paragraph
- Structured project entries (project name, role, start and end date, description)
- A short pitch under a hard character limit ("stand out in 140 characters", "why you, in one
  sentence")
- Motivation questions ("why this company", "why this programme")
- Competency questions with a word cap ("describe a time you…", 200 words)

## The rule behind everything here

**Every claim in a form field must already be supported by `01-candidate-profile.md`**, read
with its Framing policy. The interviewer reads the form next to the CV. A form field is not a
place for new claims, bigger scope or filler. It is a place to *select* from what is already
true and arrange it for the question asked. Under a `generous` policy, a stretch in a form is
the same stretch as in the CV, never a new one, and it is listed in the truth report.

All accuracy rules from `05-cv-templates.md` and `03-writing-style.md` apply unchanged.

## Field type: self-introduction paragraph

Usually 100-200 words, one paragraph, no formatting.

**Structure that works:**
1. Current status: what the candidate is doing or finishing now
2. The single strongest piece of evidence, with its number and scale
3. One line on the path: how they got here, if a change of field or a specialisation is
   genuinely interesting
4. What they want next, linked to this employer's actual work

**Rules:**
- **Lead with the strongest evidence, not the timeline.** A history told in order buries the
  best material when the strongest work is recent.
- **Write one version per role type, not one for all applications.** The same history framed
  for two different roles gives two different paragraphs. Write both, label them, and say which
  goes where.
- **Tie it to this employer in the last sentence.** Generic introductions read as generic.
- **Count the words and state the count.** Portals cut text silently. Give a shorter variant and
  name which sentence to cut first.

## Field type: structured project entries

Usually **project name, role, start date, end date, description.**

**Project name.** A descriptive name, not the employer's name: "Warehouse Inventory Forecasting
Platform" is a project, "Acme Corp" is an employer. A client may be named only if 01 Disclosure
allows it and the relationship is true (placed with them, delivered to them). Otherwise: sector
and scale only.

**Role.** The candidate's role *on that project*, which may be narrower than their job title. Do
not upgrade it.

**Dates.** The dates they worked on **that project**, which are not always the employment dates.
If a role ran two years but the project took the later part, saying so is more accurate and
avoids the low-output reading in `05-cv-templates.md` (Tenure vs visible output). Narrow the
dates only when the candidate can say when the project really started; never invent a boundary
to improve the ratio.

**Description.** 100-150 words: what the system or work did and who used it, then the hardest
problem and how it was solved, then the outcome with its number. Also give a **~60-word short
version**: portals vary, and the candidate should not have to improvise a cut.

**Scope is stricter here than on a CV.** A CV bullet can be short enough to be unclear about
ownership. A project entry with the candidate's name and role on it reads as ownership of the
whole thing. Where they contributed rather than owned, say so inside the description.

## Field type: hard character limits

These reward **a specific situation over an adjective**. Most applicants write adjectives
("passionate", "fast learner", "team player"), so a concrete situation stands out by contrast.

**Method:**
1. Pick the single most distinctive true thing: usually a number, an unusual mix of
   backgrounds, or a problem that maps onto the employer's own work.
2. Draft 4-6 candidates from different angles.
3. **Count characters with code. Do not estimate.** Text over the limit is cut mid-word.
4. Show all candidates with their counts, recommend one, and say why.

Prefer the version that **maps the candidate's problem onto the employer's problem**, where a
true mapping exists. That is what "stand out" is really asking for.

## Output format

Save a plain `.txt` file the candidate can copy from, next to the other material for that
application (for example `documents/applications/<company>_<role>/form_fields.txt`). One file
per employer, with every field that employer asked for.

Include:
- A header naming the employer and the roles it covers
- Each field, labelled, with its word or character count
- Short variants where limits may be tighter than expected
- **`NOTE TO SELF` blocks** for scope reminders and prepared answers to questions the content
  invites, clearly marked as *not for pasting into the form*
- A dates quick-reference, so date fields stay consistent

## Check before handing it over

- [ ] Every factual claim traces to `01-candidate-profile.md` (or is a stretch already in the
      truth report, under a `generous` policy only)
- [ ] No claim contradicts the CV or cover letter sent for the same role
- [ ] 01 Disclosure respected: no client named that may not be named
- [ ] Ownership scoped correctly on shared work
- [ ] Word and character counts measured, not estimated
- [ ] Unfinished qualifications described as in progress
- [ ] `NOTE TO SELF` blocks clearly marked as internal
