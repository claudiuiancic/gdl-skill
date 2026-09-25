#!/usr/bin/env python3
"""Run check.py over every fixture and compare against its expected findings.

    python3 tests/run_tests.py

Each fixture folder holds an HSF object plus expected.txt: one finding code per
line, blank lines and # comments ignored. The test passes when the set of codes
check.py reports equals the set in expected.txt — missing codes mean a check
regressed, extra codes mean a new false positive. Both are failures: a checker
that cries wolf gets ignored, which is the same as having no checker.

Run this after every change to check.py.
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CHECK = os.path.join(ROOT, "scripts", "check.py")
PREVIEW = os.path.join(ROOT, "scripts", "preview.py")
FIXTURES = os.path.join(HERE, "fixtures")


def expected_codes(folder):
    path = os.path.join(folder, "expected.txt")
    codes = set()
    if not os.path.exists(path):
        return codes
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if line:
            codes.add(line)
    return codes


def reported_codes(folder):
    """Codes from both tools, so one expected.txt covers the whole pipeline."""
    checked = subprocess.run([sys.executable, CHECK, folder],
                             capture_output=True, text=True)
    codes = set(re.findall(r"^(?:ERROR|WARN)\s+\[([a-z0-9_]+)\]", checked.stdout, re.M))
    previewed = subprocess.run([sys.executable, PREVIEW, folder],
                               capture_output=True, text=True)
    codes |= set(re.findall(r"^\[([a-z0-9_]+)\]", previewed.stdout, re.M))
    checked.stderr += previewed.stderr
    return codes, checked


def main():
    names = sorted(d for d in os.listdir(FIXTURES)
                   if os.path.isdir(os.path.join(FIXTURES, d)))
    if not names:
        sys.exit("no fixtures found in %s" % FIXTURES)

    failed = 0
    for name in names:
        folder = os.path.join(FIXTURES, name)
        want = expected_codes(folder)
        got, out = reported_codes(folder)
        if got == want:
            print("pass  %-22s %s" % (name, ", ".join(sorted(got)) or "clean"))
            continue
        failed += 1
        print("FAIL  %s" % name)
        for code in sorted(want - got):
            print("        missing: %s" % code)
        for code in sorted(got - want):
            print("        unexpected: %s" % code)
        if out.stderr.strip():
            print("        stderr: %s" % out.stderr.strip().splitlines()[-1])

    print("\n%d/%d fixtures pass" % (len(names) - failed, len(names)))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
