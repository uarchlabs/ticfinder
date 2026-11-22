# Glossary

Terms used in the ticfinder roadmap, task files and notes, grouped by
where they come from. Table 1 holds standard terms. Table 2 holds
ticfinder's own terms, often an ordinary word with a stretched meaning. Table 3 holds terms coined in TF-003 to TF-009, which have no
meaning outside this project.

## Table 1. Standard terms, used in their usual sense

| term | meaning |
|---|---|
| register | the kind of writing, such as specs, papers or blogs; each has its own normal habits |
| referent | the actual thing a word or phrase points to, like a signal or a table |
| conjunct, coordination | the items joined by "and" or "or", and the joining itself |
| apposition | a noun phrase that renames the one before it: "Postgres, the primary store," |
| participial adjunct | a trailing "-ing" phrase: ", making it faster" |
| emphatic reflexive | "the document itself" |
| clause | a group of words with its own verb: "TC-81 failed" |
| noun phrase | a noun and the words that modify it: "the stored final-target field" |
| tricolon, isocolon, antithesis | figures from classical rhetoric: a three-part series, parallel members of equal length, a contrast of opposites |
| dependency parse | spaCy's analysis of which word attaches to which |
| AUC | the chance that a randomly chosen item from one class scores higher than one from the other; 0.5 means no separation |
| bootstrap | estimating an interval by resampling the data many times |
| likelihood ratio | how much more often something occurs in one corpus than in another |
| Poisson, scan statistic | a model for counts of rare events, and a test for an unusual cluster of them in a window |
| primary category, cross-listed | arXiv files each paper under one primary category; a cross-listed paper names `cs.AR` only as a secondary category |
| first-version (v1) date | when a paper's first version was submitted; the date that places a paper in a window |
| OAI-PMH | a standard protocol for harvesting repository metadata; arXiv offers it next to its search API |
| percentile interval | a bootstrap interval made from the 2.5th and 97.5th percentiles of the resampled values |
| paired bootstrap | resampling the same papers for two measurements, so their difference keeps its pairing (planned for TF-005) |
| manner adverb | an adverb that says how or how much a verb happened: "the writes drop significantly, about 73%" |
| sentence adverb | an adverb that comments on the whole clause after it: "Significantly, the cache never misses." `HOLLOW_BOOSTER` looks for these |
| transitive, intransitive | a verb with a direct object ("passing the depth"), and one without ("posing as a refactor") |
| reflexive pronoun | a "-self" pronoun that refers back to the subject: "passing itself off as evidence" |
| passive | a clause whose subject receives the action: "the value is passed as an argument" |
| particle | the small word of a phrasal verb: the "off" in "passed off as" |
| lookbehind | a match condition on the text before the match; spaCy's Matcher has none, so a pattern can only test tokens inside its own span |

## Table 2. Project terms: borrowed words with a ticfinder meaning, defined in CLAUDE.md or the roadmap

