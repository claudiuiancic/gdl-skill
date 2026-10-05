#!/usr/bin/env python3
"""Execute the 3D script far enough to answer: does it actually build anything?

    python3 scripts/preview.py path/to/MyObject
    python3 scripts/preview.py path/to/MyObject --verbose

Compiling proves the script parses. It says nothing about whether geometry came
out, whether the geometry has the size the parameters declare, or whether a
declared parameter does anything at all. This runs a deliberately small subset of
GDL — the shape commands, the transformations, FOR, WHILE, REPEAT, IF, GOSUB to
labelled subroutines, arrays, strings and the PUT/GET buffer — and reports:

  no_geometry   shape commands ran but nothing was produced
  degenerate    the bounding box collapses on an axis
  size_mismatch the bounding box disagrees with A / B / ZZYZX
  dead_param    changing a parameter leaves the geometry identical

It is an approximation, not an engine. Unsupported commands are skipped and
counted, and anything it cannot evaluate is reported as unknown rather than
guessed. Findings here are advisory: exit code is 1 only for no_geometry, which
is never correct. Never treat a clean run as proof the object is right.
"""
import argparse
import copy
import functools
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

from gdl_source import statements, strip_comment

# Shape commands whose bounding box this subset knows how to compute.
# Everything else is counted as skipped rather than silently ignored.
SHAPE_COMMANDS = {
    "BLOCK", "BRICK", "CYLIND", "SPHERE", "ELLIPS", "CONE", "PRISM", "PRISM_",
    "CPRISM_", "BPRISM_", "SLAB", "SLAB_", "CSLAB_", "EXTRUDE", "PYRAMID",
    "REVOLVE", "MASS", "MESH", "ARMC", "ARME", "ELBOW", "RECT",
}

# Types whose value is a number the script can use in an expression.
READ_TYPES = {"Length", "Angle", "RealNum", "Integer", "Boolean",
              "PenColor", "Material", "FillPattern", "LineType", "String"}
# Types worth perturbing in the sweep. A material or pen legitimately leaves the
# geometry untouched, so sweeping them would only produce noise.
SWEEP_TYPES = {"Length", "Angle", "RealNum", "Integer", "Boolean"}

# Standard parameters Archicad adds to every library part. They are read by the
# host, not by the script, so they are expected to leave the geometry unchanged —
# reporting them as dead would be noise on every object.
FRAMEWORK_PREFIXES = ("ac_", "gs_", "ifc_", "iso_", "bim_")


# ── expression evaluation ────────────────────────────────────────────────────

@functools.lru_cache(maxsize=None)
def to_python(expr):
    """Translate a GDL expression into something Python can evaluate."""
    e = expr.strip().lower()          # GDL is case-insensitive; vars are stored lower
    e = re.sub(r"`([^`]*)`", r'"\1"', e)
    e = re.sub(r"\^", "**", e)
    e = re.sub(r"<>", "!=", e)
    # '=' means comparison inside a condition; callers handle assignment first
    e = re.sub(r"(?<![<>!=])=(?!=)", "==", e)
    e = re.sub(r"\bAND\b", " and ", e, flags=re.I)
    e = re.sub(r"\bOR\b", " or ", e, flags=re.I)
    e = re.sub(r"\bNOT\b", " not ", e, flags=re.I)
    e = re.sub(r"\bMOD\b", " % ", e, flags=re.I)
    e = e.replace("&", " and ").replace("|", " or ")
    return compile(e, "<gdl>", "eval")


SAFE = {
    "abs": abs, "min": min, "max": max, "int": int, "round": round,
    "sqr": lambda x: x * x, "sqrt": math.sqrt,
    "sin": lambda d: math.sin(math.radians(d)),
    "cos": lambda d: math.cos(math.radians(d)),
    "tan": lambda d: math.tan(math.radians(d)),
    "atn": lambda x: math.degrees(math.atan(x)),
    "acs": lambda x: math.degrees(math.acos(x)),
    "asn": lambda x: math.degrees(math.asin(x)),
    "exp": math.exp, "log": math.log, "pi": math.pi,
    "ceil": math.ceil, "frac": lambda x: x - int(x),
    "sgn": lambda x: (x > 0) - (x < 0),
    "round_int": lambda x: int(round(x)),
}


