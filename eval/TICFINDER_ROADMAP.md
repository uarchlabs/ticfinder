# ticfinder: false positives and novel internals

Handoff notes from a working session, 2026-11-17. Covers a read of the
code, a first measurement of false positives from the Pacino edit history,
and a plan for reducing false positives in a way that also makes the
implementation novel.

## 1. Goal

Two linked goals:

1. **Reduce false positives.** On the Pacino blogs, most findings are
   waived, not rewritten.
2. **Make the internals and the results novel.** Go beyond a better set of
   pattern rules.

The idea that connects them: every construction ticfinder reports is
ordinary English. A construction is a tic only when **nothing in its
context licenses it**: not the document, not the register, not its density.
Today ticfinder asks *"does this sentence have shape S?"*. The question that
separates true from false positives is *"is shape S earned here?"*. No
linter or detector in the field asks the second question. Answering it with
measurement, rather than with more hand-written rules, is where the novelty
comes from.

## 2. Where ticfinder sits among AI-text detectors

Background, so the positioning is clear.

| family | mechanism | examples | weakness |
|---|---|---|---|
| zero-shot statistical | perplexity and burstiness under a reference LM; perturbation curvature; two-model cross-perplexity | DetectGPT, Binoculars | measures resemblance to model output, not authorship; formulaic human prose scores as AI |
| trained classifiers | fine-tuned transformer on labelled human/AI pairs, hard-negative mining | Pangram, GPTZero, Originality.ai | distribution shift; style-imitating AI text evades (Epoch AI, Jul 2026: up to 48% evasion on one cell) |
| watermarking | generation-time bias of token choice (green lists, SynthID tournament sampling); keyed statistical test | SynthID-Text (Gemini) | needs provider cooperation; paraphrase dilutes it |
| feature-based / stylometric | interpretable features (Biber's 67, dependency labels) plus a simple classifier | DependencyAI [AHME], Rallapalli et al. [RALL] | lower accuracy; mostly research |

ticfinder overlaps the fourth family in what it looks at, but its job is
the opposite. It marks individual sentences for an editor and names each
construction, rather than producing one probability per document. It is
not a detector-defeat tool. Fixing ticfinder findings moves neural
classifier scores only indirectly, and doesn't touch watermarks.

## 3. Code review findings (current `main`)

From reading `tools/ticfinder.py`. None of these is caught by `make regress`.

1. **Waiver ids don't cover the whole sentence.** In `analyse()` the
   context is truncated with `[:240]` before `fingerprint()` hashes it. An
   edit past character 240 of a long sentence leaves the waiver live. That
   contradicts the README's promise that changing a flagged sentence drops
   the waiver. Fix: hash the full normalised sentence and truncate only for
   display.
2. **False high-confidence em-dash hits.** `em_dash_findings` uses
   `"not" in before`, a substring test over the preceding text. "another —",
   "nothing —" and "notes —" are all labelled `pivot (not X — Y)` at high
   confidence. Fix: test tokens (`t.lower_ in {"not", "n't", "never"}`).
3. **Detector crashes are silent.** `run_construction` has
   `except Exception: continue`. A pattern that throws reports nothing,
   which is the same silent failure the `registry` test section was
   written to catch. Fix: warn on stderr, or re-raise under a `--strict`
   flag used by tests.
4. **Dead code.** `PRAGMA_RE`, `suppressed()` and `gated_words()` (the
   start of per-construction pragma regions) are never called.
   `DependencyMatcher` is imported but unused. `tools/html_report.py`
   duplicates `build_html`.
5. **Doc drift.**
   - The README says the phrase file ships five groups, but it has six
     (`HOUSE_STYLE`).
   - The README's waiver example calls `./tools/tic_finder.py`.
   - The blog's structural list omits `GAPPED_ANTITHESIS`.
   - The blog calls `figure` both "the highest confidence the tool offers"
     and "medium". It is medium; high exists elsewhere.
6. **Bug #5 in `notes/bugs-2026-09-08.md`** (one id reported twice when a
   sentence matches twice) is still possible under the current scheme.