| term | definition | caution |
|---|---|---|
| construction | a named thing ticfinder reports, such as `TRICOLON`; the id users mute and counts are reported against | construction grammar in linguistics gives the word a stricter meaning |
| pattern | one executable query for one surface form of a construction | |
| licensing, "earned" | the context justifies a construction, so it is not a tic | linguistics uses "licensing" for something narrower and technical; this is a loose extension |
| `TRICOLON` | any coordination of three or more items | wider than the rhetorical tricolon, which is a deliberate three-part figure |
| `figure`, `list-like`, `enumeration` | ticfinder's labels for how rhetorical a list looks, from an enumeration score | invented; roadmap section 4 showed they do not separate kept from rewritten findings, but on arXiv they diverge: `list-like` and `enumeration` rose and `figure` was flat (roadmap section 11) |
| `CORRECTIVE_CONTRAST` | "X, not Y" and its variants | close to an existing linguistics term |
| `ALTERNATIVE_FRAMING`, `NEG_ESCALATION`, `BORROWED_RIGOUR`, `GAPPED_ANTITHESIS` | names for patterns ticfinder reports | invented names |
| prec* | rewritten / (rewritten + accepted) | a stand-in for precision, not true precision: deleted sentences are left out as ambiguous |
| accepted, rewritten, deleted | what `harvest.py` infers from the edit history: waived and kept, gone with a similar sentence surviving, gone with its sentence | inferred from edits, so a label can be wrong |
| masking | blanking non-prose text in place, keeping offsets, before parsing | |
| subtype | the bracketed tail of a finding's label, without the member-count field: `[3-part NOUN, list-like]` gives `list-like` | the rule is in `harvest.py`'s `subtype()`; a plain comma split would break `[X, not Y]` |
| rate | findings per 1,000 words, pooled: total findings over total words | long documents weigh more; TF-005 adds the mean of per-paper rates |
| ratio | post-window rate over pre-window rate | it measures change over time, not a likelihood ratio between LLM and human text |
| phrase construction | a construction defined by token patterns, built in (`PHRASE_PATTERNS`) or from the phrase file, rather than by a parse function | its patterns carry no pattern name; since TF-006 its test rows run through `analyse()` |
| fingerprint | the short hash that identifies a finding for waivers, over construction, pattern, matched text and sentence | widening a span changes it; offsets and line numbers are never part of it |
| waiver, stale waiver | a fingerprint the editor marked as acceptable; stale when no current finding matches it | a detector fix can make a waiver stale without invalidating it; `--prune-stale` removes it |
| all sections, body sections | in TF-005, all four section types together, against the `body` section type alone | the TF-005 `HOLLOW_BOOSTER` ratio 3.31 is body sections; all sections give 2.98 |

## Table 3. Terms from TF-003 to TF-009 with no outside standing

