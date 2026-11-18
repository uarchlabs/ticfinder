# TRICOLON referent score: a null result (TF-003 phase 2)

## Hypothesis

Accepted `TRICOLON` findings are mostly lists of referents (identifiers,
named components, defined terms). Rewritten ones are mostly lists of
qualities ("simpler, faster, and easier to debug"). A per-member
referent score should separate them better than the current
`figure`/`list-like`/`enumeration` label (roadmap 5.2).

## Method

Every `tricolon` row in `eval/labels.jsonl` (84 accepted, 19 rewritten,
136 deleted) was matched back to its series by re-parsing the document
version it came from. All 239 matched. Each member was scored as a
referent when it holds inline code or an identifier shape (underscore,
digit, mixed case), when its head is a proper noun or a named entity, when
it holds a number or quantity, or when its noun phrase recurs word for word
elsewhere in the document. It was scored as a quality when its head is an
adjective or adverb, or a noun phrase that appears once. The score is the
share of referent members. The scoring script lived in the scratchpad.
No detector code was changed.

Two readings of "member" were fixed before looking at the result:

- **A, as specified**: the member's whole subtree.
- **B, core phrase**: the head plus its compound, modifier, number and
  possessive children. A clause member (verb head) is not a referent.

## Results

| measure | accepted | rewritten |
|---|---|---|
| mean score, A | 0.55 | 0.56 |
| mean score, B | 0.36 | 0.21 |

AUC is the chance that a random accepted finding scores higher than a
random rewritten one; 0.5 is no separation.

| score | AUC |
|---|---|
| current label (figure < list-like < enumeration) | 0.53 |
| referent score A | 0.49 |
| referent score B | 0.61 (bootstrap 95% interval 0.47 to 0.72) |
| B within noun-phrase series only (40 accepted, 4 rewritten) | means 0.64 vs 0.62 |
| one flag: the series has no clause members | 0.63 |

Cuts on score B: at 0.4 or more, 31 of 84 accepted and 3 of 19 rewritten
would move to a referent label. The findings left behind would have
prec* 0.23, against 0.18 now. At 0.01 or more, the counts are 49 and 8.
Under A, every cut moves rewritten and accepted findings in about the
same proportion.

## Reading

- As specified, the score carries no signal. Clause members such as "TC-81
  failed before and passed after" contain identifiers, so they score as
  referents. The rewritten findings in the pacino blogs are full of
  identifiers too: ticket numbers, signal names, defect ids.
- Under B, all of the gain comes from one distinction: noun lists against
  clause lists. Within noun lists the referent score does not separate
  accepted from rewritten. The flag "no clause members" alone does as well
  as B (0.63). 15 of the 19 rewritten findings are clause or mixed series,
  against 44 of 84 accepted.
- 19 rewritten labels are too few for this to be firm. The B interval
  includes 0.5.

## Decision

No code change. Without a new label or pattern, no finding changes its
fingerprint and no waiver moves.

## Lead for a later task

The clause-versus-noun split was found after looking at the data, so it is
a new hypothesis and has not been tested. Clause series hold 15 of 19
rewritten and 44 of 84 accepted (prec* 0.25), and noun series hold 4 and
40 (prec* 0.09). It needs fresh labels before it can be trusted, either
from new waivers and rewrites or from the labelling UI (roadmap 5.1).
