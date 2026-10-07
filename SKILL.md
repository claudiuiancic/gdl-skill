---
name: gdl
description: Write, edit and debug GDL (Geometric Description Language) scripts for Archicad library parts — 3D scripts, 2D scripts, parameter and master scripts, HSF folders and .gsm objects. Use this skill whenever the user mentions GDL, Archicad objects, library parts, .gsm, .hsf, obiect Archicad, bibliotecă, script 3D/2D, or asks to create, modify or fix any parametric object, even if they do not name GDL explicitly.
---

# GDL for Archicad library parts

GDL is a BASIC-like language. Control flow and variable logic look familiar, but the
geometry model, the script split and the parameter system do not map onto anything
else. Most failures come from those three, not from syntax.

## Never invent a command

The command set is large and irregular, and a wrong signature either fails silently
or produces wrong geometry. `references/command-index.md` lists every command in the
GDL Reference Guide with its syntax line and page number. Look the command up there
before writing it. If it is not in the index, it is not a GDL command — say so.

When the syntax line is not enough — parameter meanings, status codes, restrictions —
read the manual pages:

```
python3 scripts/manual.py CYLIND          # print the pages for one command
python3 scripts/manual.py PRISM_ --after 2
python3 scripts/manual.py --pages 245-252 # a whole section, e.g. status codes
python3 scripts/manual.py --find texture  # search the index
```

This needs the PDF in `references/` (see `references/sources.md`). If it is missing,
say so rather than working from memory.

## Pick the path

Three kinds of task, three workflows. Read the one that matches before starting — and
if the object is not a plain free-standing one, read its subtype file in
`references/archetypes/` as well. The subtype decides the coordinate system, the
reserved parameters and the globals available; a door does not behave like a chair.

- **Creating** an object that does not exist yet → `workflows/create.md`
- **Editing** an existing object → the loop below
- **Fixing** a compile error or wrong behaviour → `workflows/debug.md`, and read it
  before touching the script: which file a reported line number refers to depends on
  which tool reported it.

All three share the same outer loop:

1. Convert the object to text if it is not already: LP_XMLConverter with
   `libpart2hsf` (one object) or `l2hsf` (a library). Never edit a `.gsm` directly.
2. Read `paramlist.xml` first — the parameters — then `ancestry.xml` for the subtype,
   then the scripts.
3. Edit the `.gdl` files.
4. Run `python3 scripts/check.py <hsf folder>`, then
   `python3 scripts/preview.py <hsf folder>`. Both are fast and need nothing
   installed. `check.py` reads the text; `preview.py` runs the 3D script and reports
   what the geometry actually came out as. Fix every error before compiling. Read the
   warnings — most are real, but some are cases the tools admit they cannot verify.
5. Compile with `convchecklibrary` (see below) rather than plain `hsf2libpart`, so
   Archicad's own checker runs too, and report the output verbatim. Capture **both
   stdout and stderr**: LP_XMLConverter on macOS writes its diagnostics to stdout, so
   a run that looks silent on stderr may still have failed.
6. Say what still needs checking in Archicad. Compilation proves the scripts parse.
   It proves nothing about the geometry.

## LP_XMLConverter

macOS, Archicad 29 (LP_XMLConverter 29.0.0). The path contains spaces — always quote
it. The executable is inside the .app bundle; a path ending in `LP_XMLConverter.app`
is a directory and fails with "permission denied".

    CONV="/Applications/Graphisoft/Archicad 29/Archicad 29.app/Contents/MacOS/LP_XMLConverter.app/Contents/MacOS/LP_XMLConverter"

Every conversion command takes `source` then `dest`, in that order:

    "$CONV" libpart2hsf <source.gsm> <destination folder>
    "$CONV" hsf2libpart <hsf folder> <destination.gsm>
    "$CONV" l2hsf <library folder> <destination folder>
    "$CONV" hsf2l <hsf folder> <destination library folder>

### Compiling with Archicad's own checker

`hsf2libpart` only converts. `convertlibrary` compiles a source tree *and* runs
Graphisoft's GDL checker over it — uninitialised variables, unused parameters,
precision warnings, thread safety of the 2D and 3D scripts, unused binary sections.
This is the authoritative check. `scripts/check.py` and `scripts/preview.py` are the
fast pre-filters that run before it; they need no Archicad and work in CI.

    "$CONV" convertlibrary -format hsf -reportlevel 2 -interpret -checkall \
            <source folder> <destination folder> "$GDL_STDLIB"

`-reportlevel 2` reports warnings as well as errors, `-interpret` runs the scripts,
`-checkall` turns on every check.

