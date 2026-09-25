# Creating an object from scratch

Use this path when there is no existing object to start from. The alternative —
copying a similar object and editing it — is usually better when one exists, because
it inherits a valid identity, subtype and parameter conventions for free.

## Start from the template, not from an empty folder

`assets/template-object/` is a minimal object that compiles and passes
`scripts/check.py`. Copy it and rename. It already contains the files, the header
blocks and the reserved parameters, which is most of what is easy to get wrong and
tedious to reconstruct.

Two things must change immediately after copying:

**A new GUID** in `libpartdata.xml`, replacing `REPLACE-WITH-A-NEW-GUID`. Two objects
sharing a GUID collide in a library. Generate one with
`python3 -c "import uuid; print(str(uuid.uuid4()).upper())"` — Archicad writes them
uppercase.

**The subtype** in `ancestry.xml`. The template uses the General GDL Object GUID
(`F938E33A-329D-4A36-BE3E-85E126820996`), which is right for a free-standing object.
For anything else — a door, a window, a lamp, a zone stamp, a label — read
`references/archetypes/` for that subtype first, and do not guess a GUID. Save an object of that subtype from Archicad, convert it with `libpart2hsf`,
and copy its `ancestry.xml`. Subtype decides which reserved parameters and global
variables the object gets, so it has to be right before any script is written.

Fill in `libpartdocs.xml` — author and licence — while copying, not later. It is the
only record of who made the object and under what terms, and an empty one propagates
through every object copied from it.

## Parameters before geometry

Write `paramlist.xml` first and completely, then the scripts. Doing it the other way
round produces scripts full of names that do not exist, which is the single most
common failure mode.

Valid type tags: `Length`, `Angle`, `RealNum`, `Integer`, `Boolean`, `String`,
`PenColor`, `FillPattern`, `LineType`, `Material`, `Title`, `Separator`. `Float`,
`Real`, `Int`, `Bool`, `Text` and `Pen` are not valid — they are the names a
programmer expects, and Archicad rejects them.

`A`, `B` and `ZZYZX` come first, carry `<Fix/>`, and mean width, depth and height.
Never introduce `width`, `height` or `depth` as aliases.

`Title` entries are not parameters, they are headings that group the list in the
settings dialog. Past five or six parameters, group them. Descriptions are wrapped in
`<![CDATA["..."]]>`, quotation marks included.

Naming follows `references/conventions.md`: `n_` for counts, `has_` for 0/1
switches, `mat_` for materials, `_thk` `_h` `_w` `_d` for dimensions.

## Then the master script

`1d.gdl` does three things and nothing else: clamp the inputs to valid ranges,
compute derived values, choose attributes shared by 2D and 3D.

Clamping belongs here because both the 2D and 3D scripts must see the same corrected
value. When a clamp changes what the user should see in the dialog, mirror it in
`vl.gdl` with `PARAMETERS`, or the dialog and the geometry disagree.

No `END`. It stops the parameter script from running, silently.

## Then 3D, 2D and vl

Choose the geometry command deliberately — `references/command-selection.md` gives the
ladder and the rule that you start at the lowest rung that works.

Build the 3D model from the parameters, never from hard-coded numbers. Hotspots at
the corners of the bounding box at minimum, or the object cannot be grabbed.

The 2D symbol is drawn, not projected. `PROJECT2` exists but it slows plan
regeneration and rules out a background fill; draw the symbol with `RECT2`, `POLY2_`,
`LINE2`, `ARC2` instead, and give it its own hotspots.

`vl.gdl` holds `VALUES`, `LOCK`, `PARAMETERS`, `HIDEPARAMETER` — and only these
belong there. The checker flags them when they appear in 2D or 3D.

## Before compiling

Run `python3 scripts/check.py <folder>`. Fix every error. Then compile with
`hsf2libpart`, capturing both stdout and stderr.

A first compile that succeeds means the scripts parse. Place the object in Archicad,
open the 3D window, and change every parameter to its extremes — most defects in a
new object appear only at the edges of the parameter ranges, not at the defaults.

## The minimum that compiles

Strictly, an object needs `libpartdata.xml` with a GUID, `ancestry.xml` with a
subtype, `paramlist.xml` with `A`, `B` and `ZZYZX`, and at least one script.
`libpartdocs.xml` and `calledmacros.xml` are written by Archicad on export and should
be kept, but an object without them still compiles. The
template adds `2d.gdl`, `3d.gdl`, `1d.gdl` and `vl.gdl` because an object without a
plan symbol is not usable, whatever the compiler says.

The version numbers in `libpartdata.xml` (`Version`, `SectVersion`) are tied to the
Archicad release. If a compile fails on something structural rather than on GDL
syntax, take those numbers from a freshly exported object of the same Archicad
version rather than editing them by hand.
