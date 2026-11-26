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
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace
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
    "CORRECTIVE_CONTRAST": ["cc_coordinated", "cc_additive", "cc_cleft",
                            "cc_parallel_sibling", "cc_negated_apposition"],
    "ALTERNATIVE_FRAMING": ["af_rather_than", "af_instead_of",
                            "af_less_than"],
    "NEG_ESCALATION": ["neg_escalation"],
    "GAPPED_ANTITHESIS": ["gapped_antithesis"],
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

    # -- gapped antithetical coordination --------------------------------
    ("GAPPED_ANTITHESIS", True,
     "The modified test failed before the fix and passed after."),
    ("GAPPED_ANTITHESIS", True, "It worked locally but broke in CI."),
    ("GAPPED_ANTITHESIS", True,
     "The build passed on Monday and failed on Tuesday."),
    ("GAPPED_ANTITHESIS", True,
     "The gate was closed before the patch and opened after."),
    ("GAPPED_ANTITHESIS", True,
     "The check succeeded in simulation but failed on hardware."),
    ("GAPPED_ANTITHESIS", False, "We ran the tests and shipped the release."),
    ("GAPPED_ANTITHESIS", False,
     "The parser reads the header and writes the payload."),
    ("GAPPED_ANTITHESIS", False, "We failed to reproduce it and moved on."),
    # sequential narration, not ellipsis: the second verb has its own object
    ("GAPPED_ANTITHESIS", False, "She opened the file and closed it again."),
    ("GAPPED_ANTITHESIS", False, "We added the flag and removed the old one."),
    ("GAPPED_ANTITHESIS", False, "It reads from Redis and writes to Postgres."),

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
    ("PARTICIPIAL_TAIL", True,
     "We rewrote the inner loop, using fewer cycles per entry."),
    ("PARTICIPIAL_TAIL", True,
     "We count the misses in hardware, using a 4-bit saturating counter."),

    # -- disguise metaphor -----------------------------------------------
    ("DISGUISE_METAPHOR", True, "A bug wrapped in an excuse trenchcoat."),
    ("DISGUISE_METAPHOR", True, "It is a rewrite dressed up as a refactor."),
    ("DISGUISE_METAPHOR", True,
     "A correctness bug wearing a performance costume."),
    ("DISGUISE_METAPHOR", True, "Technical debt masquerading as velocity."),
    ("DISGUISE_METAPHOR", False, "The parcel was wrapped in brown paper."),
    # `pose` and `pass` need an `as` frame on an intransitive, reflexive
    # or `off` use (TF-006). Literal uses are transitive or passive.
    ("DISGUISE_METAPHOR", True, "A rewrite posing as a refactor."),
    ("DISGUISE_METAPHOR", True, "It was a rewrite passed off as a refactor."),
    ("DISGUISE_METAPHOR", True, "Speculation passing itself off as "
                                "evidence."),
    ("DISGUISE_METAPHOR", False, "These workloads pose significant "
                                 "challenges."),
    ("DISGUISE_METAPHOR", False, "These workloads are posing significant "
                                 "challenges."),
    ("DISGUISE_METAPHOR", False, "Posing the question this way helps."),
    ("DISGUISE_METAPHOR", False, "The design passes all regression tests."),
    ("DISGUISE_METAPHOR", False, "A design passing all regression tests."),
    ("DISGUISE_METAPHOR", False, "It uses message passing between cores."),
    ("DISGUISE_METAPHOR", False, "The value is passed as an argument."),
    ("DISGUISE_METAPHOR", False, "The step required passing the depth as "
                                 "an argument."),
    ("DISGUISE_METAPHOR", False, "The caller reads the depth, passing it "
                                 "as an argument."),
    ("DISGUISE_METAPHOR", False, "The problem is posed as an integer "
                                 "program."),
    # Literal `passing for` is common in verification prose, so `pass for`
    # is not supported.
    ("DISGUISE_METAPHOR", False, "The test is passing for all seeds."),

    # -- hollow booster (phrase pattern, runs through analyse) ------------
    # `significantly,` is a booster only at the start of a sentence;
    # mid-sentence it is a manner adverb (TF-006).
    ("HOLLOW_BOOSTER", True, "Significantly, the cache never misses."),
    ("HOLLOW_BOOSTER", True, "Notably, this needs no extra hardware."),
    ("HOLLOW_BOOSTER", True, "And, more importantly, it removes the stall."),
    ("HOLLOW_BOOSTER", True, "Crucially, the order is preserved."),
    ("HOLLOW_BOOSTER", True, "The fix is small. Significantly, it needs "
                             "no new state."),
    ("HOLLOW_BOOSTER", False, "The number of writes drops significantly, "
                              "about 73%."),
    ("HOLLOW_BOOSTER", False, "It does not affect throughput significantly, "
                              "but it costs area."),
    ("HOLLOW_BOOSTER", False, "The miss rate fell significantly, from 9% "
                              "to 4%."),
    # `more significantly,` is a booster where `significantly` is not the
    # sentence start. The span starts at `more`.
    ("HOLLOW_BOOSTER", True, "More significantly, the table needs no new "
                             "port."),
    ("HOLLOW_BOOSTER", True, "Even more significantly, the precharge time "
                             "doubles."),
    ("HOLLOW_BOOSTER", True, "Most significantly, nothing else changes."),
    ("HOLLOW_BOOSTER", False, "Power fell, but area grew more "
                              "significantly, by about 40%."),

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

# Em-dash subtype. The 'not X -- Y' pivot must key on a negation token, not
# on the letters "not" anywhere in the preceding words.
EM_DASH_KINDS = [
    ("pivot (not X — Y)", "The fault is not in the RTL — it lives in the test."),
    ("pivot (not X — Y)", "We don't ship that path — we simulate it."),
    # "never" is not a negator here (TF-001: its one corpus hit was this)
    ("single break",
     "The flag was evaluated once and never again — fixed by gating it."),
    ("paired aside", "We added another — smaller — table."),
    ("single break", "There was nothing — the log was empty."),
    ("single break", "Read the release notes — they cover the change."),
    ("single break", "The annotated trace — shown below."),
]


