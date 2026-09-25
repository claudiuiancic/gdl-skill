# Choosing a geometry command

GDL usually offers three or four ways to build the same shape. The choice decides how
many surfaces the object costs, how easy it is to change later, and how likely it is
to compile at all. The default tendency — of a person and of a model — is to reach for
the impressive command. Resist it.

## The rule

Start at the lowest rung that can express the shape. Move up only with a reason, and
write that reason in a comment on the line where you use the higher command. If the
reason cannot be written in one clause, the rung is probably too high.

A shape built from four `BLOCK`s is easier to read, cheaper to regenerate and simpler
to parametrise than the same shape built from one `SWEEP`.

## The ladder

**1. `BLOCK`, `BRICK`, `CPRISM_`** — boxes and panels. `BLOCK a, b, c` (p.56) is the
default for anything rectangular. Move up when the shape is not a rectangular box, or
when top, bottom and sides need different surfaces — that is what `CPRISM_` (p.63) is
for.

**2. `CYLIND`, `SPHERE`, `ELLIPS`, `CONE`** — analytic solids of revolution.
`CYLIND h, r` (p.57), `CONE h, r1, r2, alpha1, alpha2` (p.59). Use these for anything a
single analytic surface covers. Move up only when one shape cannot cover it — a
stepped shaft, a vase with a neck.

**3. `PRISM_`, `BPRISM_`** — an arbitrary 2D outline extruded vertically.
`PRISM_ n, h, x1, y1, s1, ...` (p.60). This is the workhorse for non-rectangular
panels and profiles. `BPRISM_` (p.68) adds rounded vertices. Move up when the
extrusion is not vertical, or the top face must be sloped or offset.

**4. `EXTRUDE`** — an outline extruded along a vector.
`EXTRUDE n, dx, dy, dz, mask, ...` (p.105). Sloped tops, non-vertical extrusion.
Move up when the outline must rotate about an axis, or follow a curve.

**5. `REVOLVE`** — a genuine solid of revolution.
`REVOLVE n, alpha, mask, ...` (p.110). Balusters, vases, turned legs, capitals.
Justify it by stating that the shape really is rotationally symmetric — a plain
cylinder belongs at rung 2. The revolved outline cannot contain holes.

**6. `SWEEP`, `TUBE`** — a section moved along a path.
`SWEEP n, m, alpha, scale, mask, ...` (p.124), `TUBE n, m, mask, ...` (p.127).
Justify by stating that the path really is curved. A straight path is a rung-3 or
rung-4 job and will be more stable. Build a low-segment version first, confirm it
compiles, then refine.

**7. `RULED` (p.118), `COONS` (p.136), `MASS` (p.139), and `BODY`/`VERT`/`EDGE`/`PGON`
primitives** — freeform surfaces and hand-built bodies. The last resort. Primitives
in particular require a strict vertex order, correct edge directions and outward-facing
polygon normals, and they are invisible while you build them, so debugging is slow.
See `workflows/debug.md` for the sphere-per-vertex technique before starting.

## Cost, not elegance

Surface count drives regeneration speed, and objects get placed hundreds of times in a
project. Control curved-surface segmentation deliberately with `RESOL`, `TOLER` or
`RADIUS` rather than accepting the default. A closed body regenerates faster than an
open one — a `CYLIND` beats a `TUBE` used as a pipe.

Model no more detail than the drawing scale will ever show, and give the object a 3D
on/off switch so the user can drop it out of the model entirely.

## For 2D

The same principle, shorter ladder. `RECT2`, `LINE2`, `CIRCLE2`, `ARC2` first; `POLY2_`
when the outline is genuinely irregular; `FRAGMENT2` when a drawn fragment is needed at
a fine scale. `PROJECT2` last: it is slow and rules out a background fill, so it is
acceptable for a quick symbol and wrong for an object that will be placed often.

## Reviewing an existing object

When asked to optimise rather than create, walk the ladder downward: for each geometry
command, ask what the lowest rung that still expresses the shape is. Report the
candidates and the reason each one is or is not reducible. Do not rewrite the geometry
unasked — a working object that is one rung too high is not a defect.
