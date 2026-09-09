#!/usr/bin/env python3
"""Regression suite for ticfinder.

Run:  ./tests.py            all sections
      ./tests.py detectors  one section
      ./tests.py -v         show every case, not just failures

Sections:
  registry   every expected construction and pattern is still wired up
  detectors  labelled cases: does each construction fire where it should
  masking    mask_markdown preserves offsets and blanks the right regions
  spans      no detector emits an inverted, empty or zero-width span
  waivers    fingerprints survive edits elsewhere in the document
  cli        flags parse, exit codes are right, output respects width

Exits non-zero on any failure, so it works as a make target or pre-commit
hook.
"""

import importlib.util
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent

for _name in ("ticfinder.py", "tic_finder.py"):
    _cand = HERE / _name
    if _cand.exists():
        SCRIPT = _cand
        _spec = importlib.util.spec_from_file_location("_tf", _cand)
        tf = importlib.util.module_from_spec(_spec)
        sys.modules["_tf"] = tf
        _spec.loader.exec_module(tf)
        break
else:
    sys.exit(f"Could not find ticfinder.py or tic_finder.py in {HERE}")

VERBOSE = "-v" in sys.argv
FAILS = []


def check(section, name, ok, detail=""):
    if ok:
        if VERBOSE:
            print(f"  ok   {name}")
    else:
        FAILS.append((section, name, detail))
        print(f"  FAIL {name}" + (f"\n         {detail}" if detail else ""))


# --------------------------------------------------------------- registry

EXPECTED = {
    "CORRECTIVE_CONTRAST": ["cc_coordinated", "cc_cleft",
                            "cc_parallel_sibling", "cc_negated_apposition"],
    "ALTERNATIVE_FRAMING": ["af_rather_instead", "af_less_than"],
    "NEG_ESCALATION": ["neg_escalation"],
    "ABSTRACT_ADVERB": ["abstract_adverb"],
    "EMPHATIC_REFLEXIVE": ["emphatic_reflexive"],
    "PARTICIPIAL_TAIL": ["participial_tail"],
    "TRICOLON": ["tricolon", "tricolon_parataxis"],
    "DISGUISE_METAPHOR": ["disguise_metaphor"],
}

EXPECTED_PHRASE = ["FRAME_MARKER", "HOLLOW_BOOSTER", "CLOSER", "HEDGE_STACK"]


def test_registry():
    """Catches the failure where an edit silently drops a construction."""
    for cid, pats in EXPECTED.items():
        check("registry", f"{cid} present", cid in tf.CONSTRUCTIONS)
        if cid not in tf.CONSTRUCTIONS:
            continue
        have = [p[0] for p in tf.CONSTRUCTIONS[cid]["patterns"]]
        for p in pats:
            check("registry", f"{cid}.{p}", p in have,
                  f"have {have}")
    for cid in EXPECTED_PHRASE:
        check("registry", f"phrase {cid}", cid in tf.PHRASE_PATTERNS)
    for cid, meta in tf.CONSTRUCTIONS.items():
        check("registry", f"{cid} has a note", bool(meta["note"]))
        check("registry", f"{cid} confidence valid",
              meta["confidence"] in ("high", "med", "low"))


# -------------------------------------------------------------- detectors
# (construction, should_fire, text). Every case here was checked by hand
# before being added. Add a row whenever a miss or a false positive is found.

