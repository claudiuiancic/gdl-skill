# Free-standing object

The default subtype (General GDL Object,
`F938E33A-329D-4A36-BE3E-85E126820996`). Furniture, equipment, fittings — anything
placed on a storey rather than inserted into another element.

## Coordinate system

Origin at the bottom-left of the bounding box, x to the right, y away, z up. The
object sits on the storey plane, so geometry is built upward from z=0.

`A` is width along x, `B` is depth along y, `ZZYZX` is height along z. All three
carry `<Fix/>` in `paramlist.xml`.

## What it must have

Hotspots in both 2D and 3D, or the object cannot be grabbed on plan. The first
`HOTSPOT2` in the 2D script is the insertion point, so make it the natural handle —
the centre of a column, the front-left corner of a cabinet.

A drawn 2D symbol, not `PROJECT2`. The projection is slow and rules out a background
fill, and every object should have a background fill so it hides the fills and zones
underneath it. Make the fill type, its pen and the contour pen adjustable
parameters.

A 3D on/off switch, so the user can drop the object out of the 3D model without
deleting it.

## Standard parameter names

Graphisoft's own libraries use fixed names for recurring concepts; matching them lets
users edit several selected objects at once. `TREED` for the 3D switch, `D3D` for
detailed 3D, `BFT` background fill type, `BPN` background fill pen, `CPN` contour pen,
`MS` minimal space, `SW` side visible. The full list is in the Technical Standards
appendix.

## Stretchability

Objects can be made stretchable on plan where it makes sense — a beam, a worktop.
Curved fills placed in the 2D symbol do not survive stretching, so define fills in the
2D script instead. For vertical stretching use `ZZYZX`; note that `MULZ -1` before a
vertically stretchable body drops it below the automatically generated 3D hotspots, so
define the hotspots explicitly.
