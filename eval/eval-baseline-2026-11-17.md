# ticfinder false-positive baseline (2026-11-17)

Source: pacino git history. For the 7 blogs with waiver files, the first committed draft was compared against the published version using the current ticfinder (`eval/harvest.py`).

- accepted = finding in published text and waived (editor judged it OK): **142** (first written as 125, a miscount; corrected in TF-001)
- removed, rewritten = finding gone, and a similar sentence (ratio >= 0.6) survives: **47**
- removed, deleted = sentence gone entirely (ambiguous evidence): **312**

## Where accepted findings come from
| construction/pattern | rewritten | accepted | prec* |
|---|---|---|---|
| TRICOLON tricolon | 17 | 84 | 0.17 |
| ALTERNATIVE_FRAMING rather/instead | 11 | 19 | 0.37 |
| PARTICIPIAL_TAIL | 6 | 9 | 0.40 |
| CORRECTIVE_CONTRAST negated_apposition | 0 | 8 | 0.00 |
| ALTERNATIVE_FRAMING less_than | 2 | 5 | 0.29 |
| CORRECTIVE_CONTRAST coordinated | 0 | 5 | 0.00 |
| EM_DASH | 6 | 0 | 1.00 |

prec* = rewritten / (rewritten + accepted)

## Findings
- TRICOLON produces 59% of accepted findings (84 of 142). Its figure/list-like/enumeration label does not discriminate here: list-like accounts for 52 of 84 accepted and 13 of 17 rewritten.
- First licensing hypothesis tested, **null result**: the fraction of a finding's content lemmas that recur elsewhere in the document does not separate accepted from rewritten findings, for any construction. Technical prose reuses its vocabulary everywhere. Licensing has to be specific to the role (the negated X, the rejected alternative, the list members) rather than a bag of words.
- The history supplies plenty of negatives but few clean positives. More labels are needed: a direct labeling pass by the author, and pre-LLM specifications as a human-register baseline.
