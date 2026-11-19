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

Totals: **142 accepted, 47 rewritten, 312 deleted.** All existing waivers
still match the current tool. (The first draft of this section said 125
accepted; the rows below and `eval/labels.jsonl` both sum to 142. Corrected
in TF-001.)

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

- **`TRICOLON` is 59% of all accepted findings (84 of 142).** Its
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

**What the human rate is for.** ticfinder exists to make LLM prose easier
to edit: to find constructions that intrude and break the flow of
information for a reader. Two measurements decide whether a construction
deserves a confident finding, and each comes from a different source:

- **Is it LLM-typical?** The LR above. The human side needs competent
  technical writing in the same register, and it can come from any skilled
  writer. Matching the author's personal style is not required.
- **Does it intrude?** The editor's labels (section 4). These carry the
  author's judgement as a reader.

A construction should get high confidence when both hold. Density (5.4)
adds the third part: one "rather than" reads fine, and four in a paragraph
break the reading.

**Register still matters.** Academic papers, design descriptions,
progress reports and specifications each have their own normal rates for
coordination, hedging, "rather than" and set phrases. A baseline in the
wrong register can make constructions that are ordinary in the target
register look like tics. It can also hide real ones. A large corpus in the
wrong register gives a precise estimate of the wrong quantity. The registers that matter
now are design and progress descriptions, and next, technical
specifications.

**Corpora and their jobs** (details in section 6):

- **Public pre-2022 design and specification documents** by many authors
  (Python PEPs, IETF RFCs, Rust RFCs, the RISC-V ISA manuals, open hardware
  design docs). This is the primary human baseline for the design and spec
  registers. It is in register, large (millions of words), dated by
  version control, and mostly under simple licenses.
- **The author's pre-LLM specs.** About 82k words after masking (section
  9), too few on their own: a construction at 0.5 per 1,000 words gives
  about 40 instances, which cannot tell an LR of 1.5 from 3. They serve as
  a trusted check on the public baseline in the exact domain. Most of the
  author's earlier writing is company IP and unavailable. Email and other
  ad hoc text are a different register and are not worth mining for this.
- **arXiv before and after LLMs**: `cs.AR` 2018 to 2021 against 2025 to
  2026. Both sides are arXiv in one subfield. Genre cancels, so the
  change in rate is mostly LLM influence. This is the best evidence of
  which constructions LLMs increased, and it depends on no single author.
- **The pacino LLM specs, design notes and blog drafts**: the LLM side for
  each register.

**Combining them.** Estimate each LR from the public baseline and check
it against the author's specs. The arXiv change over time serves as a
prior (empirical Bayes): rare constructions borrow strength from it, and
common ones are set by in-register data. Where the sources disagree, the
gap measures the register effect.

Use 2021 as the cutoff for all pre-LLM corpora (ChatGPT launched in
November 2022). An earlier cutoff gives up data for little gain.

**Handling third-party text.** ticfinder processes these files the same
way as the author's own. The rule is also the same: cache the documents
outside the repo or under a git-ignored directory such as `private/`,
keep `--json` output from those runs there too (it holds full sentences),
and commit only aggregate tables. A normal analysis run writes nothing
else that holds source text: waivers are not needed, and `harvest.py`
does not apply without an edit history.

The questions behind this rationale are recorded in the Q&A section of
`tf_002_summary.md`.

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
| public pre-2022 design and spec documents (Python PEPs, IETF RFCs, Rust RFCs, RISC-V ISA manuals, open hardware design docs) | primary human baseline for the design and spec registers | many authors, millions of words, dated by version control; mostly public domain, MIT, Apache or CC BY; RFCs and hardware docs carry ASCII diagrams and register layouts, so check per-file masked percentages first; cache under a git-ignored directory, commit aggregates only |
| author's pre-LLM specs (36 text files in `$WRITING_SAMPLES`, some under 20 lines, some heavy with code syntax) | in-domain check on the public baseline | about 82k words after masking, too few for rare constructions on their own; pool counts across files; masking still under-masks about 10 files and the indented-code rule over-masks 6 (section 9); keep private, report aggregates only |
| LLM-written specs and planning docs in `pacino` | matched LLM side for the design and spec registers | compare against the public design docs and the author's specs, not against the blogs, or the comparison measures genre |
| Pacino blog drafts vs published | LLM side and editor labels for the narrative register | `harvest.py` |
| arXiv `cs.AR` (also `cs.PF`, `cs.DC`) | change in rates before and after LLMs (genre cancels); prior for 5.3 | API reachable; abstracts are clean text but a compressed sub-register; full text is LaTeX or PDF and needs math and `\cite` masking; abstracts and metadata are fine for local counts, full texts have mixed licenses, so count only and don't redistribute; not a direct baseline for the spec register |

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

Renumbered after TF-002. Its results (section 9) moved licensing ahead of
the base-rate work: the blog `TRICOLON` false positives are prose lists,
which masking cannot reach. They also added masking fixes and a public
corpus ahead of the LR steps (5.3).

Tidied after TF-004. Step numbers are kept stable because task files
cite them, so they do not give the order of work. The order is listed
after the steps.

Done: steps 1 to 6, 9 and 10. Planned: steps 7, 8 and 11 to 14. The
list stays in step order, so the numbers render as written.

1. Drop `harvest.py` into `ticfinder/eval/`, run it, and confirm the
   baseline numbers (TF-001, section 8).
2. Fix section 3 bugs 1 to 3, with a `tests.py` case for each (TF-001).
3. Build the code-aware masker and check the masked percentage on the
   specs and the blogs (TF-002, section 9).
4. **Masking fixes for plain-text corpora** (TF-003, phase 1). Done: the
   indented-code rule applies to markdown files only, code lines with
   trailing `#` or `//` comments are scored on the code part as well, and
   `name : value.call(arg)` DSL lines are blanked. Harvest is unchanged.
   Results in section 10.
5. **Role-specific licensing for `TRICOLON`** (TF-003, phase 2; 5.2).
   Null result: the referent score does not separate accepted from
   rewritten findings, and no code was added (section 10). The
   clause-versus-noun split it exposed needs fresh labels. Next come
   `CORRECTIVE_CONTRAST`, `ALTERNATIVE_FRAMING` and `PARTICIPIAL_TAIL`.
6. **arXiv before and after LLMs** (TF-004). Done: 955 and 2,627
   primary `cs.AR` abstracts. `PARTICIPIAL_TAIL` rose 3.1 times,
   `rather than` 3.8 times and `TRICOLON` 1.4 times. `CORRECTIVE_CONTRAST`,
   `BORROWED_RIGOUR` and `more/less ... than` were flat. `EM_DASH` could
   not be measured. Results in section 11. `harvest.py` gained
   `--by-subtype` and `--summary-only`.
7. **Collect the public design and spec baseline** (5.3, section 6):
   pre-2022 PEPs, IETF and Rust RFCs, RISC-V manuals and open hardware
   design docs. Check per-file masked percentages before trusting counts.
8. **Per-pattern LRs** for the design and spec registers: the public
   baseline and the author's specs against the `pacino` LLM specs, with
   the arXiv change as a prior.
   Before it starts, have harvest and the arXiv scripts write JSON
   summaries that step 8 can read directly.
9. **arXiv paper bodies, a pilot** (TF-005). Done: 200 papers per
   window from the TF-004 set, measured from v1 LaTeX source with a new
   masker in `eval/arxiv_bodies.py`. For 5 of the 7 constructions with
   enough findings, the body ratio lies inside the abstract interval.
   `ABSTRACT_ADVERB` rose more in bodies and `TRICOLON` less. The
   introduction ratios match the abstract ratios. Body ratios are not
   smaller, so the LLM change is not confined to abstracts and
   introductions. `EM_DASH` rose 5.3 times in bodies, and
   `HOLLOW_BOOSTER` rose 3.3 times. Results in section 12. A full run
   is recommended after steps 10 and 11.
10. **`DISGUISE_METAPHOR` and `HOLLOW_BOOSTER` fixes** (TF-006). Done.
    `pose` and `pass` now need an `as` frame that is intransitive,
    reflexive or has `off`. Of 69 arXiv findings the old code
    reproduces, the new code keeps 4, and none of the 4 is real.
    `significantly,` fires only at the start of a sentence, or as
    `More`/`Even more significantly,` there. That drops 31 manner
    adverbs and no real booster. The adjusted `HOLLOW_BOOSTER` body
    ratio is 4.07, against 3.31 in TF-005. Results in section 13.
11. **Pattern splits from TF-004** (TF-007). Done. `rather than` and
    `instead of` are now separate patterns, `af_rather_than` at `med`
    and `af_instead_of` at `low`, and `--migrate-waivers` rekeys
    waivers written under the old name. A lemma list for the
    `PARTICIPIAL_TAIL` verbs that rose is a null result, because 22 of
    the 26 frequent verbs rose in both corpora. A reading found `,
    using ...` tails almost all instrumental, so lemma `use` runs at
    `med`. Phrase entries may now carry a confidence per phrase or per
    matched form. Six forms that rose in both corpora run at `med`.
    Levels come from an interim rule over the arXiv ratios until step 8.
    Harvest labels did not change. Results in section 14.
12. **Licensing, continued from step 5.** Fresh labels for the
    `TRICOLON` clause and noun split, then the licensing tests for
    `CORRECTIVE_CONTRAST`, `ALTERNATIVE_FRAMING` and `PARTICIPIAL_TAIL`.
