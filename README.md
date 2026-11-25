# Job Search Workspace

An agent-driven workspace for running your own job search. You give it a job posting. It checks
the fit, writes a tailored CV and cover letter in LaTeX, compiles and checks the PDFs, and logs
the application. It also preps interviews and drafts direct outreach to companies.

It works for any profession and any country. Your facts, limits, pay bands and rules live in one
file, the candidate profile. The workflow reads that file and assumes nothing.

## Who it is for

Anyone who applies for jobs and wants a careful, honest assistant: an engineer, a PhD
candidate, a mathematician, a designer, a nurse. You do not need to know LaTeX.

## What you get

- `/onboard`: an interview that fills your profile.
- `/apply`: fit check, tailored CV and letter, compile, checklist, tracker row.
- `/outcome`: record a reply, interview, rejection or offer.
- `/interview`: a prep pack for the next stage.
- `/find-companies` and `/outreach`: a shortlist and a direct approach to one company.
- Three LaTeX templates: classic CV, academic CV, cover letter.
- Small Python tools and tests that keep the output files consistent.

## Which agent

- **Claude Code:** works out of the box. `CLAUDE.md` imports `AGENTS.md`, and `.claude/skills/`
  holds symlinks to the real skills in `.agents/skills/`. On Windows, enable symlinks
  (`git config core.symlinks true` and Developer Mode) or the links check out as plain text files.
- **Other agents that read `AGENTS.md`:** open `AGENTS.md`, then follow the skills in
  `.agents/skills/<name>/SKILL.md` by hand or through your agent's skill support. Slash commands
  are Claude Code names; elsewhere, ask for the skill by name.

## Start

See `SETUP.md`: five steps from clone to your first application.

## Privacy

Your profile, CVs, letters, trackers and notes are personal data. `.gitignore` keeps them out of
git by default, and every `*.pdf` is ignored. Keep your copy of this repo private if you commit
your own data (see the optional block at the bottom of `.gitignore`).

## License and credit

MIT. See `LICENSE`. Original work by Mads Lorentzen (upstream); adapted by taras-svystun.
