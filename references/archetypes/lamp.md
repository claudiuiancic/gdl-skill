# Lamp

A free-standing object that also emits light. Geometrically it behaves like
`object.md`; what makes it a lamp is the `LIGHT` command and the switch Archicad gives
the user to turn it off.

## The LIGHT command

`LIGHT red, green, blue, shadow, radius, alpha, beta, angle_falloff, distance1,
distance2, distance_falloff [, ADDITIONAL_DATA ...]` — Reference Guide p.164. Read the
page before writing it; the falloff arguments do not behave the way the names suggest.

A lamp with no `LIGHT` in its 3D script is an object that looks like a lamp and lights
nothing. Conversely, `LIGHT` in a plain object subtype will not be controlled by the
lamp switch.

## Standard parameter names

Lamps have the longest list of conventional names of any subtype, and matching them is
what lets a user select twenty luminaires and change them together. From the Technical
Standards appendix: `AFO` angle falloff, `AIL` and `AOL` inner and outer light cone
angles, `ARL` arm length, `ALA` and `AUA` arm angles, `BRL` brightener light, `DIL`
diffuse light, `DIST1` `DIST2` distances, `DIF` distance falloff, `LCR` light cone
radius, `LIR` light cone in rendering, `SC` shadow casting, `SB` show bulb, `SLC` show
light cone, `RZ` and `RX` rotations, `LIN` inclination.

Geometry and material names follow the same pattern: `GSD` and `GSMAT` for the glass
sphere, `LSH` `LSL` `LBD` `LUD` `LSMAT` for the shade, `FXD` `FXW` `FXT` for the
fixture, `LTMAT` for the stand, `PILMAT` for the pillar.

## What to watch

The light cone shown in the rendering is a separate decision from the light itself —
users expect to turn the visible cone off while keeping the illumination.

Lamp objects are placed in large numbers, so keep the 3D model cheap: `RESOL` low on
small curved parts, closed bodies rather than open tubes.

Global parameters available to lamps for listing and labelling are at p.388.