Three things about this command are easy to get wrong.

**The source is a folder of objects, not one object.** Each subfolder of the source is
compiled into one `.gsm` named after it. An HSF folder named `04_hsf` would produce
`04_hsf.gsm`, so copy the object into a temporary tree under the name it should carry.

**Ancestors must be resolvable.** Without them, every object reports
`Missing ancestor with main GUID {...}`. `$GDL_STDLIB` points at Archicad's built-in
library parts, extracted once with:

    "$CONV" extractpackage "<Archicad>/BuiltInLibraryParts.libpack" <tmp>
    "$CONV" extractcontainer <tmp>/BuiltInLibraryParts.lcf <destination>

The result is a `BuiltInLibraryParts` folder — that inner folder is what
`$GDL_STDLIB` must point at. Redo this after an Archicad upgrade.

**Exit code 0 does not mean clean.** Warnings — including uninitialised variables —
leave the code at 0, and a failing run still writes the `.gsm`. Read the text output
every time; never report success on the exit code alone.

`convchecklibrary` additionally verifies ancestry and macro-call consistency, but it
requires a full library index (`IDEntryList.dbe`) and fails without one on an
ordinary working folder.

## Anatomy of an HSF object

```
object-name/
├── libpartdata.xml    object identity — GUID, version. NOT the parameters.
├── paramlist.xml      the parameter list, typed. Read this first.
├── ancestry.xml       subtype / classification
├── libpartdocs.xml    author, licence, keywords
├── calledmacros.xml   macros this object calls
└── scripts/
    ├── 1d.gdl         master script — runs before every other script
    ├── 2d.gdl         floor plan symbol
    ├── 3d.gdl         3D model
    ├── vl.gdl         parameter script — VALUES, LOCK, PARAMETERS
    ├── ui.gdl         custom settings dialog
    ├── pr.gdl         properties / quantity take-off
    ├── fwm.gdl        forward migration (older object opened in newer Archicad)
    └── bwm.gdl        backward migration
```

There is no separate value-list script file: `vl.gdl` is the parameter script and
holds the value lists too.

Shared calculations and attribute definitions (material, fill, line type) go in the
master script, not duplicated in 2D and 3D. Anything that changes a parameter's value
or availability goes in `vl.gdl`, never in the 3D script.

Derived variables carry an underscore prefix (`_gap`, `_inner_h`) so it is visible at
a glance which names are computed and which come from `paramlist.xml`. Assign them in
the master script, before use — GDL evaluates top to bottom and an unassigned name is
a runtime error, not a compile error.

## Rules that break things when ignored

These come from Graphisoft's Technical Standards; the fuller digest is in
`references/conventions.md`.

- No `END` in the master script. It stops Archicad from running the parameter script
  at all, and the failure is silent.
- Line numbers in Archicad error messages are counted from the master script, not
  from the script you were editing. Check the master script first when a reported
  line makes no sense.
- A condition that resets a parameter in the parameter script usually needs its twin
  in the master script — `if x then parameters y=1` alongside `if x then y=1` —
  otherwise 2D and 3D calculate from a value the dialog does not show.
- Avoid circular parameter resets: X resetting Y resetting Z resetting X.
- `DEL TOP` belongs at the end of the 3D script and nowhere else. Balance every
  `ADD` / `MUL` / `ROT` with its own `DEL` instead. An unbalanced stack displaces
  everything after it, often invisibly in the current view.
- Restore the coordinate system at the end of the 3D script and close it with `END`.
- Do not redefine global variables; they affect every other object. If unavoidable,
  restore them before the script ends.
- Empty parameter buffers with `GET(NSP)` once their values are used.
- Lengths are in metres, angles in degrees. A value that looks like millimetres is a
  bug.
- `A`, `B` and `ZZYZX` are reserved (2D width, 2D depth, height). If the master script
  redefines `ZZYZX`, mirror it in the parameter script with `PARAMETERS` or the
  settings dialog shows the wrong number.

## Compiling is not the same as being placeable

An object can compile without a single error and still never appear in Archicad's
library, with no message anywhere. The compiler checks the scripts; it does not check
that the part has the metadata Archicad needs in order to classify it. Four things
cause this, in order of impact.

`ancestry.xml` must not be empty. It holds the chain of GUIDs linking the object to
its subtype, and an empty `<Ancestry></Ancestry>` means "no subtype", so there is no
category to offer it under. For a general object the chain is two GUIDs:
`F938E33A-329D-4A36-BE3E-85E126820996` then
`103E8D2C-8230-42E1-9597-46F84CCE28C0`. For any other subtype, copy `ancestry.xml`
from an object of that subtype exported from Archicad.

