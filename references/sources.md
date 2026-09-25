# Sources

Five manuals are available locally. Copy them into `references/` (they are not
bundled with the skill). Each answers a different kind of question — pick by
question type, not by whichever is nearest.

## GDL_Reference_Guide_29.pdf — 841 pages, Archicad 29

The authority on syntax. Every command, its parameters, restrictions and status
codes. Indexed in `command-index.md`; read pages with `scripts/manual.py`.
Use it for: what does this command take, what do these status bits mean, what is
this global variable called. Do not use it to learn how to build something —
it documents parts, not assemblies.

Chapter starting pages: General Overview 35, GDL Syntax 45, Coordinate
Transformations 50, 3D Shapes 56, 2D Shapes 215, Hotspots 237, Status Codes 245,
Attributes 258, Non-Geometric Scripts 289, Expressions and Functions 328,
Control Statements 354, Miscellaneous (global variables, requests) 370, Index 734.

## GDLHandbook.pdf — 494 pages

Structured teaching text with a full table of contents. Explains the model behind
the syntax: what an object is, variables and scope, the stack, arrays, string
handling, operators. Use it when the question is "why does this behave this way"
or when the Reference Guide entry assumes a concept.

Early chapters: Introduction 17, Anatomy of a GDL Object 22, Variables 42,
Operators and Expressions 54, Text Strings 65, Using the Stack 75.

## GDL_Cookbook_4.pdf — 180 pages

Worked examples. No embedded table of contents, so search it by text rather than
by page. Use it for patterns — how a real object is put together end to end.

## Crearea_obiectelor_GDL.pdf — 206 pages, Romanian

Translation of "Creating GDL Objects". Task-oriented: saving 2D symbols from the
floor plan, converting 3D models into objects, and so on. Useful for the Archicad
side of the workflow rather than the language.

## Technical__Standards_v1_0.pdf — 72 pages

Graphisoft's guidelines for professional library developers. Older (written for
Archicad 6.5) but the conventions it states are still the ones libraries follow:
naming, parameter organisation, what belongs in which script, quality checks.
This is the source for house rules, not for syntax. Several of the rules in
SKILL.md come from here.

## Credit

The pre-compile checks in `scripts/check.py` were written from scratch, but the list
of what is worth checking — and several of the false-positive filters — came from
reading OpenBrep (https://github.com/byewind1/openbrep, MIT), an Archicad GDL
workbench whose static checker solves the same problem. Its HSF parser is also what
corrected our file-layout description. The idea behind `scripts/preview.py` — run a
subset of GDL to find out whether the geometry exists, matches the declared sizes and
responds to its parameters — is theirs too, as is the fixture-and-scorecard shape of
`tests/`. No code was copied; both scripts are independent implementations.