13. Scan-statistic density (5.4), then subtree mining (5.5). This was
    step 9 before TF-004.
14. **Full arXiv body run** (recommended in section 12). All usable
    pre papers (about 775) and a matched post sample, so that one
    analysis measures the fixed and split patterns. Goes after steps
    10 and 11. The source cache is reusable.

Order: 9 and 10 are done. 11 and 7 do not depend on each other and can
run side by side. 14 goes after 11, so that one analysis measures the
fixed and split patterns. 8 needs 7 and uses 14's body ratios as its
prior (9's if 14 has not run). 12 needs new labels from blog editing, so
it goes when they exist. 13 comes last.

## 8. TF-001 results (2026-11-17)

**Step 1.** `harvest.py` reproduces the baseline. Every per-pattern row
matches section 4, and the regenerated `labels.jsonl` is identical to the
committed one. The accepted total in section 4 was a miscount; it is
142, corrected above.

**Step 2.** Bugs 1 to 3 fixed, each with a `tests.py` case that failed
before the fix.

1. Waiver ids hash the full sentence. Ids change for any finding whose
   sentence is over 240 characters: 17 of 142 waivers in `$PACINO/waivers`
   and 7 in `waivers/BLOG_bpu_14_directed_validation.waivers.json`. A normal
   run lists them as stale and names `--migrate-waivers`, which rekeys them.
   Migration cannot tell whether the sentence was edited past character 240
   since it was waived, so check the sentences it prints.
2. The em-dash pivot check tests tokens (`not`, `n't`) within the
   sentence. Across the pacino blogs, `notes/` and README (35 files) the
   substring false positives never occurred, so no finding changed subtype.
   Adding `never` produced one new high-confidence hit, "never again --
   fixed by ...", which is not a pivot, so `never` was left out.
3. A pattern that throws warns on stderr. `--strict` re-raises, and
   `tests.py` runs strict. No detector throws on any of the 35 files.

Harvest after, with migrated waivers. Accepted counts are unchanged. Eight
findings moved from `deleted` to `rewritten`, all with sentences cut at 240
characters before: harvest's similarity match now sees the whole sentence.

| pattern | rewritten | deleted | prec* before | prec* after |
|---|---|---|---|---|
| TRICOLON `tricolon` | 17 -> 19 | 138 -> 136 | 0.17 | 0.18 |
| ALTERNATIVE_FRAMING `af_rather_instead` | 11 -> 15 | 84 -> 80 | 0.37 | 0.44 |
| EM_DASH | 6 -> 8 | 11 -> 9 | 1.00 | 1.00 |

These are label corrections; the detectors did not change. Before the pacino waivers
were migrated, harvest showed those 17 waivers as `open`. All 24 were
migrated after TF-001 (entry contents unchanged, keys only), and
`labels.jsonl` was regenerated from the migrated waivers; the table above
is what it reports.


## 9. TF-002 results (2026-11-17)

**Baseline.** `make regress` passed and harvest matched the TF-001 numbers
row for row (142 accepted; `TRICOLON` 19 rewritten, 136 deleted, 84
accepted, prec* 0.18).

**`masked_pct` fix.** It is now computed over non-whitespace characters,
with `ticfinder_off` and `ticfinder_skip` regions left out of both sides.
A `cli` test with a fenced block mid-file reported 0.0 against an
expected 25.4 before the fix. It now passes. `--stats` and `--json` report
`md_masked_pct` and `code_masked_pct` alongside the total, and
`--no-code-mask` turns the new masker off. The figures quoted in the
TF-002 background (README 30%, BLOG_bpu_14 22%, BLOG_bpu_16 29%) counted
pragma regions as masked. Without them the figures are 24.5%, 20.6% and
20.8%. Only one file in the public corpus crosses the 40% warning:
`BLOG_fe_rtl_complete.md` at 46.4%. Nothing in `notes/`, README or
`samples/` does.

**The masker.** `mask_code_lines()` runs after the markdown patterns. It
scores each line on symbol density over `;{}()=[]<>` (balanced pairs
only, so link text and wrapped parentheses do not count), the share of
identifier-shaped tokens, a plain-word share used as a guard, and port,
declaration and register keywords. A code-like line is blanked when it
cannot be the middle of a sentence: it starts a block, follows a line that
ends with `.:;!?`, or follows another blanked line. A line that is very
dense in symbols and ends with `;`, `)`, `{`, `}` or `,` is blanked
anywhere. Lines containing inline code are left alone. Thresholds are
module constants with a comment on how each was set.

**Blogs: a null result.** Harvest after the change is identical to
harvest before, down to `labels.jsonl` byte for byte. The masker removed
no finding from the 7 blogs in either their draft or published form, so
prec* is unchanged for every pattern. The hypothesis fails on its second
condition: it removes nothing from the blogs. Across all 32 pacino blogs,
their drafts, `notes/`, README and `samples/` it blanks 3 lines, all real
expressions in `BLOG_bpu_2`, which is not a harvest blog. The harvest
blogs put their code in fences or backticks. Their identifier runs sit
inside backticks, and the masker leaves inline code alone by design.
The `TRICOLON` false positives in the blogs are prose lists, so they need
the licensing work in 5.2.

| file | markdown % | code % |
|---|---|---|
| BLOG_bpu_14_directed_validation | 20.6 | 0.0 |
| BLOG_bpu_15_specification_under_test | 16.3 | 0.0 |
| BLOG_bpu_16_external_anchors | 20.8 | 0.0 |
| BLOG_bpu_18_before_the_cluster | 21.4 | 0.0 |
| BLOG_bpu_20_cluster_simulation | 18.1 | 0.0 |
| BLOG_bpu_21_loop_predictor | 26.9 | 0.0 |
| BLOG_tools_1_ticfinder | 13.1 | 0.0 |
| notes/bugs-2026-09-08 | 23.4 | 0.0 |
| notes/competitive-review | 19.8 | 0.0 |
| README | 24.5 | 0.0 |

**Waivers.** The masked text of every waivered document is unchanged, so
no waiver in `$PACINO/waivers` or `waivers/` goes stale. The 3 stale
entries in `waivers/BLOG_bpu_13_contradiction_detection.waivers.json`
show with and without `--no-code-mask`, so they predate this change.

**Specs corpus.** Aggregates only. 36 text files and 18,315 lines, 2 of
them under 20 lines; one `.docx` was skipped. The specs share a directory
with the other writing samples, so all 36 were pooled.

| measure | value |
|---|---|
| words, raw | 97,901 |
| words after markdown masking | 87,301 |
| words after code masking | 81,921 (6.2% fewer than markdown alone) |
| code-masked % per file | min 0.0, median 0.3, max 33.5, none over 40, 12 at zero |
| markdown-masked % per file | min 0.0, median 3.2, max 55.2, 3 over 40 |

The first version of the masker missed two kinds of line. A netlist
instance line is a cell name plus one long port-map token, so the guard
read the cell name as half prose. A code line after an unpunctuated label
looked like the middle of a sentence. The dense-symbol
rule was added with test rows for both. It took the code-masked maximum
from 24.0% to 33.5% and cut the dense-symbol lines left in from 186 to 23.
The blogs did not change.

Spot-check, by random sample and per file:

- Over-masking by the code masker is small. 39 of 40 sampled blanked lines
  were code. In about 7 files a few short non-code lines go: bracketed
  redaction placeholders on their own line, and short labels in
  parentheses. Each such file loses only a few lines.
- Under-masking affects about 10 of 36 files. Of 40 sampled kept lines
  with code signals, about 11 were code. The kinds: DSL lines of the form
  `name : value.call(arg)` whose keywords read as words, code lines that
  end in a prose comment (`#`, `//` or a tab-separated description), XML
  attribute lines, bit-encoding table rows, and comment rule lines.
- The larger problem is in markdown masking. The 4-space indented-code
  rule blanks about 530 lines of indented prose in 6 plain-text files, and
  it accounts for all 3 files over 40%. In plain text, indentation is
  layout. This over-masking removes human prose from the base rates, which
  is the opposite error to the one this task set out to fix.

**Before 5.3 uses the specs:** (1) do not apply the indented-code rule to
`.txt` files, or let the code masker decide indented lines; (2) score a
line with a trailing `#` or `//` comment on the code part only; (3) add
the `name : value` DSL form. Each needs test rows from the failure kinds
above, written without quoting the specs.


## 10. TF-003 results (2026-11-18)

### Phase 1: masking fixes

**Baseline.** `make regress` passed. Harvest matched section 9 on every
row. `labels.jsonl` was byte-identical to the committed file. The
specs aggregates matched TF-002 exactly (97,901 / 87,301 / 81,921 words;
words counted as runs of ASCII letters).

**Changes.** Each one has test rows that failed before it.

1. `mask_markdown(..., markdown=True)`. With `markdown=False` the 4-space
   indented-code rule is skipped and indented lines go to the code masker.
   `analyse()` sets it from the file suffix with `is_markdown_path()`:
   `.md`, `.markdown`, `.mdown`, `.mkd` and `.mkdn` are markdown, and any
   other suffix, or none, is plain text. The default is markdown, so
   `harvest.py`, which calls `mask_markdown(text)` directly and writes its
   temporary files as `.md`, behaves as before.
2. Trailing comments. A line is scored twice, on the whole line and on
   the part before a trailing `//` or `#`, and it is code when either
   reads as code. The whole line is blanked, comment included. The marker
   must follow whitespace; `#` must also be followed by whitespace, which
   keeps "TD #104" and URLs out. Scoring only the code part lost 5 lines
   that had scored as code with their comment, hence both.
3. DSL statements. `name : obj.call(arg)` and `name : a.b(c).d(e)`, with
   one or two name words and one or more call chains, are blanked
   wherever they sit, like the dense-symbol lines. Glossary lines
   ("Term: a description") and "Note: ..." lines have no call chain and
   are kept.

**Harvest.** Identical before and after: summary and `labels.jsonl` byte
for byte. The blogs are markdown, so the indented-code rule still applies
to them, and they have no DSL lines or code lines with trailing comments
outside fences.

**Public files.** The masked text of all 32 pacino blogs, `notes/`,
README, `samples/` and every waivered document is unchanged. Per-file
shares for the harvest blogs, `notes/` and README are the section 9
figures. No waiver goes stale in `$PACINO/waivers` or `waivers/`; the 3
stale entries in `waivers/BLOG_bpu_13_contradiction_detection.waivers.json`
predate TF-002.

**Specs corpus.** Aggregates only, 36 text files.

| measure | TF-002 | TF-003 phase 1 |
|---|---|---|
| words, raw | 97,901 | 97,901 |
| words after markdown masking | 87,301 | 96,053 |
| words after code masking | 81,921 | 89,371 |
| words removed by the code masker | 5,380 | 6,682 |
| markdown-masked % per file (min / median / max, over 40) | 0.0 / 3.2 / 55.2, 3 | 0.0 / 0.7 / 49.2, 1 |
| code-masked % per file (min / median / max, over 40) | 0.0 / 0.3 / 33.5, 0 | 0.0 / 0.6 / 34.6, 0 |
| total masked % per file (min / median / max, over 40) | 0.0 / 9.2 / 55.2, 3 | 0.0 / 2.2 / 49.2, 1 |

The one file over 40% is a `.md` file with 14 fenced blocks, so its
masking is correct. By line: 1,592 lines were blanked by the
indented-code rule before. Of these, 1,069 are now kept, 126 are blanked
by the code masker, and 397 are still markdown-masked (the two `.md`
files). The code masker blanks 79 lines it kept before, and keeps 4 it
blanked before. Those 4 were judged by their neighbours, and the
neighbours changed when indented prose came back.

Spot-check, random samples of 40, nothing quoted:

- Lines restored from the indented-code rule: 30 prose or headings, 7
  code, 3 table or layout cells. About a fifth of the restored lines are
  code the masker does not catch: shell commands, single assignments,
  mnemonic listings and comment lines. The code-masked share still rose:
  the code masker now blanks 126 of the formerly indented lines and 79
  lines it kept before.
- Lines newly blanked by the code masker: 40 of 40 code, from two
  samples. No new over-masking was found.
- Kept lines with code signals: 17 of 40 code. TF-002 found 11 of 40, but
  its pool held no indented lines. About half of the remaining misses are
  whole-line comment and rule lines (`//...`, `# ----`). The rest are
  assembly lines, bit-encoding rows, pseudocode and fragments.

**Verdict.** The phase 1 hypothesis holds on each of its three failure
conditions: (1) harvest is unchanged; (2) the code-masked share rose;
(3) the spot-checks found no new over-masking. One qualification: about
190 code lines came back with the indented prose, an estimate from 7 of
40 sampled.

**Deferred.** Whole-line comment and rule lines are the largest
remaining kind of missed code. Next come assembly lines and bit-encoding
rows. All need test rows written without quoting the specs.

### Phase 2: TRICOLON referent score, a null result

**Baseline.** Harvest after the phase 1 commit is identical to the
phase 1 harvest, and `labels.jsonl` is unchanged.

**Offline test.** All 239 `tricolon` rows in `labels.jsonl` were matched
back to their series and scored. A member is a referent when it holds
inline code or an identifier shape, a proper noun, a number, or a noun
phrase that recurs word for word in the document. The score is the share
of referent members. Full method and tables are in
`notes/tricolon-referent-null-2026-11-18.md`.

| score | AUC, accepted over rewritten |
|---|---|
| current label | 0.53 |
| referent score, as specified | 0.49 |
| referent score, core phrase only, clause members not referents | 0.61 (95% interval 0.47 to 0.72) |
| the series has no clause members | 0.63 |

As specified, the score carries no signal. Mean scores are 0.55 for
accepted and 0.56 for rewritten. Clause members with identifiers in them
score as referents, and the rewritten blog sentences are full of
identifiers. The stricter reading's gain comes from noun lists against
clause lists. Within noun lists it does not separate (means 0.64 and
0.62).

**Decision.** Null result. No detector code changed, so no waiver moves. Steps 9 to 12 of TF-003 did not run, so
`harvest.py` has no `--by-subtype`.

**Lead.** Clause series hold 15 of 19 rewritten and 44 of 84 accepted
(prec* 0.25). Noun series hold 4 and 40 (prec* 0.09). This was found
after looking at the data. It needs fresh labels before it becomes a
detector change.

## 11. TF-004 results (2026-11-18)

### arXiv cs.AR abstracts before and after LLMs

**Data.** The arXiv API, primary category `cs.AR` only, by
first-version date. Pre window: 2018-01-01 to 2021-12-31, 955 papers.
Post window: 2025-01-01 to 2026-11-17 (the latest available), 2,627
papers. Neither window exceeds 3,000, so nothing was sampled. 797 and
1,307 cross-listed papers were counted and excluded. Abstracts and
metadata are cached under `private/arxiv/`; the committed table is
`eval/arxiv-rates-2026-11-18.md`, which holds aggregates only.

**Papers per year.** The windows differ in size because `cs.AR` grew.
Per year, post has about 5.7 times as many primary papers as pre
(about 1,370 a year against 240). Rates are per 1,000 words and mean
length barely changed, so the imbalance does not bias the rates. It
makes the pre side the main source of interval width. A shift in topic
mix (ML and LLM hardware) came with the growth; see the caveats below.

**Completeness check.** The set `cs:cs:AR` was harvested through
OAI-PMH (`oaipmh.arxiv.org/oai`, `from=2018-01-01`, 7 pages) as an
independent count. OAI's `<created>` field is not the v1 date (some
2018 papers show 2022), so the comparison dates papers by the YYMM
prefix of the arXiv id. Columns 3 to 5 use that dating. Column 2 is the
API's v1 date, which the windows use.

