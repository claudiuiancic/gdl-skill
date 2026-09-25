# Zone stamp

An object that displays information about the zone it belongs to. It is not placed by
the user in the ordinary sense — Archicad instantiates it for each zone, and it reads
that zone's data through global variables.

## Room globals

The zone's measured data arrives as `ROOM_` globals, filled in by Archicad: 
`ROOM_NAME`, `ROOM_NUMBER`, `ROOM_AREA`, `ROOM_PERIM`, `ROOM_HEIGHT`, `ROOM_BASELEV`,
`ROOM_FL_THICK`, `ROOM_WALLS_SURF`, `ROOM_DOORS_WID`, `ROOM_DOORS_SURF`,
`ROOM_WINDS_WID`, `ROOM_WINDS_SURF`, `ROOM_CORNERS`, `ROOM_CONCAVES`,
`ROOM_NET_AREA`, `ROOM_NET_PERIMETER`, `ROOM_REDUCED_AREA`, and the extraction areas
`ROOM_WALL_EXTR_AREA`, `ROOM_COLUMN_EXTR_AREA`, `ROOM_FILL_EXTR_AREA`,
`ROOM_LOW_EXTR_AREA`, `ROOM_TOTAL_EXTR_AREA`. Full list with types at p.486.

Never compute these yourself from geometry — they are the values Archicad will also
use in schedules, and a stamp that disagrees with the schedule is worse than no stamp.

## Mostly a 2D object

The work happens in the 2D script: text blocks, the fill, the boundary. Use
`TEXTBLOCK_` and `RICHTEXT2` rather than fixed `TEXT2` where the content can be long,
so that a long room name does not run off the stamp.

Formatting numbers is the recurring job — `STR(...)` with an explicit format string,
and the unit conventions taken from the project rather than hard-coded.

## Requests

Zone-specific `REQUEST`s start at p.537: `ZONE_CATEGORY` for the category name and
code, `ZONE_RELATIONS` for the elements belonging to the zone,
`WINDOW_DOOR_ZONE_RELEV` for openings' relevance to it.

Deprecated zone stamp parameters are listed at p.520 — if you meet one in an old
object, that page says what replaced it.