`paramlist.xml` must carry three hidden system parameters —
`AC_show2DHotspotsIn3D`, `ac_bottomlevel`, `ac_toplevel` — each with `<Fix/>` and
`<Flags><ParFlg_Hidden/></Flags>`. Archicad uses them for storey placement and hotspot
editing. Every placeable object exported from Archicad has them.

Every text file needs a UTF-8 BOM. Everything Archicad exports starts with `EF BB BF`,
`.xml` and `.gdl` alike.

`libpartdata.xml` should declare only the sections that exist. `Ancestry`,
`CalledMacros` and `Keywords` appear even when empty; conditional ones such as
`MigrationTable` are absent entirely on an object without migration history. Mirror a
real export rather than declaring sections for completeness.

`scripts/check.py` tests all four. `assets/template-object/` has them applied.

## What check.py looks for

Knowing the checks is useful while writing, not only after: unclosed `IF`/`ENDIF` and
`FOR`/`NEXT`; an unbalanced transformation stack; `END` in the master script; names
used but never declared in `paramlist.xml` nor assigned anywhere; `_`-prefixed derived
variables never assigned; a statement starting with something that is not a GDL
command (Archicad silently treats it as a macro call); `NOT` without parentheses;
placeholder lines left behind; a 2D script with nothing drawable in it; `VALUES` or
`LOCK` outside `vl.gdl`; a string option in a `VALUES` list that contains a comma
(Archicad then shows a text field instead of a dropdown, and nothing else reports it).

It deliberately reports "not statically verifiable" rather than guessing when pushes
sit inside a loop or a `DEL` takes an expression. A checker that cries wolf is worse
than no checker.

## What preview.py looks for

`check.py` reads the script; `preview.py` runs it. It executes the shape commands,
the transformations, `FOR`, `WHILE`, `REPEAT`, `IF`, `GOSUB`/`RETURN` to labelled
subroutines, arrays, strings and the `PUT`/`GET` buffer, with the parameter values
from `paramlist.xml`,
and reports four things text analysis cannot reach: `no_geometry` — shape commands ran
but nothing was built, usually a condition that is never true; `degenerate` — the model
is flat on an axis; `size_mismatch` — the bounding box disagrees with `A`, `B` or
`ZZYZX`, meaning the geometry ignores its own parameters; `dead_param` — perturbing a
parameter leaves the model byte-identical, so it is declared but not wired to anything.

It models a subset, so it lists the commands it skipped. A clean run is evidence, not
proof — it cannot see materials, hotspots, or whether the shape is the right shape.

## Verification checklist

Before reporting a task as done: the transformation stack balances; every parameter
referenced in the scripts exists in `libpartdata.xml`; the object has hotspots in
both 2D and 3D, otherwise it cannot be manipulated on plan; the plan symbol still
covers the 3D model; the object recompiles without errors.

<!-- TODO: add project-specific checks here as they come up. -->

## Reference files

- `references/command-index.md` — every Reference Guide entry with syntax and page
  number, plus the attribute directives. The first thing to open.
- `references/archetypes/` — one file per subtype: free-standing object, door and
  window, lamp, zone stamp, label, profile object, macro. Read the matching one
  before writing scripts for anything that is not a plain object.
- `references/conventions.md` — Graphisoft's library-development standards:
  parameters, naming, per-script rules, quality checking.
- `references/sources.md` — what each of the five manuals is good for.
- `scripts/manual.py` — prints manual pages on demand.
- `references/command-selection.md` — which geometry command to reach for. Read it
  before writing 3D geometry; the default instinct is one rung too high.
- `scripts/check.py` — the text checks, run at step 4 of the loop.
- `scripts/preview.py` — runs the 3D script and reports the bounding box, geometry
  that never gets built, sizes that disagree with A/B/ZZYZX, and parameters that do
  nothing.
- `tests/` — fixtures and `run_tests.py`. Run it after any change to either script.
- `INSTALL.md` — setting this skill up on a machine, and keeping it current after an
  Archicad upgrade. Not needed for ordinary work.
- `workflows/create.md`, `workflows/debug.md` — the two paths that are not plain
  editing. Read the whole file before starting, not while improvising.
- `assets/template-object/` — a minimal object that compiles and passes the checks.
  Copy it rather than writing an object from an empty folder.

## Output conventions

Report edits as a short list of what changed in which script and why, then the
compiler output, then what needs checking visually in Archicad. Do not paste whole
scripts back unless asked — the user has the files.
