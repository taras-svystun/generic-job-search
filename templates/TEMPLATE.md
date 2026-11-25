# LaTeX templates

Three templates. Pick one, copy it into your own folder, fill it, compile it.

| Variant | Folder | Use it for |
|---|---|---|
| Classic | `cv/classic/` | Industry jobs. One page, ATS friendly. |
| Academic | `cv/academic/` | Research, PhD and postdoc jobs. Education first, then publications, talks, grants, teaching. Can be longer than one page. |
| Cover letter | `cover-letter/` | Any job. One page. |

## How to pick

- Applying to a company: classic.
- Applying to a university or a research lab: academic.
- Not sure: classic. Use the academic one only if publications are your strongest proof.

## Compile

You need a TeX distribution (TeX Live or MiKTeX) with `pdflatex`. For a non-Latin script
(Cyrillic, Greek, Chinese and others), compile with `xelatex` instead and load `fontspec`
with a font that has those letters. Or use Overleaf: upload the files.

The repo keeps one file per application: `cv/main_<company>_<role>.tex` and
`cover_letters/cover_<company>_<role>.tex`. Start each one from a template:

    cp templates/cv/classic/resume.cls cv/
    cp templates/cv/classic/template.tex cv/main_acme_data_analyst.tex
    cp templates/cover-letter/template.tex cover_letters/cover_acme_data_analyst.tex
    cd cv && pdflatex -interaction=nonstopmode main_acme_data_analyst.tex
    cd ../cover_letters && pdflatex -interaction=nonstopmode cover_acme_data_analyst.tex

The classic CV needs `resume.cls` in the same folder as the `.tex` file. The academic CV and
the cover letter need no extra file. Delete `.aux`, `.log` and `.out` after compiling.

## Customise

- Fonts: add `\usepackage{lmodern}` or `\usepackage{helvet}` and `\renewcommand{\familydefault}{\sfdefault}` after `\documentclass`. Use plain fonts. ATS tools read them best.
- Sections: delete a section block or copy one. Put what the employer wants first.
- One page: cut instead of squeezing. Drop the oldest bullets first, then bullets that repeat
  a point. Keep the margins, font size and spacing as the template sets them.
- Page size: the classic CV uses US letter. Change `letterpaper` to `a4paper` in the `geometry` line of `template.tex` if you need A4 (most countries outside the US and Canada). The academic CV and the cover letter use A4; change `a4paper` in their `\documentclass` line the same way.
- Local norms: some countries expect a photo, a date of birth or a signature on a CV. ATS tools do not need them. Follow the norm of the country where the job is.

## ATS tips

- One column, no tables for layout, no images, no icons.
- Standard headings: Experience, Education, Skills, Projects.
- Write dates in one format everywhere.
- Put contact details as real text, not in an image.
- After compiling, select all text in the PDF and paste it into a plain text editor. If the order is wrong or characters are missing, fix it.
- Use words from the job posting only where they are true for you. The framing policy in `01` (Framing policy) decides how far a line may go.

## Credit and licence

The classic CV is the **FAANGPath Simple Template**, by the mentors at FAANGPath (www.faangpath.com).

- Source: https://www.overleaf.com/latex/templates/faangpath-simple-template/npsfpdqnxmbc
- Licence: Creative Commons CC BY 4.0, https://creativecommons.org/licenses/by/4.0/
- Changes made here: content replaced by placeholders; `resume.cls` rewritten with the same commands (`\name`, `\address`, `rSection`, `rSubsection`). The class interface comes from the "Medium Length Professional CV" of LaTeXTemplates.com (Trey Hunner, 2010).

CC BY 4.0 asks you to keep this credit and say that changes were made. Your own CV text is yours. The academic CV and the cover letter are original to this repo.
