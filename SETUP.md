# Setup: five steps

1. **Clone** the repo and open it in your agent (for Claude Code: run `claude` in the folder).
   Keep your copy private if you will commit personal data.
2. **Make a venv and run the tests.**
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   python3 -m unittest discover -s tests -t .
   ```
   All tests should pass. Optional: `pip install pypdf` for better PDF text checks.
3. **Install TeX.** You need `pdflatex` (TeX Live, MacTeX or MiKTeX) and Poppler's `pdftotext`
   (`brew install --cask mactex-no-gui` and `brew install poppler` on macOS, `sudo apt install texlive-full poppler-utils`
   on Debian or Ubuntu). Check: `pdflatex --version` and `pdftotext -v`. No TeX? Upload a template
   from `templates/` to Overleaf, but the agent can then not compile and check it for you.
4. **Run `/onboard`.** Answer the questions. The agent fills
   `.agents/skills/job-application-assistant/01-candidate-profile.md`. Read it afterwards and
   fix anything wrong: it is the only source of facts.
5. **Run `/apply`** with a real job posting (a URL or pasted text). You get a fit verdict, a CV,
   a cover letter if you ask for one, checked PDFs and a tracker row. Read the draft before you send anything.
   You send every message yourself.