## 4. Measuring false positives: `eval/harvest.py`

The tool already produces labels as a side effect of use:

- a **waived** finding is one the editor judged acceptable, so a false
  positive (or a tolerated one)
- a finding that **disappears because its sentence was rewritten** is one
  the editor judged a real tic, so a true positive

`harvest.py` runs the current ticfinder on the first committed draft and on
the published version of every Pacino post that has a waiver file, then
labels each finding:

| label | meaning |
|---|---|
| `accepted` | in the published text and waived |
| `removed` / `rewritten` | gone from the published text; a similar sentence (difflib ratio >= 0.6) survives |
| `removed` / `deleted` | gone, and the sentence is gone too (ambiguous: sections were restructured) |
| `open` | in the published text, not waived |

Usage, from the ticfinder repo root:

```bash
python3 eval/harvest.py $PACINO --waiver-dir waivers \
  --docs blogs/BLOG_bpu_14_directed_validation.md \
         blogs/BLOG_bpu_15_specification_under_test.md \
         blogs/BLOG_bpu_16_external_anchors.md \
         blogs/BLOG_bpu_18_before_the_cluster.md \
         blogs/BLOG_bpu_20_cluster_simulation.md \
         blogs/BLOG_bpu_21_loop_predictor.md \
         blogs/BLOG_tools_1_ticfinder.md
```

It writes `eval/labels.jsonl` and prints a summary per pattern. It needs
the full `pacino` history (`git fetch --unshallow` if the clone is
shallow).

### Baseline results

Totals: **125 accepted, 47 rewritten, 312 deleted.** All existing waivers
still match the current tool.

| construction / pattern | rewritten | deleted | accepted | prec* |
|---|---|---|---|---|
| TRICOLON `tricolon` | 17 | 138 | 84 | 0.17 |
| ALTERNATIVE_FRAMING `af_rather_instead` | 11 | 84 | 19 | 0.37 |
| PARTICIPIAL_TAIL | 6 | 14 | 9 | 0.40 |
| CORRECTIVE_CONTRAST `cc_negated_apposition` | 0 | 10 | 8 | 0.00 |
| EM_DASH | 6 | 11 | 0 | 1.00 |
| ALTERNATIVE_FRAMING `af_less_than` | 2 | 7 | 5 | 0.29 |
| BORROWED_RIGOUR | 0 | 10 | 3 | 0.00 |
| EMPHATIC_REFLEXIVE | 2 | 8 | 2 | 0.50 |
| CORRECTIVE_CONTRAST `cc_coordinated` | 0 | 3 | 5 | 0.00 |
| CORRECTIVE_CONTRAST `cc_parallel_sibling` | 1 | 3 | 2 | 0.33 |
| ABSTRACT_ADVERB | 0 | 8 | 1 | 0.00 |
| LLM_DICTION | 0 | 6 | 2 | 0.00 |

prec* = rewritten / (rewritten + accepted). Deleted sentences are excluded
as ambiguous evidence.

What this shows:

- **`TRICOLON` is 67% of all accepted findings (84 of 125).** Its
  `figure`/`list-like`/`enumeration` label does not discriminate in this
  register: `list-like` accounts for 52 of the accepted and 13 of the 17
  rewritten. The enumeration score is measuring the wrong thing for
  technical prose.
- Accepted `CORRECTIVE_CONTRAST` findings reject a live alternative: "the
  test, not the RTL", "a degraded fallback prediction, not a functional
  break", "a 32-bit input port, not a static parameter". In a debugging
  narrative the alternative was a real hypothesis, which is exactly the
  licensing condition in the README.