CASES = [
    # -- corrective contrast: coordinated -------------------------------
    ("CORRECTIVE_CONTRAST", True,
     "This is not merely a technical choice but an architectural commitment."),
    ("CORRECTIVE_CONTRAST", True,
     "We optimised not for throughput but for predictability."),
    ("CORRECTIVE_CONTRAST", True,
     "The lesson is not that caching is bad but that caching is a "
     "commitment."),
    ("CORRECTIVE_CONTRAST", True,
     "The answer lies not in the code but in the culture."),
    # -- cleft, including across a sentence boundary ---------------------
    ("CORRECTIVE_CONTRAST", True, "This isn't a bug, it's a feature."),
    ("CORRECTIVE_CONTRAST", True,
     "The issue isn't about speed, it's about trust."),
    ("CORRECTIVE_CONTRAST", True,
     "Its failure mode was not that it is slow. It is that it validates the "
     "rule document."),
    # -- asyndetic sibling and negated apposition ------------------------
    ("CORRECTIVE_CONTRAST", True,
     "Expected values are derived from the row, not from the design under "
     "test."),
    ("CORRECTIVE_CONTRAST", True, "It is a feature, not a bug."),
    ("CORRECTIVE_CONTRAST", True, "We chose speed, not correctness."),
    ("CORRECTIVE_CONTRAST", True, "It runs nightly, not hourly."),
    ("CORRECTIVE_CONTRAST", True,
     "The fix belongs in the parser, not the tokenizer."),
    # -- ordinary clause coordination must NOT fire ----------------------
    ("CORRECTIVE_CONTRAST", False,
     "I did not go to the meeting but I read the notes afterwards."),
    ("CORRECTIVE_CONTRAST", False, "She was not there but her laptop was."),
    ("CORRECTIVE_CONTRAST", False,
     "We could not reproduce it but we shipped the fix anyway."),
    ("CORRECTIVE_CONTRAST", False,
     "The test does not run on Windows but that is a known issue."),
    ("CORRECTIVE_CONTRAST", False, "He is not tall but he plays centre."),
    ("CORRECTIVE_CONTRAST", False,
     "The build broke on Tuesday and I fixed it on Wednesday."),
    ("CORRECTIVE_CONTRAST", False, "Sam, my editor, called about the draft."),
    ("CORRECTIVE_CONTRAST", False, "Postgres, the primary store, went down."),

    # -- alternative framing (separate id, low confidence) ---------------
    ("ALTERNATIVE_FRAMING", True,
     "Rather than rewriting it, we patched the caller."),
    ("ALTERNATIVE_FRAMING", True, "Instead of retrying, the client gives up."),
    ("ALTERNATIVE_FRAMING", True,
     "This is less about speed than about trust."),
    ("ALTERNATIVE_FRAMING", False, "We patched the caller and moved on."),

    # -- negation escalation --------------------------------------------
    ("NEG_ESCALATION", True,
     "Manual testing did not catch this, and could not have."),
    ("NEG_ESCALATION", True, "It did not work, and was never going to."),
    ("NEG_ESCALATION", True,
     "The build did not fail, and could not have failed."),
    ("NEG_ESCALATION", True, "She was not ready, and never would be."),
    ("NEG_ESCALATION", False,
     "We did not ship it and we did not test it."),
    ("NEG_ESCALATION", False,
     "I did not go to the store and I did not call."),
    ("NEG_ESCALATION", False,
     "It does not compile and I cannot fix it today."),

    # -- abstract adverb: adjective heads only ---------------------------
    ("ABSTRACT_ADVERB", True,
     "It is structurally unable to evaluate the rule document."),
    ("ABSTRACT_ADVERB", True,
     "The approach is fundamentally different from the previous one."),
    ("ABSTRACT_ADVERB", True, "The tests were architecturally sound."),
    ("ABSTRACT_ADVERB", True, "This is a fundamentally flawed assumption."),
    ("ABSTRACT_ADVERB", False,
     "An update writes these fields individually and an allocation writes a "
     "whole entry."),
    ("ABSTRACT_ADVERB", False, "The entries are updated individually."),
    ("ABSTRACT_ADVERB", False, "We processed the rows sequentially."),
    ("ABSTRACT_ADVERB", False,
     "It writes these fields conditionally and reads them serially."),

    # -- participial tail ------------------------------------------------
    ("PARTICIPIAL_TAIL", True,
     "The cache warms on startup, making subsequent requests faster."),
    ("PARTICIPIAL_TAIL", True, "We batch the writes, allowing the queue to "
                               "drain."),
    ("PARTICIPIAL_TAIL", True, "It runs nightly, ensuring the index stays "
                               "fresh."),
    ("PARTICIPIAL_TAIL", False, "Making the change took an afternoon."),

    # -- disguise metaphor -----------------------------------------------
    ("DISGUISE_METAPHOR", True, "A bug wrapped in an excuse trenchcoat."),
    ("DISGUISE_METAPHOR", True, "It is a rewrite dressed up as a refactor."),
    ("DISGUISE_METAPHOR", True,
     "A correctness bug wearing a performance costume."),
    ("DISGUISE_METAPHOR", True, "Technical debt masquerading as velocity."),
    ("DISGUISE_METAPHOR", False, "The parcel was wrapped in brown paper."),

    # -- emphatic reflexive ----------------------------------------------
    ("EMPHATIC_REFLEXIVE", True, "It cannot evaluate the rule document "
                                 "itself."),

    # -- tricolon: fires for all coordinations, but not apposition -------
    ("TRICOLON", True, "The parser is fast, correct, and easy to extend."),
    ("TRICOLON", True, "We tested, we shipped, and we rolled back."),
    ("TRICOLON", True, "The design is simpler, faster, and easier to debug."),
    ("TRICOLON", True, "It was quick, clean, and complete."),
    ("TRICOLON", True, "He came, he saw, he conquered."),
    ("TRICOLON", True,
     "A TAGE entry holds a counter, a usefulness field, and a target."),
    ("TRICOLON", True,
     "Typical examples are three-part coordination, corrective contrast, "
     "participial tails, and emphatic reflexives."),
    ("TRICOLON", False, "Sam, my editor, called about the draft."),
    ("TRICOLON", False, "Postgres, the primary store, went down."),
    ("TRICOLON", False, "It supports TAGE and ITTAGE prediction."),
    ("TRICOLON", False,
     "A TAGE or ITTAGE table entry holds a target."),
    # -- reported bugs, kept as regressions ------------------------------
    # masking must not invent a coordination by blanking inline code
    ("TRICOLON", False,
     "Some had never been driven at all: aging ran with "
     "`tage_enable_aging` and `ittage_enable_aging` held at zero in every "
     "test written to that point, so the entire epoch mechanism was dark."),
    # a construction named between backticks is a mention, not a use
    ("CORRECTIVE_CONTRAST", False,
     "The detector matches `not X but Y` in coordinated form."),
    ("CORRECTIVE_CONTRAST", False,
     "The `X, not Y` pattern needs no coordinator."),
    # ...but a construction that straddles inline code still counts
    ("CORRECTIVE_CONTRAST", True,
     "We check not `tage_enable` but `ittage_enable` in the epoch path."),
    ("CORRECTIVE_CONTRAST", True,
     "The detector matches not X but Y in coordinated form."),
    # a conjunct must not hang across a colon
    ("TRICOLON", False,
     "Both extended checks failed before the fix and passed after, with the "
     "failing values showing the exact corruption: expected c000, actual "
     "e000, and expected c000, actual b000."),
]