| year | API primary, v1 date | OAI primary, id year | API primary, id year | OAI only | API cross-listed, excluded |
|---|---|---|---|---|---|
| 2018 | 122 | 122 | 122 | 0 | 128 |
| 2019 | 136 | 136 | 136 | 0 | 109 |
| 2020 | 310 | 308 | 308 | 0 | 221 |
| 2021 | 387 | 388 | 388 | 0 | 339 |
| 2025 | 1,116 | 1,105 | 1,103 | 2 | 598 |
| 2026 (to Nov 17) | 1,511 | 1,524 | 1,524 | 0 | 709 |

The API missed no paper in either window. The 2 OAI-only papers have
v1 dates of 2024-12-20 and 2024-12-31 and January 2025 ids, so they are
outside the post window. Every API paper is primary `cs.AR` in OAI as
well. The two datings differ near month ends, where a late submission
gets the next month's id. `eval/arxiv_rates.py check` reruns the
check from the harvested pages in `private/arxiv/oai/` (`--refresh`
harvests again). It exits 1 if the fetch missed a paper.

**Method.** `eval/arxiv_rates.py fetch` and `analyse`. LaTeX math and
reference commands are blanked in place, and `\emph{}`-style commands
keep their argument. ticfinder runs with its defaults (`en_core_web_md`,
code masker, phrase lists) at commit 69e1743 with no uncommitted
changes. Each abstract is written as a `.txt` file, since abstracts are
not markdown. Rates are pooled findings per 1,000 words. Intervals come
from a bootstrap over papers: 2,000 draws, seed 4004.

**Sanity measures.**

| measure | pre | post |
|---|---|---|
| words analysed | 179,136 | 500,093 |
| mean abstract length, words | 187.6 (183.9 to 191.2) | 190.4 (188.5 to 192.2) |
| LaTeX-masked share of non-space characters | 0.21% | 0.46% |
| Unicode em and en dashes | 0 | 0 |

Length barely moved, so it does not explain the changes in rate.
The arXiv API serves abstracts in ASCII. `EM_DASH` finds nothing in
either window, so the hypothesis cannot be tested for it here. A proxy
(TeX `---` and spaced ` -- `) went from 0.24 to 0.32 per 1,000 words,
ratio 1.32 (0.85 to 2.25): flat, with few instances.

**Results per construction** (ratio of post rate over pre rate, 95%
interval; rows with fewer than 20 findings left out):