class Unknown(Exception):
    pass


class _End(Exception):
    """END / EXIT: the script stops here, from any depth."""
    def __init__(self, matrix):
        self.matrix = matrix


class _Return(_End):
    """RETURN: back to the statement after the GOSUB."""


class GArray(dict):
    """A GDL array. 1-based, indexed by any numeric expression."""

    def __getitem__(self, k):
        return dict.__getitem__(self, int(round(k)))


def label_key(value):
    """GOSUB "name" and GOSUB 100 both look labels up through this."""
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return value.lower()
    return float(value)


def evaluate(expr, vars_, nsp=0):
    """A number or a string. Anything else, or any failure, is Unknown."""
    try:
        env = dict(SAFE)
        env.update(vars_)
        env["nsp"] = nsp
        value = eval(to_python(expr), {"__builtins__": {}}, env)  # noqa: S307
    except Exception:
        raise Unknown(expr)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, str):
        return value
    if not isinstance(value, (int, float)):
        raise Unknown(expr)
    return float(value)


# One statement: name, optional [i][j] indices, value.
ASSIGN_RE = re.compile(r"^(?:LET\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*((?:\[[^\]]*\]\s*)*)=(?!=)(.*)$", re.I)


def block_end(stmts, i, end, open_re, close_re):
    """Index just past the statement that closes the block opened before i."""
    depth, j = 1, i
    while j < end and depth:
        u = stmts[j].strip().upper()
        if re.match(open_re, u):
            depth += 1
        elif re.match(close_re, u):
            depth -= 1
        j += 1
    return j


# ── transformation stack ─────────────────────────────────────────────────────

def identity():
    return [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]]


def multiply(a, b):
    out = []
    for r in range(3):
        row = []
        for c in range(4):
            v = sum(a[r][k] * (b[k][c] if k < 3 else 0) for k in range(3))
            if c == 3:
                v += a[r][3]
            row.append(v)
        out.append(row)
    return out


def translation(x, y, z):
    m = identity()
    m[0][3], m[1][3], m[2][3] = x, y, z
    return m


def scaling(x, y, z):
    return [[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0]]


def rotation(axis, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "X":
        return [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0]]
    if axis == "Y":
        return [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0]]
    return [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0]]


def apply(m, p):
    return tuple(m[r][0] * p[0] + m[r][1] * p[1] + m[r][2] * p[2] + m[r][3]
                 for r in range(3))


# ── the interpreter ──────────────────────────────────────────────────────────

