# Installing the GDL skill

Written for macOS with Archicad 29 and zsh. On Windows the paths differ but the
sequence is the same. Run the sections in order and verify each one before moving on.

## 1. Put the skill where Claude Code looks for it

Clone the repository straight into the skill folder, so it *is* the skill and
`git pull` updates it in place:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/claudiuiancic/gdl-skill.git ~/.claude/skills/gdl
ls ~/.claude/skills/gdl                 # SKILL.md assets references scripts tests workflows
```

To keep the clone elsewhere, link it: `ln -s /your/path/gdl-skill ~/.claude/skills/gdl`.

For a skill that belongs to a team, add it to the object repository instead, at
`.claude/skills/gdl` — as a submodule it stays a single copy:

```bash
git submodule add https://github.com/claudiuiancic/gdl-skill.git .claude/skills/gdl
```

Everyone who clones the object repository (with `--recurse-submodules`) gets it, and
cloud sessions load it too.

## 2. Add the manuals

The manuals are licensed material and large, so they are not in the repository
(`*.pdf` is gitignored). Copy the ones you have into `references/`;
`references/sources.md` says what each is good for. Only the Reference Guide is
needed by the scripts.

```bash
cp ~/Documents/GDL_Reference_Guide_29.pdf ~/.claude/skills/gdl/references/
```

## 3. Python dependency

```bash
python3 -m pip install pymupdf
```

If pip refuses because the environment is externally managed, use
`python3 -m pip install --user pymupdf` or pipx. `scripts/manual.py` also accepts
`pypdf`, or poppler's `pdftotext` if it is already on the PATH. `check.py`,
`preview.py` and the tests need nothing beyond the standard library.

## 4. Environment variables

Put them in `~/.zshrc` so every shell has them, including the ones Claude Code starts.

```bash
cat >> ~/.zshrc <<'EOF'

# GDL skill
export GDL_MANUAL="$HOME/.claude/skills/gdl/references/GDL_Reference_Guide_29.pdf"
export GDL_CONVERTER="/Applications/Graphisoft/Archicad 29/Archicad 29.app/Contents/MacOS/LP_XMLConverter.app/Contents/MacOS/LP_XMLConverter"
export GDL_STDLIB="$HOME/Library/Application Support/gdl-skill/BuiltInLibraryParts"
EOF
source ~/.zshrc
```

`GDL_MANUAL` is needed as soon as `references/` holds more than one PDF; with only the
Reference Guide there, `manual.py` finds it on its own.

The converter path ends at the executable **inside** the `.app` bundle. A path ending
in `LP_XMLConverter.app` is a directory, and running it fails with "permission denied".

## 5. Extract Archicad's built-in library

Compiling with Archicad's checker needs the built-in library parts, so that every
object's ancestors resolve (see "Compiling with Archicad's own checker" in
`SKILL.md`). Extract them once, and again after every Archicad upgrade:

```bash
TMP=$(mktemp -d)
"$GDL_CONVERTER" extractpackage "/Applications/Graphisoft/Archicad 29/BuiltInLibraryParts.libpack" "$TMP"
"$GDL_CONVERTER" extractcontainer "$TMP/BuiltInLibraryParts.lcf" "$HOME/Library/Application Support/gdl-skill"
ls "$GDL_STDLIB" | head -3
```

If the `.libpack` is not at that path, search the Archicad folder for
`BuiltInLibraryParts.libpack`. `GDL_STDLIB` must point at the inner
`BuiltInLibraryParts` folder the second command creates.

## 6. Verify each tool on its own

Do this from the terminal before involving Claude Code. A tool that fails here will
fail for the agent too, and diagnosing it through an intermediary is much harder.

```bash
cd ~/.claude/skills/gdl
python3 tests/run_tests.py                          # 8/8 fixtures pass
python3 scripts/manual.py CYLIND | head -5          # prints the manual page
python3 scripts/preview.py assets/template-object   # 0.600 x 0.400 x 0.750
"$GDL_CONVERTER" help | head -5                     # prints the option list
```

The last one is the most likely to fail. "Permission denied" means the path stops at
the `.app` instead of reaching the binary inside. If macOS blocks the executable, clear
the quarantine flag: `xattr -d com.apple.quarantine "$GDL_CONVERTER"`.

## 7. The working repository

The skill is installed globally, but Claude Code is started in the folder holding the
objects, not in the skill folder.

```bash
mkdir -p ~/dev/gdl-library && cd ~/dev/gdl-library
git init
"$GDL_CONVERTER" libpart2hsf "/path/to/Object.gsm" ./Object
git add -A && git commit -m "Object, initial import"
```

Commit before changing anything. It gives you a point to return to and makes the diffs
readable — which is the main reason to work in HSF rather than on `.gsm` files.

## 8. Claude Code settings

Two things need configuring, both in `.claude/settings.json` in the object repository.

Claude Code reads only from the folder it started in, so the skill's scripts have to be
declared. And the checking commands should not need approval every time.

```bash
mkdir -p .claude
cat > .claude/settings.json <<'EOF'
{
  "permissions": {
    "additionalDirectories": ["~/.claude/skills/gdl"],
    "allow": [
      "Bash(python3:*)",
      "Bash(git status:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)"
    ]
  }
}
EOF
```

Leave LP_XMLConverter out of the allow list at first. Recompiling writes `.gsm` files,
and in early sessions it is worth seeing the command before approving it. Add the rule
later through the `/permissions` command rather than by hand — it builds the pattern
correctly for the command you actually ran.

Note that the VS Code extension has been reported not to honour these rules the way the
terminal CLI does. If you are prompted for everything despite the allow list, try the
CLI in a terminal.

## 9. First real session

```bash
cd ~/dev/gdl-library
claude
```

Ask for something concrete and checkable on the imported object — what parameters it
has, what the 3D script builds. Watch the list of files read: if the skill triggered, it
opens `paramlist.xml` before the scripts and consults `command-index.md` when it reaches
a command.

If it does not trigger, the problem is almost certainly the `description` field in the
frontmatter, not the rest of the file.

## 10. Optional: checks on every push

The scripts need neither Archicad nor the PDF, so they run in CI. This requires the
skill committed to the object repository at `.claude/skills/gdl`, not only installed
personally.

```yaml
# .github/workflows/check.yml
name: check
on: [push, pull_request]
jobs:
  gdl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: |
          for obj in */; do
            [ -d "$obj/scripts" ] || continue
            python3 .claude/skills/gdl/scripts/check.py "$obj"
          done
