---
framework_version: 2.0.0
---

# Cover Letter Template and Tailoring Guide

## Template: `templates/cover-letter/` (plain `article`, pdflatex)

- **Skeleton:** `templates/cover-letter/template.tex`. Copy it; never edit the template itself
  for one application. `templates/TEMPLATE.md` says how to compile it and how to change fonts
  and page size.
- **Facts** come only from `01-candidate-profile.md`. Old letters in `cover_letters/` give shape
  and phrasing, never facts.
- **Output:** `cover_letters/cover_<company>_<role>.tex`. Copy any other file from the template
  folder beside it.
- **Compile:** `cd cover_letters && pdflatex -interaction=nonstopmode cover_<company>_<role>.tex`,
  or `xelatex` for a non-Latin script (see the pitfalls below).
- **Exactly 1 page**, signature included. Read the PDF: nothing cut off, bullets in the body
  font.

## Shape of a good letter

1. Greeting.
2. Opening: the company's own product or problem, then one line on what the candidate does. A
   full letter adds one real story from 01 Stories that the CV does not tell.
3. A short lead-in, then 3-4 bullets, each with a bold label mapped to a line of the posting.
4. "Why this role": what the candidate brings to the team, not what they need from it.
5. Logistics only if they help (start date, time zone, notice period), from 01.
6. A short ask and the closing.

## Known LaTeX pitfalls

- **`\\` after a list.** A line break (`\\`) right after `\end{itemize}`, or a macro that adds
  one, gives `! LaTeX Error: There's no line here to end.` and no PDF. End the paragraph before
  the list and start a new one after it.
- **A doubled line break at the closing** gives the same error. Use one break, or none.
- **Non-Latin scripts** (Cyrillic, Greek, Chinese, Arabic...). If the template font has no
  glyphs for the script, the letter may compile with **no error** and print a page of missing
  characters. Use the same fix as `05-cv-templates.md` (LaTeX special characters): xelatex,
  `fontspec` and a font that covers the script. After compiling, confirm the log has no
  `Missing character` warnings.
- **Punctuation in other languages.** The "no em-dashes" rule in `03-writing-style.md` is for
  English prose. Other languages have their own punctuation rules, and some need a dash. Follow
  the rules of the letter's language.

## Tailoring guidelines

### Salutation
- If you know the hiring manager's name: "Dear [First Last],"
- Default: "Hi [Company] team," or the formal norm of the posting's language. Never "To whom it
  may concern".

### Content
- A personal project is named as the candidate's own ("In <Project Name>, my own end-to-end
  build..."), so it never reads as client work.
- The letter says what the CV cannot: why this company, how the candidate thinks. It never
  repeats a CV sentence, and it says each number once.
- **Salary:** none, unless the posting asks for it in the letter and has no form field for it;
  then one sentence with the figure from 01 Pay bands (the target or ask, never the floor).

### Length: hard 1-page limit
- **Word budget: 250-300 words** of body text (not counting LaTeX markup). 350 words usually
  overflow.
- **When the posting asks for "a few lines"** or a short note: 120-180 words.
- Count the blocks: opening + bullet paragraph + closing = 3. Add a 4th only if the others are
  short.
- When you add company content, trim elsewhere; do not add net length.

### Spacing
- Extra space between sections only if there is room. Never shrink spacing to fit; cut words.

### Bullet lists
- 3-5 bullets; each starts with a bold label (`\textbf{Label:}`) or an action verb.
- A bullet that starts with a literal `[` is braced, `\item {[text]}`, or it prints off the page
  and drops out of the text layer.

### LaTeX special characters
Escape these wherever they appear in body text:
- Ampersand: `\&` (company names: H\&M). Unescaped, the compile fails loudly.
- Percent: `\%` ("grew revenue 30\%"). Unescaped, it does **not** fail: everything after the
  `%` on that line is silently eaten as a comment.
- Dollar: `\$`, hash: `\#`, underscore: `\_`
- Tilde: `\textasciitilde{}`, caret: `\textasciicircum{}`, backslash: `\textbackslash{}`

### Letters in other languages
- Same structure in the posting's language, only if 01 Languages shows the candidate works in
  it; local date format and closing.

The checklist is in `/apply` Step 6; content rules are in `03-writing-style.md`. Send only the
documents the employer asks for, and follow its rules on anonymity (some employers ask for no
photo, no name or no age).