| term | meaning | where |
|---|---|---|
| referent score | the share of a list's items that name real things (identifiers, proper nouns, numbers, recurring noun phrases) | roadmap 5.2, TF-003 phase 2 |
| quality member | a list item that describes rather than names ("faster", "simpler"); the referent/quality split is the project's idea, not a linguistics category | roadmap 5.2, TF-003 phase 2 |
| `catalog` | a proposed subtype label for lists of referents; never built | TF-003 option (a) |
| excess constructions | constructions whose rate rose after LLMs; coined by analogy with "excess words" in Kobak et al. | roadmap section 6, TF-004 |
| core phrase | the main word of a list item plus its modifiers, without clauses attached to it | TF-003 phase 2, variant B |
| variant A, variant B | two readings of "list member" in the referent test: the whole subtree, and the core phrase | TF-003 phase 2 |
| clause series, noun series | lists whose items are whole clauses, against lists of noun phrases | TF-003 phase 2 |
| clause-list hypothesis | untested: rewritten `TRICOLON` findings are mostly clause series, accepted ones mostly noun series | TF-003 phase 2, lead for a later task |
| code part | the part of a line before a trailing `//` or `#` comment | TF-003 phase 1 |
| DSL line | a line of the form `name : obj.call(arg)` | TF-002, TF-003 phase 1 |
| pre window, post window | primary `cs.AR` papers with v1 dates 2018-01-01 to 2021-12-31, and 2025-01-01 to the latest date in the fetch | TF-004 |
| `rose`, `flat`, `fell`, `too few` | the verdict on a ratio: interval above 1, includes 1, below 1, or under 20 findings in total | TF-004 report |
| em dash proxy | TeX `---` and spaced ` -- ` counted in place of Unicode em dashes, which the API's ASCII abstracts don't contain | TF-004 |
| id year | the year from an arXiv id's YYMM prefix, used to date papers in the completeness check | TF-004 `check` |
| sanity reading | reading 20 random findings per window and counting the real instances | TF-004, TF-005 |
| text type | where the counted text comes from: abstract, introduction, body, conclusion or related work | TF-005 draft |
| ratio of ratios | a construction's body ratio over its abstract ratio | TF-005 draft |
| recheck | rerunning stored arXiv findings under the committed and the new detector, each stored sentence parsed on its own (`eval/arxiv_recheck.py`) | TF-006 |
| isolated parse | parsing one stored sentence without the rest of its document; it reproduced 69 of 71 and 282 of 282 stored findings | TF-006 |
| reproduced | a stored finding that the old code gives again, with the same matched text, on the isolated sentence | TF-006 |
| kept, dropped | a reproduced finding that a new span still covers, and one that no new span covers | TF-006 |
| covering span | a new span that contains the old one, as `More significantly,` contains `significantly,`; it counts as kept | TF-006 phase 2 |
| adjusted rate, adjusted ratio | kept findings over the words in the private per-paper tables, and its post over pre ratio; a point estimate | TF-006 |
| scaled rate | the stored count times kept over reproduced, over the same words; it corrects for findings the isolated parse misses | TF-006 |
| `as` frame | an `as` phrase on `pose` or `pass`; it counts as a disguise only when the verb is intransitive, reflexive or has `off` | TF-006 phase 1 |
| anchored pattern | a pattern whose first token must start a sentence (`IS_SENT_START`); without lookbehind, the anchor word sits in the span | TF-006 phase 2 |
| interim rule | sets a confidence from arXiv ratios until calibration: `med` when the interval lies above 1 in both TF-004 abstracts and TF-005 bodies, each with at least 20 findings; never more than one level above the construction | roadmap section 14, TF-007 |
| rename map | `RENAMED_PATTERNS` in `ticfinder.py`, new pattern name to old; `--migrate-waivers` uses it to rekey waivers written under the old name | TF-007 phase 1 |
| old-style id | a waiver id computed the old way: the sentence cut at 240 characters, an old pattern name, or both; a normal run counts them and `--migrate-waivers` rekeys them | TF-001, TF-007 phase 1 |
| per-finding confidence | a level a detector returns with one finding, overriding its pattern and construction | TF-007 phases 1 and 2 |
| instrumental tail | a participial tail that names the method, data or tool (`, using a 4-bit counter`); against a restating tail, which repeats the main clause | TF-007 phase 2 |
| per-phrase confidence | a level set on one phrase-file entry with `{"phrase": ..., "confidence": ...}` | TF-007 phase 3 |
| per-form override | a level set on one matched text, lowercased, of a lemma entry, through the entry's `forms` | TF-007 phase 3 |
| matched text | a phrase finding's text, whitespace-normalised and lowercased; the key of the TF-004 phrase rows and of `forms` | TF-004, TF-007 phase 3 |
| pilot | the TF-005 body run: the first 200 usable papers per window | TF-005, TF-008 |
| full run | the TF-008 body run: every usable pre paper (778) and as many post papers, walked in the same shuffle as the pilot | TF-008 |
| pilot subset | the pilot's 400 papers taken from the full run's tables and bootstrapped with the pilot's seed; its rows differ from the pilot report only where code changed | TF-008 phase 3 |
| prefix check | confirming that the pilot's kept papers are the first 200 kept in each full window, in order, with the same skip reasons | TF-008 phase 2 |
| code effect, sample effect | a change in a row caused by a detector change, against one caused by measuring more papers | TF-008 phase 3 |
| width ratio | a ratio interval's width over another's, both on the log scale; sampling 3.9 times the papers predicts about 0.51 | TF-008 phase 3 |
| pinned rebuild | rewriting a report from a stored table written by an earlier ticfinder, named by its sha256 prefix with `--table-sha` | TF-008 phase 1 |
| JSON summary | the numbers of a report or of the harvest summary as one JSON object, schema 1, for step 8 to read (`--json`) | TF-008 phase 1 |
| public baseline | the pre-2022 design and spec corpus of TF-009: PEPs, IETF RFCs, Rust RFCs, the RISC-V manuals and the OpenTitan hardware docs, dated 2018 to 2021 | roadmap section 16, TF-009 |
| source | one of the five public baseline collections; each has its own exclusions and its own index matrix in the bootstrap | TF-009 |
| pool | the five sources together; a pooled rate by words is total findings over total words | TF-009 |
| equal-weight pool | the mean of the five source rates, so each source counts once whatever its size; the rate TF-009 compares against | TF-009 |
| exclusion | a per-source masking rule that blanks non-prose text in place before ticfinder's own masking, such as RFC page furniture or PEP literal blocks | TF-009 phase 2 |
| table file | a RISC-V chapter whose markup is over 80% table, figure or verbatim environments, blanked whole | TF-009 phase 2 |
| residue | markup or code left in kept text after masking, counted in a spot-check of 40 random sentences per source | TF-005, TF-009 |