| construction | pre rate | post rate | ratio | verdict |
|---|---|---|---|---|
| `PARTICIPIAL_TAIL` | 1.81 | 5.67 | 3.14 (2.79 to 3.57) | rose |
| `DISGUISE_METAPHOR` | 0.02 | 0.05 | 2.87 (1.10 to inf) | rose, false positives |
| `TRICOLON` | 4.24 | 6.11 | 1.44 (1.32 to 1.56) | rose |
| `CONSULTANT_REGISTER` | 1.65 | 2.35 | 1.43 (1.23 to 1.67) | rose |
| `LLM_DICTION` | 2.99 | 3.81 | 1.27 (1.14 to 1.44) | rose |
| `ABSTRACT_ADVERB` | 0.69 | 0.88 | 1.27 (1.02 to 1.59) | rose |
| `ALTERNATIVE_FRAMING` | 0.76 | 0.94 | 1.23 (1.02 to 1.51) | rose |
| `HOLLOW_BOOSTER` | 0.06 | 0.08 | 1.43 (0.79 to 3.56) | flat |
| `EMPHATIC_REFLEXIVE` | 0.07 | 0.09 | 1.30 (0.74 to 2.63) | flat |
| `CORRECTIVE_CONTRAST` | 0.21 | 0.22 | 1.04 (0.71 to 1.57) | flat |
| `BORROWED_RIGOUR` | 0.31 | 0.31 | 1.02 (0.74 to 1.45) | flat |
| `VAGUE_QUANTIFIER` | 0.87 | 0.73 | 0.85 (0.70 to 1.03) | flat |
| `FRAME_MARKER` | 0.09 | 0.02 | 0.27 (0.12 to 0.56) | fell, mixed |

**Within constructions** the split is often sharper than between them:

- `ALTERNATIVE_FRAMING`: `rather than` rose 3.84 (2.29 to 8.06).
  `instead of` (1.07), `less ... than` (1.20) and `more ... than` (0.79)
  were flat. The harvest labels agree: by subtype, `rather than` has prec*
  0.54 on the blogs and `instead of` 0.12.
- `TRICOLON`: `list-like` rose 1.56 and `enumeration` 1.49; `figure` was
  flat at 1.00. The blog prec* order is the same (0.22, 0.12, 0.10).
- `PARTICIPIAL_TAIL`: the rise is in particular verbs. `Enabling` rose
  6.6 times, `achieving` 4.5, `demonstrating` 8.1, `highlighting` and
  `leaving` from zero to 45 and 48. `Using`, `resulting` and `allowing`
  were flat.
- Phrase lists: `leverages` rose 3.5, `landscape` 4.7, `essential` 1.9,
  `comprehensive` 1.6 and `increasingly` 2.0. `Dynamic`, `paradigm`,
  `robust`, `crucial` and `optimize` were flat. `A wide range of` (0.37)
  and `a variety of` (0.16) fell.

With about 20 pattern rows tested at 95%, one or two verdicts near an
interval edge are expected by chance.

**Sanity reading.** 20 random findings per window (all of them when
fewer) for the three constructions with the largest change in either
direction, among rows with at least 20 findings. Counts only.

| construction | pre: real / read | post: real / read |
|---|---|---|
| `PARTICIPIAL_TAIL` | 17 / 20 | 20 / 20 |
| `DISGUISE_METAPHOR` | 0 / 3 | 0 / 20 |
| `FRAME_MARKER` | 8 / 16 | 6 / 12 |

- `PARTICIPIAL_TAIL` is accurate here. The 3 misses were parse errors:
  a gerund subject, a participle inside a from/to phrase, and one inside
  a parenthetical example.
- `DISGUISE_METAPHOR` has no real instance. Every `pose` finding is
  `posing (significant) challenges`, and every `pass` finding is literal
  (`passing tests`, `message passing`). `pose` and `pass` are in the
  always-metaphorical set, so the detector fires without `as`. Its
  rise measures `posing challenges`, a phrase that did rise, under the
  wrong id. A fix needs a test row first (requiring `as`, as in
  `poses as` and `passes for`); this task could not change `tools/`.
- `FRAME_MARKER` changed composition. `It is important to` and
  `it is worth mentioning` (7 pre, 0 post) are advance organizers.
  `In today's ...` is mostly a plain time phrase (counted as not real,
  except one `in today's era`). `At its core,` (6 post) is an organizer;
  `At its core is a ...` (4 post) describes a component and was counted
  as not real. With 28 findings the fall is not reliable.

**Verdict.** The hypothesis holds in part. It is not a null result: six
constructions rose beyond their intervals, and the measured risers
match the blog labels where both exist. Two of its predictions failed.
`TRICOLON` was expected flat and rose 1.44, carried by `list-like` and
`enumeration`. `EM_DASH` could not be tested on ASCII abstracts.

**What it implies for confidence in the academic register.**

- Raise: `PARTICIPIAL_TAIL` (3.1 times, accurate here), and
  `rather than` as its own pattern or subtype. A lemma list for the participial
  verbs that rose is a candidate pattern split.
- Keep low and treat as a rate signal: `TRICOLON` `list-like` and
  `enumeration` (about 1.5 times), via density (5.4). `figure` is
  ordinary academic English.
- Lower in this register: `CORRECTIVE_CONTRAST` `cc_coordinated`,
  `BORROWED_RIGOUR`, `af_less_than`, `instead of`, `VAGUE_QUANTIFIER`
  and the flat `LLM_DICTION` words (`dynamic`, `paradigm`, `robust`,
  `crucial`). Their rates did not move, so here they mark the register.
  They do not mark LLM influence.
- Split by phrase: `LLM_DICTION` and `CONSULTANT_REGISTER` hold both
  risers and flat words. Per-phrase confidence fits the data better
  than one confidence per list.
- Fix before trusting: `DISGUISE_METAPHOR` (`pose`, `pass` without
  `as`).

The post window mixes human and LLM-assisted papers, so each ratio
understates the LLM rate. Topic also shifted (LLM accelerators
and LLM-for-EDA papers are new in 2025 to 2026), which genre matching
does not remove. These ratios fit the empirical-Bayes prior in 5.3.
They are not LRs.

### harvest.py by subtype

`eval/harvest.py --by-subtype` groups the summary by construction,
pattern and subtype. `--summary-only PATH` regroups an existing
`labels.jsonl` without loading spaCy or reading `$PACINO` (about 0.1 s).

**Parsing rule.** Take the last `[...]` group at the end of
`label_text`. If it starts with a member-count field (`3-part NOUN, `
or `3 clauses, `), drop that field. Otherwise the whole bracket is the
subtype. A label with no bracket groups as `-`. The rule does not split
on every comma, because `[X, not Y]` and `[cleft, across sentences]`
are single names with commas in them. Splitting would merge
`cc_negated_apposition` `X, not Y` into a `not Y` row.

**Byte identity.** Without the option, a full harvest before and after
the change gave the same summary and `labels.jsonl`, byte for byte, and
both match the committed `labels.jsonl`. `--summary-only` on the
committed file prints the same summary. A full harvest with
`--by-subtype` writes the same `labels.jsonl`, and its summary equals
the regrouped one.

**Check against TF-003's hand counts** (`TRICOLON tricolon`):

| subtype | accepted | rewritten | deleted | prec* | TF-003 by hand |
|---|---|---|---|---|---|
| `list-like` | 52 | 15 | 89 | 0.22 | 52 / 15 / 89 |
| `enumeration` | 23 | 3 | 39 | 0.12 | 23 / 3 / 39 |
| `figure` | 9 | 1 | 8 | 0.10 | 9 / 1 / 8 |

No difference. `tools/tests.py` is unchanged; this table stands in for
a test row.

## 12. TF-005 results (2026-11-18)

### arXiv cs.AR paper bodies, a pilot

**Data.** Each window's TF-004 primary `cs.AR` ids were shuffled with
seed `20261118-bodies-<window>` and walked in order until 200 papers
had usable LaTeX source. Source came from
`export.arxiv.org/e-print/<id>v1`, the v1 version, so a pre-window body
cannot hold a later revision. The API abstracts are the latest version,
as in TF-004. Source, expanded text and findings are under
`private/arxiv/`; the committed table is `eval/arxiv-bodies-2026-11-18.md`.

| measure | pre | post |
|---|---|---|
| walked / kept | 246 / 200 | 223 / 200 |
| skipped: PDF only | 41 | 13 |
| skipped: no main file found | 0 | 8 |
| skipped: under 300 words after masking | 4 | 2 |
| skipped: placeholder text (pages as images) | 1 | 0 |
| body words (all sections) | 1,298,043 | 931,293 |
| mean paper length, words | 6,490 | 4,656 |
| abstract words | 38,478 | 37,794 |

The pre side lost more papers to PDF-only source, which may select for
LaTeX users. Post papers are shorter. Rates are per 1,000 words, so
length does not bias them.

**Method.** `eval/arxiv_bodies.py`. The main file is the one with
`\documentclass` and `\begin{document}`; `\input` and `\include` are
expanded. A LaTeX masker blanks in place: preamble, comments, back
matter, math, floats and code with their captions, references,
footnotes, headings, command names, the abstract and the
acknowledgements. Text commands keep their argument. TeX `---` becomes
U+2014. `selftest` holds 64 rows on synthetic LaTeX. Sections are
classified from `\section` headings: the first section or an
"introduction" heading is introduction, then conclusion, related and
body by keyword. ticfinder ran with its defaults at 69e1743 (sha256
c1c7d5943a28), with no uncommitted changes. The bootstrap uses 2,000
draws over papers, seed 5005, with one index matrix per window shared
by all text types, so the comparisons between text types are paired.

**Masking checks.** The median masked share inside the kept body is
29.9% pre and 33.8% post; 39 and 56 papers exceed 40%, almost all
because of large figures and tables. No float was left unclosed. A
spot-check of 40 random masked sentences per window found LaTeX
residue in 1 pre and 0 post, under the pilot limit of 2. An automatic
scan of all 102k sentences found user reference macros
(`\Fig{fig:x}`) leaking label keys; the masker drops them now, with
self-test rows.

**Hypothesis: abstract ratios hold for bodies.** Rows with at least 20
findings in both windows of both text types. Ratio is post rate over
pre rate.