# Cases whose text contains markdown; these go through mask_markdown first.
NEEDS_MASKING = {2}


# Tricolon classification: the label, not just whether it fired.
TRICOLON_KINDS = [
    # bug 2: the apposition antecedent must not join the series, so this
    # three-item list reports as 3-part, not 4-part
    ("enumeration",
     "Three of the specification errors were found by the assistant "
     "reporting a discrepancy: the allocation write-data field order, the "
     "pred_strong carryover, and the stored final-target field."),
    ("figure", "The parser is fast, correct, and easy to extend."),
    ("figure", "We tested, we shipped, and we rolled back."),
    ("figure", "It was quick, clean, and complete."),
    ("enumeration",
     "Typical examples are three-part coordination, corrective contrast, "
     "participial tails, and emphatic reflexives."),
    ("enumeration",
     "A TAGE entry holds a counter, a usefulness field, and a target."),
    ("enumeration",
     "The CTR tables specify the conditions when a given CTR is incremented, "
     "decremented, or unmodified."),
    ("list-like", "Supported formats include JSON, YAML, and TOML."),
    ("list-like",
     "We ran the test, the build passed, and the results were archived in "
     "the usual place."),
]


def test_detectors(nlp):
    for cid, want, text in CASES:
        if cid not in tf.CONSTRUCTIONS:
            check("detectors", f"{cid} missing", False)
            continue
        # Cases containing markdown go through analyse(), which applies
        # masking AND the inline-code suppression that run_construction
        # alone does not see.
        if "`" in text:
            with tempfile.TemporaryDirectory() as d:
                pth = Path(d) / "c.md"
                pth.write_text(text + "\n", encoding="utf-8")
                found, _ = tf.analyse(str(pth), nlp, only={cid})
            got = any(x.construction == cid for x in found)
        else:
            got = bool(tf.run_construction(cid, nlp(text), nlp))
        check("detectors", f"{cid} {'fires' if want else 'silent'}",
              got == want, f"want={want} got={got}: {text[:70]}")

    count_cases = [
        (3, "Three of the specification errors were found by the assistant "
            "reporting a discrepancy: the allocation write-data field order, "
            "the pred_strong carryover, and the stored final-target field."),
        (3, "A TAGE entry holds a counter, a usefulness field, and a "
            "target."),
        (3, "The parser is fast, correct, and easy to extend."),
    ]
    for n, text in count_cases:
        hits = tf.run_construction("TRICOLON", nlp(text), nlp)
        got = hits[0][1].split("-part")[0] if hits else "?"
        check("detectors", f"tricolon counts {n} items", got == str(n),
              f"want {n}-part got {got}-part: {text[:60]}")

    for want, text in TRICOLON_KINDS:
        hits = tf.run_construction("TRICOLON", nlp(text), nlp)
        got = hits[0][1].split(", ")[-1] if hits else "none"
        check("detectors", f"tricolon kind {want}", got == want,
              f"want={want} got={got}: {text[:70]}")


