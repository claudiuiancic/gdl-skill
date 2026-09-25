# Profile object

An object whose cross-section comes from an Archicad complex profile rather than from
coordinates written in the script. Used for cornices, skirtings, framing members,
extrusions that must match a profile the project already defines.

## Reading the profile

Five requests, from p.553. All of them return dummy values and raise a warning if
called from the parameter script, so read profiles in the master or 3D script only.

`REQUEST("NAME_OF_PROFILE", index, name)` turns an index into a name.

`REQUEST("PROFILE_COMPONENTS", name_or_index, nComponents, compType1, ...)` gives the
number of components and their types: 0 core, 1 finish, 2 other. This is what lets an
object treat the structural core differently from the finish layers.

`REQUEST("PROFILE_DEFAULT_BOUNDINGBOX", name_or_index, xmin, ymin, xmax, ymax)`
returns the bounding rectangle relative to the profile origin — the cheapest way to
size something around a profile without walking its geometry.

`REQUEST("PROFILE_DEFAULT_GEOMETRY", ...)` returns the full polygon: vertex counts per
contour, then per vertex the coordinates and the edge visibility and status flags.
`REQUEST("PROFILE_COMPONENT_INFO", ...)` returns per-component data.

All five were introduced in Archicad 21.

## Using it

Declare the receiving arrays with `DIM ... []` and let the request size them; do not
assume a vertex count.

A request that fails returns 0. Check the return value before using the output — a
profile that was deleted from the project leaves an index that resolves to nothing,
and the object should degrade visibly rather than build garbage geometry.

The geometry arrives as contours with status flags per vertex. Those flags map onto
the same masking conventions as `PRISM_` and `POLY2_`, so the polygon can usually be
passed through with little translation; check the status code chapter at p.245 rather
than inventing the mask values.

## Sections and 2D

An extruded profile shows in section as the profile itself, so the 2D representation
should be derived from the same request rather than drawn separately — otherwise plan
and section disagree the first time someone edits the profile.