| construction | abstract ratio (95% CI) | body ratio (95% CI) | body over abstract (95% CI) | inside |
|---|---|---|---|---|
| `PARTICIPIAL_TAIL` | 3.31 (2.51 to 4.53) | 4.06 (3.46 to 4.74) | 1.22 (0.88 to 1.61) | yes |
| `TRICOLON` | 1.80 (1.48 to 2.23) | 1.41 (1.27 to 1.57) | 0.79 (0.63 to 0.95) | no |
| `LLM_DICTION` | 1.20 (0.90 to 1.60) | 1.29 (1.03 to 1.63) | 1.08 (0.81 to 1.44) | yes |
| `CONSULTANT_REGISTER` | 1.16 (0.79 to 1.73) | 1.52 (1.19 to 1.96) | 1.31 (0.89 to 1.94) | yes |
| `ALTERNATIVE_FRAMING` | 1.10 (0.67 to 1.85) | 1.17 (1.02 to 1.34) | 1.06 (0.64 to 1.73) | yes |
| `VAGUE_QUANTIFIER` | 0.96 (0.61 to 1.53) | 1.10 (0.74 to 1.56) | 1.14 (0.66 to 1.97) | yes |
| `ABSTRACT_ADVERB` | 0.93 (0.54 to 1.60) | 1.84 (1.50 to 2.25) | 1.98 (1.21 to 3.34) | no |

The hypothesis holds for 5 of 7 constructions, so it is not rejected.
The test is weak: 200 abstracts hold about 38k words per window, and
the abstract intervals are wide. The two exceptions differ in kind.

- `TRICOLON`: the sample's abstract ratio (1.80) is high against the
  full TF-004 set (1.44, 1.32 to 1.56). The body ratio (1.41) agrees
  with TF-004. The exception comes from the 200-abstract sample.
- `ABSTRACT_ADVERB`: the body ratio (1.84) is above both the sample
  abstract ratio and TF-004's (1.27, 1.02 to 1.59). This construction
  rose more in bodies.

**Alternative: LLM editing concentrates in abstracts and
introductions.** The introduction ratios lie inside the abstract
intervals for all 7 rows. The body ratios are not smaller. For 8 of
10 rows the body ratio lies inside the introduction interval. The two
exceptions are larger in bodies: `ABSTRACT_ADVERB` by 1.54 times and
`BORROWED_RIGOUR` by 2.35 times. Only `TRICOLON` is smaller in bodies than
in sample abstracts. The data does not support the alternative for
these constructions.

**Related work and conclusions.** The report also compares these
sections with abstracts and with bodies. Related sections hold 167k
words pre and 105k post. Conclusions hold 46k and 32k. Against abstracts, the section
ratio lies inside the abstract interval for 6 of 7 rows (related) and
5 of 6 (conclusion). Body intervals are narrow, so the fairer test
against bodies is the paired ratio of ratios. Its interval excludes 1
for five rows:

| row | section over body (95% CI) |
|---|---|
| related: `ALTERNATIVE_FRAMING` | 1.48 (1.11 to 1.95) |
| related: `ABSTRACT_ADVERB` | 0.69 (0.51 to 0.94) |
| related: `BORROWED_RIGOUR` | 0.52 (0.30 to 0.97) |
| conclusion: `TRICOLON` | 1.36 (1.07 to 1.72) |
| conclusion: `ABSTRACT_ADVERB` | 0.52 (0.29 to 0.88) |

For `PARTICIPIAL_TAIL` the conclusion ratio is 1.60 times the abstract
ratio (1.05 to 2.41). These sections have few findings. With about 40
paired comparisons, one or two of these rows could be chance.
`ABSTRACT_ADVERB` and `BORROWED_RIGOUR` rose most in body sections.

**What changed most in bodies** (construction or pattern, at least 20
findings):

| row | pre rate | post rate | ratio (95% CI) | in TF-004 abstracts |
|---|---|---|---|---|
| `EM_DASH` | 0.18 | 0.95 | 5.28 (2.87 to 10.98) | not measurable |
| `cc_negated_apposition` | 0.02 | 0.10 | 4.96 (2.37 to 11.53) | too few |
| `PARTICIPIAL_TAIL` | 1.13 | 4.57 | 4.06 (3.46 to 4.74) | 3.14 |
| `HOLLOW_BOOSTER` | 0.06 | 0.18 | 3.31 (2.25 to 4.93) | flat, few |
| `af_rather_instead` | 0.29 | 0.74 | 2.51 (2.01 to 3.14) | 2.15 |
| `ABSTRACT_ADVERB` | 0.47 | 0.86 | 1.84 (1.50 to 2.25) | 1.27 |
| `BORROWED_RIGOUR` | 0.16 | 0.26 | 1.60 (1.16 to 2.18) | 1.02, flat |
| `CORRECTIVE_CONTRAST` | 0.29 | 0.40 | 1.41 (1.06 to 1.91) | 1.04, flat |
| `af_less_than` | 0.74 | 0.47 | 0.64 (0.53 to 0.78) | 0.90, flat |
| `EMPTY_FRAME` | 0.11 | 0.07 | 0.62 (0.39 to 0.96) | too few |
| `HEDGE_STACK` | 0.02 | 0.01 | 0.25 (0.05 to 0.73) | too few |

`BORROWED_RIGOUR` and `CORRECTIVE_CONTRAST` were flat in abstracts and
rose in bodies. TF-004 listed both as candidates to lower in this
register; the body data says to keep them. `HEDGE_STACK` fell, on 26
findings.

**`EM_DASH`.** Bodies have the dashes that abstracts lack. The kept
text held 259 TeX `---` pre and 350 post, and 1 Unicode em dash pre
against 433 post. The rate rose in every section, from 3.6 times in
introductions to 8.8 in conclusions (55 findings there). One caveat:
spaced ` -- ` (219 pre, 195 post) is an en dash in TeX that some
authors use as an em dash, and ticfinder does not count it. Counted as
em dashes, they bring the ratio over all sections from 4.9 to about
3.3. Either way it rose.

**Sanity reading.** 20 random body findings per window for the three
constructions with the largest body ratio change (`EM_DASH`,
`PARTICIPIAL_TAIL`, `HEDGE_STACK`), plus `HOLLOW_BOOSTER` since
`EM_DASH` was in the three. Counts only.

| construction | pre: real / read | post: real / read |
|---|---|---|
| `EM_DASH` | 19 / 20 | 18 / 20 |
| `PARTICIPIAL_TAIL` | 18 / 20 | 20 / 20 |
| `HEDGE_STACK` | 20 / 20 | 4 / 4 |
| `HOLLOW_BOOSTER` | 15 / 20 | 20 / 20 |

- `EM_DASH` misses are en dashes in a byte range and in a hyphenated
  compound.
- `PARTICIPIAL_TAIL` misses are a participle followed by a coordinated
  main verb, and a gerund subject.
- `HOLLOW_BOOSTER` misses are all the manner adverb `significantly,`
  before a comma (`drop significantly, about 73%`). Post findings are
  sentence-initial `Notably,`, `Crucially,` and `Importantly,`. The
  misses sit in pre, so the true ratio is higher than 3.3. A fix needs
  a test row first.

**Check against TF-004.** The sample's abstract counts equal the
TF-004 per-paper counts for the same papers. The sample's abstract
ratio lies inside the TF-004 interval for 9 of 17 rows, and the TF-004
ratio lies inside the sample interval for 14 of 17. A 200-paper
interval is two to three times as wide as the TF-004 one, so about half
the sample points are expected inside it by sampling alone. The rows
where neither holds are `TRICOLON` (above) and `FRAME_MARKER` (5 and 0
findings). This is what sampling 200 papers costs: abstract ratios from
the pilot alone are not reliable, and bodies give 25 to 34 times the
words.

**For step 8.** Use the body ratios (all sections) as the prior, with
the TF-004 abstract ratios as a check. Bodies are closer to the design
register and hold 25 to 34 times the words per paper. They also give
`EM_DASH` a value. Where the two agree, either serves. Where they differ
(`ABSTRACT_ADVERB`, `BORROWED_RIGOUR`, `CORRECTIVE_CONTRAST`), the body
value is the one in register. Both remain ratios over a mixed post
window, so they understate the LLM rate and are not LRs. The topic
shift noted in section 11 applies here too.

**A full run.** Worth doing. The pre window has 955 papers, and at this
pilot's skip rate about 775 have usable source, which would give about
four times the pre words. That narrows the intervals for the rare rows
(`HEDGE_STACK`, `GAPPED_ANTITHESIS`, `cc_parallel_sibling`,
`DISGUISE_METAPHOR`) and makes subtype splits measurable. Do it after
steps 10 and 11, so that one analysis measures the fixed and split
patterns. The source cache is reusable; analysis took about 4 seconds
per paper.

## 13. TF-006 results (2026-11-18)

Both fixes follow the same method. Test rows come first and fail
before the change. `make regress` and `harvest.py --by-subtype` run
before and after. `eval/arxiv_recheck.py` takes the stored arXiv
findings for one construction (TF-004 abstracts, TF-005 bodies),
parses each stored sentence on its own, and runs the committed and the
new detector on it. A stored finding is reproduced when the old code
gives the same matched text. It is kept when a new span covers it. The
adjusted rate is kept findings over the words in the private per-paper
tables, a point estimate. The committed arXiv reports were not rerun
(step 14).

### Phase 1: `DISGUISE_METAPHOR`

