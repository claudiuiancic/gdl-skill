"""Split GDL source into statements. Shared by check.py and preview.py.

A physical line is not a statement. A command whose argument list ends a line
with a comma continues on the next line, and one line can hold several
statements separated by ':'. A label is a number or a string followed by ':' at
the start of a statement — "cutie": or 100: — and marks a GOSUB/GOTO target.
"""
import re

LABEL_RE = re.compile(r'^\s*("[^"]*"|\'[^\']*\'|`[^`]*`|\d+(?:\.\d*)?)\s*$')


def strip_comment(line):
    """Cut at the first '!' that is not inside a string."""
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == "!":
            return line[:i]
    return line


def split_outside_quotes(text, sep):
    """Split on sep wherever it is not inside a string."""
    parts, cur, quote = [], "", None
    for ch in text:
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'`":
            quote = ch
        elif ch == sep:
            parts.append(cur)
            cur = ""
            continue
        cur += ch
    parts.append(cur)
    return parts


def statements(lines):
    """[(line_number, label_or_None, statement)] from comment-free lines.

    line_number is 1-based and points at the line where the statement starts.
    Empty statements are dropped; a label on its own yields a statement of "".
    """
    out = []
    i = 0
    while i < len(lines):
        start = i + 1
        text = lines[i].rstrip()
        i += 1
        while text.endswith(",") and i < len(lines):
            text += " " + lines[i].strip()
            i += 1
        parts = split_outside_quotes(text, ":")
        for k, part in enumerate(parts):
            stmt = part.strip()
            m = LABEL_RE.match(stmt)
            if m and k < len(parts) - 1:          # a ':' followed it
                out.append((start, m.group(1).strip("\"'`"), ""))
            elif stmt:
                out.append((start, None, stmt))
    return out
