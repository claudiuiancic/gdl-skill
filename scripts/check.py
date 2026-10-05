#!/usr/bin/env python3
"""Deterministic checks on an HSF library part, before compiling.

    python3 scripts/check.py path/to/MyObject      # an HSF folder

Exit code 1 if any error is found, 0 otherwise. Warnings never fail the run.
No LLM, no Archicad, no network — plain text analysis, milliseconds.
This is a filter, not a compiler: passing means the obvious mistakes are gone,
not that the object is correct. Always compile afterwards.

The command vocabulary comes from references/command-index.md, which was
extracted from the GDL Reference Guide.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET

from gdl_source import statements

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(os.path.dirname(HERE), "references", "command-index.md")

SCRIPTS = {
    "1d.gdl": "master",
    "2d.gdl": "2D",
    "3d.gdl": "3D",
    "vl.gdl": "parameter",
    "ui.gdl": "interface",
    "pr.gdl": "properties",
    "fwm.gdl": "forward migration",
    "bwm.gdl": "backward migration",
}

# Reserved parameters every object has.
RESERVED = {"A", "B", "ZZYZX"}

# Prefixes of Archicad-supplied variables. Anything starting with one of these
# is provided by the host, not declared by the object.
GLOBAL_PREFIXES = ("GLOB_", "SYMB_", "WIDO_", "REQ_", "GS_", "AC_", "IFC_", "FM_")

# Keywords that are language, not commands, and that the index does not list
# as separate entries.
KEYWORDS = {
    "IF", "THEN", "ELSE", "ELSIF", "ENDIF", "FOR", "TO", "STEP", "NEXT",
    "WHILE", "ENDWHILE", "DO", "REPEAT", "UNTIL", "GOTO", "GOSUB", "RETURN",
    "END", "EXIT", "AND", "OR", "NOT", "EXOR", "MOD", "DIM", "LET", "VALUES",
    "RANGE", "PARAMETERS", "LOCK", "HIDEPARAMETER", "PRINT", "PUT", "GET",
    "USE", "NSP", "CALL", "TRUE", "FALSE", "PI", "SET", "DEFINE",
    # the attribute kinds that follow DEFINE
    "EMPTY_FILL", "FILLA", "IMAGE_FILL", "LINEAR_GRADIENT_FILL", "SOLID_FILL",
    "RADIAL_GRADIENT_FILL", "SYMBOL_FILL", "TRANSLUCENT_FILL", "SYMBOL_LINE",
    "TEXTURE", "LINE",
    # words inside other statements: CALL ... PARAMETERS ALL RETURNED_PARAMETERS,
    # SHADOW OFF, MODEL SOLID
    "RETURNED_PARAMETERS", "ALL", "ON", "OFF", "AUTO", "WIRE", "SURFACE", "SOLID",
}

# Built-in functions. The index lists them only as section titles ("Arithmetical
# Functions — p.340"), so they are spelled out here from GDL Reference Guide 29,
# pp. 340-345 and 353.
FUNCTIONS = {
    "ABS", "CEIL", "INT", "FRA", "ROUND_INT", "SGN", "SQR",       # arithmetical
    "ACS", "ASN", "ATN", "COS", "SIN", "TAN",                     # circular
    "EXP", "LGT", "LOG",                                          # transcendental
    "MIN", "MAX", "RND",                                          # statistical
    "BITTEST", "BITSET",                                          # bit
    "IND", "REQ", "REQUEST", "APPLICATION_QUERY", "LIBRARYGLOBAL",  # special
    "SPLIT", "STR", "STRLEN", "STRSTR", "STRSUB", "STW",          # string
    "STRTOUPPER", "STRTOLOWER",
}

# Functions that write results into variables passed as arguments, e.g.
# n = REQUEST ("Name_of_program", "", programName). Every bare name after the
# first argument is an output, hence an assignment.
OUTPUT_ARG_RE = re.compile(r"\b(REQUEST(?:\{\d+\})?|REQ|APPLICATION_QUERY|"
                           r"LIBRARYGLOBAL|INPUT|CALLFUNCTION|SPLIT)\s*\(", re.I)

PUSH_RE = re.compile(r"\b(ADD[XYZ]?|ADD2|MUL[XYZ]?|MUL2|ROT[XYZ]?|ROT2)\b", re.I)
POP_RE = re.compile(r"\bDEL\s+(\d+|TOP)\b|\bDEL\b(?!\s*(\d|TOP))", re.I)
DELALL_RE = re.compile(r"\bDELALL\b", re.I)
# Applied to one statement, not one line: `a = 1 : b = 2` holds two.
# Also matches an array element, `h[i] = x`, a dictionary field, `d.key[i].name = x`,
# and the LET form.
ASSIGN_RE = re.compile(r"^\s*(?:LET\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*"
                       r"(?:\[[^\]=]*\]\s*|\.\s*[A-Za-z_][A-Za-z0-9_]*\s*)*=(?!=)", re.I)
FOR_RE = re.compile(r"^\s*FOR\s+([A-Za-z_][A-Za-z0-9_]*)\s*=", re.I)
DIM_RE = re.compile(r"^\s*DIM\s+(.*)$", re.I)
# The statement after THEN or ELSE on the same line: IF x THEN n = 1 ELSE n = 2
THEN_RE = re.compile(r"\b(?:THEN|ELSE)\s+(.*?)(?=\bELSE\b|$)", re.I)
# Attributes defined inline get a name that is then used bare: STYLE txtStyle
DEFINED_RE = re.compile(r'\b(?:DEFINE\s+[A-Z_]+(?:\{\d+\})?|TEXTBLOCK_?|PARAGRAPH)\s+"([^"]+)"', re.I)
# Not after a '.', which makes it a dictionary key, not a variable.
IDENT_RE = re.compile(r"(?<!\.)\b([A-Za-z_][A-Za-z0-9_]*)\b")
# CALL "macro" PARAMETERS name = value, ...: the names are the macro's parameters.
CALL_PARAM_RE = re.compile(r"(?:\bPARAMETERS\b|,)\s*([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)", re.I)
FIRSTWORD_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)")


def load_commands():
    """Command names from the index, normalised (CPRISM_{2} -> CPRISM_)."""
    names = set(KEYWORDS)
    try:
        with open(INDEX, encoding="utf-8") as fh:
            for line in fh:
                # entries with a syntax line, and entries without one
                m = re.match(r"^- `([^`]+)`", line) or re.match(r"^- (.+?) — p\.\d+", line)
                if not m:
                    continue
                for part in re.split(r"[/\-\s]+", m.group(1)):
                    part = re.sub(r"\{.*?\}", "", part).strip().upper()
                    if re.fullmatch(r"[A-Z][A-Z0-9_]*", part or ""):
                        names.add(part)
    except OSError:
        pass
    return names


def assigned_in(stmt):
    """Names one statement gives a value to."""
    names = set()
    for m in (ASSIGN_RE.match(stmt), FOR_RE.match(stmt)):
        if m:
            names.add(m.group(1).upper())
    m = DIM_RE.match(stmt)
    if m:
        names |= {n.upper() for n in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", m.group(1))}
    for m in THEN_RE.finditer(stmt):
        m2 = ASSIGN_RE.match(m.group(1))
        if m2:
            names.add(m2.group(1).upper())
    for m in OUTPUT_ARG_RE.finditer(stmt):
        args, depth, cur = [], 1, ""
        for ch in stmt[m.end():]:
            depth += (ch == "(") - (ch == ")")
            if depth == 0 or (ch == "," and depth == 1):
                args.append(cur.strip())
                cur = ""
                if depth == 0:
                    break
                continue
            cur += ch
        names |= {a.upper() for a in args[1:]
                  if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", a)}
    return names


def assigned_names(text):
    """Every name the script gives a value to, anywhere."""
    names = set()
    for _, _, stmt in statements(text.splitlines()):
        names |= assigned_in(stmt)
    return names


def strip_code(text):
    """Drop comments and string contents, keep line numbers by blanking."""
    out = []
    for line in text.splitlines():
        i = line.find("!")
        clean = line[:i] if i >= 0 else line
        clean = re.sub(r'"[^"]*"|`[^`]*`|\'[^\']*\'', '""', clean)
        out.append(clean)
    return out


class Report:
    """Findings carry a stable code so tests and tools can match on them."""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def error(self, code, where, msg):
        self.errors.append((code, where, msg))

    def warn(self, code, where, msg):
        self.warnings.append((code, where, msg))


def read_params(root):
    """Parameter names declared in paramlist.xml, plus the reserved ones."""
    path = os.path.join(root, "paramlist.xml")
    names = set(RESERVED)
    if not os.path.exists(path):
        return names, False
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        raise SystemExit("paramlist.xml is not valid XML: %s" % exc)
    for el in tree.iter():
        name = el.get("Name")
        if name:
            names.add(name.upper())
    return names, True


def check_blocks(lines, fname, rep):
    """IF/ENDIF and FOR/NEXT pairing. Single-line IF ... THEN <stmt> needs no ENDIF."""
    depth_if, depth_for, depth_while = 0, 0, 0
    for n, line in enumerate(lines, 1):
        up = line.upper()
        if re.search(r"\bIF\b", up) and re.search(r"\bTHEN\b", up):
            after = up.split("THEN", 1)[1].strip()
            if not after:
                depth_if += 1
        if re.search(r"\bENDIF\b", up):
            depth_if -= 1
            if depth_if < 0:
                rep.error("block_mismatch", "%s:%d" % (fname, n), "ENDIF without a matching multi-line IF")
                depth_if = 0
        if re.search(r"\bFOR\b.*\bTO\b", up):
            depth_for += 1
        if re.search(r"\bNEXT\b", up):
            depth_for -= 1
            if depth_for < 0:
                rep.error("block_mismatch", "%s:%d" % (fname, n), "NEXT without FOR")
                depth_for = 0
        if re.search(r"\bWHILE\b", up) and not re.search(r"\bENDWHILE\b", up):
            depth_while += 1
        if re.search(r"\bENDWHILE\b", up):
            depth_while -= 1
    if depth_if > 0:
        rep.error("block_mismatch", fname, "%d multi-line IF block(s) never closed with ENDIF" % depth_if)
    if depth_for > 0:
        rep.error("block_mismatch", fname, "%d FOR loop(s) never closed with NEXT" % depth_for)
    if depth_while > 0:
        rep.error("block_mismatch", fname, "%d WHILE loop(s) never closed with ENDWHILE" % depth_while)


def check_stack(lines, fname, rep):
    """Transformation stack balance.

    Counting is only meaningful when every push and pop happens a fixed number
    of times. Pushes inside a loop, a DEL whose argument is an expression, and
    DELALL all make the count unverifiable — say so instead of guessing, since
    a false alarm here trains the reader to ignore the checker.
    """
    code = "\n".join(lines)
    if DELALL_RE.search(code):
        rep.warn("stack_unverifiable", fname, "DELALL present — stack balance not statically verifiable")
        return

    loop_depth = 0
    push = pop = 0
    push_in_loop = False
    del_expr = False
    has_del_top = False
    if_delta = []          # net push-pop per open IF block

    for line in lines:
        up = line.upper()
        pushes_here = len(PUSH_RE.findall(up))
        if pushes_here and loop_depth:
            push_in_loop = True
        push += pushes_here
        delta = pushes_here

        for m in re.finditer(r"\bDEL\b[ \t]*([A-Za-z_0-9+\-* ]*)", up):
            arg = m.group(1).strip()
            if arg.startswith("TOP"):
                has_del_top = True
            elif arg == "" or arg.isdigit():
                n = int(arg or 1)
                pop += n
                delta -= n
            else:
                del_expr = True

        if if_delta:
            if_delta[-1] += delta

        if re.search(r"\bIF\b", up) and re.search(r"\bTHEN\b", up) \
                and not up.split("THEN", 1)[1].strip():
            if_delta.append(0)
        if re.search(r"\bENDIF\b", up) and if_delta:
            d = if_delta.pop()
            if d:
                rep.warn("stack_branch", fname, "an IF block leaves %+d transformation(s) "
                                "on the stack — the geometry after it shifts only "
                                "when the branch runs" % d)
        if re.search(r"\bFOR\b.*\bTO\b", up) or re.search(r"\bWHILE\b", up) \
                or re.search(r"\bREPEAT\b", up):
            loop_depth += 1
        if re.search(r"\b(NEXT|ENDWHILE|UNTIL)\b", up) and loop_depth:
            loop_depth -= 1

    if push_in_loop or del_expr:
        rep.warn("stack_unverifiable", fname, "transformation stack not statically "
                 "verifiable (pushes inside a loop, or DEL with an expression) — "
                 "check by hand that every ADD/MUL/ROT is undone")
        return
    if has_del_top:
        if pop > push:
            rep.error("stack_imbalance", fname, "stack pops (%d) exceed pushes (%d) before DEL TOP" % (pop, push))
        return
    if push != pop:
        rep.error("stack_imbalance", fname, "transformation stack unbalanced: %d push "
                 "vs %d pop (each ADD/ADDX/ADDY/ADDZ/MUL/ROT needs its DEL)" % (push, pop))


def check_master_end(lines, rep):
    """END in the master script silently stops the parameter script from running."""
    for n, line in enumerate(lines, 1):
        if re.match(r"^\s*(END|EXIT)\s*(!.*)?$", line.strip(), re.I):
            rep.error("master_end", "1d.gdl:%d" % n,
                      "END in the master script — Archicad will not run the "
                      "parameter script at all, silently")


def check_idents(scripts, declared, has_paramlist, commands, rep):
    """Names used but never declared or assigned anywhere in the object."""
    assigned = set()
    for text in scripts.values():
        assigned |= assigned_names(text)

    macro_params = set()
    for text in scripts.values():
        for _, _, stmt in statements(text.splitlines()):
            if re.match(r"\s*CALL\b", stmt, re.I):
                macro_params |= {m.group(1).upper() for m in CALL_PARAM_RE.finditer(stmt)}
    assigned |= macro_params

    for fname, text in scripts.items():
        seen = set()
        for m in IDENT_RE.finditer(text):
            name = m.group(1)
            up = name.upper()
            if up in seen or up in commands or up in assigned or up in declared:
                continue
            if name.startswith("_") or len(name) == 1:
                continue
            if any(up.startswith(p) for p in GLOBAL_PREFIXES):
                continue
            seen.add(up)
            if has_paramlist:
                rep.error("undefined_var", fname, "'%s' is not declared in paramlist.xml "
                                 "and is never assigned" % name)
            else:
                rep.warn("undefined_var", fname, "'%s' is never assigned (no paramlist.xml "
                                "to check against)" % name)


def check_derived(scripts, rep):
    """Underscore-prefixed derived variables must be assigned before use."""
    master = scripts.get("1d.gdl", "")
    master_assigned = assigned_names(master)
    for fname in ("3d.gdl", "2d.gdl"):
        text = scripts.get(fname)
        if not text:
            continue
        here = assigned_names(text)
        seen = set()
        for m in IDENT_RE.finditer(text):
            name = m.group(1)
            if not name.startswith("_") or name.upper() in seen:
                continue
            seen.add(name.upper())
            if name.upper() not in master_assigned and name.upper() not in here:
                rep.error("forward_decl", fname, "derived variable '%s' is used but assigned "
                                 "neither in 1d.gdl nor here" % name)


def check_unknown_commands(scripts, commands, assigned_names, rep):
    """First word of a statement that is neither a command nor an assignment."""
    for fname, text in scripts.items():
        seen = set()
        for n, _, stmt in statements(text.splitlines()):
            if not stmt or ASSIGN_RE.match(stmt):
                continue
            m = FIRSTWORD_RE.match(stmt)
            if not m:
                continue
            word = m.group(1).upper()
            if word in commands or word in assigned_names or word in seen:
                continue
            if any(word.startswith(p) for p in GLOBAL_PREFIXES):
                continue
            seen.add(word)
            rep.warn("unknown_command", "%s:%d" % (fname, n),
                     "'%s' is not a known GDL command — Archicad reads this as a "
                     "macro call without CALL" % m.group(1))


def check_bare_not(scripts, rep):
    """NOT requires parentheses: NOT (x), not NOT x."""
    for fname, text in scripts.items():
        for n, line in enumerate(text.splitlines(), 1):
            if re.search(r"\bNOT\s+(?!\()", line, re.I):
                rep.error("bare_not", "%s:%d" % (fname, n),
                          "NOT without parentheses — write NOT (expression)")


def check_stubs(scripts, rep):
    """Lines left as ellipsis: a model stopped generating there."""
    for fname, text in scripts.items():
        for n, line in enumerate(text.splitlines(), 1):
            if re.match(r"^\s*(\.\.\.|…)\s*$", line):
                rep.error("stub", "%s:%d" % (fname, n), "placeholder line left in the script")


def check_placeable(root, rep):
    """An object can compile cleanly and still never appear in the library.

    These are the metadata Archicad needs in order to classify the part. None of
    them is a GDL error, so the compiler reports nothing and the .gsm is written —
    the object simply never shows up as placeable.
    """
    anc = os.path.join(root, "ancestry.xml")
    if not os.path.exists(anc):
        rep.error("no_ancestry", root, "no ancestry.xml — the object has no subtype "
                  "and Archicad will not offer it for placement")
    else:
        try:
            guids = [e.text.strip() for e in ET.parse(anc).iter()
                     if e.tag.endswith("MainGUID") and (e.text or "").strip()]
        except ET.ParseError:
            rep.error("xml_parse", "ancestry.xml", "not valid XML")
            guids = []
        if not guids:
            rep.error("no_ancestry", "ancestry.xml", "empty ancestry — the object has "
                      "no subtype and will compile but never be placeable")
        elif len(guids) == 1:
            rep.warn("no_ancestry", "ancestry.xml", "only one ancestor GUID; objects "
                     "exported by Archicad carry the whole chain, usually two or more")

    lpd = os.path.join(root, "libpartdata.xml")
    if os.path.exists(lpd):
        try:
            text = open(lpd, encoding="utf-8-sig").read()
        except OSError:
            text = ""
        if "<IsPlaceable>false</IsPlaceable>" in text:
            rep.warn("not_placeable", "libpartdata.xml", "IsPlaceable is false")
        if "REPLACE-WITH" in text:
            rep.error("template_guid", "libpartdata.xml",
                      "the template placeholder GUID is still there — generate one")

    params = os.path.join(root, "paramlist.xml")
    if os.path.exists(params):
        text = open(params, encoding="utf-8-sig", errors="replace").read().lower()
        missing = [n for n in ("ac_show2dhotspotsin3d", "ac_bottomlevel", "ac_toplevel")
                   if 'name="%s"' % n not in text]
        if missing:
            rep.warn("missing_std_params", "paramlist.xml",
                     "objects exported by Archicad carry these hidden parameters and "
                     "their absence is a suspected cause of silent non-placement: %s"
                     % ", ".join(missing))


def check_encoding(root, rep):
    """Archicad writes every HSF text file with a UTF-8 BOM."""
    bad = []
    for dirpath, _, names in os.walk(root):
        for n in sorted(names):
            if not n.endswith((".xml", ".gdl")):
                continue
            with open(os.path.join(dirpath, n), "rb") as fh:
                if fh.read(3) != b"\xef\xbb\xbf":
                    bad.append(os.path.relpath(os.path.join(dirpath, n), root))
    if bad:
        rep.warn("no_bom", root, "no UTF-8 BOM, unlike files Archicad exports: %s"
                 % ", ".join(bad[:6]) + (" …" if len(bad) > 6 else ""))


def check_macros(root, scripts, rep):
    """Macros called by name must exist, and must be declared in calledmacros.xml."""
    called = set()
    for text in scripts.values():
        for m in re.finditer(r'\bCALL\s+"([^"]+)"', text, re.I):
            called.add(m.group(1))
        for m in re.finditer(r"\bCALL\s+([A-Za-z_][A-Za-z0-9_]*)", text, re.I):
            rep.warn("macro_call", "scripts", "CALL without quotation marks around "
                     "'%s' — write CALL \"%s\"" % (m.group(1), m.group(1)))
    if not called:
        return
    declared = set()
    path = os.path.join(root, "calledmacros.xml")
    if os.path.exists(path):
        try:
            for el in ET.parse(path).iter():
                txt = (el.text or "").strip()
                if txt:
                    declared.add(txt)
                if el.get("Name"):
                    declared.add(el.get("Name"))
        except ET.ParseError:
            rep.error("xml_parse", "calledmacros.xml", "not valid XML")
            return
    else:
        rep.warn("macro_call", root, "macros are called but there is no "
                 "calledmacros.xml: %s" % ", ".join(sorted(called)))
        return
    missing = {c for c in called if c not in declared}
    if missing:
        rep.warn("macro_call", "calledmacros.xml",
                 "called but not declared: %s" % ", ".join(sorted(missing)))


def check_roles(scripts, rep):
    """Each script has to do its own job."""
    if scripts.get("2d.gdl") is not None:
        body = scripts["2d.gdl"]
        if not re.search(r"\b(PROJECT2|PROJECT2\{\d\}|POLY2_?|RECT2|LINE2|CIRCLE2|ARC2|FRAGMENT2)\b", body, re.I):
            rep.error("no_2d", "2d.gdl", "no drawing command — the object will have no plan symbol")
        if not re.search(r"\bHOTSPOT2\b", body, re.I):
            rep.warn("no_hotspot", "2d.gdl", "no HOTSPOT2 — the object cannot be grabbed on plan")
    if scripts.get("3d.gdl") and not re.search(r"\bHOTSPOT\b", scripts["3d.gdl"], re.I):
        rep.warn("no_hotspot", "3d.gdl", "no HOTSPOT in 3D")
    for fname in ("3d.gdl", "2d.gdl"):
        text = scripts.get(fname)
        if text and re.search(r"\b(VALUES|LOCK|HIDEPARAMETER)\b", text, re.I):
            rep.error("wrong_script", fname, "VALUES/LOCK/HIDEPARAMETER belong in vl.gdl, not here")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    root = sys.argv[1]
    sdir = os.path.join(root, "scripts")
    if not os.path.isdir(sdir):
        sys.exit("%s does not look like an HSF folder (no scripts/ inside)" % root)

    commands = load_commands() | FUNCTIONS
    declared, has_paramlist = read_params(root)
    rep = Report()
    if not has_paramlist:
        rep.warn("no_paramlist", root, "no paramlist.xml — parameter checks are degraded")

    scripts, lines_by_file, raws = {}, {}, {}
    for fname in SCRIPTS:
        path = os.path.join(sdir, fname)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8-sig", errors="replace") as fh:
            raw = fh.read()
        raws[fname] = raw
        lines = strip_code(raw)
        lines_by_file[fname] = lines
        scripts[fname] = "\n".join(lines)

    if not scripts:
        sys.exit("no .gdl scripts found in %s" % sdir)

    for fname, lines in lines_by_file.items():
        check_blocks(lines, fname, rep)
    if "3d.gdl" in lines_by_file:
        check_stack(lines_by_file["3d.gdl"], "3d.gdl", rep)
    if "1d.gdl" in lines_by_file:
        check_master_end(lines_by_file["1d.gdl"], rep)

    assigned = set()
    for text in scripts.values():
        assigned |= assigned_names(text)

    # Unknown statement heads first, so a misspelled command is not also
    # reported as an undeclared variable.
    before = len(rep.warnings)
    check_unknown_commands(scripts, commands, assigned, rep)
    mistyped = {w[2].split("'")[1].upper() for w in rep.warnings[before:]}

    macro_names = {m.group(1).upper() for text in raws.values()
                   for m in re.finditer(r'\bCALL\s+"?([A-Za-z_][A-Za-z0-9_]*)"?', text, re.I)}
    defined = {m.group(1).upper() for text in raws.values() for m in DEFINED_RE.finditer(text)}
    check_idents(scripts, declared | defined, has_paramlist,
                 commands | mistyped | macro_names, rep)
    check_derived(scripts, rep)
    check_bare_not(scripts, rep)
    check_stubs(scripts, rep)
    check_roles(scripts, rep)
    check_macros(root, raws, rep)
    check_placeable(root, rep)
    check_encoding(root, rep)

    for code, where, msg in rep.warnings:
        print("WARN  [%s] %s: %s" % (code, where, msg))
    for code, where, msg in rep.errors:
        print("ERROR [%s] %s: %s" % (code, where, msg))
    print("\n%d error(s), %d warning(s)" % (len(rep.errors), len(rep.warnings)))
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
