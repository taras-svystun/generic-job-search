---
name: onboard
description: Interview a new candidate and fill the candidate profile (01-candidate-profile.md) and the behavioural profile (02-behavioral-profile.md). Use on first setup, when 01 is empty, or when the candidate says "onboard me", "set up my profile" or "update my profile".
---

# /onboard - Fill the Candidate Profile

You interview the candidate and write their answers into two files:
- `.agents/skills/job-application-assistant/01-candidate-profile.md` (required)
- `.agents/skills/job-application-assistant/02-behavioral-profile.md` (optional)

Every other skill reads 01 as its only source of facts. A gap here becomes a guess later, so
this interview is worth the time. It works for any profession and any country.

## Rules

- **Rounds.** Ask at most 5 numbered questions per round. Then stop and wait for the answers.
  A round below that lists topics instead of questions: turn each topic into a question; if
  there are more than 5, split it into two rounds.
- **Each question has a recommended answer and a short reason**, in this form:
  `3. Which contract types work for you? Recommended: employee or contractor, because it keeps
  more postings open.` Base the recommendation on what you know so far. With no data, recommend
  the safe default.
- **Define every term** the first time you use it, in plain words. For example: "ATS (the
  screening software that reads your CV before a person does)", "gross (before tax)".
- **Never invent a fact.** Write only what the candidate said or what the imported file shows.
  A missing fact is a question, not a guess.
- **Write after each round.** Put the answers into 01 or 02 at once, under the matching heading.
  Keep the headings exactly as they are: other skills point at them. Add the date
  (YYYY-MM-DD) to facts that change over time.
- **"None" is an answer.** When a section does not apply, write "none".
- **Language.** Talk in the language the candidate prefers. Write 01 and 02 in English unless the
  candidate asks for another language. Keep sentences short and plain.
- **Privacy.** Before the first round, say once: "01 will hold your personal data. Keep your copy
  of this repository private."

## Step 0. Check the current state

Read 01 and 02.
- If 01 is empty (only the skeleton): run every round below.
- If 01 already has content: show which sections are filled and which are empty, and ask
  whether to update one section or start over. Then run only the rounds for those sections.

## Round 1. Import and basics

Ask:
1. Do you have a CV or a LinkedIn profile export (a PDF or a text file)? If yes, give the file
   path or paste the text. Recommended: yes, because importing it first saves most of the
   interview.
2. Which roles are you aiming for right now, in order? Recommended: one or two, because a clear
   target makes every document sharper.
3. Which language should your CV be in? Recommended: the language of most postings you target,
   because recruiters screen in that language.
4. What location should the CV header show? Recommended: the true place that matches the
   postings you target (a city and country, or a country only), because recruiters filter by
   location.
5. What is your current status and earliest start date? Recommended: state it plainly, because
   forms ask for it.

If the candidate gives a file, read it. Draft Identity, Experience, Education, Skills and
Projects from it. Show the draft in short form and ask the candidate to correct it. Mark every
number you took from the file as "from CV, how measured?" for Round 6.

## Round 1b. Contact details

Run this round when there is no file, or the file lacks any of these fields. Ask only for the
missing ones:
1. Your name exactly as it should appear on documents. Recommended: the name on your ID or
   diploma, because background checks compare them.
2. The email for employers. Recommended: a plain one with your name, because recruiters judge
   it at a glance.
3. Your phone, with the country code. Recommended: include it, because many recruiters call
   first. Answer "none" to leave it off.
4. Links to show employers (LinkedIn, portfolio, GitHub, publications). Recommended: one or
   two that show real work, because a recruiter opens at most one or two.

Write the answers to 01 Identity.

## Round 2. Constraints

