# Archetypes

One file per subtype. The subtype is not a label — it decides which reserved
parameters the object gets, which global variables Archicad fills in for it, how it is
placed, and what it is allowed to do. Read the matching file before writing any script
for an object that is not a plain free-standing one.

| If the object… | read |
|---|---|
| stands on a slab and can be placed anywhere | `object.md` |
| is inserted into a wall and cuts a hole in it | `door-window.md` |
| emits light | `lamp.md` |
| displays information about a zone | `zone-stamp.md` |
| annotates another element and follows it | `label.md` |
| reads or draws a complex profile | `profile.md` |
| is called by other objects and never placed | `macro.md` |

The subtype lives in `ancestry.xml` as a GUID. Never guess it: export an object of the
right subtype from Archicad, convert it with `libpart2hsf`, and copy its
`ancestry.xml`. Getting this wrong is not a cosmetic error — the object will be
missing the parameters its scripts expect and will fail at runtime, not at compile.

Page numbers refer to the GDL Reference Guide; read them with
`python3 scripts/manual.py --pages N-M`.
