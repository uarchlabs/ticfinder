#!/usr/bin/env python3
"""Invariants every detector must satisfy, regardless of input.

Catches the class of bug where a span is built as doc[a:b] with a > b, which
spaCy silently clamps to an empty span instead of raising. The finding then
reports empty text and highlights nothing.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for name in ("ticfinder.py", "tic_finder.py"):
    cand = HERE / name
    if cand.exists():
        spec = importlib.util.spec_from_file_location("_tf", cand)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_tf"] = mod
        spec.loader.exec_module(mod)
        break
else:
    sys.exit(f"Could not find ticfinder.py in {HERE}")

nlp = mod.load_model("en_core_web_md")

TEXT = """
An update writes these fields individually and an allocation writes a whole
entry. A TAGE or ITTAGE table entry holds a counter, a usefulness field, an
epoch field, and an indirect branch target. This is not merely a technical
choice but an architectural commitment. It is a feature, not a bug. The issue
isn't about speed, it's about trust. Manual testing did not catch this, and
could not have. Expected values come from the row, not from the design under
test. The cache warms on startup, making requests faster. Rather than
rewriting it, we patched the caller. It is structurally unable to evaluate the
document itself. The parser is fast, correct, and easy to extend. Ultimately,
this is the real problem. A bug wrapped in an excuse trenchcoat. Instead of
retrying, the client gives up. We processed the rows sequentially and wrote
them individually.
"""

fails = 0
doc = nlp(TEXT)
for cid in mod.CONSTRUCTIONS:
    for pname, fn, _ in mod.CONSTRUCTIONS[cid]["patterns"]:
        try:
            hits = fn(doc, nlp)
        except Exception as e:
            fails += 1
            print(f"FAIL {cid}.{pname}: raised {e!r}")
            continue
        for span, sub in hits:
            if span.end <= span.start:
                fails += 1
                print(f"FAIL {cid}.{pname}: inverted/empty span "
                      f"[{span.start}:{span.end}]")
            elif not span.text.strip():
                fails += 1
                print(f"FAIL {cid}.{pname}: whitespace-only span {span.text!r}")
            elif span.start_char >= span.end_char:
                fails += 1
                print(f"FAIL {cid}.{pname}: zero-width char range")
        print(f"ok   {cid}.{pname}: {len(hits)} hit(s), all well-formed")

print("\nFAILURES:", fails)
sys.exit(1 if fails else 0)

