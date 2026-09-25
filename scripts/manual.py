#!/usr/bin/env python3
"""Print the GDL Reference Guide pages that document a command.

    python3 scripts/manual.py CYLIND
    python3 scripts/manual.py PRISM_ --after 2      # 2 extra pages
    python3 scripts/manual.py --pages 245-252       # explicit page range
    python3 scripts/manual.py --find "texture"      # search the index

The PDF is not bundled. Put GDL_Reference_Guide_29.pdf in references/ next to
command-index.md, or set the GDL_MANUAL environment variable to its path.
Page numbers are PDF page numbers, which is what command-index.md records.
"""
import argparse
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INDEX = os.path.join(ROOT, "references", "command-index.md")
DEFAULT_PDF = os.path.join(ROOT, "references", "GDL_Reference_Guide_29.pdf")


def find_pdf():
    """GDL_MANUAL wins; otherwise take the only PDF in references/."""
    path = os.environ.get("GDL_MANUAL")
    if path:
        if os.path.exists(path):
            return path
        sys.exit("GDL_MANUAL points at %s, which does not exist." % path)
    if os.path.exists(DEFAULT_PDF):
        return DEFAULT_PDF
    folder = os.path.join(ROOT, "references")
    found = sorted(f for f in os.listdir(folder) if f.lower().endswith(".pdf"))
    if len(found) == 1:
        return os.path.join(folder, found[0])
    if not found:
        sys.exit("No PDF in %s. Copy the GDL Reference Guide there, or set "
                 "GDL_MANUAL to its path." % folder)
    sys.exit("Several PDFs in %s: %s. Set GDL_MANUAL to the one to use."
             % (folder, ", ".join(found)))


def read_index():
    """Return [(name, signature, page)] in document order."""
    if not os.path.exists(INDEX):
        sys.exit("command-index.md not found at %s" % INDEX)
    entries = []
    line_re = re.compile(r"^- (?:`(?P<n>[^`]+)` — `(?P<s>[^`]*)`|(?P<t>.+?)) — p\.(?P<p>\d+)")
    with open(INDEX, encoding="utf-8") as fh:
        for line in fh:
            m = line_re.match(line.strip())
            if m:
                entries.append((m.group("n") or m.group("t"), m.group("s") or "", int(m.group("p"))))
    return entries


def extract(pdf, first, last):
    """Return text of pages first..last (1-based, inclusive)."""
    try:
        import pymupdf  # noqa
        doc = pymupdf.open(pdf)
        return "\n".join(doc[p - 1].get_text() for p in range(first, min(last, len(doc)) + 1))
    except ImportError:
        pass
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf)
        pages = reader.pages[first - 1:last]
        return "\n".join(p.extract_text() for p in pages)
    except ImportError:
        pass
    import shutil
    import subprocess
    if shutil.which("pdftotext"):
        return subprocess.run(
            ["pdftotext", "-f", str(first), "-l", str(last), "-layout", pdf, "-"],
            capture_output=True, text=True, check=True).stdout
    sys.exit("Install pymupdf or pypdf (pip install pymupdf), or poppler's pdftotext.")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("command", nargs="?", help="GDL command name, e.g. CYLIND")
    ap.add_argument("--pages", help="explicit page range, e.g. 245-252")
    ap.add_argument("--find", help="substring search over the index")
    ap.add_argument("--after", type=int, default=0, help="extra pages past the entry")
    args = ap.parse_args()

    entries = read_index()

    if args.find:
        needle = args.find.lower()
        for name, sig, page in entries:
            if needle in name.lower() or needle in sig.lower():
                print("%-28s p.%-4d %s" % (name, page, sig))
        return

    if args.pages:
        first, _, last = args.pages.partition("-")
        first = int(first)
        last = int(last or first)
        print(extract(find_pdf(), first, last))
        return

    if not args.command:
        ap.print_help()
        return

    name = args.command
    hits = [i for i, e in enumerate(entries) if e[0].upper() == name.upper()]
    if not hits:
        near = [e[0] for e in entries if name.upper() in e[0].upper()]
        sys.exit("%s is not in the index. Did you mean: %s" % (name, ", ".join(near[:8]) or "(nothing similar)"))

    i = hits[0]
    first = entries[i][2]
    # run to the start of the next entry, so the whole section is printed
    last = entries[i + 1][2] if i + 1 < len(entries) else first + 2
    if last > first:
        last -= 1
    last += args.after

    print("=== %s — GDL Reference Guide p.%d-%d ===\n" % (entries[i][0], first, last))
    print(extract(find_pdf(), first, last))


if __name__ == "__main__":
    main()