**Fix.** `pose` and `pass` fire only with an `as` frame. The frame
must be intransitive (`posing as`), reflexive (`passing itself off
as`) or have `off` (`passed off as`). A literal `as` use is passive or
has an object: `is passed as an argument`, `is posed as an integer
program`, `passing it as an argument`. Those stay silent. `pass for`
is not supported, because `passing for all seeds` is literal in
verification prose and parses the same way as the disguise use. The
other verbs are unchanged. 14 new rows; 7 of the 11 negatives failed
before the fix. The other 4 were already silent. The detector reads
only participles, so it never fired on finite `pose` or `passes`.

**Harvest.** The 3 `DISGUISE_METAPHOR` labels were all literal `pass`
(1 accepted, 2 deleted, 0 rewritten). All 3 drop out, so prec* cannot
be measured before or after. Totals went from 142 accepted, 54
rewritten and 304 deleted to 141, 54 and 302. No other row changed.
The one accepted label has a waiver in the pacino waiver directory,
which now matches nothing and shows as stale.

**arXiv recheck.**

| source | window | stored | reproduced | kept | stored /1k | kept /1k |
|---|---|---|---|---|---|---|
| TF-004 abstracts | pre | 3 | 3 | 0 | 0.017 | 0.000 |
| TF-004 abstracts | post | 24 | 23 | 0 | 0.048 | 0.000 |
| TF-005 bodies, all sections | pre | 20 | 19 | 2 | 0.015 | 0.002 |
| TF-005 bodies, all sections | post | 24 | 24 | 2 | 0.026 | 0.002 |

The isolated parse reproduces 69 of 71 stored findings. The new code
adds none. The adjusted body ratio is 1.39 on 2 findings against 2, so
it carries no information. The abstract ratio is undefined.

**Reading.** Counts only.

| group | real / read |
|---|---|
| pre dropped | 0 / 20 (all) |
| post dropped | 0 / 20 (sampled from 45) |
| pre kept | 0 / 2 |
| post kept | 0 / 2 |

The other 25 post findings were scanned for `off`, `-self` and
`posing as`, and none matched. Dropped findings are `posing ...
challenges` and literal `pass` (`passing tests`, `message passing`,
`passed as input`). Three of the 4 kept findings come from `mask ...
as` and `package ... as`, which this fix did not change. The fourth is
`passing off ... as`, used literally about counterfeit parts.

**Verdict.** The hypothesis holds. The fix removes every false
positive read and loses no real instance. The TF-004 rise for this
construction measured `posing challenges`. A candidate follow-up is a
literal `package as` and `mask as` with an `as` frame, which needs
rows first.

### Phase 2: `HOLLOW_BOOSTER`

**Phrase rows.** `test_detectors()` routes a row whose id is a phrase
construction (built in or from the phrase file) through
`analyse(..., only={cid})`. The verbose detector output for the
existing rows is identical before and after the change.

**Fix.** `significantly` left the shared booster pattern. It now has
three patterns: `Significantly ,` with `IS_SENT_START`, `More` or
`Most significantly ,` at the start of a sentence, and `Even more` or
`Even most significantly ,` there. The other booster words keep their
pattern and span. Phrase patterns carry no pattern name, so the
fingerprint of a finding that keeps its span is unchanged. 12 new
rows; the 3 manner-adverb negatives failed before the change.

The first version used `IS_SENT_START` alone. On the stored findings
it dropped 2 real boosters, `More significantly,` and `Even more
significantly,`, so the two `more` patterns were added with rows first.
The Matcher cannot look behind a token, so those spans start at `More`
or `Even`. This changes the matched text and fingerprint of those
findings only. No waiver holds `HOLLOW_BOOSTER`. A mid-sentence
comparative (`area grew more significantly, by about 40%`) stays
silent, which is why the `more` patterns are anchored at the start of
the sentence.

**Harvest.** No `HOLLOW_BOOSTER` labels. Summary and `labels.jsonl` are
byte-identical before and after.

**arXiv recheck.** The old code reproduces every stored finding, and
the new code adds none.

| source | window | stored | kept | stored /1k | kept /1k |
|---|---|---|---|---|---|
| TF-004 abstracts | pre | 10 | 9 | 0.056 | 0.050 |
| TF-004 abstracts | post | 40 | 37 | 0.080 | 0.074 |
| TF-005 bodies, all sections | pre | 74 | 57 | 0.057 | 0.044 |
| TF-005 bodies, all sections | post | 158 | 148 | 0.170 | 0.159 |
| TF-005 body sections | pre | 51 | 39 | 0.056 | 0.042 |
| TF-005 body sections | post | 121 | 114 | 0.184 | 0.173 |

| source | stored ratio | adjusted ratio |
|---|---|---|
| TF-004 abstracts | 1.43 | 1.47 |
| TF-005 bodies, all sections | 2.98 | 3.62 |
| TF-005 body sections | 3.31 (2.25 to 4.93) | 4.07 |

The 3.31 in section 12 is the `body` section type. All sections give
2.98 in the committed report. Both adjusted ratios rose, as predicted,
because the removed findings sit mostly in pre.

**Reading.** Counts only.

| group | real / read |
|---|---|
| pre dropped | 0 / 18 (all) |
| post dropped | 0 / 13 (all) |
| pre kept | 20 / 20 (sampled from 66) |
| post kept | 20 / 20 (sampled from 185) |

Every dropped finding is a manner or degree adverb before a comma
(`slowed down significantly, resulting in`). Kept findings are
`Notably,`, `Importantly,`, `Crucially,`, `Critically,` and the two
`more significantly,` forms.

**Not covered.** In markdown the bullet token takes the sentence start,
so `- Significantly,` and `**Significantly,**` no longer fire.
`And, significantly,` does not fire either. Neither form occurs in the
pacino markdown, and `\item` is blanked in the arXiv text.

**Verdict.** The hypothesis holds with one correction. Sentence-initial
use alone dropped `More significantly,`, a real booster. With the
`more` patterns, the fix removes 31 false positives and no real
instance. The adjusted body ratio rises from 3.31 to 4.07.

## 14. TF-007 results (2026-11-19)

Step 11: pattern splits and interim confidence from the TF-004 and
TF-005 ratios. Each phase ran `make regress` and `harvest.py
--by-subtype` before and after.

### Interim confidence rule

Used in all three phases until calibration (step 8) replaces it.

- A pattern, lemma or phrase gets `med` when its ratio interval lies
  above 1 in both the TF-004 abstracts and the TF-005 bodies (all
  sections), with at least 20 findings in each corpus (pre and post
  together). Otherwise it keeps its construction's confidence.
- A level is never raised more than one step above the construction's
  confidence.
- The rule only raises. A pattern or phrase that fell keeps the
  default.

Abstract values come from the committed TF-004 report
(`eval/arxiv-rates-2026-11-18.md`). The committed TF-005 report gives
subtype rows for the `body` section type only, so body values over all
sections are computed from the private per-paper tables with the TF-005
bootstrap (2,000 draws over papers, seed 5005, the same index matrix).
That computation reproduces the committed `body` rows exactly, for
example `use` at 1.33 (0.90 to 2.05).

### Phase 1: `ALTERNATIVE_FRAMING`

**Split.** `af_rather_instead` became `af_rather_than` and
`af_instead_of`. Spans and subtypes are unchanged. By the rule,
`af_rather_than` runs at `med` and `af_instead_of` keeps the
construction's `low`.

| pattern | abstracts n | abstract ratio (95% CI) | bodies n | body ratio, all sections (95% CI) | confidence |
|---|---|---|---|---|---|
| `af_rather_than` | 164 | 3.84 (2.29 to 8.06) | 691 | 4.44 (3.27 to 6.10) | `med` |
| `af_instead_of` | 88 | 1.07 (0.68 to 1.90) | 373 | 1.02 (0.77 to 1.36) | `low` |

The `body` section type alone gives 4.60 (3.22 to 6.70) and 0.98
(0.72 to 1.34), with the same verdicts.

The first pattern of a construction has no confidence slot in the
registry, so `af_rather_than` returns `med` per finding.

**Rename map.** `RENAMED_PATTERNS` in `ticfinder.py` maps each new
pattern name to the old one. `legacy_fingerprints()` returns every
old-style id a finding may carry: the pre-TF-001 sentence cut, the old
pattern name, and both. A normal run counts these as old-style ids.
`--migrate-waivers` rekeys them. When an entry's `pattern` field held
the old name, it now holds the new one.

**Fingerprints.** The id of every finding from the two new patterns
changed. Affected waivers:

| directory | `rather than` | `instead of` | total |
|---|---|---|---|
| this repo, `waivers/` | 11 | 4 | 15 |
| `$PACINO/waivers` | 12 | 7 | 19 |

The task file counted 20 and 9. It missed the 5 in
`BLOG_bpu_13_contradiction_detection.waivers.json`, whose entries
have an empty `pattern` field. One of those 5 also carried a
pre-TF-001 id and became held after migration (bpu_13: 11 waived and
3 stale before, 12 and 2 after). `save_waivers()` sorts entries by
line, so the bpu_13 file was reordered; its contents changed only in
the 5 ids.

**Harvest.** Totals 141 accepted, 54 rewritten, 302 deleted, as
before. `ALTERNATIVE_FRAMING` rows:

| run | pattern | subtype | rewr | del | acc | open | prec* |
|---|---|---|---|---|---|---|---|
| before | `af_rather_instead` | rather than | 14 | 77 | 12 | 0 | 0.54 |
| before | `af_rather_instead` | instead of | 1 | 3 | 7 | 0 | 0.12 |
| after, no migration | `af_rather_than` | rather than | 14 | 77 | 0 | 12 | 1.00 |
| after, no migration | `af_instead_of` | instead of | 1 | 3 | 0 | 7 | 1.00 |
| after, migrated copy | `af_rather_than` | rather than | 14 | 77 | 12 | 0 | 0.54 |
| after, migrated copy | `af_instead_of` | instead of | 1 | 3 | 7 | 0 | 0.12 |

The migrated run equals the baseline row for row once the pattern is
renamed. The only other change in `labels.jsonl` is the confidence of
the 103 `rather than` rows. The committed `labels.jsonl` comes from
the migrated copy, so it matches `$PACINO` once its waivers are
migrated.

**arXiv recheck.** `arxiv_recheck.py ALTERNATIVE_FRAMING` against the
committed code: every reproduced finding is kept (108 and 395 in
abstracts, 853 and 908 in bodies), and none is new.

**Verdict.** The hypothesis holds. The two patterns differ in blog
precision and in their arXiv change. The split moves no finding, and
the migration keeps every waiver.

### Phase 2: `PARTICIPIAL_TAIL`

**Lemma table.** Every lemma with at least 20 findings in either
corpus. Bodies are all sections. An abstract cell without a ratio has
fewer than 20 findings, so the TF-004 report does not list it; its
count comes from the private findings.

Rose in both (22):

| lemma | abstracts n | abstract ratio (95% CI), verdict | bodies n | body ratio (95% CI), verdict |
|---|---|---|---|---|
| `achieve` | 188 | 4.45 (2.80 to 8.96) rose | 129 | 9.84 (5.89 to 19.25) rose |
| `cause` | 28 | 4.66 (1.56 to inf) rose | 78 | 2.95 (1.48 to 6.70) rose |
| `create` | 25 | inf (inf to inf) rose | 42 | 8.36 (3.64 to 43.04) rose |
| `deliver` | 36 | 6.09 (2.13 to inf) rose | 24 | 6.97 (2.32 to 36.76) rose |
| `demonstrate` | 118 | 8.10 (3.95 to 37.68) rose | 85 | 9.38 (4.85 to 25.49) rose |
| `eliminate` | 48 | 8.24 (2.97 to inf) rose | 45 | 6.45 (3.03 to 18.93) rose |
| `enable` | 251 | 6.56 (4.15 to 13.89) rose | 363 | 7.04 (4.92 to 10.77) rose |
| `ensure` | 43 | 4.78 (1.90 to inf) rose | 150 | 24.74 (12.51 to 77.37) rose |
| `highlight` | 45 | inf (inf to inf) rose | 50 | 68.30 (19.83 to inf) rose |
| `improve` | 43 | 2.21 (1.05 to 7.09) rose | 49 | 2.40 (1.32 to 4.90) rose |
| `lead` | 102 | 2.96 (1.72 to 6.81) rose | 200 | 2.37 (1.56 to 3.76) rose |
| `leave` | 48 | inf (inf to inf) rose | 74 | 5.48 (3.16 to 10.98) rose |
| `leverage` | 32 | 5.37 (1.82 to inf) rose | 31 | 7.25 (2.59 to inf) rose |
| `limit` | 62 | 4.08 (2.06 to 19.75) rose | 48 | 4.69 (2.30 to 11.54) rose |
| `make` | 208 | 2.40 (1.65 to 3.85) rose | 320 | 7.18 (5.18 to 10.43) rose |
| `offer` | 61 | 6.93 (3.01 to inf) rose | 62 | 6.46 (3.12 to 18.04) rose |
| `provide` | 73 | 1.82 (1.08 to 3.79) rose | 149 | 3.33 (2.20 to 5.40) rose |
| `reduce` | 113 | 3.01 (1.80 to 6.55) rose | 137 | 3.15 (2.09 to 4.85) rose |
| `require` | 43 | 4.78 (1.97 to inf) rose | 81 | 3.98 (2.39 to 7.54) rose |
| `show` | 54 | 2.87 (1.40 to 9.22) rose | 58 | 2.65 (1.49 to 5.19) rose |
| `support` | 21 | 3.40 (1.08 to inf) rose | 34 | 5.38 (2.26 to 19.67) rose |
| `yield` | 24 | 8.24 (2.16 to inf) rose | 76 | 7.43 (3.85 to 19.81) rose |

Flat in both (1):

| lemma | abstracts n | abstract ratio (95% CI), verdict | bodies n | body ratio (95% CI), verdict |
|---|---|---|---|---|
| `use` | 73 | 1.09 (0.67 to 2.00) flat | 245 | 1.30 (0.93 to 1.84) flat |

Mixed or too few (39):

| lemma | abstracts n | abstract ratio (95% CI), verdict | bodies n | body ratio (95% CI), verdict |
|---|---|---|---|---|
| `account` | 4 | too few | 23 | 9.29 (3.40 to inf) rose |
| `add` | 3 | too few | 30 | 2.41 (0.93 to 13.87) flat |
| `address` | 15 | too few | 24 | 15.33 (4.82 to inf) rose |
| `allow` | 72 | 1.48 (0.87 to 3.12) flat | 259 | 4.72 (3.48 to 6.76) rose |
| `assume` | 0 | too few | 27 | 0.82 (0.32 to 2.03) flat |
| `avoid` | 15 | too few | 41 | 3.37 (1.58 to 9.62) rose |
| `combine` | 20 | 3.22 (1.06 to inf) rose | 14 | 5.11 (1.48 to inf) too few |
| `compare` | 6 | too few | 21 | 2.79 (1.11 to 11.07) rose |
| `confirm` | 11 | too few | 39 | inf (inf to inf) rose |
| `consider` | 7 | too few | 31 | 1.31 (0.56 to 2.75) flat |
| `correspond` | 9 | too few | 39 | 3.55 (1.78 to 10.52) rose |
| `cover` | 14 | too few | 22 | 13.94 (4.71 to inf) rose |
| `enhance` | 7 | too few | 26 | inf (inf to inf) rose |
| `focus` | 21 | 3.40 (1.11 to inf) rose | 24 | 2.32 (0.99 to 6.62) flat |
| `form` | 5 | too few | 25 | 7.32 (2.78 to 37.88) rose |
| `generate` | 14 | too few | 29 | 2.28 (0.96 to 6.16) flat |
| `give` | 5 | too few | 39 | 3.14 (1.49 to 9.21) rose |
| `increase` | 16 | too few | 45 | 1.59 (0.84 to 3.09) flat |
| `incur` | 15 | too few | 20 | 4.18 (1.60 to 20.63) rose |
| `indicate` | 9 | too few | 106 | 5.32 (3.35 to 10.43) rose |
| `introduce` | 19 | too few | 29 | 5.34 (2.13 to 23.75) rose |
| `maintain` | 3 | too few | 20 | 26.48 (6.40 to inf) rose |
| `match` | 7 | too few | 21 | 13.24 (4.05 to inf) rose |
| `mean` | 4 | too few | 54 | 1.12 (0.54 to 2.43) flat |
| `minimize` | 13 | too few | 23 | 3.95 (1.59 to 18.65) rose |
| `motivate` | 14 | too few | 26 | 10.69 (3.75 to inf) rose |
| `optimize` | 10 | too few | 21 | 8.36 (2.46 to inf) rose |
| `outperform` | 31 | 10.75 (2.88 to inf) rose | 13 | 7.67 (2.05 to inf) too few |
| `prevent` | 4 | too few | 36 | 4.18 (2.08 to 11.17) rose |
| `produce` | 14 | too few | 47 | 9.52 (3.94 to 47.51) rose |
| `range` | 6 | too few | 24 | 2.32 (0.98 to 5.99) flat |
| `reach` | 14 | too few | 28 | 6.41 (2.51 to 41.83) rose |
| `reflect` | 1 | too few | 49 | 32.75 (11.61 to inf) rose |
| `represent` | 3 | too few | 30 | 3.25 (1.42 to 9.52) rose |
| `result` | 82 | 0.92 (0.57 to 1.63) flat | 219 | 2.97 (2.05 to 4.60) rose |
| `start` | 0 | too few | 27 | 1.50 (0.66 to 3.34) flat |
| `suggest` | 6 | too few | 39 | 12.20 (4.64 to 68.05) rose |
| `target` | 16 | too few | 26 | 3.14 (1.24 to 10.34) rose |
| `validate` | 8 | too few | 22 | 8.83 (2.95 to inf) rose |

**Lemma list: a null result.** `use` is the only lemma flat in both
corpora. Of the 26 lemmas with at least 20 findings in both corpora,
22 rose in both. `allow` and `result` were flat in abstracts and rose
in bodies, and `focus` rose in abstracts and was flat in bodies. A list
of risers would hold
nearly every frequent verb, so it does not separate risers from flat
verbs. The construction is already `high`, so the interim rule has no
level to raise a lemma to either. No list was added.

**Reading `, using ...` tails.** `arxiv_recheck.py` gained
`--subtype`, which keeps stored findings whose subtype matches (the
harvest rule). With `--sources body --subtype use --show 20 --seed
tf007` it samples 20 of the reproduced body findings per window. 239
of the 245 stored `use` findings reproduce on the isolated sentence.

| window | instrumental | restating | other |
|---|---|---|---|
| pre | 19 | 0 | 1 |
| post | 17 | 0 | 3 |