Ask about each field in 01's Constraints and Languages: work mode, locations and relocation,
working hours and time zones, contract types, work authorisation (where they may work without a
visa, and what to answer on forms), company size, stage or sector limits (for example "no
start-ups" or "no gambling companies"), each language with its level and whether they work
in it, and whether translation tools are fine for a language needed only in writing. Recommended answers lean towards keeping more postings open, unless the candidate has a
firm limit. Say that each constraint becomes a gate: a posting that breaks it fails at once.

## Round 3. Pay bands and fit rubric

Ask:
1. Your target pay per market or contract type: amount, currency, gross or net, and per year,
   month, day or hour. Recommended: a range, not one number, because it leaves room to
   negotiate.
2. The exact sentence you will say when asked about pay. Recommended: "I'm targeting <range>,
   depending on the overall package.", because it is short and anchors the talk.
3. Your floor: the lowest pay worth a talk. Recommended: flag postings near or under your band,
   and reject only a published range whose top is below the floor, because most postings publish
   no pay and the rest is negotiable.
4. Must-haves, deal-breakers and nice-to-haves (things that raise the score but never fail a
   posting). Recommended: three must-haves and three deal-breakers at most, because a long list
   fails almost every posting.
5. Weights for the fit score, or the defaults in `04-job-evaluation.md`. Recommended: the
   defaults, unless one area clearly matters more to you.

Remind the candidate that pay bands are internal: they never go into a CV or a letter unless the
posting asks for them there.

## Round 4. Positioning

Ask about the role tracks in order of interest and why the evidence fits each one, roles to
avoid (postings that compete on weak points), target sectors, what excites them about the work
and what drains them (in their own words), and the "years of experience" line they want, next to the strictest true
reading. Write both readings in 01.

## Round 5. Framing policy and disclosure

Explain the choice first, in plain words:

> Every document shows your true facts in their best light. The question is whether it may also
> stretch them a little.
> - **strict**: only true facts. No stretched number, scope or skill. Safest in interviews.
> - **generous**: small stretches inside limits you set, for example a slightly rounded-up
>   number, or a tool next to your real work that you learn before the interview. Each stretch
>   is listed in a truth report after every application, so you always know what you claimed.
>
> The risk of generous: an interviewer can probe any line of your CV. A stretched claim that you
> cannot explain in depth can cost you the offer, and it can hurt trust in the rest of the CV.
> Employers, official titles, dates and degrees are never changed under either policy.

Ask:
1. Strict or generous? Recommended: strict, because it carries no interview risk. Choose
   generous only if you will prepare every stretch before the interview.
2. Only if generous: what may stretch, and how far? Recommended: numbers by a small margin you
   can defend, and skills one step from your real work that you close before any interview,
   because both can be made true in time.
3. Anything you never want stretched, beyond employers, titles, dates and degrees?
   Recommended: add any licence, certificate or legal status, because a false one can end an
   offer.
4. What may be named in documents, and what may not (for example clients under an NDA, a
   non-disclosure agreement)? Recommended: name employers; describe clients by sector and size
   only, such as "a mid-size logistics company", because it is safe under most contracts.
5. Any style rule of your own (words to avoid, a tone)? Recommended: none, because the defaults
   in 01's Style already fit most roles.

Write the answer and today's date into 01's Framing policy section. If the candidate does not
answer, write `strict`, today's date, and "(default, no answer given)".

## Round 6. Experience, stories and current situation

Go through each Experience entry, newest first, one or two entries per round. Ask:
- What did you own, build or change? What was the result?
- Each number: how was it measured, or how can you explain the estimate?
- Which tools and methods did you use?
- Anything that must never be named (see Disclosure)?

Then ask for three to five Stories: real cases that prove a strength. Each needs the situation,
the task, what the candidate did, and the result (the STAR shape: Situation, Task, Action,
Result). Tie each story to its Experience or Project entry.

Then ask for References (role and relation only, letters or reviews in hand) and the Current
situation: notice period, why looking now, anything in parallel, anything that must stay out of
documents.

## Round 7. Behavioural profile (optional)

Ask whether to fill 02 now. Recommended: yes if the candidate has any assessment or manager
review, because it backs the culture-fit score with evidence. If yes, ask about: any formal
assessment (name, date, main results), work style, two to four strengths with a story each,
growth areas (internal only), and posting phrases that signal a strong fit or friction. Also
fill 01's Behavioral summary from the answers.

## Final check

1. Read 01 again. List every section with its state: filled, "none", or empty.
2. For each empty section, ask one last round (at most 5 questions), or write "none" with the
   candidate's agreement.
3. Check that Framing policy has a policy and a date. If not, write `strict` and today's date.
   Check that Identity has Name and Email. For CV template and File-name prefix, list the value
   or the default ("the `apply` skill picks from the posting"; "first initial and surname") and
   ask whether the default is fine.
4. Check that no section holds a guess: every fact came from the candidate or the imported file.
5. Show a short summary: the target roles, the gates from Constraints, the framing policy, and
   the number of Experience entries and Stories.

Then tell the candidate: "Your profile is ready. Open `SETUP.md` and do its next step." Run the
`onboard` skill again at any time to update a section.
