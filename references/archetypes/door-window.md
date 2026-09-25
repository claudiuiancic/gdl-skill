# Door and window

The hardest subtype, and the one where guessing costs the most. An object inserted
into a wall, cutting an opening in it, reacting to how the wall is drawn and how the
user clicks.

## The coordinate system is rotated

Once inserted, the x-y plane is **vertical** and the z axis points horizontally into
the wall. The origin sits at the bottom centre of the wall opening, on the exterior
side of the wall. This is what lets you model the elevation in the x-y plane, but it
inverts every intuition carried over from free-standing objects.

Three consequences worth memorising. Think of project zero as the external wall
surface. Anything inside the wall — the frame — is above zero. A door panel opening
outwards is below zero. When you draw in the floor plan window to build the shape,
visualise it as seen from inside the wall.

The 2D symbol is not drawn by your script in the usual sense: it comes from a built-in
projection not otherwise available, an upside-down side view from 90 degrees. Symbol
and 3D shape are fitted to the origin by the lower edge in y and the centre in x, with
no adjustment in z, so the object may extend beyond the wall in either z direction.

Reference Guide p.659 onwards.

## Eight positions, three globals

A door is correct when clicking to the right of the insertion point makes the leaf
open to the right. A window is correct when the side clicked is the outer side.

The position is a combination of three global variables: `SYMB_MIRRORED` (mirrored to
the Y-Z plane in 3D, to the Y axis in 2D), `SYMB_ROTANGLE` (180 means mirrored by the
wall's longitudinal axis), and `WIDO_REVEAL_SIDE` (flipping). Eight states in total,
illustrated at p.660.

Different parts react differently: a leaf follows the transformations, a cavity
closure must not. Decide part by part and neutralise what should not move. The
canonical neutralising block is at p.662 — `bRotated = round_int(SYMB_ROTANGLE) = 180`,
then `ROT2 180` / `ROTY 180`, `MUL2 -1, 1` / `MULX -1`, and an `EXOR` test before
shifting by the wall thickness.

For a manufacturer library modelling a real window, flipping is physically wrong — a
real window cannot be turned inside out. The script should undo what Archicad does, or
the object should refuse the option.

## Matching the wall

The wall's own attributes are available as globals, which is how a jamb or a filling
body can match the wall it sits in: `WALL_MAT_A`, `WALL_MAT_B` and `WALL_MAT_EDGE` for
surfaces; in 2D, `WALL_SECT_PEN`, `WALL_FILL_PEN` and `WALL_FILL`. Composite walls use
the corresponding composite globals. Full list at p.390.

The bottom surface of an element should match the outside of the wall, the top surface
the inside.

## Cutting the opening

`WALLHOLE` is the simplest way to cut a custom hole, with two limitations: the opening
cannot be concave, and in curved walls the side surfaces stay parallel rather than
radial. The workaround for non-rectangular openings is to add filling bodies to the
rectangular hole Archicad cuts automatically.

A filling body must match the wall's attributes, must use the same resolution as the
wall in the curved case — the start point of the `CPRISM_` has to coincide with the
wall's, or the segments will not line up — and must be neutralised against mirroring,
rotation and flipping, since it should never follow them.

In 2D the family is `WALLHOLE2`, `WALLBLOCK2`, `WALLLINE2`, `WALLARC2`, documented
from p.663.

## Details panel

The oversize and wall inset fields accept only parameters and global variables, and
only 127 characters. There is no flow control there, so use logical expressions
instead: `(a<100)*x` means "x if a<100", `not(a<100)*x` means "0 if a<100".

The nominal frame thickness matters in three places: flipping mirrors the part and
drags it back by that value; the parapet wall inset needs it for zones to update
correctly; and it shifts placement in curved walls.

## Scale sensitivity

Plan symbols for doors and windows normally change with `GLOB_SCALE`. Below 1:20 there
is usually nothing worth drawing — if finer detail is genuinely needed, draw fragments
in the 2D symbol window and place them with `FRAGMENT2`.

## Sections

There is no separate section script. `GLOB_CONTEXT` tells the script which context it
is running in — section, elevation, the library part editor, the settings dialog,
listing — and each needs its own specification. For sections, prefer `PLANE`, `EXTRUDE`
and polygon commands over prisms so the model is hollow and shows as lines rather than
filled polygons; mask unwanted boundary lines as invisible.