- Accepted `PARTICIPIAL_TAIL` findings carry new information ("closing TD
  #94 and TD #95", "resulting in incompatible implementations"). The
  rewritten ones restate.
- The similarity of removed findings is bimodal. Findings at 0.8 or above
  sit in lightly edited sentences; anything at 0.4 or below sits in a
  sentence that no longer exists. The 0.6 cut is at a natural gap.

### First licensing test: a null result

Hypothesis: a finding whose content words recur elsewhere in the document
is about things the document is really discussing, so it is licensed.

Measure: the fraction of the finding's content lemmas that occur at least
two more times elsewhere in the same document version.

| construction | accepted | rewritten |
|---|---|---|
| TRICOLON | 0.68 | 0.75 |
| ALTERNATIVE_FRAMING | 0.70 | 0.94 |
| CORRECTIVE_CONTRAST | 0.68 | 0.50 (n=1) |
| PARTICIPIAL_TAIL | 0.73 | 0.69 |

It does not separate the classes, and for some constructions it points the
wrong way. Technical prose reuses its vocabulary everywhere, so a bag of
words over the whole finding carries no signal. **Licensing checks have to
be specific to the role**: the negated X, the rejected alternative, the list
members, the information in the tail.

### Limits of the history

There are plenty of negatives (125) but few clean positives (47), which is
too few to tune each pattern. Two more label sources are needed (section 6).
Also record the decision explicitly: when a waiver goes stale, note whether
the sentence was *fixed* or just *changed*, so the ledger becomes a log of
decisions as well as a suppression list.

## 5. Plan: features that cut false positives and are novel

Recommended order: 1, then 2 and 3 (measured by 1), then 4 and 5 (which
need the base rates from 3).

### 5.1 Evaluation harness (started)

`harvest.py` plus a fixed evaluation set. Every change to a detector is
reported as the change in precision per pattern against the labels. This
turns detector development from anecdote into measurement.

Extensions:

- a small **labelling UI**: the existing HTML report plus a y/n button per
  card, writing to the labels file
- the **fixed/changed decision** recorded on stale waivers

### 5.2 Licensing checks, specific to the role

A second test per detector that looks at document context. Each one is a
measurable hypothesis: precision before and after.

- **`CORRECTIVE_CONTRAST`**: is the rejected X said or entertained
  earlier? Extract the negated constituent (not the whole span) and search
  earlier sentences for it as an argument of a related predicate, using
  lemma match on the head noun plus vector similarity on the phrase. A
  debugging narrative that considered "the RTL" as a cause licenses "the
  test, not the RTL".
- **`ALTERNATIVE_FRAMING`**: is the rejected alternative (the object of
  `rather than` / `instead of`) discussed as an option elsewhere in the
  document? "rather than a CAM" in a post that compares a CAM with a hash
  table is a real choice.
- **`PARTICIPIAL_TAIL`**: does the tail add information? Compare the
  tail's entities and content words with the main clause and the previous
  sentence. Restating means a tic; new entities (ticket numbers,
  identifiers, consequences) mean the tail is carrying content. The BP-045
  rewrite in the blog was the second kind, which is why promoting it to a
  main clause helped.
- **`EMPHATIC_REFLEXIVE`**: is there a contrast set? "the document itself"
  is earned when another referent of the same type is nearby (a summary of
  the document, a copy of it).
- **`TRICOLON`**: are the members referents, rather than qualities? Score
  each member as a catalog item if it is an identifier shape (underscores,
  digit suffix, mixed case, code in the source), a proper noun, or a
  defined term that recurs *as the same noun phrase*. Abstract nouns and
  adjectives that appear once ("simpler, faster, and easier to debug") are
  the figure. This replaces the noun-phrase-only enumeration signals and
  fixes the bare-identifier `figure` bug from the other direction.

### 5.3 Calibration against reference corpora (empirical confidence)

Replace hand-set high/med/low with a measured likelihood ratio per pattern:

```
LR(pattern) = rate in LLM text of register R / rate in human text of register R
```

- A pattern with LR near 1 is ordinary English in that register: mute it
  or report it at low confidence.
- Confidence tiers become LR bands, and each register gets its own table.
  That is the **register setting** from the blog's future-work list, with
  data behind it.

Corpora (section 6): the author's pre-LLM specifications, pre-2022 arXiv,
and the LLM-written specs and drafts in `pacino`.

### 5.4 Density with a null model

The tool's stated premise is clustering, but it reports single instances.
Given a base rate from 5.3, run a **scan statistic** over a sliding window
(paragraph or section): flag a construction only when its local count is
improbable under Poisson at the human base rate.

- "Three tricolons in one paragraph" is a finding; one in 3,000 words is
  not.
- The biggest gain is on the rate-signal constructions (`TRICOLON` and the
  phrase lists), which are exactly the noisiest classes.
- It gives a per-paragraph "tic load" heat map for the HTML report.

### 5.5 Discovery: induce constructions from corpora

The most novel piece. Parse matched human and LLM corpora and mine
**dependency-subtree patterns** that are significantly overrepresented in
the LLM side: frequent-subgraph mining over dependency labels and POS
tags, with lemmas optionally abstracted, ranked by log-likelihood ratio and
a minimum support. The output is a ranked list of candidate constructions
for a human to name and turn into detectors.

The Vale packages hand-enumerate surface forms; this *induces*
constructions, with interpretable results and a person reviewing them.

### 5.6 Smaller false-positive fixes

- **Parse agreement.** Run `en_core_web_md` and `en_core_web_trf`.
  Downgrade findings that only one parse produces. Many false positives are
  parse errors, and disagreement between the two parses is a cheap measure
  of parse uncertainty.
- **A code-aware masker.** Detect code-like lines and runs (high symbol
  density, `;{}()=`, identifier shapes like `foo_bar_p1`, port or register
  listings) and blank them the way fenced code is blanked. Report the
  masked percentage per file. This is required before the spec corpus is
  usable (section 6) and helps the blogs too.
- Section 3 bugs 1 to 3.

## 6. Corpora

| corpus | role | notes |
|---|---|---|
| author's pre-LLM specs (~40 files, some under 20 lines, some heavy with code syntax) | human baseline in the target register, in the author's own voice | pool counts across all files, so short files are fine; **needs the code-aware masker first**, otherwise unmasked code inflates human base rates and makes tics look ordinary; keep private, report aggregates only |
| LLM-written specs and planning docs in `pacino` | matched LLM side for the spec register | compare against the author's specs, not against the blogs, or the comparison measures genre |
| Pacino blog drafts vs published | LLM side and editor labels for the narrative register | `harvest.py` |
| arXiv `cs.AR` (also `cs.PF`, `cs.DC`) | volume; a third (academic) baseline | API reachable; abstracts are clean text but a compressed sub-register; full text is LaTeX or PDF and needs math and `\cite` masking; abstracts and metadata are fine for local counts, full texts have mixed licenses, so count only and don't redistribute |

### The arXiv opportunity: excess constructions over time

Kobak et al. measured *excess words* in post-LLM abstracts; Rallapalli et
al. measured Biber features. As far as we know, nobody has measured
**excess dependency-level constructions**.

Design:

1. `cs.AR` abstracts from 2018 to 2021 (safe cutoff: ChatGPT launched in
   November 2022) against 2025 to 2026.
2. Run ticfinder over both.
3. Measure the change in rate for each construction and pattern, with
   confidence intervals.

Constructions whose rates rose after LLMs are measured tics. Flat ones are
ordinary English in that register, which is where the false positives come
from. The same run feeds 5.3 (empirical confidence) and 5.5 (where to mine
for candidates). It is also a natural follow-up blog post.

## 7. Next steps

1. Drop `harvest.py` into `ticfinder/eval/`, run it, and confirm the
   baseline numbers.
2. Fix section 3 bugs 1 to 3. Add a `tests.py` case for each.
3. Build the code-aware masker; check the masked percentage on the specs
   and the blogs.
4. Pull `cs.AR` abstracts for both windows and run the comparison of rates
   over time.
5. Run the specs against the `pacino` LLM specs to get per-pattern LRs for
   the spec register.
6. Implement role-specific licensing for `TRICOLON` first (the largest
   false-positive source), measured with the harness; then
   `CORRECTIVE_CONTRAST`, `ALTERNATIVE_FRAMING` and `PARTICIPIAL_TAIL`.
7. Scan-statistic density, then subtree mining.
