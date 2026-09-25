#!/usr/bin/env python3
"""Execute the 3D script far enough to answer: does it actually build anything?

    python3 scripts/preview.py path/to/MyObject
    python3 scripts/preview.py path/to/MyObject --verbose

Compiling proves the script parses. It says nothing about whether geometry came
out, whether the geometry has the size the parameters declare, or whether a
declared parameter does anything at all. This runs a deliberately small subset of
GDL — the shape commands, the transformations, FOR and IF — and reports:

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
import math
import os
import re
import sys
import xml.etree.ElementTree as ET

# Shape commands whose bounding box this subset knows how to compute.
# Everything else is counted as skipped rather than silently ignored.
SHAPE_COMMANDS = {
    "BLOCK", "BRICK", "CYLIND", "SPHERE", "ELLIPS", "CONE", "PRISM", "PRISM_",
    "CPRISM_", "BPRISM_", "SLAB", "SLAB_", "CSLAB_", "EXTRUDE", "PYRAMID",
    "REVOLVE", "MASS", "MESH", "ARMC", "ARME", "ELBOW", "RECT",
}

# Types whose value is a number the script can use in an expression.
READ_TYPES = {"Length", "Angle", "RealNum", "Integer", "Boolean",
              "PenColor", "Material", "FillPattern", "LineType"}
# Types worth perturbing in the sweep. A material or pen legitimately leaves the
# geometry untouched, so sweeping them would only produce noise.
SWEEP_TYPES = {"Length", "Angle", "RealNum", "Integer", "Boolean"}

# Standard parameters Archicad adds to every library part. They are read by the
# host, not by the script, so they are expected to leave the geometry unchanged —
# reporting them as dead would be noise on every object.
FRAMEWORK_PREFIXES = ("ac_", "gs_", "ifc_", "iso_", "bim_")


# ── expression evaluation ────────────────────────────────────────────────────

def to_python(expr):
    """Translate a GDL expression into something Python can evaluate."""
    e = expr.strip().lower()          # GDL is case-insensitive; vars are stored lower
    e = re.sub(r"\^", "**", e)
    e = re.sub(r"<>", "!=", e)
    # '=' means comparison inside a condition; callers handle assignment first
    e = re.sub(r"(?<![<>!=])=(?!=)", "==", e)
    e = re.sub(r"\bAND\b", " and ", e, flags=re.I)
    e = re.sub(r"\bOR\b", " or ", e, flags=re.I)
    e = re.sub(r"\bNOT\b", " not ", e, flags=re.I)
    e = re.sub(r"\bMOD\b", " % ", e, flags=re.I)
    return e


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


def evaluate(expr, vars_):
    try:
        env = dict(SAFE)
        env.update({k.lower(): v for k, v in vars_.items()})
        value = eval(to_python(expr), {"__builtins__": {}}, env)  # noqa: S307
    except Exception:
        raise Unknown(expr)
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if not isinstance(value, (int, float)):
        raise Unknown(expr)
    return float(value)


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

    MAX_ITERATIONS = 20000

    def __init__(self, params):
        self.vars = dict(params)
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
        self.execute(lines, 0, len(lines), identity(), [])

    def execute(self, lines, start, end, matrix, stack):
        i = start
        while i < end:
            self.steps += 1
            if self.steps > self.MAX_ITERATIONS:
                return matrix
            raw = lines[i]
            line = raw.strip()
            i += 1
            if not line:
                continue

            up = line.upper()
            if re.match(r"^(END|EXIT)\b", up):
                return matrix

            # assignment
            m_assign = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*=(?!=)(.*)$", line)
            if m_assign and not re.match(r"^(IF|FOR|WHILE)\b", up):
                try:
                    self.vars[m_assign.group(1).lower()] = evaluate(m_assign.group(2), self.vars)
                except Unknown:
                    self.unknown += 1
                continue

            # FOR ... NEXT
            m_for = re.match(r"^FOR\s+([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.+?)\s+TO\s+(.+?)(?:\s+STEP\s+(.+))?$",
                             line, re.I)
            if m_for:
                depth, j = 1, i
                while j < end and depth:
                    u = lines[j].strip().upper()
                    if re.match(r"^FOR\b", u):
                        depth += 1
                    elif re.match(r"^NEXT\b", u):
                        depth -= 1
                    j += 1
                body_end = j - 1
                try:
                    v0 = evaluate(m_for.group(2), self.vars)
                    v1 = evaluate(m_for.group(3), self.vars)
                    step = evaluate(m_for.group(4), self.vars) if m_for.group(4) else 1.0
                except Unknown:
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
                    matrix = self.execute(lines, i, body_end, matrix, stack)
                    value += step
                    guard += 1
                    if guard > 2000 or self.steps > self.MAX_ITERATIONS:
                        break
                i = j
                continue

            if re.match(r"^NEXT\b", up):
                continue

            # IF
            m_if = re.match(r"^IF\s+(.+?)\s+THEN\s*(.*)$", line, re.I)
            if m_if:
                try:
                    truth = evaluate(m_if.group(1), self.vars) != 0
                except Unknown:
                    self.unknown += 1
                    truth = True        # assume the branch runs, so geometry appears
                tail = m_if.group(2).strip()
                if tail:                                  # single-line form
                    if truth:
                        matrix = self.execute([tail], 0, 1, matrix, stack)
                    continue
                depth, j, else_at = 1, i, None
                while j < end and depth:
                    u = lines[j].strip().upper()
                    if re.match(r"^IF\b.*\bTHEN\s*$", u):
                        depth += 1
                    elif re.match(r"^ENDIF\b", u):
                        depth -= 1
                    elif re.match(r"^ELSE\b", u) and depth == 1 and else_at is None:
                        else_at = j
                    j += 1
                endif_at = j - 1
                if truth:
                    matrix = self.execute(lines, i, else_at if else_at else endif_at,
                                          matrix, stack)
                elif else_at:
                    matrix = self.execute(lines, else_at + 1, endif_at, matrix, stack)
                i = j
                continue

            if re.match(r"^(ENDIF|ELSE)\b", up):
                continue

            # command + arguments
            m_cmd = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*(.*)$", line)
            if not m_cmd:
                continue
            cmd = m_cmd.group(1).upper()
            rest = m_cmd.group(2).strip()

            if cmd in ("ADD", "ADDX", "ADDY", "ADDZ", "MUL", "MULX", "MULY",
                       "MULZ", "ROT", "ROTX", "ROTY", "ROTZ"):
                try:
                    args = [evaluate(a, self.vars) for a in split_args(rest)]
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
                        count = int(evaluate(rest or "1", self.vars))
                    except Unknown:
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
                    args = [evaluate(a, self.vars) for a in split_args(rest)]
                except Unknown:
                    self.skipped[cmd] = self.skipped.get(cmd, 0) + 1
                    continue
                self.shape(cmd, args, matrix)
                continue

            if cmd in ("HOTSPOT", "MATERIAL", "PEN", "RESOL", "TOLER", "RADIUS",
                       "MODEL", "SHADOW", "BODY", "BASE", "COOR", "CALL", "GOSUB",
                       "RETURN", "PRINT", "SET", "DEFINE", "LET"):
                continue

            self.skipped[cmd] = self.skipped.get(cmd, 0) + 1

        return matrix

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
    """Name → numeric value, from paramlist.xml. Non-numeric types are skipped."""
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
        value = el.findtext("Value")
        types[name.lower()] = tag
        if tag in READ_TYPES and value is not None:
            try:
                params[name.lower()] = float(value.strip())
            except ValueError:
                pass
    return params, types


def load_script(root, name="3d.gdl"):
    path = os.path.join(root, "scripts", name)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8-sig", errors="replace") as fh:
        raw = fh.read()
    lines = []
    for line in raw.splitlines():
        i = line.find("!")
        lines.append(line[:i] if i >= 0 else line)
    return lines


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
            probe = dict(params)
            if types.get(name) == "Boolean":
                probe[name] = 0.0 if value else 1.0
            else:
                probe[name] = value * 1.7 + 0.05 if value else 1.0
            try:
                probed = run_preview(probe, master, script)
            except Exception:
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
    if pv.unknown and args.verbose:
        print("%d expression(s) could not be evaluated" % pv.unknown)

    for code, msg in findings:
        print("%-14s %s" % ("[" + code + "]", msg))
    if not findings:
        print("no semantic problems found (this is not proof the object is correct)")

    sys.exit(1 if any(c == "no_geometry" for c, _ in findings) else 0)


if __name__ == "__main__":
    main()
