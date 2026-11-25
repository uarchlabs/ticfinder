# ticfinder: object relatives and trailing verbs (context for a Claude Code session)

This captures a design discussion and a patch prepared outside the repo. It is
context for continuing the work in a session that has the full repo, the arXiv
corpora and the pacino blogs.

## 1. The problem

The user edits LLM-generated prose (blogs, specs, code comments) and keeps
rewriting one pattern: **the verb arrives at the end of a phrase, after the
clause's own subject**, so the reader holds a noun until the verb resolves it.

Examples from real text:

- "Note the count of the array write the last primitive made."
- "Defaults for every variable the loops assign."
- "p-stage names, as the planning documents use since ..."
- `// Undo a pop the p3 type does not have, or apply a missed one.` (RAS code)

The user is new to linguistics. Use the terms below, and explain them briefly
when they first come up.

## 2. Vocabulary

| Term | Meaning | Example |
|---|---|---|
| Object relative clause (ORC) | The modified noun is the object of the clause's verb. The verb comes after the clause's subject, with a gap where the object would be. | "the dog (that) the man bit" |
| Subject relative clause (SRC) | The modified noun is the subject. Easier to process. | "the dog that bit the man" |
| Zero / reduced / contact clause | A relative clause with no "that" or "which". | "every variable the loops assign" |
| Nominalization | A verb used as a noun, which hides the action. | "a write", "a pop" |
| Light verb | An empty verb that carries a nominalized action. | "made" in "the write the primitive made" |
| Noun stacking / compound | Nouns modifying nouns. | "array write" |
| Dependency distance / locality | How far a word is from the word it attaches to. Long distances are hard to read (Gibson's Dependency Locality Theory). | "write" ... "made" |
| Garden path | The first parse is wrong, so the reader has to re-read. | "the array write ..." read as a subject and verb |
| End-focus / end-weight | English puts heavy, important material last. A stranded light verb puts an empty word there. | |
| As-parenthetical | An "as" clause with a gap (Potts 2002). | "as the documents use [them]" |
| Passivization + whiz-deletion | ORC to reduced passive, which is technically an SRC. | "every variable the loops assign" -> "every variable assigned by the loops" |

Key points from the discussion:

- The zero relative itself is ordinary human English ("the file you sent"),
  especially in speech. What reads as LLM-like is the **dense combination**: a
  zero ORC with a full noun-phrase subject, a stacked or nominalized head noun,
  nesting inside a prepositional phrase, and a clause-final verb.
- The user's complaint is the **verb's position**, not the missing "that".
  Adding "that" back does not fix it.

## 3. Evidence this is an LLM trait

**Clark, T. H., Martin, M. B., & Mahowald, K. (2026). "Why is AI-generated
language so hard to understand?" arXiv:2610.29162.**
https://arxiv.org/abs/2610.29162

- Compared with human writing, most frontier models use longer dependencies,
  more stacked nouns and more reduced ORCs, especially in conversation. They
  also overuse inanimate subjects with animate verbs, denominal verbs and
  low-frequency n-grams.
- Compared with paraphrases of their own output, frontier models overuse
  reduced ORCs and underuse ORCs with "that", which suggests a preference for
  dropping optional words.
- The effect grows from base to instruct to "think" models. The authors'
  hypothesis is that post-training rewards correctness and information density
  over clarity, together with context limits. A length-penalty experiment on a
  small model produced a strong preference for the shorter alternation.
- Their feature list is a ready-made list of candidate constructions, and their
  round-trip paraphrase method is a way to separate model preference from
  register.

Also relevant: Reinhart et al., "Do LLMs write like humans? Variation in
grammatical and rhetorical styles" (arXiv:2410.16107, *PNAS* 2025).
Instruction tuning amplifies grammatical differences, and nominalizations
appear at 1.5 to 2 times the human rate.

## 4. The patch: `adv1-object-relative.patch`

The user has this file. It applies to `jeffnye-gh/adv1`, built against commit
`c0d95d4`. Apply it alone. Two earlier patch files from the discussion are
superseded and should not be applied.

```bash
git checkout jeffnye-gh/adv1
git apply --check adv1-object-relative.patch
git apply adv1-object-relative.patch
pip install lemminflect        # optional, for rewrite suggestions
make regress
```

**`tools/tests.py` has NOT been run.** The detectors were extracted with `ast`
and run against the exact new rows of `CASES`, `PATTERN_CASES` and
`SUGGESTION_CASES` on `en_core_web_md`: 48 checks, 0 failures. The full suite,
`jsoncheck`, `harvest` and `arxiv_recheck` interactions are unverified, so run
`make regress` first. If the patch does not apply, regenerate it against
current `adv1`.

### What it adds

**`TRAILING_LIGHT_VERB`** (med). A nominalized action closed by a light verb
(make, do, perform, execute, issue, conduct) with no object of its own:
"the array write the last primitive made". Collocations such as "the decision
the team made" report as low. Known false positive: "make" meaning "create"
("the tests the team made").

**`OBJECT_RELATIVE`** (base low), with two patterns:

- `zero_object_relative`: "every variable the loops assign". Graded by load,
  one point each for:
  - **nested**: the head follows a preposition
  - **stacked**: a noun modifies the head, or the head was tagged as a verb
    (a nominalization)
  - **long**: the clause subject is three or more tokens
  - **final**: the verb ends the sentence or clause

  A load of 2 or more reports at med, otherwise low.
- `that_object_relative`: "every variable that the loops assign". Always low.

Both patterns skip pronoun subjects ("the file you sent"), adverbial heads
(way, time, day, reason, ...) and light verbs, which belong to
`TRAILING_LIGHT_VERB`.

**Rewrite suggestions.** `OBJECT_RELATIVE` sets `span._.tf_suggestion` to a
reduced passive ("every variable assigned by the loops"), using lemminflect's
`getInflection(lemma, tag="VBN")`. `analyse()` copies it into a new
`Finding.suggestion` field, which is shown as `try: ...` in the terminal
report, on the HTML card and in `--json`. It is **not** part of the
fingerprint, so waivers are unaffected. No suggestion is made for stranded
prepositions, verbs with no natural passive (`_NO_PASSIVE`: have, lack, cost,
contain, ...) or "by" phrases longer than 5 tokens. Without lemminflect the
findings still report and the suggestion tests are skipped.

Also in the patch: test rows in `tests.py`, two README table rows, and README
install notes for lemminflect.

### Design decision: surface POS, not the dependency parse

This is the most important finding. **spaCy misparses exactly the sentences
that matter.** On "Note the count of the array write the last primitive made",
both `sm` and `md` tag "write" as a verb and attach the clause's subject as its
object, so `relcl` never appears. "Check every register the decode stage
writes" gets no `relcl` on either model. spaCy also labels "that" in ORCs
inconsistently (`mark` or `dobj`), and it got "the dog that the man bit"
entirely wrong.

So both detectors match a POS sequence instead:

```
DET [ADJ|NOUN]* HEAD [that|which]? DET [ADJ|NOUN]* NOUN VERB (no object follows)
```

They also include guards for misreads with the same tags, each covered by a
test:

- A main verb must exist outside the span ("In the end the team decided").
- A subordinator with no comma is skipped ("When the build finishes the tests
  run").
- "whose" or "which" in the subject's DET slot is skipped.
- A verb-tagged head must be base form (VB/VBP); "A normal run counts ..." is
  rejected.
- A verb-tagged head after a noun needs a past-tense clause verb
  ("The 155 JSON rows match the report rows").
- A VBN followed by "by" or preceded by an auxiliary is a real participle.
- Bare-noun time adverbs after the verb are allowed ("wrote yesterday").

On `sm`, 3 positive cases fail, which is acceptable because the project uses
`md`.

### Precision check done so far

`zero_object_relative` was run over about 25,000 words of the repo's own prose:
samples, README, roadmap, competitive review, glossary, TF-008 and TF-009. This
text is treated as human-written. After the two fixes it produced 7 findings,
all of them real ORCs, for example "the papers the pilot walked", "a citation
line the masker left" and "the ones the two manuals \input" in TF-009 (med).
**No measurement has been made on LLM text yet.**

## 5. Known gaps

- **Verbs after an auxiliary.** The RAS comment "a pop the p3 type does not
  have" is not flagged, because only finite VBD/VBP/VBZ/VBN verbs are checked.
  Add ORCs whose verb follows does/did/can/will (+ not).
- **As-parentheticals.** "as the planning documents use" is a transitive verb
  in an "as" clause with no object. A narrow rule could catch it: an as-clause
  whose verb normally needs an object. Verbs like know, say and expect allow
  the gap naturally ("as you know") and must be excluded.
- **Position in general.** `OBJECT_RELATIVE` scores load heuristically. A
  dependency-distance measure (TextDescriptives) or per-token surprisal would
  quantify "the verb is too far away" directly.
- **Comments in code.** The masker blanks code, so source comments are not
  checked today. That needs a comment extractor that maps findings back to
  file and line, plus an LLM second pass for cases the rules miss.

## 6. Suggested next work (for the session with the corpora)

1. **Apply and regress** the patch. Fix anything the full suite finds.
2. **Measure on real LLM text.** Run on the pacino blogs, then add the
   findings to the harvest labels. Compare precision for each pattern and load
   level: are med findings the ones that get rewritten?
3. **Before/after rates on arXiv** (TF-004/005/008 machinery). Rate per 1,000
   words for `zero_object_relative`, `that_object_relative` and
   `TRAILING_LIGHT_VERB` in pre-LLM versus post-LLM `cs.AR`, and against the
   TF-009 spec baseline. Clark et al. predict a rising zero:that ratio. That
   ratio may be a better signal than either count, because it controls for
   register. Use the roadmap's likelihood-ratio approach (step 8) to set
   confidence.
4. **Harvest gap.** `harvest.py` labels only sentences a detector already
   flagged. Diff drafts against edited text for sentences that nothing flagged
   but the user rewrote, to feed roadmap 5.5 (subtree mining) with real
   examples.
5. **Parse agreement (roadmap 5.6).** Test `en_core_web_trf` on the CASES rows
   above. If it parses them correctly, a dependency-based path could raise
   precision.
6. **Surprisal prototype.** Use minicons (`scorer.IncrementalLMScorer`, a small
   pinned GPT-2-class model) on masked text, scoring per-token spikes relative
   to the sentence mean. A first test: do rewritten sentences in
   `labels.jsonl` show bigger spikes than accepted ones? Use it to rank
   candidates, not as a calibrated score. Surprisal finds where garden paths
   are but underestimates how hard they are (van Schijndel & Linzen 2021;
   Arehalli et al. 2022). Pin the model as spaCy models are pinned.
7. **Close the gaps in section 5**, each with CASES rows first.
8. **Upstream prevention.** Add construction names plus before/after examples
   to the CLAUDE.md used when generating prose and comments.

## 7. Working preferences observed

- The user wants plain explanations of linguistic terms alongside the
  technical ones.
- Findings are suggestions for a human to accept, not automatic rewrites. Keep
  "the flag means look, not delete".
- Prefer measured precision on real text over intuition, and record null
  results, as the adv1 branch already does.

## References

- Clark, Martin & Mahowald (2026), arXiv:2610.29162. https://arxiv.org/abs/2610.29162
- Reinhart et al. (2025), "Do LLMs write like humans?" https://arxiv.org/abs/2410.16107
- Hale (2001), surprisal. https://aclanthology.org/N01-1021/
- Levy (2008), expectation-based comprehension. https://escholarship.org/uc/item/66v7520b
- van Schijndel & Linzen (2021), *Cognitive Science* 45:e12988. https://tallinzen.net/media/papers/van_schijndel_linzen_2021_cognitive_science.pdf
- Arehalli, Dillon & Linzen (2022), CoNLL. https://aclanthology.org/2022.conll-1.20
- minicons: https://pypi.org/project/minicons/
- TextDescriptives dependency distance: https://hlasse.github.io/TextDescriptives/dependencydistance.html
- benepar (constituency parser for spaCy): https://github.com/nikitakit/self-attentive-parser
- lemminflect (verb inflection for spaCy): https://pypi.org/project/lemminflect/
- Style background: Williams, *Style: Lessons in Clarity and Grace*; Pinker,
  *The Sense of Style*; Huddleston & Pullum, *A Student's Introduction to
  English Grammar*.
