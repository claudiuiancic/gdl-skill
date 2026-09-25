# Fixing an object

## First, classify the failure

The four kinds fail differently and are diagnosed differently. Getting this wrong
wastes the most time, because a conversion failure looks like a script error.

**Conversion** — LP_XMLConverter refuses the folder. Messages look like
`(0) : error: Missing ParamSectHeader`, with a number in parentheses at the front.
The problem is in the XML, not in any `.gdl` file. Check `paramlist.xml` and
`libpartdata.xml` for unclosed tags, unescaped `<`, `>` or `&`, a missing
`<![CDATA[...]]>` around a description, or a wrong encoding.

**Parse** — Archicad reports at load or on opening the object:
`Error in 3D script, line 12: Missing END`. The script is syntactically wrong.
`scripts/check.py` reproduces most of these offline, so run it first.

**Runtime** — the object compiles and only fails when placed or when a parameter
changes: undefined variable, illegal value, missing macro. These depend on parameter
values, so they hide at the defaults and appear at the extremes.

**Silent** — it compiles, places, and is simply wrong. No message to work from. Go to
the last section.

## Which file does the reported line belong to

It depends on the tool, and getting this wrong sends you to the wrong file.

**LP_XMLConverter reports per file.** A message like
`cub_new(17) : warning: (in Script_3D) : Uninitialized variable` means line 17 of
`3d.gdl` itself. Verified against Archicad 29 — the master script's length does not
shift it. The script is named in the message, so trust it.

**Archicad's own error dialog may not.** The Technical Standards, written for Archicad
6.5, state that the line number in Archicad's alert is counted from the top of the
master script, because the scripts are concatenated before execution. This has not
been re-verified on a current version. Take it as a fallback rather than a rule: if a
number reported by Archicad lands past the end of the file, or on a blank line,
subtract the length of `1d.gdl` and look there.

## Order of work

1. Run `python3 scripts/check.py <folder>`. Fix every error it reports before
   reading the Archicad message again — one syntax defect often produces several
   misleading messages downstream.
2. Look up the failing command with `python3 scripts/manual.py <COMMAND>`. Wrong
   argument counts and wrong argument order are the most common cause of a command
   that "should work".
3. Make the smallest change that could fix it, then recompile. Do not rewrite a
   script that mostly works — a rewrite trades one known defect for several unknown
   ones, and loses the parameter names other objects may depend on.
4. If the cause is not obvious, bisect: comment out half the 3D script with `!`, or
   reduce a loop to one iteration, and recompile. The half that still fails contains
   the defect.

## Message to cause

| Message | Cause | Fix |
|---|---|---|
| `Missing END` | 3D script does not end with `END` | `END` on the last line of the main flow; sub-routines end with `RETURN`, not `END` |
| `ENDIF expected` | multi-line `IF ... THEN` never closed | add `ENDIF` |
| `Unexpected ENDIF` | single-line `IF ... THEN <statement>` given an `ENDIF` | delete it, or split into a multi-line block |
| `NEXT expected` / `NEXT without FOR` | unbalanced loop | one `NEXT` per `FOR`, nesting included |
| `Undefined variable <name>` | name absent from `paramlist.xml` and never assigned | declare it, or assign it in `1d.gdl` before use. Watch for semantic aliases — `width` instead of `A` |
| `Missing parameter(s) after function` | `NOT` written without parentheses | `NOT (expression)` |
| `Missing CALL keyword (not recommended)` | a statement starts with a word that is not a GDL command | usually a typo in a command name; check `references/command-index.md` |
| `Wrong number of arguments` | command signature mismatch | most often `PRISM_` without its height argument, or a vertex count that disagrees with `n` |
| `illegal (0) value of variable` | a parameter was disabled by a condition and left at zero | give it a default when the condition changes, in both `1d.gdl` and `vl.gdl` |
| stack unbalanced / `DEL without ADD` | transformations not undone on every path | balance each branch separately; `DEL TOP` only at the end |
| parameter script appears not to run | `END` present in the master script | remove it |

## Instruments

`PRINT` writes to an alert box or the report window — the fastest way to see what a
variable actually holds (Reference Guide p.366). `OUTPUT` writes to a file (p.367).
`BREAKPOINT` is documented at p.360.

For a primitive-based body whose shape is wrong, substitute a small sphere for each
vertex to see where the vertices actually land, then limit the loop to one, two, three
iterations to see the order in which they are placed. Vertices are invisible, so
without this you are debugging blind (GDL Handbook, chapter 20.8).

For a parameter script that misbehaves, the Handbook covers the technique at
section 15.11.3.

## When it compiles but never appears in the library

A different failure from wrong geometry, and the more confusing one because there is
no message at all. The cause is metadata, not GDL — see the placeability section in
`SKILL.md`, and run `scripts/check.py`, which tests for all four causes.

The diagnostic that finds anything the checker misses: in Archicad, create a new object
of the same subtype by hand, paste the suspect scripts into it, save it, and convert it
back with `libpart2hsf`. Comparing that reference folder against the failing one, file
by file and including the encoding bytes, exposes the difference quickly. Do not guess
in the GDL scripts — when an object compiles but is not placeable, the scripts are
almost never the cause.

## When it compiles but looks wrong

Start with `python3 scripts/preview.py <folder>`. It runs the 3D script and reports the
bounding box, geometry that never gets built, sizes that disagree with `A`/`B`/`ZZYZX`,
and parameters that move nothing. A dead parameter and a model that ignores its own
height are the two cases it catches that no amount of reading the script reliably does.

If it comes back clean, work down this list.

Transformation stack: an unbalanced `ADD`/`ROT`/`MUL` displaces everything that
follows, and the displacement is often invisible in the current view. This is the
first thing to check, every time.

Units: lengths in metres, angles in degrees. A value that looks like millimetres is a
bug that produces geometry a thousand times too large.

`MULZ -1` before a vertically stretchable object drops it below the automatically
generated 3D hotspots — define hotspots explicitly.

Shadows wrong through a hollowed shape with transparent infill: `BODY -1` after it.

Texture mapping wrong: `COOR` sets the method. A coordinate box larger than the model
also makes the settings-dialog preview no longer fit.

The plan symbol does not match the model: 2D and 3D are separate scripts and nothing
keeps them in sync. Check that both read the same parameters, and that any clamping
happens in the master script where both can see it.

Something behaves correctly at the default values and wrongly elsewhere: the defect
is in a range, not in a line. Change each parameter to its minimum and maximum before
concluding the object is fixed.