# Which pattern fires, and at what confidence: (construction, text,
# {pattern name: confidence}). TF-007 split af_rather_instead by phrase.
PATTERN_CASES = [
    ("ALTERNATIVE_FRAMING", "We hash the key rather than compare it.",
     {"af_rather_than": "med"}),
    ("ALTERNATIVE_FRAMING", "Use a table instead of a CAM.",
     {"af_instead_of": "low"}),
    ("ALTERNATIVE_FRAMING",
     "We hash the key rather than compare it, and use a table instead of "
     "a CAM.",
     {"af_rather_than": "med", "af_instead_of": "low"}),
    ("ALTERNATIVE_FRAMING",
     "Rather than rewriting it, we patched the caller.",
     {"af_rather_than": "med"}),
    ("ALTERNATIVE_FRAMING", "Instead of retrying, the client gives up.",
     {"af_instead_of": "low"}),
    # TF-007 phase 2: lemma `use` runs one level below the construction.
    # Most `, using ...` tails give the method; the lemma cannot tell a
    # restating one apart, so both report at med.
    ("PARTICIPIAL_TAIL", "We rewrote the inner loop, using fewer cycles "
                         "per entry.", {"participial_tail": "med"}),
    ("PARTICIPIAL_TAIL", "We count the misses in hardware, using a 4-bit "
                         "saturating counter.", {"participial_tail": "med"}),
    ("PARTICIPIAL_TAIL", "The cache warms on startup, making subsequent "
                         "requests faster.", {"participial_tail": "high"}),
    # TF-013: levels from the TF-012 LRs under set C (roadmap s.19, s.20).
    # Every `tricolon` label reports at med; the figure row was med before.
    ("TRICOLON", "A TAGE entry holds a counter, a usefulness field, and a "
                 "target.", {"tricolon": "med"}),                # enumeration
    ("TRICOLON", "Supported formats include JSON, YAML, and TOML.",
     {"tricolon": "med"}),                                       # list-like
    ("TRICOLON", "The parser is fast, correct, and easy to extend.",
     {"tricolon": "med"}),                                       # figure
    ("EMPHATIC_REFLEXIVE", "The rule document itself is the reference.",
     {"emphatic_reflexive": "low"}),
]


