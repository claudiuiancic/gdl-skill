# Macro and macro object

A library part called by other objects rather than placed by the user. The mechanism
for reusing geometry without copying it.

## When to make one

When several objects need the same part. A macro extracted for a single caller makes
future changes harder, not easier, and should not exist.

Avoid macros that call macros — it makes a library nearly impossible to check.

Prefer macro objects to plain `.gdl` macro files: they can carry a preview picture,
comments and parameters, which matters when someone else has to work out what the
thing does.

## Calling

Always `CALL "name"`, with the name in quotation marks. Use underscores instead of
spaces in macro names — it makes the call unambiguous and makes renaming safe.

Never build a macro name out of a parameter. Archive files keep only the default
macro, so an object that chooses its macro at runtime breaks the moment the project is
archived.

Macro calls are documented at p.650.

## Writing one

Open the script with its parameter definitions, as a comment block naming what each
letter means — the convention in Graphisoft's own macros is a header listing
`a=width, b=height, c=thickness` and so on, plus who edited it and when.

Use the same variable names in the macro and in the object calling it. A macro whose
`c` means thickness in one caller and depth in another is a defect waiting to happen.

End the script by clearing every coordinate transformation and emptying every
parameter buffer, then `END`. A macro that leaves a transformation on the stack
displaces everything the caller draws afterwards, and the caller has no way to see
why.

## Master GDL

Attributes shared across a whole library — materials, fills, line types — belong in a
Master GDL script rather than in each object. The file must be named
`Master_GDL <name>.gdl`. Reference Guide covers macro objects at p.364.
