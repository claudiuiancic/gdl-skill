# gdl-skill

A [Claude Code](https://claude.com/claude-code) skill for writing, editing and
debugging GDL — the scripting language of Archicad library parts (`.gsm` objects).

It gives the agent what GDL does not forgive guessing at:

- **A command index** (`references/command-index.md`) with the syntax line and manual
  page of every entry in the GDL Reference Guide for Archicad 29. The rule is never to
  write a command that is not in it.
- **Graphisoft's conventions** for library parts, digested, plus per-subtype notes
  (object, door/window, lamp, label, zone stamp, profile, macro).
- **Two fast checkers that need no Archicad.** `scripts/check.py` reads an HSF folder
  and reports the metadata and script problems that make an object fail to load or
  misbehave. `scripts/preview.py` runs the 3D script and reports the geometry it builds.
- **A verified compile recipe** with LP_XMLConverter and Archicad's own GDL checker,
  including the steps that fail silently.
- **Workflows** for creating an object and for diagnosing one, and a minimal template
  object that compiles and places.

## Requirements

- Claude Code.
- Archicad 29 for compiling (its bundled `LP_XMLConverter`). Editing and the two Python
  checkers work without it, including in CI and cloud sessions.
- Python 3; `pymupdf` (or `pypdf`) only for reading the manual.
- The GDL manuals, which are **not included**: they are licensed by their publishers.
  Copy your own into `references/` — `references/sources.md` lists them.

Written and tested on macOS with zsh. On Windows the paths differ, the sequence does not.

## Install

```bash
git clone https://github.com/claudiuiancic/gdl-skill.git ~/.claude/skills/gdl
```

then follow [INSTALL.md](INSTALL.md): manuals, environment variables, Archicad's
built-in library, and a check of each tool.

## Layout

```
SKILL.md                 entry point Claude Code loads
INSTALL.md               setup and updating
references/              command index, conventions, subtype archetypes, sources
scripts/                 check.py, preview.py, manual.py
workflows/               create.md, debug.md
assets/template-object/  minimal HSF object to start from
tests/                   fixtures for the two checkers — python3 tests/run_tests.py
```

## License

MIT, see [LICENSE](LICENSE). This covers the skill itself, not the GDL manuals or
Archicad, which belong to their respective owners. GDL and Archicad are trademarks of
Graphisoft SE; this project is not affiliated with Graphisoft.