# ----------------------------------------------------------------- masking

MASK_KEEP = [
    ("blockquote", "Para one.\n\n> quoted\n\nPara two.\n",
     ["Para one", "Para two"], ["quoted"]),
    ("table", "Before.\n\n| a | b |\n| - | - |\n\nAfter.\n",
     ["Before", "After"], []),
    ("indented code", "Intro.\n\n    code_here()\n\nOutro.\n",
     ["Intro", "Outro"], ["code_here"]),
    ("fenced code", "One.\n\n```py\nSECRET = 1\n```\n\nTwo.\n",
     ["One", "Two"], ["SECRET"]),
    ("hr", "Top.\n\n---\n\nBottom.\n", ["Top", "Bottom"], []),
    # Inline code keeps its content -- blanking it mid-sentence made the
    # parser read across the hole and invent coordinations. Only the
    # backticks are removed.
    ("inline code", "Call `foo()` to start.\n",
     ["Call", "foo()", "to start"], ["`"]),
    ("link target", "See [the docs](http://x.com/y) now.\n",
     ["the docs", "now"], ["x.com"]),
    ("pragma off/on",
     "Before.\n\n<!-- ticfinder_off -->\nBIO\n<!-- ticfinder_on -->\n\n"
     "After.\n", ["Before", "After"], ["BIO"]),
    ("pragma unclosed",
     "Kept.\n\n<!-- ticfinder_off -->\nGONE\n", ["Kept"], ["GONE"]),
    ("pragma hyphen",
     "A.\n\n<!-- ticfinder-off -->\nX\n<!-- ticfinder on -->\n\nB.\n",
     ["A.", "B."], ["X"]),
    ("pragma case",
     "C.\n\n<!-- TICFINDER_OFF -->\nY\n<!-- TicFinder_On -->\n\nD.\n",
     ["C.", "D."], ["Y"]),
    ("pragma skip one block",
     "<!-- ticfinder_skip -->\nSKIPPED\n\nKept after.\n",
     ["Kept after"], ["SKIPPED"]),
]


def test_masking():
    for name, src, keep, gone in MASK_KEEP:
        m = tf.mask_markdown(src)
        check("masking", f"{name}: length preserved", len(m) == len(src),
              f"{len(m)} vs {len(src)}")
        nl_ok = all(m[i] == "\n" for i, ch in enumerate(src) if ch == "\n")
        check("masking", f"{name}: newlines preserved", nl_ok)
        for t in keep:
            check("masking", f"{name}: kept {t!r}", t in m)
        for t in gone:
            check("masking", f"{name}: masked {t!r}", t not in m)


# ------------------------------------------------------------------- spans

SPAN_TEXT = " ".join(t for _, _, t in CASES)


def test_spans(nlp):
    doc = nlp(SPAN_TEXT)
    for cid in tf.CONSTRUCTIONS:
        for pname, fn, _ in tf.CONSTRUCTIONS[cid]["patterns"]:
            try:
                hits = fn(doc, nlp)
            except Exception as e:
                check("spans", f"{cid}.{pname} runs", False, repr(e))
                continue
            bad = [h[0] for h in hits
                   if h[0].end <= h[0].start
                   or not h[0].text.strip()
                   or h[0].start_char >= h[0].end_char]
            check("spans", f"{cid}.{pname} well-formed spans", not bad,
                  f"{len(bad)} malformed of {len(hits)}")


# ----------------------------------------------------------------- waivers

def test_waivers(nlp):
    """A waiver must survive edits elsewhere in the document."""
    base = ("The parser is fast, correct, and easy to extend.\n\n"
            "Ultimately, this is the real problem, not the parser.\n")
    shifted = "A new opening paragraph.\n\n" + base
    reflowed = base.replace("fast, correct, and easy to extend",
                            "fast, correct,\nand easy to extend")

    def fps(text):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "a.md"
            p.write_text(text, encoding="utf-8")
            f, _ = tf.analyse(str(p), nlp)
            return {tf.fingerprint(x) for x in f}

    a, b, c = fps(base), fps(shifted), fps(reflowed)
    check("waivers", "ids survive an inserted paragraph", a <= b,
          f"lost {sorted(a - b)}")
    check("waivers", "ids survive reflowing", a <= c,
          f"lost {sorted(a - c)}")
    # stale entries must be listed, not just counted
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "a.md"
        src.write_text(base, encoding="utf-8")
        f, _ = tf.analyse(str(src), nlp)
        for x in f:
            x.fp = tf.fingerprint(x)
        wp = tf.waiver_path(str(src))
        tf.save_waivers(wp, str(src),
                        {x.fp: {"construction": x.construction,
                                "pattern": x.pattern,
                                "line_when_waived": x.line,
                                "text": x.text} for x in f})
        src.write_text("Nothing here at all.\n", encoding="utf-8")
        w, warn = tf.load_waivers(wp, str(src))
        f2, _ = tf.analyse(str(src), nlp)
        live = {tf.fingerprint(x) for x in f2}
        stale = set(w) - live
        check("waivers", "orphaned waivers are detectable",
              len(stale) == len(w) and len(stale) > 0,
              f"{len(stale)} stale of {len(w)}")
        check("waivers", "stale entries retain text for reporting",
              all(w[fp].get("text") for fp in stale))

    check("waivers", "ids are 6 hex chars",
          all(len(x) == 6 and all(ch in "0123456789abcdef" for ch in x)
              for x in a))