# Whether one pattern fires: (construction, pattern, want, text). A
# construction row can pass because a sibling pattern fires; these rows
# test the pattern itself. TF-010: failure kinds from a reading of the
# TF-009 spec findings, written as synthetic sentences.
PATTERN_ROWS = [
    # -- cc_coordinated: corrective forms it must keep -------------------
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "This is not merely a technical choice but an architectural "
     "commitment."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The gap was not in the plan but in the execution."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The caller does not pass the exact size, but rather the number of "
     "pages."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "Retry is not built into the protocol but is instead left to the "
     "client."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The archive is used not for distribution but as a temporary "
     "exchange format."),
    # negation in the second conjunct
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The flag is optional but not deprecated."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The register is readable but not writable from user mode."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The cache is flushed on reset but not on resume."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The parser accepts tabs but never emits them."),
    # negation in a subordinate clause after `but`
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The handler retries the write but stops if the device does not "
     "respond."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The tool caches the result but drops it when the key is not found."),
    # concessive: first conjunct negated, the second adds `still` or its
    # own modal
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The old flag is no longer documented but is still accepted."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The option is not set by default but can be enabled at build time."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "Comments should not be generated but must be accepted."),
    # additive `not only ... but also`: its own pattern, not this one
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The change affects not only the parser but also the code "
     "generator."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "Errors are reported not just to the caller but also to the log."),
    # TF-011: concessive pairs. The first conjunct concedes a limit and
    # the second asserts something that does not take the negated
    # element's place. Emphatic `do` in the second conjunct (C1)
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "This proposal does not attempt to cover every case, but does aim to "
     "settle the common ones."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The linter does not try to fix the layout, but does flag the worst "
     "cases."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "Most users never build from source, but do upgrade to each stable "
     "release."),
    # a different verb and no corrective marker (C2)
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The driver does not support hot plug, but handles a cold restart "
     "cleanly."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The library does not ship a parser, but documents the grammar in "
     "full."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "This note does not settle the naming question, but tries to stay "
     "compatible with either answer."),
    # a negated predicate adjective or participle, then a lexical verb (C3)
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The listing is not runnable but shows the calling sequence."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The scheme is not fully general, but handles most real inputs."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The buffer is not visible to software but feeds the hash engine "
     "directly."),
    # the second conjunct carries its own negation (C4)
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The cache does not save much area, but does not slow the pipeline "
     "either."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The scan did not find the bug, but never reported a false one."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The flag does not change the output, but is not free to compute."),
    # the second conjunct is a clause whose subject is `there` or a
    # clause (C5)
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The keyword is not in the language yet, but there is a proposal to "
     "add it."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "The draft does not commit to a schedule, but there is real value in "
     "naming the targets."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", False,
     "That case does not matter here, but in general, knowing which is "
     "which will be important."),
    # TF-011: corrective forms a concessive cue could hit by mistake.
    # A repeated verb
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "Do not take the global lock, but take the per-queue lock."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The size does not include the header, but does include the "
     "padding."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The reader does not parse the whole file but parses the index."),
    # a different verb without a marker
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "Proxies should not rewrite the header fields, but pass them along."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The loader does not copy the image into memory but maps it in "
     "place."),
    # a passive second conjunct
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The session key is not chosen by the client but is assigned by the "
     "server."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "These limits are not fixed by the standard but are left to each "
     "vendor."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The address is not computed in hardware but is supplied by "
     "firmware."),
    # constituent negation
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The cost lies not in the decoder but in the register file."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The flag is read not at reset but at the first fetch."),
    # a negated predicate adjective or noun, then a lexical verb
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "Retention of the state is not optional but depends on the mode."),
    ("CORRECTIVE_CONTRAST", "cc_coordinated", True,
     "The two counters are not redundant but measure different events."),
    # -- cc_additive: not only X but also Y ------------------------------
    ("CORRECTIVE_CONTRAST", "cc_additive", True,
     "The change affects not only the parser but also the code "
     "generator."),
    ("CORRECTIVE_CONTRAST", "cc_additive", True,
     "Errors are reported not just to the caller but also to the log."),
    ("CORRECTIVE_CONTRAST", "cc_additive", True,
     "Writes are visible not only to other cores but to devices as well."),
    ("CORRECTIVE_CONTRAST", "cc_additive", True,
     "This is not merely a style rule but also a correctness rule."),
    ("CORRECTIVE_CONTRAST", "cc_additive", False,
     "This is not merely a technical choice but an architectural "
     "commitment."),
    ("CORRECTIVE_CONTRAST", "cc_additive", False,
     "The flag is optional but not deprecated."),

    # -- cc_cleft: forms it must keep ------------------------------------
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "This isn't a bug, it's a feature."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "The issue isn't about speed, it's about trust."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "Its failure mode was not that it is slow. It is that it validates "
     "the rule document."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "Archival is not a permanent state, it is a note on the current "
     "status."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "The deliverable is not that the test passed; it is that the test "
     "failed for the right defect."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "Version 2 is NOT RECOMMENDED. Instead, it is RECOMMENDED to deploy "
     "version 3."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "Their predictor is not a general solution. It is a collection of "
     "three heuristics."),
    # parallel `to` clauses, and the same modal on both copulas
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "The goal of the flag is not to block the build; it is to warn the "
     "author."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "That cache may not be the one that served the read. It may be "
     "another cache on the same bus."),
    # a line break between the two clauses is not a word
    ("CORRECTIVE_CONTRAST", "cc_cleft", True,
     "The pattern is not haste in execution;\nit is the absence of the "
     "document at the moment of the choice."),
    # the second copula starts a new statement
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The checker may not be strict. It would be slow on large inputs."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The field is not optional. It is possible to omit the header."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The field is not present in version 1. For example, it is possible "
     "to omit it entirely."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The cookie is not valid on the second server. This is because each "
     "server keeps its own table."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The checker is not run by default. It would be slow on large "
     "inputs."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "This may not be possible on every target. It is the job of the "
     "loader to check."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The role of the flag is not clear. Specifically, it is unclear when "
     "it is read."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The role is not obvious. So, for example, this is the same type."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The second pass is not cheap. This is mainly due to the extra copy."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The value is not final. It is uncertain whether the vendor will "
     "change it."),
    # a causal or concessive link
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "Although the header is not required, it is useful for debugging."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "Even if the cache is not warm, it is safe to read."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The result is not cached, so it is recomputed on every call."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "Since the buffer is not shared, it is safe to free."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The flag is not set, though it is documented as the default."),
    # the second copula inside a relative or subordinate clause
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The value is not a valid index, which is why the check fails."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The page is not locked, and the client writes only the part that is "
     "locked."),
    ("CORRECTIVE_CONTRAST", "cc_cleft", False,
     "The tool is not strict here, and nobody knows whether it is "
     "correct."),

    # -- af_less_than: one description framed against another ------------
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "This is less about speed than about trust."),
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "It is less a bug than a feature."),
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "The limit is more a convention than a rule."),
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "The review is more of a conversation than an audit."),
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "The choice was less about cost than about risk."),
    ("ALTERNATIVE_FRAMING", "af_less_than", True,
     "The fault lies more in the review than in the code."),
    # comparison with a number or a count
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "A request may carry more than one header."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The field must not occur more than once."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The timeout is less than 8 seconds."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The method goes back more than sixty years."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The run produced one more finding. Running every target rather "
     "than one took longer."),
    # comparison with a value or a limit
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The length must be less than or equal to the buffer size."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The round trip may be less than the clock granularity."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "Supervisor mode is less privileged than machine mode."),
    # comparative of degree
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The new syntax is more readable than the old one."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "A keyed hash is more secure than a checksum."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "This form is more expressive than the old API."),
    # `more about` compared with a clause: a quantity
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The tool learns more about the network than it would from a log."),
    # more or less with a noun
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The trait offers more features than a callback."),
    ("ALTERNATIVE_FRAMING", "af_less_than", False,
     "The motor drew more power than desired."),

    # -- neg_escalation: gapped conjuncts it must keep --------------------
    ("NEG_ESCALATION", "neg_escalation", True,
     "Manual testing did not catch this, and could not have."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "The build did not fail, and could not have failed."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "The key is not (and cannot be) stored in the file."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "These protocols cannot, and should not, run over the open "
     "Internet."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "Default values do not work well (and may never)."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "The test did not catch the bug, and could not have caught it."),
    ("NEG_ESCALATION", "neg_escalation", True,
     "The table need not be, and usually will not be, as large as the "
     "cache."),
    # paired normative negatives with their own verbs
    ("NEG_ESCALATION", "neg_escalation", False,
     "The client MUST NOT add the entry and MUST NOT return an error."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The instruction shall not read the register and shall not cause "
     "any side effects."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "Applications SHOULD NOT use these types and SHOULD NOT declare "
     "support for them."),
    # descriptive paired negatives with their own verbs
    ("NEG_ESCALATION", "neg_escalation", False,
     "The server will not retry the request and will not log the "
     "failure."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The upper layer cannot see the radio and cannot fix the problem."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The router does not support the feature and will not take part in "
     "balancing."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The module does not compile and will not run."),
    # the verb repeated with objects of its own
    ("NEG_ESCALATION", "neg_escalation", False,
     "The patch must not break the build, and must not break the tests."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The values are not generic and would not be a fair test."),
    # a gapped disjunction of modals
    ("NEG_ESCALATION", "neg_escalation", False,
     "The option either SHOULD NOT or MUST NOT be used."),
    ("NEG_ESCALATION", "neg_escalation", False,
     "The flag need not, or must not, be set, depending on the mode."),
]

# PATTERN_ROWS that fail before a fix lands (TF-010), keyed by
# (pattern, text). They print as xfail and do not fail the suite; an
# entry that passes prints as xpass and fails it, so the set is emptied
# with the fix. TF-011: the concessive rows, one group per cue. No cue
# passed both its held-out test and the arXiv recheck, so none was
# merged and the rows stay pending (roadmap section 18).
PENDING = {
    ("cc_coordinated", t) for t in (
        "This proposal does not attempt to cover every case, but does aim "
        "to settle the common ones.",
        "The linter does not try to fix the layout, but does flag the "
        "worst cases.",
        "Most users never build from source, but do upgrade to each "
        "stable release.",
        "The driver does not support hot plug, but handles a cold restart "
        "cleanly.",
        "The library does not ship a parser, but documents the grammar in "
        "full.",
        "This note does not settle the naming question, but tries to stay "
        "compatible with either answer.",
        "The listing is not runnable but shows the calling sequence.",
        "The scheme is not fully general, but handles most real inputs.",
        "The buffer is not visible to software but feeds the hash engine "
        "directly.",
        "The cache does not save much area, but does not slow the pipeline "
        "either.",
        "The scan did not find the bug, but never reported a false one.",
        "The flag does not change the output, but is not free to compute.",
        "The keyword is not in the language yet, but there is a proposal "
        "to add it.",
        "The draft does not commit to a schedule, but there is real value "
        "in naming the targets.",
        "That case does not matter here, but in general, knowing which is "
        "which will be important.",
    )}


# Phrase-list confidence per matched text (TF-007 phase 3):
# (construction, text, {matched text, lowercased: confidence}). Raised
# forms rose in arXiv abstracts and bodies; the others keep the
# construction's low.
PHRASE_CONF_CASES = [
    ("LLM_DICTION", "The survey gives a comprehensive view of the field.",
     {"comprehensive": "med"}),
    ("LLM_DICTION", "The schedule is dynamic.", {"dynamic": "low"}),
    ("LLM_DICTION", "The landscapes differ.", {"landscapes": "low"}),
    ("CONSULTANT_REGISTER", "The design leverages a shared buffer.",
     {"leverages": "med"}),
    ("CONSULTANT_REGISTER", "Leveraging a shared buffer, the design saves "
                            "area.", {"leveraging": "med"}),
    ("CONSULTANT_REGISTER", "We leverage a shared buffer.",
     {"leverage": "low"}),
    ("CONSULTANT_REGISTER", "The buffer was leveraged across products.",
     {"leveraged": "low"}),
    ("CONSULTANT_REGISTER", "We are optimizing the inner loop.",
     {"optimizing": "med"}),
    ("CONSULTANT_REGISTER", "The inner loop is optimized.",
     {"optimized": "low"}),
]


def test_detectors(nlp):
    extra = []
    for name in tf.DEFAULT_PHRASE_FILES:
        if (HERE / name).exists():
            extra.extend(tf.load_phrase_file(HERE / name))
    phrase_ids = set(tf.PHRASE_PATTERNS) | {e["id"] for e in extra}
    for cid, want, text in CASES:
        if cid not in tf.CONSTRUCTIONS and cid not in phrase_ids:
            check("detectors", f"{cid} missing", False)
            continue
        # Cases containing markdown, and phrase-list constructions, go
        # through analyse(), which applies masking AND the inline-code
        # suppression that run_construction alone does not see.
        if "`" in text or cid not in tf.CONSTRUCTIONS:
            with tempfile.TemporaryDirectory() as d:
                pth = Path(d) / "c.md"
                pth.write_text(text + "\n", encoding="utf-8")
                found, _ = tf.analyse(str(pth), nlp, only={cid},
                                      extra=extra)
            got = any(x.construction == cid for x in found)
        else:
            got = bool(tf.run_construction(cid, nlp(text), nlp))
        check("detectors", f"{cid} {'fires' if want else 'silent'}",
              got == want, f"want={want} got={got}: {text[:70]}")

    for cid, text, want in PHRASE_CONF_CASES:
        with tempfile.TemporaryDirectory() as d:
            pth = Path(d) / "c.md"
            pth.write_text(text + "\n", encoding="utf-8")
            found, _ = tf.analyse(str(pth), nlp, only={cid}, extra=extra)
        got = {" ".join(x.text.split()).lower(): x.confidence
               for x in found if x.construction == cid}
        check("detectors", f"{cid} confidence {sorted(want)}",
              got == want, f"want={want} got={got}: {text[:70]}")

    # Phrase entries as objects: a per-phrase level, a per-form level, and
    # a plain string that keeps the construction's level.
    with tempfile.TemporaryDirectory() as d:
        pf = Path(d) / "p.json"
        pf.write_text(json.dumps({"constructions": [
            {"id": "T_TEXT", "confidence": "low", "phrases": [
                "deep dive", {"phrase": "ground truth", "confidence": "med"}]},
            {"id": "T_LEMMA", "confidence": "low", "match_lemma": True,
             "phrases": [{"phrase": "leverage",
                          "forms": {"leverages": "high"}}]}]}),
            encoding="utf-8")
        ex = tf.load_phrase_file(pf)
        pth = Path(d) / "c.md"
        pth.write_text("A deep dive into ground truth. It leverages X. "
                       "We leverage Y.\n", encoding="utf-8")
        found, _ = tf.analyse(str(pth), nlp, only={"T_TEXT", "T_LEMMA"},
                              extra=ex)
        got = sorted((x.construction, x.text.lower(), x.confidence)
                     for x in found)
        want = [("T_LEMMA", "leverage", "low"),
                ("T_LEMMA", "leverages", "high"),
                ("T_TEXT", "deep dive", "low"),
                ("T_TEXT", "ground truth", "med")]
        check("detectors", "phrase objects set confidence per phrase/form",
              got == want, f"got {got}")
        check("detectors", "phrase findings keep an empty pattern name",
              all(x.pattern == "" for x in found))

    for cid, pname, want, text in PATTERN_ROWS:
        names = [p for p, _, _ in tf.CONSTRUCTIONS.get(cid, {}).get(
            "patterns", [])]
        got = pname in names and any(
            h[3] == pname for h in tf.run_construction(cid, nlp(text), nlp))
        name = f"{pname} {'fires' if want else 'silent'}: {text[:40]}"
        detail = f"want={want} got={got}: {text[:70]}"
        if (pname, text) in PENDING:
            if got == want:
                check("detectors", f"xpass {name}", False,
                      "passes; remove it from PENDING")
            elif VERBOSE:
                print(f"  xfail {name}")
            continue
        check("detectors", name, got == want, detail)

    for cid, text, want in PATTERN_CASES:
        hits = tf.run_construction(cid, nlp(text), nlp)
        got = {}
        for _span, _sub, conf, pname in hits:
            got[pname] = conf
        check("detectors", f"{cid} patterns {sorted(want)}: {text[:30]}",
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

    for want, text in EM_DASH_KINDS:
        doc = nlp(text)
        subs = [h[1] for h in tf.em_dash_findings(doc, text)]
        got = subs[0] if subs else "none"
        check("detectors", f"em dash {want}: {text[:30]}", got == want,
              f"want={want} got={got}: {text[:70]}")

    # A pattern that throws must not look like a pattern that found nothing.
    def _boom(doc, nlp):
        raise RuntimeError("deliberate test failure")
    pats = tf.CONSTRUCTIONS["TRICOLON"]["patterns"]
    pats.append(("_boom", _boom, None))
    try:
        import contextlib
        import io
        err = io.StringIO()
        saved, tf.STRICT = tf.STRICT, False
        with contextlib.redirect_stderr(err):
            tf.run_construction("TRICOLON", nlp("A, B, and C."), nlp)
        check("detectors", "crashing pattern warns on stderr",
              "_boom" in err.getvalue() and "deliberate" in err.getvalue(),
              repr(err.getvalue()[:120]))
        tf.STRICT = True
        raised = False
        try:
            tf.run_construction("TRICOLON", nlp("A, B, and C."), nlp)
        except RuntimeError:
            raised = True
        check("detectors", "crashing pattern raises under strict", raised)
    finally:
        tf.STRICT = saved
        pats.remove(("_boom", _boom, None))


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

    # Code-aware masker: code that is not fenced or backticked. Positive
    # rows must be blanked; prose around them must survive.
    ("code: port listing line",
     "The fetch stage has two ports.\n\n"
     "input  logic [31:0] pc_i, output logic valid_o\n\n"
     "Both are registered.\n",
     ["The fetch stage has two ports", "Both are registered"],
     ["pc_i", "valid_o", "[31:0]"]),
    ("code: port listing run",
     "The ports are:\n"
     "  input  logic        clk_i,\n"
     "  input  logic [31:0] pc_i,\n"
     "  output logic        valid_o\n\n"
     "That is all.\n",
     ["The ports are:", "That is all"], ["clk_i", "pc_i", "valid_o"]),
    ("code: identifier run",
     "These are the stage signals.\n\nfoo_bar_p1, baz_q2, qux_r3\n\n"
     "They are all registered.\n",
     ["These are the stage signals", "They are all registered"],
     ["foo_bar_p1", "baz_q2", "qux_r3"]),
    ("code: expression lines",
     "The update rule is:\n\n"
     "  bit_out  = ghr_mem[(ghist_ptr + H) % GHR_WIDTH];\n"
     "  if (stall_i) { cnt_q = cnt_q; }\n\n"
     "where H is the history depth.\n",
     ["The update rule is:", "where H is the history depth"],
     ["ghr_mem", "stall_i", "cnt_q"]),
    ("code: register table as plain lines",
     "The block has three registers.\n\n"
     "CTRL     0x00  [7:0]   RW  enable\n"
     "STATUS   0x04  [3:0]   RO  busy\n"
     "DATA     0x08  [31:0]  RW  payload\n\n"
     "Reset clears all three.\n",
     ["The block has three registers", "Reset clears all three"],
     ["0x04", "STATUS", "payload"]),

    # Netlist instance lines: two tokens (cell name, port map), so a
    # token-share prose guard reads the cell name as half prose. Dense
    # balanced symbols and a code ending (;) override it. Found in the
    # specs spot-check (TF-002 step 7).
    ("code: netlist instance lines",
     "The cells are:\n\n"
     "dff r3b2(.clk(clk),.q(q3[2]),.e(wen[3]),.d(di[2]));\n"
     "inv iwa1 (.y(wa0_[1]), .a(wa0[1]));\n\n"
     "Done.\n",
     ["The cells are:", "Done."], ["r3b2", "iwa1", "wa0_"]),
    # ... and after a label line with no closing punctuation.
    ("code: dense line after an unpunctuated label",
     "Register file cells\n"
     "dff r0b4(.clk(clk),.q(q0[4]),.e(wen[0]),.d(di[4]));\n",
     ["Register file cells"], ["r0b4", "wen[0]"]),

    # Negative rows: prose that mentions code must be kept whole.
    # A wrapped prose line dense in brackets that ends the sentence with a
    # full stop (BLOG_bpu_21 line 414).
    ("prose: wrapped bracket-dense line ending a sentence",
     "Each SC table's 9-bit index moves from\nPC[11:3] to PC[9:1].\n",
     ["PC[11:3] to PC[9:1]."], []),
    ("prose: one backticked identifier",
     "The `ftq_enq` signal stalls when the queue is full.\n",
     ["ftq_enq", "signal stalls when the queue is full."], ["`"]),
    ("prose: one bare identifier",
     "The ftq_enq signal stalls when the queue is full.\n",
     ["The ftq_enq signal stalls when the queue is full."], []),
    ("prose: two bare identifiers",
     "Raising ftq_enq while ftq_full_q is high drops the entry.\n",
     ["Raising ftq_enq while ftq_full_q is high drops the entry."], []),
    ("prose: list of ordinary words",
     "The design is small, fast, and easy to test.\n",
     ["The design is small, fast, and easy to test."], []),
    ("prose: parenthetical abbreviations",
     "Each entry holds a counter (CTR), a usefulness field (USE)\n"
     "and an epoch field (EPC).\n",
     ["a counter (CTR), a usefulness field (USE)",
      "and an epoch field (EPC)."], []),
    # A wrapped prose line can be mostly identifiers. It is the middle of
    # a sentence, so blanking it would leave a hole the parser reads across.
    ("prose: wrapped identifier line mid-sentence",
     "The testbench has the shared tasks (tb_msg, tb_info, tb_warn,\n"
     "tb_error, tb_pf, start_test, stop_test, assert_reset),\n"
     "and the top level.\n",
     ["tb_error, tb_pf, start_test, stop_test, assert_reset),"], []),
    # Link targets are blanked but the link text keeps its "[", which is
    # markdown, not a code symbol (BLOG_bpu_11 line 280).
    ("prose: line of link texts",
     "## Debt\n\n[TD# 43](#td-43-a), [TD# 44](#td-44-a), and\n"
     "[TD# 45](#td-45-a) were opened in session-036.\n",
     ["[TD# 43", "[TD# 44", "were opened"], ["#td-43-a"]),

    # Trailing comments (TF-003). The part before the comment marker is
    # scored; when it is code the whole line goes, comment included.
    ("code: line ending in a // comment",
     "The counter update is:\n\n"
     "next_cnt = cnt_q + incr_i;   // count up on every valid beat\n\n"
     "Reset clears it.\n",
     ["The counter update is:", "Reset clears it."],
     ["next_cnt", "every valid beat"]),
    ("code: line ending in a # comment",
     "The pop is:\n\n"
     "head_q = fifo_pop(fetch_fifo)   # oldest entry first, if any\n\n"
     "It never blocks.\n",
     ["The pop is:", "It never blocks."],
     ["fifo_pop", "oldest entry first"]),
    ("code: line ending in a // comment with no space after the marker",
     "The enable is:\n\n"
     "wr_en_q <= wr_i & ~full_q; //gated by the full flag\n\n"
     "It is registered.\n",
     ["The enable is:", "It is registered."], ["wr_en_q", "gated by"]),
    # Negative rows: a "#" or "//" that is not a comment marker.
    ("prose: ticket number with #",
     "We closed TD #104 after the review and moved to the next item.\n",
     ["We closed TD #104 after the review and moved to the next item."], []),
    ("prose: line with a URL",
     "The draft is at https://example.com/specs/bpu.html for review.\n",
     ["The draft is at https://example.com/specs/bpu.html for review."], []),
    ("prose: markdown heading",
     "## Results for the cache # sweep\n\nThe sweep ran twice.\n",
     ["## Results for the cache # sweep", "The sweep ran twice."], []),

    # DSL statements, name : value.call(arg) (TF-003). Unambiguous in
    # shape, so they are blanked wherever they sit, also after a label
    # line with no closing punctuation.
    ("code: DSL name : value.call(arg) lines",
     "Buffer setup\n"
     "buffer  : rxFifo.depth(16)\n"
     "port    : rxFifo.attach(busA)   # receive side\n\n"
     "Both are optional.\n",
     ["Buffer setup", "Both are optional."],
     ["rxFifo", "busA", "receive side"]),
    ("code: DSL name : a.b(c).d(e) chain",
     "Bank setup\n"
     "bank : sramX.size(64KB).ports(2)\n\n"
     "That is the default.\n",
     ["Bank setup", "That is the default."], ["sramX", "64KB"]),
    # Negative rows: glossary and note lines share the "name :" shape.
    ("prose: glossary line",
     "Glossary\n"
     "Victim buffer: a small store that holds lines evicted from the cache.\n",
     ["Victim buffer: a small store that holds lines evicted from the "
      "cache."], []),
    ("prose: note line",
     "Note: see the section above.\n",
     ["Note: see the section above."], []),
]

# Rows that depend on the input type (TF-003). The 4-space indented-code
# rule is markdown syntax; in plain text indentation is layout, so indented
# lines are left to the code masker. (name, src, markdown, keep, gone,
# which masker must have done the blanking: "md", "code" or None)
MASK_TYPED = [
    ("plain: indented prose kept",
     "The cache has two modes.\n\n"
     "    In the first mode the tags are compared in parallel\n"
     "    and the hit way is selected late in the cycle.\n\n"
     "That is all.\n", False,
     ["In the first mode the tags are compared in parallel",
      "and the hit way is selected late in the cycle."], [], None),
    ("plain: indented code blanked by the code masker",
     "The update is:\n\n"
     "    cnt_q <= cnt_q + 1;\n"
     "    if (rst_i) cnt_q <= 0;\n\n"
     "Done.\n", False,
     ["The update is:", "Done."], ["cnt_q", "rst_i"], "code"),
    ("markdown: indented code blanked by the markdown rule",
     "Intro.\n\n    code_here()\n\nOutro.\n", True,
     ["Intro", "Outro"], ["code_here"], "md"),
    ("markdown: indented prose still blanked by the markdown rule",
     "Intro.\n\n    In the first mode the tags are compared.\n\nOutro.\n",
     True, ["Intro", "Outro"], ["first mode"], "md"),
]

# File type from the suffix: markdown suffixes get markdown syntax rules.
MARKDOWN_SUFFIXES = [("a.md", True), ("a.markdown", True), ("a.MD", True),
                     ("a.txt", False), ("notes", False), ("a.text", False)]

# The same rows with the code masker off: positive rows keep their code.
MASK_OFF_KEEP = [
    ("code mask off: identifier run",
     "These are the stage signals.\n\nfoo_bar_p1, baz_q2, qux_r3\n",
     ["foo_bar_p1, baz_q2, qux_r3"]),
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
    for name, src, keep in MASK_OFF_KEEP:
        try:
            m = tf.mask_markdown(src, code_mask=False)
        except TypeError as e:
            check("masking", f"{name}: code_mask=False accepted", False,
                  str(e))
            continue
        check("masking", f"{name}: length preserved", len(m) == len(src))
        for t in keep:
            check("masking", f"{name}: kept {t!r}", t in m)

    for name, src, md, keep, gone, by in MASK_TYPED:
        st = {}
        try:
            m = tf.mask_markdown(src, st, markdown=md)
        except TypeError as e:
            check("masking", f"{name}: markdown= accepted", False, str(e))
            continue
        check("masking", f"{name}: length preserved", len(m) == len(src))
        nl_ok = all(m[i] == "\n" for i, ch in enumerate(src) if ch == "\n")
        check("masking", f"{name}: newlines preserved", nl_ok)
        for t in keep:
            check("masking", f"{name}: kept {t!r}", t in m)
        for t in gone:
            check("masking", f"{name}: masked {t!r}", t not in m)
        if by == "code":
            check("masking", f"{name}: blanked by the code masker",
                  st.get("code_masked_chars", 0) > 0
                  and st.get("md_masked_chars") == 0, str(st))
        elif by == "md":
            check("masking", f"{name}: blanked by the markdown rule",
                  st.get("md_masked_chars", 0) > 0, str(st))
    # harvest.py calls mask_markdown(text) with no type: markdown is the
    # default, so its behaviour for .md files is unchanged.
    src = "Intro.\n\n    In the first mode the tags are compared.\n"
    check("masking", "mask_markdown defaults to markdown input",
          "first mode" not in tf.mask_markdown(src))
    fn = getattr(tf, "is_markdown_path", None)
    check("masking", "is_markdown_path exists", fn is not None)
    if fn is not None:
        for p, want in MARKDOWN_SUFFIXES:
            check("masking", f"is_markdown_path({p!r}) is {want}",
                  fn(Path(p)) is want)

    # Split statistics: markdown and code masking are counted separately,
    # over non-whitespace characters.
    st = {}
    src = ("Prose line here.\n\n```\nfenced_x = 1\n```\n\n"
           "foo_bar_p1, baz_q2, qux_r3\n")
    tf.mask_markdown(src, st)
    nonws = lambda s: sum(1 for ch in s if not ch.isspace())
    check("masking", "stats: md_masked_chars counts the fence",
          st.get("md_masked_chars") == nonws("```\nfenced_x = 1\n```"),
          str(st.get("md_masked_chars")))
    check("masking", "stats: code_masked_chars counts the code line",
          st.get("code_masked_chars") == nonws("foo_bar_p1, baz_q2, qux_r3"),
          str(st.get("code_masked_chars")))


# ------------------------------------------------------------------- spans

SPAN_TEXT = " ".join([t for _, _, t in CASES] +
                     [t for _, _, _, t in PATTERN_ROWS])


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

    # An edit anywhere in the flagged sentence must change its id, including
    # past character 240 of a long sentence.
    head = "The parser is fast, correct, and easy to extend"
    pad = (", which matters because the downstream stages consume its "
           "output directly and any delay in the front end shows up as "
           "stalls in every later pass of the pipeline that depends on it "
           "and in the reports that are generated at the very end")
    long_a = head + pad + " of the nightly run.\n"
    long_b = head + pad + " of the weekly run.\n"
    assert long_a.index("nightly") > 240
    fa, fb = fps(long_a), fps(long_b)
    check("waivers", "edit past char 240 changes the id",
          bool(fa) and not (fa & fb), f"shared {sorted(fa & fb)}")

    # Old-style ids (sentence cut at 240 chars) are reported on a normal
    # run without touching the file, and rekeyed by --migrate-waivers.
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "long.md"
        src.write_text(long_a, encoding="utf-8")
        f, _ = tf.analyse(str(src), nlp)
        x = next(x for x in f if len(x.context) > 240)
        old, new = tf.legacy_fingerprint(x), tf.fingerprint(x)
        check("waivers", "legacy id differs for a long sentence", old != new)
        wp = tf.waiver_path(str(src))
        tf.save_waivers(wp, str(src), {old: {
            "construction": x.construction, "pattern": x.pattern,
            "line_when_waived": x.line, "enabled": True, "text": x.text}})
        before = wp.read_text(encoding="utf-8")
        env = dict(os.environ)
        env["COLUMNS"] = "100"
        r = subprocess.run([sys.executable, str(SCRIPT), str(src), "--plain"],
                           capture_output=True, text=True, env=env, cwd=d)
        check("waivers", "normal run reports old-style ids",
              "--migrate-waivers" in r.stdout, r.stdout[-300:])
        check("waivers", "normal run leaves the waiver file alone",
              wp.read_text(encoding="utf-8") == before)
        r = subprocess.run([sys.executable, str(SCRIPT), str(src), "--plain",
                            "--migrate-waivers"],
                           capture_output=True, text=True, env=env, cwd=d)
        w, _ = tf.load_waivers(wp, str(src))
        check("waivers", "--migrate-waivers rekeys old ids",
              new in w and old not in w, f"{sorted(w)} {r.stderr[-200:]}")

    # A waiver written under a renamed pattern (TF-007: af_rather_instead
    # became af_rather_than and af_instead_of) is reported as old-style,
    # rekeyed by --migrate-waivers, and held afterwards.
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "renamed.md"
        src.write_text("We hash the key rather than compare it.\n\n"
                       "Use a table instead of a CAM.\n", encoding="utf-8")
        f, _ = tf.analyse(str(src), nlp, only={"ALTERNATIVE_FRAMING"})
        f = [x for x in f if x.pattern in ("af_rather_than",
                                           "af_instead_of")]
        check("waivers", "renamed patterns found", len(f) == 2,
              str([(x.pattern, x.text) for x in f]))
        olds = {tf.fingerprint(replace(x, pattern="af_rather_instead")): x
                for x in f}
        news = {tf.fingerprint(x) for x in f}
        check("waivers", "old pattern name gives a different id",
              not (set(olds) & news))
        check("waivers", "renamed id is listed as legacy",
              all(old in tf.legacy_fingerprints(x)
                  for old, x in olds.items()))
        wp = tf.waiver_path(str(src))
        tf.save_waivers(wp, str(src), {old: {
            "construction": x.construction, "pattern": "af_rather_instead",
            "line_when_waived": x.line, "enabled": True, "text": x.text}
            for old, x in olds.items()})
        before = wp.read_text(encoding="utf-8")
        env = dict(os.environ)
        env["COLUMNS"] = "100"
        cmd = [sys.executable, str(SCRIPT), str(src), "--plain",
               "--only", "ALTERNATIVE_FRAMING"]
        r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           cwd=d)
        check("waivers", "renamed-pattern waiver reported as old-style",
              "--migrate-waivers" in r.stdout, r.stdout[-300:])
        check("waivers", "renamed-pattern waiver file untouched",
              wp.read_text(encoding="utf-8") == before)
        r = subprocess.run(cmd + ["--migrate-waivers"], capture_output=True,
                           text=True, env=env, cwd=d)
        w, _ = tf.load_waivers(wp, str(src))
        check("waivers", "--migrate-waivers rekeys renamed pattern",
              set(w) == news, f"{sorted(w)} {r.stderr[-200:]}")
        check("waivers", "migrated entry records the new pattern",
              sorted(v.get("pattern") for v in w.values())
              == ["af_instead_of", "af_rather_than"],
              str([v.get("pattern") for v in w.values()]))
        r = subprocess.run(cmd, capture_output=True, text=True, env=env,
                           cwd=d)
        check("waivers", "migrated renamed-pattern waivers are held",
              "2 waived" in r.stdout and "old-style" not in r.stdout,
              r.stdout[-300:])

    # A per-phrase confidence override must not change a finding's id.
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "conf.md"
        src.write_text("It leverages a comprehensive table.\n",
                       encoding="utf-8")

        def ids(phrases):
            pf = Path(d) / "p.json"
            pf.write_text(json.dumps({"constructions": [
                {"id": "T", "confidence": "low", "match_lemma": True,
                 "phrases": phrases}]}), encoding="utf-8")
            ex = tf.load_phrase_file(pf)
            f, _ = tf.analyse(str(src), nlp, only={"T"}, extra=ex)
            return {(tf.fingerprint(x), x.confidence) for x in f}
        plain = ids(["comprehensive", "leverage"])
        over = ids([{"phrase": "comprehensive", "confidence": "med"},
                    {"phrase": "leverage", "forms": {"leverages": "med"}}])
        check("waivers", "confidence override keeps fingerprints",
              len(plain) == 2 and {i for i, _ in plain} == {i for i, _ in over},
              f"{sorted(plain)} {sorted(over)}")
        check("waivers", "confidence override changes the level",
              {c for _, c in plain} == {"low"} and {c for _, c in over}
              == {"med"}, f"{sorted(plain)} {sorted(over)}")

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
                      ["--only", "TRICOLON"], ["--off", "TRICOLON"],
                      ["--no-code-mask"], ["--stats", "--no-code-mask"]):
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

        # --gen-waivers: writes once, then refuses
        gw = d / "gw.md"
        gw.write_text("The parser is fast, correct, and easy to extend.\n",
                      encoding="utf-8")
        r1 = subprocess.run(
            [sys.executable, str(SCRIPT), str(gw), "--gen-waivers"],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "--gen-waivers writes a file", r1.returncode == 0,
              r1.stderr[-200:])
        wf = d / "gw.waivers.json"
        check("cli", "--gen-waivers file exists", wf.exists())
        r2 = subprocess.run(
            [sys.executable, str(SCRIPT), str(gw), "--gen-waivers"],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "--gen-waivers refuses to overwrite",
              r2.returncode != 0, r2.stdout[-200:])
        r3 = subprocess.run(
            [sys.executable, str(SCRIPT), str(gw), "--gen-waivers",
             "--no-waivers"],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "--gen-waivers rejects conflicting flags",
              r3.returncode != 0)

        # --gen-waivers state: enabled suppresses, disabled does not
        st = d / "state.md"
        st.write_text("The parser is fast, correct, and easy to extend.\n",
                      encoding="utf-8")
        import json as _json
        for state, expect_suppressed in (("enabled", True),
                                         ("disabled", False)):
            wf = d / "state.waivers.json"
            if wf.exists():
                wf.unlink()
            r = subprocess.run(
                [sys.executable, str(SCRIPT), str(st), "--gen-waivers",
                 state, "--ascii", "--plain", "--summary"],
                capture_output=True, text=True, env=env, cwd=str(d))
            check("cli", f"--gen-waivers {state} runs", r.returncode == 0,
                  r.stderr[-200:])
            if wf.exists():
                got = _json.loads(wf.read_text())["waivers"]
                want = state == "enabled"
                check("cli", f"--gen-waivers {state} sets enabled={want}",
                      all(v.get("enabled") is want for v in got.values()))
            r2 = subprocess.run(
                [sys.executable, str(SCRIPT), str(st), "--ascii", "--plain",
                 "--summary"],
                capture_output=True, text=True, env=env, cwd=str(d))
            suppressed = "0 findings" in r2.stdout
            check("cli", f"{state} waivers "
                         f"{'suppress' if expect_suppressed else 'do not suppress'}",
                  suppressed == expect_suppressed, r2.stdout[:200])

        # a waiver file with no `enabled` field still suppresses
        wf = d / "state.waivers.json"
        obj = _json.loads(wf.read_text())
        for v in obj["waivers"].values():
            v.pop("enabled", None)
            v["enabled"] = None
            del v["enabled"]
        wf.write_text(_json.dumps(obj), encoding="utf-8")
        r3 = subprocess.run(
            [sys.executable, str(SCRIPT), str(st), "--ascii", "--plain",
             "--summary"],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "missing enabled field defaults to enabled",
              "0 findings" in r3.stdout, r3.stdout[:200])

        # masked_pct counts masking anywhere in the file, not just at the
        # ends. Blanking is in place, so a length ratio over strip() only
        # moved when the masked text touched the start or end of the file.
        mp = d / "mp.md"
        prose = ("The parser reads each line and reports what it finds "
                 "in the text.\n\n")
        fence = "```\n" + "".join(f"x{i} = y{i} + z{i}\n"
                                  for i in range(12)) + "```\n\n"
        mp_src = prose * 3 + fence + prose * 3
        mp.write_text(mp_src, encoding="utf-8")
        nonws = lambda s: sum(1 for ch in s if not ch.isspace())
        want = 100 * nonws(fence) / nonws(mp_src)
        jout = d / "mp.json"
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(mp), "--no-waivers",
             "--json", str(jout)],
            capture_output=True, text=True, env=env, cwd=str(d))
        got = None
        if jout.exists():
            got = _json.loads(jout.read_text())[str(mp)]["stats"].get(
                "masked_pct")
        check("cli", "masked_pct counts a fenced block mid-file",
              got is not None and abs(got - want) < 2.0,
              f"got {got}, want ~{want:.1f}")

        # --json carries the split; --no-code-mask turns the code part off
        cm = d / "cm.md"
        cm.write_text(prose + "foo_bar_p1, baz_q2, qux_r3\n\n" + prose,
                      encoding="utf-8")
        split = {}
        for flag in ([], ["--no-code-mask"]):
            jo = d / "cm.json"
            r = subprocess.run(
                [sys.executable, str(SCRIPT), str(cm), "--no-waivers",
                 "--json", str(jo), *flag],
                capture_output=True, text=True, env=env, cwd=str(d))
            check("cli", f"code mask json runs with {flag or ['(none)']}",
                  r.returncode == 0, r.stderr[-200:])
            if jo.exists():
                split[bool(flag)] = _json.loads(jo.read_text())[str(cm)][
                    "stats"]
        if len(split) == 2:
            check("cli", "--json reports code_masked_pct",
                  split[False].get("code_masked_pct", 0) > 0,
                  str(split[False]))
            check("cli", "--no-code-mask reports code_masked_pct 0",
                  split[True].get("code_masked_pct") == 0,
                  str(split[True]))
            check("cli", "md_masked_pct reported",
                  "md_masked_pct" in split[True])

        # analyse() takes the input type from the suffix: indented prose is
        # markdown-masked in a .md file and kept in a .txt file (TF-003).
        ind = (prose + "    In the first mode the tags are compared in "
               "parallel\n    and the hit way is selected late.\n\n" + prose)
        md_pct = {}
        for suf in (".md", ".txt"):
            p = d / f"ind{suf}"
            p.write_text(ind, encoding="utf-8")
            jo = d / f"ind{suf}.json"
            r = subprocess.run(
                [sys.executable, str(SCRIPT), str(p), "--no-waivers",
                 "--json", str(jo)],
                capture_output=True, text=True, env=env, cwd=str(d))
            if jo.exists():
                md_pct[suf] = _json.loads(jo.read_text())[str(p)][
                    "stats"].get("md_masked_pct")
        check("cli", "indented prose markdown-masked in .md",
              (md_pct.get(".md") or 0) > 0, str(md_pct))
        check("cli", "indented prose kept in .txt",
              md_pct.get(".txt") == 0, str(md_pct))

        # bad phrase file fails loudly
        bad = d / "bad.json"
        bad.write_text('{"constructions":[{"id":"X","confidence":"urgent",'
                       '"phrases":["a"]}]}', encoding="utf-8")
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(src), "--phrases", str(bad)],
            capture_output=True, text=True, env=env, cwd=str(d))
        check("cli", "invalid confidence rejected", r.returncode != 0,
              r.stdout[-200:])

        # phrase entries: string or {"phrase", "confidence", "forms"}
        def load(obj):
            f = d / "pl.json"
            f.write_text(json.dumps(obj), encoding="utf-8")
            return tf.load_phrase_file(f)

        def rejects(obj):
            try:
                load(obj)
            except ValueError:
                return True
            return False
        ok = load({"constructions": [{"id": "X", "phrases": [
            "a b", {"phrase": "c", "confidence": "med"},
            {"phrase": "d", "forms": {"ds": "high"}}]}]})
        check("cli", "phrase objects load as phrase strings",
              ok and ok[0]["phrases"] == ["a b", "c", "d"], str(ok))
        check("cli", "shorthand list still loads",
              load(["a", "b"])[0]["phrases"] == ["a", "b"])
        check("cli", "shorthand mapping still loads",
              load({"J": ["a"]})[0]["id"] == "J")
        for name, bad_entry in [
                ("bad phrase confidence", {"phrase": "c",
                                           "confidence": "urgent"}),
                ("bad form confidence", {"phrase": "c",
                                         "forms": {"cs": "urgent"}}),
                ("forms not a mapping", {"phrase": "c", "forms": ["cs"]}),
                ("missing phrase", {"confidence": "med"}),
                ("empty phrase", {"phrase": " "}),
                ("unknown key", {"phrase": "c", "level": "med"}),
                ("not a string or object", 3)]:
            check("cli", f"phrase entry rejected: {name}",
                  rejects({"constructions": [{"id": "X",
                                              "phrases": [bad_entry]}]}))

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
    # A detector that throws must fail the suite, not pass as "silent".
    tf.STRICT = True
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