class Preview:
    """Runs a 3D script and accumulates a bounding box."""

    MAX_STEPS = 400000
    MAX_GOSUB_DEPTH = 64

    def __init__(self, params):
        # deep: the master script writes into parameter arrays (h[i] = x), and
        # every sweep run has to start from the same values
        self.vars = copy.deepcopy(params)
        self.buffer = []         # the parameter buffer: PUT, GET, USE, NSP
        self.depth = 0           # GOSUB nesting
        self.truncated = False
        self.texts, self.labels = [], {}
        self.lo = [None, None, None]
        self.hi = [None, None, None]
        self.boxes = []          # one rounded box per shape, for the fingerprint
        self.shapes = 0
        self.skipped = {}
        self.unknown = 0
        self.steps = 0

    # bounding box of a local axis-aligned box, through the current transform
    def add_box(self, m, x0, y0, z0, x1, y1, z1):
        self.shapes += 1
        local = [None, None, None, None, None, None]
        for px in (x0, x1):
            for py in (y0, y1):
                for pz in (z0, z1):
                    p = apply(m, (px, py, pz))
                    for i in range(3):
                        if self.lo[i] is None or p[i] < self.lo[i]:
                            self.lo[i] = p[i]
                        if self.hi[i] is None or p[i] > self.hi[i]:
                            self.hi[i] = p[i]
                        if local[i] is None or p[i] < local[i]:
                            local[i] = p[i]
                        if local[i + 3] is None or p[i] > local[i + 3]:
                            local[i + 3] = p[i]
        self.boxes.append(tuple(round(v, 6) for v in local))

    def shape(self, cmd, args, m):
        """Bounding box per command. Polygon commands use their vertex list."""
        def n(i):
            return args[i]
        try:
            if cmd in ("BLOCK", "BRICK"):
                self.add_box(m, 0, 0, 0, n(0), n(1), n(2))
            elif cmd == "RECT":
                self.add_box(m, 0, 0, 0, n(0), n(1), 0)
            elif cmd == "CYLIND":
                r = n(1)
                self.add_box(m, -r, -r, 0, r, r, n(0))
            elif cmd == "SPHERE":
                r = n(0)
                self.add_box(m, -r, -r, -r, r, r, r)
            elif cmd == "ELLIPS":
                r = n(1)
                self.add_box(m, -r, -r, 0, r, r, n(0))
            elif cmd == "CONE":
                r = max(n(1), n(2))
                self.add_box(m, -r, -r, 0, r, r, n(0))
            elif cmd in ("PRISM", "PRISM_", "CPRISM_", "BPRISM_", "SLAB", "SLAB_",
                         "CSLAB_", "EXTRUDE", "PYRAMID", "MASS"):
                self.polygon_shape(cmd, args, m)
            elif cmd == "MESH":
                self.add_box(m, 0, 0, 0, n(0), n(1), max(args[5:] or [0]))
            else:
                raise Unknown(cmd)
        except (IndexError, Unknown):
            self.skipped[cmd] = self.skipped.get(cmd, 0) + 1

    def polygon_shape(self, cmd, args, m):
        """Vertex lists differ per command; take the x,y pairs and the height."""
        layouts = {
            "PRISM": (0, 1, 2, 2), "PRISM_": (0, 1, 2, 3),
            "CPRISM_": (3, 4, 5, 3), "BPRISM_": (3, 4, 6, 3),
            "SLAB": (0, None, 1, 3), "SLAB_": (0, 1, 2, 4),
            "CSLAB_": (3, 4, 5, 4), "EXTRUDE": (0, None, 5, 3),
            "PYRAMID": (0, 1, 3, 3), "MASS": (3, None, 7, 4),
        }
        n_idx, h_idx, first, stride = layouts[cmd]
        count = int(args[n_idx])
        height = args[h_idx] if h_idx is not None else 0.0
        if cmd == "EXTRUDE":
            height = args[3]          # dz
        if cmd == "MASS":
            height = args[6]
        xs, ys = [], []
        for k in range(count):
            base = first + k * stride
            if base + 1 >= len(args):
                break
            xs.append(args[base])
            ys.append(args[base + 1])
        if not xs:
            raise Unknown(cmd)
        z0, z1 = (0.0, height) if height >= 0 else (height, 0.0)
        self.add_box(m, min(xs), min(ys), z0, max(xs), max(ys), z1)

    def run(self, lines):
        items = statements(lines)
        self.texts = [s for _, _, s in items]
        self.labels = {}
        for k, (_, label, _) in enumerate(items):
            if label is not None:
                self.labels.setdefault(label_key(label), k)
        try:
            self.execute(self.texts, 0, len(self.texts), identity(), [])
        except _End:
            pass

    def ev(self, expr):
        return evaluate(expr, self.vars, len(self.buffer))

    def eval_args(self, rest, numeric=True):
        """Evaluate an argument list. GET (n) and USE (n) expand to n buffer values."""
        out = []
        for a in split_args(rest):
            m = re.fullmatch(r"(GET|USE)\s*\((.+)\)", a, re.I)
            if m:
                n = int(self.ev(m.group(2)))
                if n > len(self.buffer):
                    raise Unknown(a)
                out.extend(self.buffer[:n])
                if m.group(1).upper() == "GET":
                    del self.buffer[:n]
                continue
            out.append(self.ev(a))
        if numeric and any(isinstance(v, str) for v in out):
            raise Unknown(rest)
        return out

    def store(self, name, indices, value):
        """x[i] = v and x[i][j] = v. The array springs into being if needed."""
        arr = self.vars.get(name)
        if not isinstance(arr, GArray):
            arr = self.vars[name] = GArray()
        for k in indices[:-1]:
            k = int(round(k))
            if not isinstance(arr.get(k), GArray):
                dict.__setitem__(arr, k, GArray())
            arr = dict.__getitem__(arr, k)
        dict.__setitem__(arr, int(round(indices[-1])), value)

    def gosub(self, expr, matrix, stack):
        """Run from the label to its RETURN, on the same transformation stack."""
        try:
            target = self.ev(expr)
        except Unknown:
            self.unknown += 1
            return matrix
        k = self.labels.get(label_key(target))
        if k is None or self.depth >= self.MAX_GOSUB_DEPTH:
            self.skipped["GOSUB"] = self.skipped.get("GOSUB", 0) + 1
            return matrix
        self.depth += 1
        try:
            matrix = self.execute(self.texts, k, len(self.texts), matrix, stack)
        except _Return as r:
            matrix = r.matrix
        finally:
            self.depth -= 1
        return matrix

    def execute(self, stmts, start, end, matrix, stack):
        i = start
        while i < end:
            self.steps += 1
            if self.steps > self.MAX_STEPS:
                self.truncated = True
                return matrix
            line = stmts[i].strip()
            i += 1
            if not line:
                continue

            up = line.upper()
            if re.match(r"^(END|EXIT)\b", up):
                raise _End(matrix)
            if re.match(r"^RETURN\b", up):
                raise _Return(matrix)

            # assignment, including array elements: h[i] = x
            m_assign = ASSIGN_RE.match(line)
            if m_assign:
                try:
                    value = self.ev(m_assign.group(3))
                    idx = [self.ev(x) for x in re.findall(r"\[([^\]]*)\]", m_assign.group(2))]
                    if idx:
                        self.store(m_assign.group(1).lower(), idx, value)
                    else:
                        self.vars[m_assign.group(1).lower()] = value
                except Unknown:
                    self.unknown += 1
                continue
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*[.\[].*=", line):
                self.unknown += 1             # dictionary field, d.key = x
                continue

            # FOR ... NEXT
            m_for = re.match(r"^FOR\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$",
                             line, re.I)
            if m_for:
                j = block_end(stmts, i, end, r"^FOR\b", r"^NEXT\b")
                body_end = j - 1
                try:
                    v0, v1 = self.eval_args(m_for.group(2) + "," + m_for.group(3))
                    step = self.eval_args(m_for.group(4))[0] if m_for.group(4) else 1.0
                except (Unknown, ValueError, IndexError):
                    self.unknown += 1
                    i = j
                    continue
                if step == 0:
                    i = j
                    continue
                var = m_for.group(1).lower()
                value, guard = v0, 0
                while (step > 0 and value <= v1 + 1e-9) or (step < 0 and value >= v1 - 1e-9):
                    self.vars[var] = value
                    matrix = self.execute(stmts, i, body_end, matrix, stack)
                    value += step
                    guard += 1
                    if guard > 2000 or self.steps > self.MAX_STEPS:
                        break
                i = j
                continue

            # WHILE ... DO ... ENDWHILE and REPEAT ... UNTIL
            m_while = re.match(r"^WHILE\s+(.+?)\s+DO\s*$", line, re.I)
            if m_while or re.match(r"^REPEAT\s*$", up):
                if m_while:
                    j = block_end(stmts, i, end, r"^WHILE\b.*\bDO\s*$", r"^ENDWHILE\b")
                    cond, until = m_while.group(1), False
                else:
                    j = block_end(stmts, i, end, r"^REPEAT\s*$", r"^UNTIL\b")
                    cond, until = stmts[j - 1].strip()[5:], True
                for _ in range(2000):
                    if not until and not self.truth(cond, default=False):
                        break
                    matrix = self.execute(stmts, i, j - 1, matrix, stack)
                    if until and self.truth(cond, default=True):
                        break
                    if self.steps > self.MAX_STEPS:
                        break
                i = j
                continue

            if re.match(r"^(NEXT|ENDWHILE|UNTIL|ENDIF)\b", up):
                continue

            # IF
            m_if = re.match(r"^IF\s+(.+?)\s+(THEN|GOTO|GOSUB)\b\s*(.*)$", line, re.I)
            if m_if:
                truth = self.truth(m_if.group(1), default=True)   # unknown: assume it runs
                kw, tail = m_if.group(2).upper(), m_if.group(3).strip()
                if kw == "GOSUB":
                    tail = "GOSUB " + tail
                elif kw == "GOTO" or re.match(r'^(GOTO\b|\d|")', tail, re.I):
                    self.skipped["GOTO"] = self.skipped.get("GOTO", 0) + 1
                    continue
                if tail:                                  # single-line form
                    parts = re.split(r"\bELSE\b", tail, maxsplit=1, flags=re.I)
                    branch = parts[0] if truth else (parts[1] if len(parts) > 1 else "")
                    if branch.strip():
                        matrix = self.execute([branch], 0, 1, matrix, stack)
                    continue
                depth, j, else_at, else_inline = 1, i, None, None
                while j < end and depth:
                    u = stmts[j].strip().upper()
                    if re.match(r"^IF\b.*\bTHEN\s*$", u):
                        depth += 1
                    elif re.match(r"^ENDIF\b", u):
                        depth -= 1
                    elif re.match(r"^ELSE\s*\S", u):
                        # ELSE with a statement on its line closes the block, no ENDIF
                        if depth == 1:
                            else_at, else_inline = j, stmts[j].strip()[4:].strip()
                            j += 1
                            break
                        depth -= 1
                    elif re.match(r"^ELSE\b", u) and depth == 1 and else_at is None:
                        else_at = j
                    j += 1
                block_close = j if else_inline is not None else j - 1
                if truth:
                    matrix = self.execute(stmts, i, else_at if else_at is not None
                                          else block_close, matrix, stack)
                elif else_inline is not None:
                    matrix = self.execute([else_inline], 0, 1, matrix, stack)
                elif else_at is not None:
                    matrix = self.execute(stmts, else_at + 1, block_close, matrix, stack)
                i = j
                continue

            if re.match(r"^ELSE\b", up):
                continue

            m_gosub = re.match(r"^GOSUB\s+(.+)$", line, re.I)
            if m_gosub:
                matrix = self.gosub(m_gosub.group(1), matrix, stack)
                continue

            # command + arguments
            m_cmd = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(.*)$", line)
            if not m_cmd:
                continue
            cmd = m_cmd.group(1).upper()
            rest = m_cmd.group(2).strip()

            if cmd == "PUT":
                try:
                    self.buffer.extend(self.eval_args(rest, numeric=False))
                except Unknown:
                    self.unknown += 1
                continue

            if cmd in ("ADD", "ADDX", "ADDY", "ADDZ", "MUL", "MULX", "MULY",
                       "MULZ", "ROT", "ROTX", "ROTY", "ROTZ"):
                try:
                    args = self.eval_args(rest)
                except Unknown:
                    self.unknown += 1
                    args = None
                if args is None:
                    stack.append(matrix)
                    continue
                stack.append(matrix)
                if cmd == "ADD":
                    matrix = multiply(matrix, translation(*pad(args, 3)))
                elif cmd == "ADDX":
                    matrix = multiply(matrix, translation(args[0], 0, 0))
                elif cmd == "ADDY":
                    matrix = multiply(matrix, translation(0, args[0], 0))
                elif cmd == "ADDZ":
                    matrix = multiply(matrix, translation(0, 0, args[0]))
                elif cmd == "MUL":
                    matrix = multiply(matrix, scaling(*pad(args, 3, 1.0)))
                elif cmd == "MULX":
                    matrix = multiply(matrix, scaling(args[0], 1, 1))
                elif cmd == "MULY":
                    matrix = multiply(matrix, scaling(1, args[0], 1))
                elif cmd == "MULZ":
                    matrix = multiply(matrix, scaling(1, 1, args[0]))
                elif cmd in ("ROTZ", "ROT"):
                    matrix = multiply(matrix, rotation("Z", args[-1]))
                elif cmd == "ROTX":
                    matrix = multiply(matrix, rotation("X", args[0]))
                elif cmd == "ROTY":
                    matrix = multiply(matrix, rotation("Y", args[0]))
                continue

            if cmd == "DEL":
                arg = rest.strip().upper()
                count = len(stack) if arg.startswith("TOP") else None
                if count is None:
                    try:
                        count = int(self.ev(rest or "1"))
                    except (Unknown, ValueError):
                        count = 1
                for _ in range(max(0, count)):
                    if stack:
                        matrix = stack.pop()
                continue

            if cmd == "DELALL":
                if stack:
                    matrix = stack[0]
                    stack.clear()
                continue

            if cmd in SHAPE_COMMANDS:
                try:
                    args = self.eval_args(rest)
                except Unknown:
                    self.skipped[cmd] = self.skipped.get(cmd, 0) + 1
                    continue
                self.shape(cmd, args, matrix)
                continue

            if cmd == "DIM":
                for name in re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*\[", rest):
                    self.vars[name.lower()] = GArray()
                continue

            if cmd in ("HOTSPOT", "MATERIAL", "PEN", "RESOL", "TOLER", "RADIUS",
                       "MODEL", "SHADOW", "BODY", "BASE", "COOR", "CALL",
                       "PRINT", "SET", "DEFINE", "LET", "STYLE", "BUILDING_MATERIAL"):
                continue

            self.skipped[cmd] = self.skipped.get(cmd, 0) + 1

        return matrix

    def truth(self, cond, default):
        try:
            value = self.ev(cond)
        except Unknown:
            self.unknown += 1
            return default
        return bool(value) if isinstance(value, str) else value != 0

    # bounding box measured from the origin, so both corner-based and centred
    # objects give the size a user would read off the settings dialog
    def fingerprint(self):
        """Every shape's own box, so a change inside the model still shows up."""
        return tuple(sorted(self.boxes))

    def span(self):
        if self.lo[0] is None:
            return None
        return tuple(max(self.hi[i], 0) - min(self.lo[i], 0) for i in range(3))


def pad(args, n, fill=0.0):
    return (list(args) + [fill] * n)[:n]


def split_args(rest):
    """Split on commas that are not inside brackets or quotes."""
    out, depth, cur, quoted = [], 0, "", False
    for ch in rest:
        if ch == '"':
            quoted = not quoted
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == "," and depth == 0 and not quoted:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        out.append(cur)
    return [a for a in (x.strip() for x in out) if a]


# ── project loading ──────────────────────────────────────────────────────────

def read_parameters(root):
    """Name → value, from paramlist.xml: a number, a string, or a GArray."""
    path = os.path.join(root, "paramlist.xml")
    params, types = {}, {}
    if not os.path.exists(path):
        return params, types
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        sys.exit("paramlist.xml is not valid XML: %s" % exc)
    for el in tree.iter():
        name = el.get("Name")
        if not name:
            continue
        tag = el.tag
        types[name.lower()] = tag
        if tag not in READ_TYPES:
            continue
        array = el.find("ArrayValues")
        if array is not None:
            values = GArray()
            for av in array.findall("AVal"):
                v = param_value(tag, av.text)
                if v is None:
                    continue
                row, col = int(av.get("Row", "1")), av.get("Column")
                if col is None:
                    dict.__setitem__(values, row, v)
                else:
                    if row not in values:
                        dict.__setitem__(values, row, GArray())
                    dict.__setitem__(dict.__getitem__(values, row), int(col), v)
            params[name.lower()] = values
            continue
        v = param_value(tag, el.findtext("Value"))
        if v is not None:
            params[name.lower()] = v
    return params, types


def param_value(tag, text):
    """Strings are stored lower-case, like everything the evaluator sees."""
    if text is None:
        return None
    text = text.strip()
    if tag == "String":
        return text.strip('"').lower()
    try:
        return float(text)
    except ValueError:
        return None


def load_script(root, name="3d.gdl"):
    path = os.path.join(root, "scripts", name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        raw = fh.read()
    return [strip_comment(line) for line in raw.splitlines()]


def perturb(value, boolean, direction=1):
    """A different value of the same shape; arrays change in every element."""
    if isinstance(value, GArray):
        out = GArray()
        for k, v in value.items():
            dict.__setitem__(out, k, perturb(v, boolean, direction))
        return out
    if not isinstance(value, float):
        return value
    if boolean:
        return 0.0 if value else 1.0
    if direction < 0:
        return value * 0.5 if value else -1.0
    return value * 1.7 + 0.05 if value else 1.0


def run_preview(params, master, script):
    pv = Preview(params)
    if master:
        pv.run(master)
        carried = dict(pv.vars)
    else:
        carried = dict(params)
    pv2 = Preview(carried)
    pv2.run(script)
    return pv2


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("folder")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    root = args.folder
    script = load_script(root, "3d.gdl")
    if script is None:
        sys.exit("no scripts/3d.gdl in %s" % root)
    master = load_script(root, "1d.gdl")
    params, types = read_parameters(root)

    pv = run_preview(params, master, script)
    span = pv.span()
    fingerprint = pv.fingerprint()

    findings = []
    mentions_shape = any(
        re.match(r"^\s*([A-Za-z_]+)", l) and re.match(r"^\s*([A-Za-z_]+)", l).group(1).upper() in SHAPE_COMMANDS
        for l in script)

    if span is None:
        if mentions_shape:
            findings.append(("no_geometry", "shape commands are present but nothing "
                                            "was built — check the conditions around them"))
        else:
            findings.append(("no_geometry", "the 3D script builds no geometry at all"))
    else:
        for i, axis in enumerate("xyz"):
            if span[i] < 1e-6:
                findings.append(("degenerate",
                                 "the model is flat on %s — %s extent is zero" % (axis, axis)))
        declared = [params.get("a"), params.get("b"), params.get("zzyzx")]
        for i, (name, value) in enumerate(zip(("A", "B", "ZZYZX"), declared)):
            if not value:
                continue
            got = span[i]
            if got < value * 0.5 or got > value * 2.0:
                findings.append(("size_mismatch",
                                 "%s is %.3f but the model measures %.3f along %s"
                                 % (name, value, got, "xyz"[i])))

    # dead parameters: perturb one at a time and see whether anything moves
    if span is not None:
        for name, value in sorted(params.items()):
            if name in ("a", "b", "zzyzx"):
                continue
            if types.get(name) not in SWEEP_TYPES:
                continue
            if name.startswith(FRAMEWORK_PREFIXES):
                continue
            # up first, then down: a value already at the maximum the master
            # script clamps to only shows it is alive when it decreases
            directions = (1,) if types.get(name) == "Boolean" else (1, -1)
            probed = None
            for direction in directions:
                probe = dict(params)
                probe[name] = perturb(value, types.get(name) == "Boolean", direction)
                try:
                    probed = run_preview(probe, master, script)
                except Exception:
                    probed = None
                    break
                if probed.span() is None or probed.fingerprint() != fingerprint:
                    break
            if probed is None:
                continue
            if probed.span() is None:
                findings.append(("dead_param",
                                 "changing '%s' makes the geometry disappear" % name))
            elif probed.fingerprint() == fingerprint:
                findings.append(("dead_param",
                                 "'%s' is declared but changing it does not move "
                                 "the model" % name))

    if span is not None:
        print("bounding box: %.3f x %.3f x %.3f m, from %d shape command(s)"
              % (span[0], span[1], span[2], pv.shapes))
    if pv.skipped:
        print("not modelled: %s" % ", ".join(
            "%s x%d" % (k, v) for k, v in sorted(pv.skipped.items())))
    if pv.truncated:
        print("stopped after %d statements — the box covers only what ran by then"
              % pv.MAX_STEPS)
    if pv.unknown and args.verbose:
        print("%d expression(s) could not be evaluated" % pv.unknown)

    for code, msg in findings:
        print("%-14s %s" % ("[" + code + "]", msg))
    if not findings:
        print("no semantic problems found (this is not proof the object is correct)")

    sys.exit(1 if any(c == "no_geometry" for c, _ in findings) else 0)


if __name__ == "__main__":
    main()
