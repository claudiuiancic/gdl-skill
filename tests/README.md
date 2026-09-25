# Tests

```
python3 tests/run_tests.py
```

Each folder under `fixtures/` is an HSF object plus `expected.txt`, one finding code
per line. The runner executes `check.py` and `preview.py` over every fixture and
compares the set of codes reported against the set expected.

Both directions are failures. A missing code means a check regressed. An unexpected
code means a new false positive — which matters just as much, because a tool that
reports problems on correct objects stops being read.

`valid-basic` and `valid-loop` are correct objects and must stay clean, apart from the
one warning `valid-loop` legitimately earns for a stack the checker cannot verify
statically. The `broken-*` fixtures each carry a specific defect. The `semantic-*`
fixtures compile and pass the text checks, and are only caught by `preview.py`.

When you add a rule to either script, add a fixture for it here at the same time. When
a real object exposes a defect neither tool caught, that object — reduced to the
smallest version that still fails — becomes the next fixture.