An instrumental tail names the method, data, tool or setting (`, using
a 4-bit counter`, `, using the ImageNet dataset`). None of the 40
restates the main clause. The four others are parse errors: two list
items after `e.g.` or inside a parenthesis, one gerund subject, and
one member of a list of techniques.

**Change.** `participial_tail()` returns per-finding confidence from
`PT_LEMMA_CONFIDENCE`, which holds `use: med`, one level below the
construction. The interim rule only raises, so this level comes from
the reading. It is the only lemma whose level was set that way. Spans,
subtypes and the pattern name are unchanged, so no fingerprint
changed. The lemma cannot tell a restating `, using ...` tail from an
instrumental one, so both report at `med`; rows record that.

**Harvest.** The blogs hold no `use` tail. Summary and `labels.jsonl`
are byte-identical before and after.

**Verdict.** The lemma list is a null result. The narrower claim holds:
`, using ...` tails are almost all instrumental, and `use` now runs at
`med`.

### Phase 3: per-phrase confidence

**Phrase table.** Every `LLM_DICTION` and `CONSULTANT_REGISTER`
matched text, lowercased, with at least 20 findings in either corpus.
Both constructions match by lemma, so one entry gives several rows
(`leverage`, `leverages`, `leveraging`, `leveraged`). Abstract
values come from the TF-004 report, which lists rows with at least 20
findings; smaller counts come from the private findings. Body values
cover all sections, with the TF-005 bootstrap (2,000 draws over papers,
seed 5005). Summed over phrases, the body counts equal the per-paper
construction counts (4,091 and 2,274).

| construction | matched text | abstracts n | abstract ratio (95% CI) | verdict | bodies n | body ratio, all sections (95% CI) | verdict | interim |
| `CONSULTANT_REGISTER` | `leverages` | 185 | 3.54 (2.25 to 6.84) | rose | 178 | 2.81 (1.76 to 4.56) | rose | `med` |
| `CONSULTANT_REGISTER` | `leveraging` | 219 | 1.88 (1.32 to 2.88) | rose | 258 | 2.00 (1.36 to 3.03) | rose | `med` |
| `CONSULTANT_REGISTER` | `optimizing` | 139 | 1.81 (1.19 to 2.98) | rose | 237 | 1.53 (1.05 to 2.30) | rose | `med` |
| `CONSULTANT_REGISTER` | `at scale` | 12 | - | too few | 28 | 6.41 (2.45 to 42.94) | rose | `low` |
| `CONSULTANT_REGISTER` | `holistic` | 33 | 0.96 (0.45 to 2.30) | flat | 44 | 1.53 (0.55 to 5.41) | flat | `low` |
| `CONSULTANT_REGISTER` | `leverage` | 86 | 0.83 (0.53 to 1.34) | flat | 311 | 0.97 (0.69 to 1.38) | flat | `low` |
| `CONSULTANT_REGISTER` | `leveraged` | 18 | - | too few | 58 | 0.63 (0.30 to 1.31) | flat | `low` |
| `CONSULTANT_REGISTER` | `optimize` | 201 | 1.24 (0.89 to 1.82) | flat | 345 | 0.96 (0.64 to 1.48) | flat | `low` |
| `CONSULTANT_REGISTER` | `optimized` | 388 | 1.19 (0.92 to 1.59) | flat | 634 | 1.37 (1.03 to 1.83) | rose | `low` |
| `CONSULTANT_REGISTER` | `optimizes` | 96 | 1.36 (0.85 to 2.51) | flat | 89 | 1.56 (0.94 to 2.64) | flat | `low` |
| `LLM_DICTION` | `comprehensive` | 206 | 1.64 (1.16 to 2.50) | rose | 278 | 3.51 (1.83 to 6.38) | rose | `med` |
| `LLM_DICTION` | `essential` | 176 | 1.89 (1.33 to 3.00) | rose | 250 | 2.16 (1.45 to 3.41) | rose | `med` |
| `LLM_DICTION` | `landscape` | 28 | 4.66 (1.62 to inf) | rose | 39 | 6.37 (2.20 to 45.74) | rose | `med` |
| `LLM_DICTION` | `crucial` | 133 | 1.18 (0.82 to 1.86) | flat | 159 | 2.71 (1.86 to 3.93) | rose | `low` |
| `LLM_DICTION` | `dynamic` | 520 | 1.01 (0.79 to 1.30) | flat | 1106 | 1.11 (0.77 to 1.59) | flat | `low` |
| `LLM_DICTION` | `dynamics` | 52 | 1.50 (0.58 to 8.03) | flat | 86 | 2.35 (1.05 to 5.86) | rose | `low` |
| `LLM_DICTION` | `harness` | 24 | 0.87 (0.34 to 5.05) | flat | 42 | 8.36 (1.39 to 47.29) | rose | `low` |
| `LLM_DICTION` | `innovative` | 33 | 2.01 (0.88 to 8.97) | flat | 33 | 3.21 (1.33 to 9.57) | rose | `low` |
| `LLM_DICTION` | `orchestrate` | 8 | - | too few | 22 | 0.96 (0.33 to 2.51) | flat | `low` |
| `LLM_DICTION` | `paradigm` | 191 | 0.82 (0.57 to 1.29) | flat | 196 | 1.51 (0.78 to 2.90) | flat | `low` |
| `LLM_DICTION` | `paradigms` | 42 | 1.15 (0.57 to 2.89) | flat | 48 | 1.79 (0.75 to 3.93) | flat | `low` |
| `LLM_DICTION` | `robust` | 121 | 1.45 (0.96 to 2.42) | flat | 169 | 2.18 (1.28 to 3.93) | rose | `low` |
| `LLM_DICTION` | `seamless` | 24 | 2.51 (0.95 to inf) | flat | 51 | 6.50 (2.55 to 22.43) | rose | `low` |
| `LLM_DICTION` | `significant` | 622 | 1.22 (1.01 to 1.49) | rose | 1320 | 0.80 (0.64 to 1.01) | flat | `low` |
| `LLM_DICTION` | `versatile` | 32 | 1.55 (0.69 to 5.62) | flat | 40 | 1.26 (0.41 to 4.63) | flat | `low` |
| `LLM_DICTION` | `vital` | 25 | 0.76 (0.35 to 2.16) | flat | 18 | 0.89 (0.15 to 2.93) | too few | `low` |

**Agreement.** 22 rows have at least 20 findings in both corpora. The
verdicts agree for 14, and the body ratio lies inside the abstract
interval for 17. Of the 8 rows whose verdicts differ, 7 rose in bodies
and were flat in abstracts (`crucial`, `robust`, `seamless`,
`innovative`, `harness`, `dynamics`, `optimized`). Bodies hold
several times the words, so they detect smaller changes. The eighth,
`significant`, rose slightly in abstracts, 1.22 (1.01 to 1.49), and
was flat in bodies, 0.80 (0.64 to 1.01). No row fell in either corpus,
so no phrase is listed as a candidate for removal.

Of the words TF-004 named, `leverages`, `landscape`, `essential`
and `comprehensive` rose in both corpora. `increasingly` belongs to
`VAGUE_QUANTIFIER`, which this task did not cover. Of the flat words,
`dynamic`, `paradigm` and `optimize` stayed flat in bodies, and
`robust` (2.18) and `crucial` (2.71) rose there.

**Lemma entries.** `leverage` and `optimize` hold forms with
different verdicts. The task stopped there and the user chose a
per-form override. That keeps one lemma entry, which fires on exactly
the tokens it did before, and leaves the phrase list unchanged.

**Format.** An entry in `phrases` is a string or an object
`{"phrase": ..., "confidence": ..., "forms": {...}}`. `confidence`
sets the phrase's level. `forms` maps a matched text, lowercased, to
a level. A string keeps the construction's level. `load_phrase_file()`
rejects an unknown key, an empty phrase, a bad level and a `forms`
value that is not a mapping. `analyse()` still adds one Matcher key
per construction and finds the phrase again from the span's token
values. The matched text, the empty pattern name and the fingerprint
are unchanged; a `waivers` test checks the fingerprint. The shorthand
forms still load.

**Applied.** By the rule, six forms run at `med`, all through
`forms`, because the rule's unit is the matched text: `comprehensive`,
`essential` and `landscape` in `LLM_DICTION`, and `leverages`,
`leveraging` and `optimizing` in `CONSULTANT_REGISTER`. Rarer forms
of the same entries (`landscapes`, 5 findings; `essentials`, 2) keep
`low`. No phrase is raised by its entry `confidence`.

**Harvest.** The blogs hold 9 findings from these lists (`harness`,
`significant`, `dynamic`, `delve`, `values added`), and none is a
raised form. Summary and `labels.jsonl` are byte-identical.
Confidence counts on the harvest blogs, before and after:

| findings | high | med | low |
|---|---|---|---|
| final version | 29 | 26 | 89 |
| removed in editing | 53 | 133 | 170 |

On the arXiv findings the change is visible. The share of findings at
`med` rises from pre to post:

| source | construction | pre | post |
|---|---|---|---|
| TF-004 abstracts | `LLM_DICTION` | 0.13 | 0.18 |
| TF-004 abstracts | `CONSULTANT_REGISTER` | 0.25 | 0.40 |
| TF-005 bodies, all sections | `LLM_DICTION` | 0.09 | 0.19 |
| TF-005 bodies, all sections | `CONSULTANT_REGISTER` | 0.25 | 0.34 |

**Verdict.** The hypothesis holds. Body and abstract ratios agree for
most phrases with enough findings, and the lists hold both risers and
flat words. Per-phrase levels separate them where one level per list
could not.
