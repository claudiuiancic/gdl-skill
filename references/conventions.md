# Conventions

Digest of Graphisoft's GDL Technical Standards (guidelines for professional library
developers). Written for an older Archicad, but these are the conventions the
standard libraries still follow. Read this when creating a new object or reviewing
one, not for syntax questions.

## Parameters

Keep the count to the minimum that does the job; a very configurable object is a
hard-to-use object. Beyond five to ten parameters, group them under title
parameters. The hard ceiling is 125 per object.

The same concept must use the same variable name and the same parameter name in
every object of a library, otherwise multi-selection editing breaks. Variable names
run two to eight characters, parameter names up to twenty, both named after the
function they serve.

Keep values and combinations inside valid limits with the parameter script rather
than letting the object throw errors. Use `LOCK` for parameters that cannot apply in
the current configuration, and show their real values with `PARAMETERS`.

Automatic resets need care. Circular resets are a defect. `GLOB_MODPAR_NAME` gives
the name of the last modified parameter, which is what makes conditional defaults
possible. If a parameter is disabled under some condition, give it a sane default
when that condition later changes, or the object errors on an illegal zero value.

## Master script

It holds the definitions and calculations that both 2D and 3D need, plus the
attribute definitions — material, fill, line type — so a change happens in one place.

No `END` here: it prevents the parameter script from running at all.

The Technical Standards state that error line numbers reported by Archicad's own
dialog are counted from the master script, the scripts being concatenated. This is
from the Archicad 6.5 era and has not been re-verified. LP_XMLConverter, by contrast,
reports per file — confirmed on Archicad 29.

When the master script clamps a parameter, the parameter script must set the same
value with `PARAMETERS` so the settings dialog agrees with the geometry.

## 2D script and symbol

Plan symbols follow drawing standards and stay simple enough to read at a glance.
Only necessary hotspots; the first one is the natural insertion point of the element.

Give every object a background fill to hide fills and zones underneath, with type,
pen and contour pen adjustable.

Make symbols scale-sensitive where it matters, driven by `GLOB_SCALE`. Below 1:20
there is normally nothing worth drawing.

Avoid `PROJECT2`: it slows plan regeneration and rules out background fills. Avoid
text placed in the 2D symbol; script it instead so it stays scale-sensitive and
translatable. For stretchable objects, define fills in the script rather than the
symbol — curved fills in a symbol do not survive stretching.

Always check that the plan symbol covers the 3D model.

## 3D script

Model no more detail than the drawing needs, and give every object a 3D on/off
switch. Control the segmentation of curved surfaces with `RESOL`, `TOLER` and
`RADIUS`. Closed bodies regenerate faster than open ones.

Use status codes to keep hidden-line output clean: contours of curved surfaces
visible, unnecessary edges hidden.

`DEL TOP` only at the end of the script. Restore the coordinate system before `END`.

`MULZ -1` before a vertically stretchable object drops it below the automatically
generated 3D hotspots; define the hotspots explicitly to avoid it.

`BODY -1` after a hollowed shape whose holes are filled with transparent surfaces —
without it, shadows are wrong.

Empty parameter buffers with `GET(NSP)` once used.

Never redefine global variables. If there is no alternative, restore them at the end.

Use `COOR` when the default texture mapping gives a bad result. Note that a
coordinate box larger than the model makes the object preview no longer fit its
window in the settings dialog.

Style: definitions and calculations at the top, command names in capitals, indented
flow-control bodies, comments in English.

## Macros

A macro is worth extracting when several objects call it — not for a single caller,
which only makes changes harder. Avoid macros calling macros. Prefer macro objects
to plain macro files: they can carry previews and comments.

Never build a macro name out of a parameter; archives only keep the default macro.
Call with `CALL "name"`, quotation marks included, and use underscores instead of
spaces in macro names. Macro files open with their parameter definitions, and close
by clearing transformations and buffers, then `END`.

Custom attributes shared across a library belong in a Master GDL script, named
`Master_GDL <name>.gdl`.

## Naming and structure

Names state function and stay short. Object names cannot exceed 27+3 characters or
Archicad will not load them. No special characters. Do not mix object types in one
folder; keep macros and textures in their own folders. No two files in a library may
share a name even with different extensions. Keep the folder tree under six levels.

## Quality checking

Load the library and check for missing parts. Place every object and every
door/window on a plan, check the 2D symbols, then open the 3D window — errors during
generation show up in the report. Browse the settings dialogs for previews and
interface windows. Verify defaults. Delete cache and precompiled binaries before
delivery.

## Parameter naming (house convention)

Not from Graphisoft — a convention worth keeping consistent across our own library,
because it makes the parameter table readable and makes `check.py` more useful.

Prefix quantities with `n_` (`n_shelves`), booleans with `has_` (`has_back`, values
0/1), materials with `mat_`. Suffix dimensions with `_thk`, `_h`, `_w`, `_d`.
Derived variables computed in the master script start with `_`.

Never invent a semantic alias for a reserved parameter: width is `A`, depth is `B`,
height is `ZZYZX`. Writing `width` or `height` creates an unassigned variable that
compiles fine and fails at runtime.
