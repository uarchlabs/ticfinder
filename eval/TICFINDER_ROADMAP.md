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

Done:

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

Planned:

7. **Collect the public design and spec baseline** (5.3, section 6):
   pre-2022 PEPs, IETF and Rust RFCs, RISC-V manuals and open hardware
   design docs. Check per-file masked percentages before trusting counts.
8. **Per-pattern LRs** for the design and spec registers: the public
   baseline and the author's specs against the `pacino` LLM specs, with
   the arXiv change as a prior.
9. **arXiv paper bodies, a pilot** (TF-005). About 200 papers per
   window from the TF-004 set, from LaTeX source. Needs a LaTeX masker
   for full papers. Reports rates per section next to the same papers'
   abstracts, which tests whether the abstract ratios hold for whole
   papers. It also gives `EM_DASH` a measurement through TeX dashes, and
   intervals for the constructions that were too rare in abstracts.
   A full run is a separate decision.
10. **`DISGUISE_METAPHOR` fix** (from TF-004). `pose` and `pass` fire
    without `as`: every arXiv finding read was `posing challenges` or a
    literal `passing`. Test rows first.
11. **Pattern splits from TF-004.** `rather than` apart from
    `instead of`; a lemma list for the `PARTICIPIAL_TAIL` verbs that
    rose; confidence per phrase for `LLM_DICTION` and
    `CONSULTANT_REGISTER`. Measure each with `harvest.py --by-subtype`
    and the arXiv tables.
12. **Licensing, continued from step 5.** Fresh labels for the
    `TRICOLON` clause and noun split, then the licensing tests for
    `CORRECTIVE_CONTRAST`, `ALTERNATIVE_FRAMING` and `PARTICIPIAL_TAIL`.
13. Scan-statistic density (5.4), then subtree mining (5.5). This was
    step 9 before TF-004.

Order: 9 and 7 do not depend on each other and can run side by side.
10 is small and can go at any time. 11 waits for 9, whose section rates
may change the evidence for the splits. 8 needs 7 and uses 9 as its
prior. 12 needs new labels from blog editing, so it goes when they
exist. 13 comes last.

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
