#!/usr/bin/env python3
"""Regression tests for mask_markdown -- the offset and coverage guarantees.

Run after any change to mask_markdown:
    ./masktest.py
    python3 masktest.py

Finds the detector module next to this file whether it is named
ticfinder.py or tic_finder.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

mask_markdown = None
for mod in ("ticfinder", "tic_finder"):
    try:
        mask_markdown = __import__(mod).mask_markdown
        break
    except ImportError:
        continue
if mask_markdown is None:
    sys.exit("Cannot find ticfinder.py or tic_finder.py next to this script.")

CASES = [
 ("blockquote does not eat the rest",
  "Para one here.\n\n> quoted\n\nPara two here.\n", ["Para one", "Para two"]),
 ("table does not eat the rest",
  "Before text.\n\n| a | b |\n| - | - |\n\nAfter text.\n", ["Before", "After"]),
 ("indented code does not eat the rest",
  "Intro line.\n\n    code_here()\n\nOutro line.\n", ["Intro", "Outro"]),
 ("fenced code is masked but rest survives",
  "One.\n\n```py\nx = 1  # not prose\n```\n\nTwo.\n", ["One", "Two"]),
 ("hr does not eat the rest",
  "Top text.\n\n---\n\nBottom text.\n", ["Top", "Bottom"]),
 ("inline code masked, sentence survives",
  "Call `foo()` to start the process now.\n", ["Call", "to start"]),
 ("link text kept, target masked",
  "See [the docs](http://x.com/y) for details.\n", ["the docs", "for details"]),
 ("html tag masked",
  "Text <br/> continues after the tag.\n", ["Text", "continues"]),
]

fails = 0
for name, src, must in CASES:
    m = mask_markdown(src)
    assert len(m) == len(src), f"{name}: LENGTH CHANGED ({len(m)} vs {len(src)})"
    for i, ch in enumerate(src):
        if ch == "\n":
            assert m[i] == "\n", f"{name}: newline at {i} destroyed"
    miss = [t for t in must if t not in m]
    if miss:
        fails += 1
        print(f"FAIL {name}: lost {miss}")
    else:
        print(f"ok   {name}")

# pragma regions
PRAGMA = [
 ("off/on region masked, prose either side kept",
  "Before here.\n\n<!-- ticfinder_off -->\nBIO TEXT\n<!-- ticfinder_on -->\n\nAfter here.\n",
  ["Before here", "After here"], ["BIO TEXT"]),
 ("unclosed off runs to EOF",
  "Kept text.\n\n<!-- ticfinder_off -->\nGONE ONE\nGONE TWO\n",
  ["Kept text"], ["GONE ONE", "GONE TWO"]),
 ("hyphen and space spellings accepted",
  "Keep A.\n\n<!-- ticfinder-off -->\nX1\n<!-- ticfinder on -->\n\nKeep B.\n",
  ["Keep A", "Keep B"], ["X1"]),
 ("case insensitive",
  "Keep C.\n\n<!-- TICFINDER_OFF -->\nX2\n<!-- TicFinder_On -->\n\nKeep D.\n",
  ["Keep C", "Keep D"], ["X2"]),
 ("skip takes one block only",
  "<!-- ticfinder_skip -->\nSKIPPED BLOCK\n\nKept after skip.\n",
  ["Kept after skip"], ["SKIPPED BLOCK"]),
 ("two separate regions",
  "A here.\n\n<!-- ticfinder_off -->\nG1\n<!-- ticfinder_on -->\n\nB here.\n\n<!-- ticfinder_off -->\nG2\n<!-- ticfinder_on -->\n\nC here.\n",
  ["A here", "B here", "C here"], ["G1", "G2"]),
]
for name, src, keep, gone in PRAGMA:
    m = mask_markdown(src)
    assert len(m) == len(src), f"{name}: length changed"
    for i, ch in enumerate(src):
        if ch == "\n":
            assert m[i] == "\n", f"{name}: newline at {i} destroyed"
    bad = [t for t in keep if t not in m] + [t for t in gone if t in m]
    if bad:
        fails += 1; print(f"FAIL {name}: {bad}")
    else:
        print(f"ok   {name}")

# masked content must actually be gone
neg = [("```py\nSECRET\n```", "SECRET"), ("> QUOTED", "QUOTED"),
       ("| CELL |", "CELL"), ("    INDENTED", "INDENTED"),
       ("`INLINE`", "INLINE")]
for src, tok in neg:
    if tok in mask_markdown(src):
        fails += 1; print(f"FAIL: {tok!r} survived masking")
    else:
        print(f"ok   masked {tok}")

print("\nFAILURES:", fails)
sys.exit(1 if fails else 0)
sys.exit(1 if fails else 0)