```

---

# Updating the skill

## Updating the content

Nothing to reinstall. The skill is a folder of files that Claude Code reads at the start
of each session, so an edit takes effect in the next session. Edit, commit, done.

```bash
cd ~/.claude/skills/gdl
# edit
python3 tests/run_tests.py
git add -A && git commit -m "what changed and why"
```

**Run the tests after any change to `check.py` or `preview.py`.** They are the only
thing standing between a new rule and a false positive that trains you to ignore the
output. A new rule needs a fixture in the same commit — see `tests/README.md`.

The most common update is a line in the pitfalls section of `SKILL.md`: every time you
had to correct the agent by hand is a piece of context that was missing. That is the
loop that makes the skill improve rather than decay.

## After an Archicad upgrade

Three things are version-bound and need checking when Archicad changes major version.

The converter path contains the version number, so `GDL_CONVERTER` in `~/.zshrc` and the
block in `SKILL.md` both need updating.

`references/command-index.md` was generated from the Reference Guide for Archicad 29. A
new release adds commands and moves page numbers, so the index and the page pointers in
`references/` and `workflows/` go stale together. Replace the PDF and regenerate the
index rather than patching it — the generator walks the PDF's table of contents, so it
takes minutes.

The version numbers in `assets/template-object/libpartdata.xml` (`Version`,
`SectVersion`) belong to the Archicad release. If a compile starts failing on something
structural rather than on GDL syntax, export a fresh object from the new Archicad,
convert it with `libpart2hsf`, and take those numbers from it.

## Keeping several machines in sync

Git is the mechanism; there is no built-in sync.

```bash
cd ~/.claude/skills/gdl && git pull
```

Remember the PDF is gitignored, so a freshly cloned copy needs it placed by hand before
`manual.py` works.

Custom skills do not sync between surfaces. A skill uploaded to claude.ai is not
available in Claude Code, and the reverse is also true. Claude Code can download the
skills enabled on your claude.ai account, but only in a non-interactive run with
`CLAUDE_CODE_SYNC_SKILLS=1 claude -p "..."`, which writes them to
`~/.claude/skills/synced/` and must be re-run after every change. For this skill that
path is not worth using: the repository is the single source, and everything else is a
copy that goes stale.

## What does not work outside a local Claude Code session

Worth knowing before wondering why something is missing. The claude.ai sandbox is
isolated from your filesystem: the knowledge files work, but `manual.py` has no PDF,
`preview.py` has no objects, and there is no converter. Cloud sessions can run `check.py`
and `preview.py` against objects in the cloned repository, but cannot compile. Only a
local session has all three.