# --------------------------------------------------------------------- cli

def test_cli():
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        src = d / "a.md"
        src.write_text(
            "The parser is fast, correct, and easy to extend.\n\n"
            "Ultimately, this is the real problem, not the parser.\n",
            encoding="utf-8")

        # Inherit the caller's environment. Replacing it wholesale would
        # drop VIRTUAL_ENV, PYTHONPATH and PATH, so the child interpreter
        # could not import spacy. Override only what the test needs.
        env = dict(os.environ)
        env["COLUMNS"] = "100"
        env.pop("NO_COLOR", None)

        def run(*args):
            return subprocess.run(
                [sys.executable, str(SCRIPT), str(src), "--no-waivers",
                 *args],
                capture_output=True, text=True, env=env, cwd=str(d))

        for flags in ([], ["--compact"], ["--summary"], ["--context"],
                      ["--explain"], ["--by-position"], ["--patterns"],
                      ["--stats"], ["--ascii"], ["--plain"],
                      ["--only", "TRICOLON"], ["--off", "TRICOLON"]):
            r = run(*flags)
            check("cli", f"runs with {flags or ['(no flags)']}",
                  r.returncode == 0, r.stderr[-300:])
            if r.returncode == 0:
                wide = [l for l in r.stdout.split("\n") if len(l) > 100]
                check("cli", f"width respected with {flags or ['(none)']}",
                      not wide, f"{len(wide)} lines over 100")

        r = run("--ascii", "--plain")
        check("cli", "--ascii emits no non-ASCII",
              all(ord(ch) < 128 for ch in r.stdout))

        r = run("--plain")
        check("cli", "piped output has no ANSI escapes",
              "\033" in r.stdout is False or "\033" not in r.stdout)

        # bad phrase file fails loudly
        bad = d / "bad.json"
        bad.write_text('{"constructions":[{"id":"X","confidence":"urgent",'
                       '"phrases":["a"]}]}', encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(src), "--phrases", str(bad)],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "invalid confidence rejected", r.returncode != 0,
              r.stdout[-200:])

        # html report
        r = run("--html", str(d / "rep"))
        out = d / "rep" / "a.html"
        check("cli", "--html writes a file", out.exists())
        if out.exists():
            h = out.read_text(encoding="utf-8")
            body = h[h.index('<div class="src">'):h.index('<div class="side">')]
            depth, ok = 0, True
            for i in range(len(body)):
                if body.startswith("<mark", i):
                    depth += 1
                elif body.startswith("</mark", i):
                    depth -= 1
                if depth > 1 or depth < 0:
                    ok = False
            check("cli", "html marks do not nest", ok)
            check("cli", "html has no empty marks",
                  "<mark" not in h or "></mark>" not in h.replace(" ", ""))


# -------------------------------------------------------------------- main

SECTIONS = {
    "registry": lambda nlp: test_registry(),
    "detectors": test_detectors,
    "masking": lambda nlp: test_masking(),
    "spans": test_spans,
    "waivers": test_waivers,
    "cli": lambda nlp: test_cli(),
}


def main():
    wanted = [a for a in sys.argv[1:] if not a.startswith("-")]
    todo = wanted or list(SECTIONS)
    unknown = [w for w in todo if w not in SECTIONS]
    if unknown:
        sys.exit(f"unknown section(s): {', '.join(unknown)}\n"
                 f"available: {', '.join(SECTIONS)}")

    nlp = tf.load_model("en_core_web_md")
    for name in todo:
        print(f"\n{name}")
        SECTIONS[name](nlp)

    print()
    if FAILS:
        print(f"{len(FAILS)} FAILURE(S)")
        for sec, name, _ in FAILS:
            print(f"  {sec}: {name}")
        sys.exit(1)
    print("all passed")


if __name__ == "__main__":
    main()

