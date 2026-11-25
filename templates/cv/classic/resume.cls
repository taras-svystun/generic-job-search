% resume.cls
% One-page resume class used by the FAANGPath Simple Template.
% The interface (\name, \address, rSection, rSubsection) follows the
% class that the FAANGPath template uses. It comes from the LaTeXTemplates.com
% "Medium Length Professional CV" by Trey Hunner (2010). This file is a fresh
% rewrite of that interface, not a copy of the original source.
% FAANGPath Simple Template: (c) FAANGPath, www.faangpath.com,
% licence Creative Commons CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/).
% Changes: placeholders only, class rewritten, layout kept.
\ProvidesClass{resume}[2024/01/01 One-page resume class]
\LoadClass[11pt,letterpaper]{article}

\usepackage[parfill]{parskip}
\usepackage{array}
\usepackage{ifthen}
\usepackage[hidelinks]{hyperref}
\pagestyle{empty}
\setlength{\tabcolsep}{0pt}

% Header
\def\name#1{\def\@name{#1}}
\def\@name{}
\def\addressSep{$\diamond$}
\let\@addressone\relax
\let\@addresstwo\relax
\let\@addressthree\relax
\def\address#1{%
  \@ifundefined{@addressone}{\def\@addressone{#1}}{%
    \ifx\@addressone\relax\def\@addressone{#1}\else
      \ifx\@addresstwo\relax\def\@addresstwo{#1}\else
        \def\@addressthree{#1}\fi\fi}}
\def\printaddress#1{\begingroup\def\\{\addressSep\ }\centerline{#1}\endgroup\par}
\def\printname{\centerline{\namesize\bfseries\MakeUppercase{\@name}}\par\nameskip}
\let\ori@document=\document
\renewcommand{\document}{%
  \ori@document
  \printname
  \ifx\@addressone\relax\else\printaddress{\@addressone}\fi
  \ifx\@addresstwo\relax\else\printaddress{\@addresstwo}\fi
  \ifx\@addressthree\relax\else\printaddress{\@addressthree}\fi}

\newcommand{\namesize}{\LARGE}
\newcommand{\nameskip}{\medskip}
\newcommand{\sectionskip}{\smallskip}
\newcommand{\sectionlineskip}{\medskip}

% A section: bold upper-case title, then a rule.
\newenvironment{rSection}[1]{%
  \sectionskip
  \MakeUppercase{\bf #1}%
  \sectionlineskip
  \hrule
  \begin{list}{}{\setlength{\leftmargin}{1.5em}\setlength{\itemsep}{0pt}%
    \setlength{\parsep}{0pt}\setlength{\topsep}{2pt}}
  \item[]
}{\end{list}}

% A subsection: {Organisation}{dates}{title}{place}
\newenvironment{rSubsection}[4]{%
  {\bf #1} \hfill {#2}%
  \ifthenelse{\equal{#3}{}}{}{\\ {\em #3} \hfill {\em #4}}%
  \smallskip
  \begin{list}{$\cdot$}{\leftmargin=0em\labelwidth=0.5em\itemsep=0pt\parsep=0pt\topsep=0pt}
  \renewcommand{\makelabel}[1]{\hfil ##1}
}{\end{list}\medskip}
