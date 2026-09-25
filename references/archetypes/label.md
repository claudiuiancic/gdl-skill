# Label

An annotation object attached to another element, or placed independently. It reads
the element it labels and writes text about it. Almost entirely a 2D object.

## What a label can see

A label gets the parameters of the element it is attached to, which is most of the
global-variable chapter: door and window parameters (p.387), wall (p.394), column
(p.396), beam (p.402), slab (p.407), roof (p.453), fill (p.454), mesh (p.455), curtain
wall (p.458), skylight (p.463), morph (p.468), stairs and railings (p.410 onwards).
Attribute sets for those elements are at p.476 onwards.

Label-specific parameters are at p.389, and the label parameter block at p.516.
Deprecated label globals at p.471.

`REQUEST "CUSTOM_AUTO_LABEL"` (p.532) is how a label asks for the automatic text
Archicad would otherwise generate.

## Behaviour

The label follows its element. Position, rotation and the pointer line are handled by
Archicad, so the script draws in the label's own coordinate system and should not try
to compensate for the host element's rotation unless it genuinely needs to stay
horizontal.

Text length is the recurring problem: use `TEXTBLOCK_` with a width, and let the block
wrap, rather than assuming the string fits.

A label that reads a parameter the host element does not have gets an empty or zero
value rather than an error. Test against every element type the label claims to
support, not only the one you developed it against.
