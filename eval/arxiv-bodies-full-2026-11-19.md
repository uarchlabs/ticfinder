# ticfinder construction rates in arXiv cs.AR paper bodies, full run

Generated 2026-11-21 by `eval/arxiv_bodies.py` (TF-008). Aggregates only: no paper text, titles or ids. Ratios are rates over two periods (post over pre), not likelihood ratios.

## Setup

| item | value |
|---|---|
| papers | TF-004 primary `cs.AR` sets (month manifests); windows by v1 date: pre 2018-01-01 to 2021-12-31, post 2025-01-01 to the latest TF-004 date |
| sample | each window's ids shuffled with seed `20261118-bodies-<window>` and walked in order: every pre id, then post until it kept as many papers with usable LaTeX source as pre kept. The pilot's papers are the first 200 kept in each window |
| source | `export.arxiv.org/e-print/<id>v1` (the v1 source, so a body cannot hold a later revision), 3.5 s between requests |
| abstracts | the same papers' API abstracts (latest version, as in TF-004), masked with the TF-004 masker |
| ticfinder | `tools/ticfinder.py` at 651302d (sha256 81ade1e30516); defaults: `en_core_web_md`, code masker on, `ticfinder-phrases.json`; text analysed as `.txt` |
| LaTeX masker | `arxiv_bodies.py`, blanks in place: preamble, comments, back matter (bibliography and appendices), math, floats and code with captions, references, labels, URLs, footnotes, headings, command names (text commands keep their argument), `\item` markers, the abstract and acknowledgements. TeX `---` becomes U+2014 and two spaces. `selftest` holds its rows |
| sections | A section runs from its \section heading to the next one. The first section, or any heading containing "introduction", is introduction. Otherwise a heading containing "conclusion", "summary" or "future work" is conclusion, and one containing "related work", "background" or "prior work" is related. Everything else is body. Matching ignores case. Text between \begin{document} and the first \section (after the title, abstract and keywords are masked) counts as introduction, since an unheaded opening is the introduction; a paper with no \section is all introduction. Findings are assigned to a section by offset |
| bootstrap | 2000 draws over papers, seed 8008; one index matrix per window shared by every text type, so comparisons between text types are paired; percentile 95% intervals (nearest rank for ratios) |
| rates | pooled: total findings / total words x 1,000; mean: the mean of per-paper rates over papers with words in that text type. Words are alphabetic spaCy tokens after masking |

## Sample and masking

| measure | pre | post |
|---|---|---|
| TF-004 primary papers | 955 | 2627 |
| walked / kept | 955 / 778 | 866 / 778 |
| skipped: no source | 1 | 0 |
| skipped: PDF only | 158 | 62 |
| skipped: no main file found | 0 | 24 |
| skipped: unpack error | 0 | 0 |
| skipped: other format | 0 | 0 |
| skipped: too little text | 16 | 2 |
| skipped: placeholder text | 2 | 0 |
| masked share, all non-space characters | min 14.5%, median 47.6%, max 96.9%; 532 over 40% | min 10.0%, median 48.5%, max 94.1%; 565 over 40% |
| masked share inside the kept body | min 4.0%, median 30.4%, max 93.8%; 134 over 40% | min 4.8%, median 33.2%, max 93.6%; 203 over 40% |
| several main-file candidates (longest expanded text kept) | 66 | 11 |
| papers with no `\section` | 6 | 3 |
| unresolved `\input` / `\include` | 96 | 44 |
| TeX `---` in kept text | 724 | 1626 |
| spaced ` -- ` in kept text | 786 | 829 |
| Unicode em dash in kept text | 10 | 1336 |
| Unicode en dash in kept text | 45 | 1161 |
| ticfinder masked_pct, mean per paper | 0.05% | 0.04% |
| findings outside any section | 0 | 1 |
| papers where section words do not sum to ticfinder's count | 0 | 0 |

## Words per text type

| text type | pre words | pre papers with text | post words | post papers with text |
|---|---|---|---|---|
| abstract | 148,862 | 778 | 149,941 | 778 |
| introduction | 665,137 | 777 | 547,211 | 777 |
| body | 3,583,793 | 765 | 2,723,016 | 773 |
| related | 562,843 | 546 | 437,113 | 563 |
| conclusion | 163,915 | 716 | 121,417 | 740 |
| all | 4,975,688 | 778 | 3,828,757 | 778 |

Mean paper length, all sections, words (95% interval): pre 6,395 (6,006 to 6,824), post 4,921 (4,736 to 5,101).

Mean abstract length, words (95% interval): pre 191 (187 to 195), post 193 (189 to 196).

## `EM_DASH` per text type

| text type | pre n | pre rate (95% CI) | post n | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|
| abstract | 0 | 0.00 (0.00 to 0.00) | 0 | 0.00 (0.00 to 0.00) | - (- to -) | too few |
| introduction | 142 | 0.21 (0.15 to 0.29) | 611 | 1.12 (0.93 to 1.30) | 5.23 (3.68 to 7.69) | rose |
| body | 505 | 0.14 (0.10 to 0.19) | 2537 | 0.93 (0.76 to 1.12) | 6.61 (4.72 to 9.80) | rose |
| related | 105 | 0.19 (0.11 to 0.28) | 430 | 0.98 (0.80 to 1.19) | 5.27 (3.38 to 9.23) | rose |
| conclusion | 19 | 0.12 (0.05 to 0.19) | 173 | 1.42 (1.07 to 1.80) | 12.29 (6.93 to 26.99) | rose |
| all | 771 | 0.15 (0.11 to 0.20) | 3751 | 0.98 (0.82 to 1.15) | 6.32 (4.61 to 8.96) | rose |

## Abstract against body

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | body n pre / post | body ratio (95% CI) | body over abstract (95% CI) | body ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 103 / 123 | 1.19 (0.89 to 1.56) | 1690 / 2104 | 1.64 (1.48 to 1.83) | 1.38 (1.05 to 1.85) | no |
| `ALTERNATIVE_FRAMING` | 117 / 138 | 1.17 (0.90 to 1.51) | 3741 / 3135 | 1.10 (1.01 to 1.21) | 0.94 (0.72 to 1.23) | yes |
| `BORROWED_RIGOUR` | 46 / 51 | 1.10 (0.70 to 1.68) | 694 / 748 | 1.42 (1.18 to 1.73) | 1.29 (0.83 to 2.06) | yes |
| `CONSULTANT_REGISTER` | 245 / 336 | 1.36 (1.13 to 1.64) | 2407 / 2638 | 1.44 (1.25 to 1.67) | 1.06 (0.87 to 1.28) | yes |
| `CORRECTIVE_CONTRAST` | 33 / 26 | 0.78 (0.45 to 1.34) | 910 / 1064 | 1.54 (1.31 to 1.79) | 1.97 (1.14 to 3.48) | no |
| `LLM_DICTION` | 440 / 541 | 1.22 (1.06 to 1.42) | 4426 / 4341 | 1.29 (1.16 to 1.45) | 1.06 (0.91 to 1.23) | yes |
| `PARTICIPIAL_TAIL` | 293 / 834 | 2.83 (2.47 to 3.28) | 4277 / 11535 | 3.55 (3.26 to 3.89) | 1.26 (1.08 to 1.45) | no |
| `TRICOLON` | 626 / 909 | 1.44 (1.29 to 1.61) | 11012 / 11584 | 1.38 (1.29 to 1.48) | 0.96 (0.86 to 1.07) | yes |
| `VAGUE_QUANTIFIER` | 135 / 113 | 0.83 (0.65 to 1.05) | 539 / 394 | 0.96 (0.79 to 1.17) | 1.16 (0.87 to 1.58) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 / 82 | 0.96 (0.70 to 1.32) | 2668 / 1195 | 0.59 (0.53 to 0.65) | 0.62 (0.45 to 0.84) | no |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 / 22 | 0.75 (0.42 to 1.32) | 685 / 712 | 1.37 (1.19 to 1.57) | 1.82 (1.01 to 3.25) | no |
| `TRICOLON / tricolon` | 626 / 909 | 1.44 (1.29 to 1.61) | 11009 / 11582 | 1.38 (1.29 to 1.48) | 0.96 (0.86 to 1.07) | yes |

7 of 12 rows have the body ratio inside the abstract interval.

## Introduction against body

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | introduction n pre / post | introduction ratio (95% CI) | body n pre / post | body ratio (95% CI) | body over introduction (95% CI) | body ratio inside introduction interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 501 / 555 | 1.35 (1.16 to 1.56) | 1690 / 2104 | 1.64 (1.48 to 1.83) | 1.22 (1.04 to 1.43) | no |
| `ALTERNATIVE_FRAMING` | 570 / 540 | 1.15 (0.98 to 1.34) | 3741 / 3135 | 1.10 (1.01 to 1.21) | 0.96 (0.82 to 1.13) | yes |
| `BORROWED_RIGOUR` | 240 / 176 | 0.89 (0.68 to 1.17) | 694 / 748 | 1.42 (1.18 to 1.73) | 1.59 (1.19 to 2.12) | no |
| `CLOSER` | 82 / 68 | 1.01 (0.72 to 1.39) | 214 / 194 | 1.19 (0.93 to 1.53) | 1.18 (0.80 to 1.77) | yes |
| `CONSULTANT_REGISTER` | 866 / 1092 | 1.53 (1.34 to 1.76) | 2407 / 2638 | 1.44 (1.25 to 1.67) | 0.94 (0.82 to 1.09) | yes |
| `CORRECTIVE_CONTRAST` | 219 / 242 | 1.34 (1.08 to 1.67) | 910 / 1064 | 1.54 (1.31 to 1.79) | 1.15 (0.90 to 1.46) | yes |
| `EMPHATIC_REFLEXIVE` | 84 / 77 | 1.11 (0.79 to 1.54) | 400 / 355 | 1.17 (0.95 to 1.45) | 1.05 (0.73 to 1.53) | yes |
| `EM_DASH` | 142 / 611 | 5.23 (3.68 to 7.69) | 505 / 2537 | 6.61 (4.72 to 9.80) | 1.26 (0.87 to 1.76) | yes |
| `HOLLOW_BOOSTER` | 44 / 64 | 1.77 (1.20 to 2.62) | 166 / 451 | 3.58 (2.89 to 4.56) | 2.02 (1.34 to 3.18) | no |
| `LLM_DICTION` | 1496 / 1919 | 1.56 (1.41 to 1.72) | 4426 / 4341 | 1.29 (1.16 to 1.45) | 0.83 (0.74 to 0.93) | no |
| `PARTICIPIAL_TAIL` | 1055 / 2851 | 3.28 (2.96 to 3.66) | 4277 / 11535 | 3.55 (3.26 to 3.89) | 1.08 (0.99 to 1.18) | yes |
| `TRICOLON` | 2612 / 3115 | 1.45 (1.35 to 1.56) | 11012 / 11584 | 1.38 (1.29 to 1.48) | 0.96 (0.89 to 1.03) | yes |
| `VAGUE_QUANTIFIER` | 405 / 400 | 1.20 (1.03 to 1.38) | 539 / 394 | 0.96 (0.79 to 1.17) | 0.80 (0.65 to 0.99) | no |
| `ALTERNATIVE_FRAMING / af_instead_of` | 107 / 76 | 0.86 (0.62 to 1.19) | 721 / 478 | 0.87 (0.74 to 1.02) | 1.01 (0.71 to 1.43) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 389 / 218 | 0.68 (0.54 to 0.85) | 2668 / 1195 | 0.59 (0.53 to 0.65) | 0.87 (0.70 to 1.09) | yes |
| `ALTERNATIVE_FRAMING / af_rather_than` | 74 / 246 | 4.04 (3.09 to 5.48) | 352 / 1462 | 5.47 (4.48 to 6.68) | 1.35 (0.99 to 1.81) | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 176 / 201 | 1.39 (1.11 to 1.75) | 685 / 712 | 1.37 (1.19 to 1.57) | 0.99 (0.77 to 1.27) | yes |
| `TRICOLON / tricolon` | 2612 / 3115 | 1.45 (1.35 to 1.56) | 11009 / 11582 | 1.38 (1.29 to 1.48) | 0.96 (0.89 to 1.03) | yes |

13 of 18 rows have the body ratio inside the introduction interval.

## Abstract against introduction

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | introduction n pre / post | introduction ratio (95% CI) | introduction over abstract (95% CI) | introduction ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 103 / 123 | 1.19 (0.89 to 1.56) | 501 / 555 | 1.35 (1.16 to 1.56) | 1.14 (0.86 to 1.51) | yes |
| `ALTERNATIVE_FRAMING` | 117 / 138 | 1.17 (0.90 to 1.51) | 570 / 540 | 1.15 (0.98 to 1.34) | 0.98 (0.75 to 1.29) | yes |
| `BORROWED_RIGOUR` | 46 / 51 | 1.10 (0.70 to 1.68) | 240 / 176 | 0.89 (0.68 to 1.17) | 0.81 (0.53 to 1.26) | yes |
| `CONSULTANT_REGISTER` | 245 / 336 | 1.36 (1.13 to 1.64) | 866 / 1092 | 1.53 (1.34 to 1.76) | 1.13 (0.94 to 1.34) | yes |
| `CORRECTIVE_CONTRAST` | 33 / 26 | 0.78 (0.45 to 1.34) | 219 / 242 | 1.34 (1.08 to 1.67) | 1.72 (1.00 to 2.99) | no |
| `LLM_DICTION` | 440 / 541 | 1.22 (1.06 to 1.42) | 1496 / 1919 | 1.56 (1.41 to 1.72) | 1.28 (1.10 to 1.47) | no |
| `PARTICIPIAL_TAIL` | 293 / 834 | 2.83 (2.47 to 3.28) | 1055 / 2851 | 3.28 (2.96 to 3.66) | 1.16 (0.99 to 1.35) | no |
| `TRICOLON` | 626 / 909 | 1.44 (1.29 to 1.61) | 2612 / 3115 | 1.45 (1.35 to 1.56) | 1.01 (0.90 to 1.11) | yes |
| `VAGUE_QUANTIFIER` | 135 / 113 | 0.83 (0.65 to 1.05) | 405 / 400 | 1.20 (1.03 to 1.38) | 1.44 (1.13 to 1.92) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 / 82 | 0.96 (0.70 to 1.32) | 389 / 218 | 0.68 (0.54 to 0.85) | 0.71 (0.50 to 1.01) | no |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 / 22 | 0.75 (0.42 to 1.32) | 176 / 201 | 1.39 (1.11 to 1.75) | 1.84 (1.04 to 3.31) | no |
| `TRICOLON / tricolon` | 626 / 909 | 1.44 (1.29 to 1.61) | 2612 / 3115 | 1.45 (1.35 to 1.56) | 1.01 (0.90 to 1.11) | yes |

6 of 12 rows have the introduction ratio inside the abstract interval.

## Abstract against all sections

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | all n pre / post | all ratio (95% CI) | all over abstract (95% CI) | all ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 103 / 123 | 1.19 (0.89 to 1.56) | 2662 / 3125 | 1.53 (1.39 to 1.68) | 1.29 (0.99 to 1.69) | yes |
| `ALTERNATIVE_FRAMING` | 117 / 138 | 1.17 (0.90 to 1.51) | 4929 / 4277 | 1.13 (1.05 to 1.23) | 0.96 (0.75 to 1.25) | yes |
| `BORROWED_RIGOUR` | 46 / 51 | 1.10 (0.70 to 1.68) | 1270 / 1129 | 1.16 (0.99 to 1.35) | 1.05 (0.70 to 1.64) | yes |
| `CONSULTANT_REGISTER` | 245 / 336 | 1.36 (1.13 to 1.64) | 4267 / 4803 | 1.46 (1.31 to 1.65) | 1.07 (0.90 to 1.28) | yes |
| `CORRECTIVE_CONTRAST` | 33 / 26 | 0.78 (0.45 to 1.34) | 1408 / 1576 | 1.45 (1.28 to 1.65) | 1.86 (1.09 to 3.22) | no |
| `LLM_DICTION` | 440 / 541 | 1.22 (1.06 to 1.42) | 7283 / 7684 | 1.37 (1.25 to 1.50) | 1.12 (0.98 to 1.29) | yes |
| `PARTICIPIAL_TAIL` | 293 / 834 | 2.83 (2.47 to 3.28) | 6297 / 16997 | 3.51 (3.25 to 3.82) | 1.24 (1.07 to 1.43) | no |
| `TRICOLON` | 626 / 909 | 1.44 (1.29 to 1.61) | 16114 / 17574 | 1.42 (1.34 to 1.50) | 0.98 (0.89 to 1.09) | yes |
| `VAGUE_QUANTIFIER` | 135 / 113 | 0.83 (0.65 to 1.05) | 1203 / 1025 | 1.11 (0.98 to 1.25) | 1.33 (1.04 to 1.75) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 / 82 | 0.96 (0.70 to 1.32) | 3444 / 1590 | 0.60 (0.54 to 0.66) | 0.63 (0.46 to 0.85) | no |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 / 22 | 0.75 (0.42 to 1.32) | 1110 / 1133 | 1.33 (1.18 to 1.49) | 1.76 (1.01 to 3.11) | no |
| `TRICOLON / tricolon` | 626 / 909 | 1.44 (1.29 to 1.61) | 16111 / 17572 | 1.42 (1.34 to 1.50) | 0.98 (0.89 to 1.09) | yes |

7 of 12 rows have the all ratio inside the abstract interval.

## Abstract against related work

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | related n pre / post | related ratio (95% CI) | related over abstract (95% CI) | related ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 103 / 123 | 1.19 (0.89 to 1.56) | 360 / 379 | 1.36 (1.13 to 1.64) | 1.14 (0.84 to 1.58) | yes |
| `ALTERNATIVE_FRAMING` | 117 / 138 | 1.17 (0.90 to 1.51) | 475 / 468 | 1.27 (1.09 to 1.48) | 1.08 (0.80 to 1.44) | yes |
| `BORROWED_RIGOUR` | 46 / 51 | 1.10 (0.70 to 1.68) | 264 / 167 | 0.81 (0.64 to 1.07) | 0.74 (0.48 to 1.23) | yes |
| `CONSULTANT_REGISTER` | 245 / 336 | 1.36 (1.13 to 1.64) | 734 / 782 | 1.37 (1.17 to 1.59) | 1.01 (0.81 to 1.24) | yes |
| `CORRECTIVE_CONTRAST` | 33 / 26 | 0.78 (0.45 to 1.34) | 221 / 203 | 1.18 (0.95 to 1.46) | 1.51 (0.87 to 2.70) | yes |
| `LLM_DICTION` | 440 / 541 | 1.22 (1.06 to 1.42) | 906 / 1015 | 1.44 (1.22 to 1.69) | 1.18 (0.96 to 1.43) | no |
| `PARTICIPIAL_TAIL` | 293 / 834 | 2.83 (2.47 to 3.28) | 727 / 2026 | 3.59 (3.16 to 4.08) | 1.27 (1.07 to 1.50) | no |
| `TRICOLON` | 626 / 909 | 1.44 (1.29 to 1.61) | 1896 / 2165 | 1.47 (1.34 to 1.61) | 1.02 (0.89 to 1.16) | yes |
| `VAGUE_QUANTIFIER` | 135 / 113 | 0.83 (0.65 to 1.05) | 173 / 182 | 1.35 (1.07 to 1.69) | 1.63 (1.18 to 2.31) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 / 82 | 0.96 (0.70 to 1.32) | 286 / 118 | 0.53 (0.40 to 0.66) | 0.55 (0.38 to 0.80) | no |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 / 22 | 0.75 (0.42 to 1.32) | 198 / 165 | 1.07 (0.85 to 1.35) | 1.42 (0.80 to 2.63) | yes |
| `TRICOLON / tricolon` | 626 / 909 | 1.44 (1.29 to 1.61) | 1896 / 2165 | 1.47 (1.34 to 1.61) | 1.02 (0.89 to 1.16) | yes |

8 of 12 rows have the related ratio inside the abstract interval.

## Body against related work

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | body n pre / post | body ratio (95% CI) | related n pre / post | related ratio (95% CI) | related over body (95% CI) | related ratio inside body interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 1690 / 2104 | 1.64 (1.48 to 1.83) | 360 / 379 | 1.36 (1.13 to 1.64) | 0.83 (0.69 to 1.01) | no |
| `ALTERNATIVE_FRAMING` | 3741 / 3135 | 1.10 (1.01 to 1.21) | 475 / 468 | 1.27 (1.09 to 1.48) | 1.15 (0.99 to 1.34) | no |
| `BORROWED_RIGOUR` | 694 / 748 | 1.42 (1.18 to 1.73) | 264 / 167 | 0.81 (0.64 to 1.07) | 0.57 (0.42 to 0.79) | no |
| `CLOSER` | 214 / 194 | 1.19 (0.93 to 1.53) | 34 / 23 | 0.87 (0.49 to 1.50) | 0.73 (0.40 to 1.30) | no |
| `CONSULTANT_REGISTER` | 2407 / 2638 | 1.44 (1.25 to 1.67) | 734 / 782 | 1.37 (1.17 to 1.59) | 0.95 (0.80 to 1.13) | yes |
| `CORRECTIVE_CONTRAST` | 910 / 1064 | 1.54 (1.31 to 1.79) | 221 / 203 | 1.18 (0.95 to 1.46) | 0.77 (0.61 to 0.98) | no |
| `EMPHATIC_REFLEXIVE` | 400 / 355 | 1.17 (0.95 to 1.45) | 91 / 93 | 1.32 (0.95 to 1.83) | 1.13 (0.78 to 1.60) | yes |
| `EM_DASH` | 505 / 2537 | 6.61 (4.72 to 9.80) | 105 / 430 | 5.27 (3.38 to 9.23) | 0.80 (0.56 to 1.22) | yes |
| `HOLLOW_BOOSTER` | 166 / 451 | 3.58 (2.89 to 4.56) | 23 / 68 | 3.81 (2.35 to 6.59) | 1.06 (0.64 to 1.86) | yes |
| `LLM_DICTION` | 4426 / 4341 | 1.29 (1.16 to 1.45) | 906 / 1015 | 1.44 (1.22 to 1.69) | 1.12 (0.93 to 1.32) | yes |
| `PARTICIPIAL_TAIL` | 4277 / 11535 | 3.55 (3.26 to 3.89) | 727 / 2026 | 3.59 (3.16 to 4.08) | 1.01 (0.89 to 1.14) | yes |
| `TRICOLON` | 11012 / 11584 | 1.38 (1.29 to 1.48) | 1896 / 2165 | 1.47 (1.34 to 1.61) | 1.06 (0.96 to 1.16) | yes |
| `VAGUE_QUANTIFIER` | 539 / 394 | 0.96 (0.79 to 1.17) | 173 / 182 | 1.35 (1.07 to 1.69) | 1.41 (1.06 to 1.87) | no |
| `ALTERNATIVE_FRAMING / af_instead_of` | 721 / 478 | 0.87 (0.74 to 1.02) | 124 / 81 | 0.84 (0.60 to 1.13) | 0.96 (0.69 to 1.31) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 2668 / 1195 | 0.59 (0.53 to 0.65) | 286 / 118 | 0.53 (0.40 to 0.66) | 0.90 (0.69 to 1.14) | no |
| `ALTERNATIVE_FRAMING / af_rather_than` | 352 / 1462 | 5.47 (4.48 to 6.68) | 65 / 269 | 5.33 (3.99 to 7.49) | 0.97 (0.72 to 1.41) | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 685 / 712 | 1.37 (1.19 to 1.57) | 198 / 165 | 1.07 (0.85 to 1.35) | 0.78 (0.61 to 1.02) | no |
| `TRICOLON / tricolon` | 11009 / 11582 | 1.38 (1.29 to 1.48) | 1896 / 2165 | 1.47 (1.34 to 1.61) | 1.06 (0.96 to 1.16) | yes |

10 of 18 rows have the related ratio inside the body interval.

## Abstract against conclusion

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | conclusion n pre / post | conclusion ratio (95% CI) | conclusion over abstract (95% CI) | conclusion ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 103 / 123 | 1.19 (0.89 to 1.56) | 111 / 87 | 1.06 (0.78 to 1.42) | 0.89 (0.61 to 1.28) | yes |
| `ALTERNATIVE_FRAMING` | 117 / 138 | 1.17 (0.90 to 1.51) | 143 / 134 | 1.27 (0.96 to 1.67) | 1.08 (0.76 to 1.55) | yes |
| `BORROWED_RIGOUR` | 46 / 51 | 1.10 (0.70 to 1.68) | 72 / 38 | 0.71 (0.44 to 1.11) | 0.65 (0.37 to 1.12) | yes |
| `CONSULTANT_REGISTER` | 245 / 336 | 1.36 (1.13 to 1.64) | 260 / 291 | 1.51 (1.22 to 1.88) | 1.11 (0.88 to 1.44) | yes |
| `CORRECTIVE_CONTRAST` | 33 / 26 | 0.78 (0.45 to 1.34) | 58 / 67 | 1.56 (1.02 to 2.40) | 1.99 (1.05 to 3.83) | no |
| `LLM_DICTION` | 440 / 541 | 1.22 (1.06 to 1.42) | 455 / 409 | 1.21 (1.03 to 1.43) | 0.99 (0.83 to 1.19) | yes |
| `PARTICIPIAL_TAIL` | 293 / 834 | 2.83 (2.47 to 3.28) | 238 / 585 | 3.32 (2.78 to 4.02) | 1.17 (0.95 to 1.46) | no |
| `TRICOLON` | 626 / 909 | 1.44 (1.29 to 1.61) | 594 / 710 | 1.61 (1.41 to 1.83) | 1.12 (0.96 to 1.30) | no |
| `VAGUE_QUANTIFIER` | 135 / 113 | 0.83 (0.65 to 1.05) | 86 / 49 | 0.77 (0.51 to 1.13) | 0.93 (0.61 to 1.46) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 / 82 | 0.96 (0.70 to 1.32) | 101 / 59 | 0.79 (0.56 to 1.12) | 0.82 (0.54 to 1.29) | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 / 22 | 0.75 (0.42 to 1.32) | 51 / 55 | 1.46 (0.93 to 2.31) | 1.93 (0.97 to 3.99) | no |
| `TRICOLON / tricolon` | 626 / 909 | 1.44 (1.29 to 1.61) | 594 / 710 | 1.61 (1.41 to 1.83) | 1.12 (0.96 to 1.30) | no |

7 of 12 rows have the conclusion ratio inside the abstract interval.

## Body against conclusion

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | body n pre / post | body ratio (95% CI) | conclusion n pre / post | conclusion ratio (95% CI) | conclusion over body (95% CI) | conclusion ratio inside body interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 1690 / 2104 | 1.64 (1.48 to 1.83) | 111 / 87 | 1.06 (0.78 to 1.42) | 0.65 (0.48 to 0.86) | no |
| `ALTERNATIVE_FRAMING` | 3741 / 3135 | 1.10 (1.01 to 1.21) | 143 / 134 | 1.27 (0.96 to 1.67) | 1.15 (0.88 to 1.50) | no |
| `BORROWED_RIGOUR` | 694 / 748 | 1.42 (1.18 to 1.73) | 72 / 38 | 0.71 (0.44 to 1.11) | 0.50 (0.31 to 0.77) | no |
| `CONSULTANT_REGISTER` | 2407 / 2638 | 1.44 (1.25 to 1.67) | 260 / 291 | 1.51 (1.22 to 1.88) | 1.05 (0.87 to 1.30) | yes |
| `CORRECTIVE_CONTRAST` | 910 / 1064 | 1.54 (1.31 to 1.79) | 58 / 67 | 1.56 (1.02 to 2.40) | 1.01 (0.66 to 1.58) | yes |
| `LLM_DICTION` | 4426 / 4341 | 1.29 (1.16 to 1.45) | 455 / 409 | 1.21 (1.03 to 1.43) | 0.94 (0.80 to 1.10) | yes |
| `PARTICIPIAL_TAIL` | 4277 / 11535 | 3.55 (3.26 to 3.89) | 238 / 585 | 3.32 (2.78 to 4.02) | 0.93 (0.80 to 1.11) | yes |
| `TRICOLON` | 11012 / 11584 | 1.38 (1.29 to 1.48) | 594 / 710 | 1.61 (1.41 to 1.83) | 1.17 (1.02 to 1.33) | no |
| `VAGUE_QUANTIFIER` | 539 / 394 | 0.96 (0.79 to 1.17) | 86 / 49 | 0.77 (0.51 to 1.13) | 0.80 (0.54 to 1.19) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 2668 / 1195 | 0.59 (0.53 to 0.65) | 101 / 59 | 0.79 (0.56 to 1.12) | 1.34 (0.96 to 1.85) | no |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 685 / 712 | 1.37 (1.19 to 1.57) | 51 / 55 | 1.46 (0.93 to 2.31) | 1.06 (0.68 to 1.70) | yes |
| `TRICOLON / tricolon` | 11009 / 11582 | 1.38 (1.29 to 1.48) | 594 / 710 | 1.61 (1.41 to 1.83) | 1.17 (1.02 to 1.33) | no |

5 of 12 rows have the conclusion ratio inside the body interval.

## Check against TF-004

The sample's abstract ratio against the TF-004 interval for the full abstract sets (955 and 2,627 papers), for rows with at least 20 findings in TF-004.

| row | TF-004 ratio (95% CI) | sample abstract n pre / post | sample abstract ratio (95% CI) | sample ratio inside TF-004 interval | TF-004 ratio inside sample interval |
|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 1.27 (1.02 to 1.59) | 103 / 123 | 1.19 (0.89 to 1.56) | yes | yes |
| `ALTERNATIVE_FRAMING` | 1.23 (1.02 to 1.51) | 117 / 138 | 1.17 (0.90 to 1.51) | yes | yes |
| `BORROWED_RIGOUR` | 1.02 (0.74 to 1.45) | 46 / 51 | 1.10 (0.70 to 1.68) | yes | yes |
| `CONSULTANT_REGISTER` | 1.43 (1.23 to 1.67) | 245 / 336 | 1.36 (1.13 to 1.64) | yes | yes |
| `CORRECTIVE_CONTRAST` | 1.04 (0.71 to 1.57) | 33 / 26 | 0.78 (0.45 to 1.34) | yes | yes |
| `DISGUISE_METAPHOR` | 2.87 (1.10 to inf) | 0 / 0 | - (- to -) | no | no |
| `EMPHATIC_REFLEXIVE` | 1.30 (0.74 to 2.63) | 8 / 15 | 1.86 (0.80 to 5.27) | yes | yes |
| `FRAME_MARKER` | 0.27 (0.12 to 0.56) | 13 / 6 | 0.46 (0.12 to 1.13) | yes | yes |
| `HOLLOW_BOOSTER` | 1.43 (0.79 to 3.56) | 8 / 12 | 1.49 (0.61 to 4.47) | yes | yes |
| `LLM_DICTION` | 1.27 (1.14 to 1.44) | 440 / 541 | 1.22 (1.06 to 1.42) | yes | yes |
| `PARTICIPIAL_TAIL` | 3.14 (2.79 to 3.57) | 293 / 834 | 2.83 (2.47 to 3.28) | yes | yes |
| `TRICOLON` | 1.44 (1.32 to 1.56) | 626 / 909 | 1.44 (1.29 to 1.61) | yes | yes |
| `VAGUE_QUANTIFIER` | 0.85 (0.70 to 1.03) | 135 / 113 | 0.83 (0.65 to 1.05) | yes | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 0.90 (0.72 to 1.17) | 85 / 82 | 0.96 (0.70 to 1.32) | yes | yes |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 2.15 (1.56 to 3.29) | 32 / 56 | 1.74 (1.14 to 2.77) | yes | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 1.00 (0.69 to 1.57) | 29 / 22 | 0.75 (0.42 to 1.32) | yes | yes |
| `TRICOLON / tricolon` | 1.44 (1.32 to 1.56) | 626 / 909 | 1.44 (1.29 to 1.61) | yes | yes |

16 of 17 sample abstract ratios lie inside the TF-004 interval; the TF-004 ratio lies inside the sample interval for 16 of 17. TF-004 ran an earlier ticfinder (69e1743), so rows whose code changed in TF-006 and TF-007 can differ for that reason as well as from sampling and from keeping only papers with usable LaTeX.

## Rates per text type

Sorted by ratio. `n` is findings; the verdict is `rose` when the ratio interval is above 1, `fell` below, `flat` when it spans 1, `too few` under 20 findings in both windows together. Construction tables list every row with a finding; pattern tables list rows with at least 20.

### abstract

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `NEG_ESCALATION` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | inf (inf to inf) | too few |
| `CLOSER` | 1 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.04) | 3 | 0.02 (0.00 to 0.05) | 0.02 (0.00 to 0.05) | 2.98 (0.00 to inf) | too few |
| `PARTICIPIAL_TAIL` | 293 | 1.97 (1.72 to 2.21) | 1.95 (1.70 to 2.21) | 834 | 5.56 (5.22 to 5.94) | 5.63 (5.26 to 6.02) | 2.83 (2.47 to 3.28) | rose |
| `EMPHATIC_REFLEXIVE` | 8 | 0.05 (0.02 to 0.09) | 0.06 (0.02 to 0.11) | 15 | 0.10 (0.05 to 0.16) | 0.09 (0.05 to 0.15) | 1.86 (0.80 to 5.27) | flat |
| `HOLLOW_BOOSTER` | 8 | 0.05 (0.02 to 0.09) | 0.05 (0.02 to 0.09) | 12 | 0.08 (0.04 to 0.13) | 0.08 (0.04 to 0.13) | 1.49 (0.61 to 4.47) | flat |
| `TRICOLON` | 626 | 4.21 (3.85 to 4.55) | 4.28 (3.91 to 4.65) | 909 | 6.06 (5.63 to 6.49) | 6.13 (5.69 to 6.59) | 1.44 (1.29 to 1.61) | rose |
| `CONSULTANT_REGISTER` | 245 | 1.65 (1.41 to 1.89) | 1.66 (1.42 to 1.90) | 336 | 2.24 (1.98 to 2.51) | 2.30 (2.03 to 2.59) | 1.36 (1.13 to 1.64) | rose |
| `LLM_DICTION` | 440 | 2.96 (2.63 to 3.30) | 3.02 (2.66 to 3.38) | 541 | 3.61 (3.28 to 3.95) | 3.76 (3.40 to 4.12) | 1.22 (1.06 to 1.42) | rose |
| `ABSTRACT_ADVERB` | 103 | 0.69 (0.55 to 0.85) | 0.67 (0.53 to 0.83) | 123 | 0.82 (0.67 to 0.97) | 0.82 (0.66 to 0.98) | 1.19 (0.89 to 1.56) | flat |
| `ALTERNATIVE_FRAMING` | 117 | 0.79 (0.65 to 0.93) | 0.80 (0.65 to 0.96) | 138 | 0.92 (0.77 to 1.09) | 0.89 (0.74 to 1.06) | 1.17 (0.90 to 1.51) | flat |
| `BORROWED_RIGOUR` | 46 | 0.31 (0.22 to 0.41) | 0.30 (0.22 to 0.40) | 51 | 0.34 (0.24 to 0.44) | 0.33 (0.24 to 0.43) | 1.10 (0.70 to 1.68) | flat |
| `VAGUE_QUANTIFIER` | 135 | 0.91 (0.76 to 1.06) | 0.86 (0.72 to 1.02) | 113 | 0.75 (0.62 to 0.89) | 0.79 (0.65 to 0.96) | 0.83 (0.65 to 1.05) | flat |
| `CORRECTIVE_CONTRAST` | 33 | 0.22 (0.15 to 0.30) | 0.23 (0.15 to 0.33) | 26 | 0.17 (0.11 to 0.25) | 0.17 (0.11 to 0.24) | 0.78 (0.45 to 1.34) | flat |
| `HEDGE_STACK` | 2 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.03) | 1 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 0.50 (0.00 to inf) | too few |
| `FRAME_MARKER` | 13 | 0.09 (0.05 to 0.14) | 0.10 (0.05 to 0.17) | 6 | 0.04 (0.01 to 0.07) | 0.04 (0.01 to 0.08) | 0.46 (0.12 to 1.13) | too few |
| `EMPTY_FRAME` | 2 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.03) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `ALTERNATIVE_FRAMING / af_rather_than` | 13 | 0.09 (0.04 to 0.15) | 0.09 (0.04 to 0.15) | 38 | 0.25 (0.17 to 0.34) | 0.24 (0.16 to 0.32) | 2.90 (1.54 to 6.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 293 | 1.97 (1.72 to 2.21) | 1.95 (1.70 to 2.21) | 834 | 5.56 (5.22 to 5.94) | 5.63 (5.26 to 6.02) | 2.83 (2.47 to 3.28) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 8 | 0.05 (0.02 to 0.09) | 0.06 (0.02 to 0.11) | 15 | 0.10 (0.05 to 0.16) | 0.09 (0.05 to 0.15) | 1.86 (0.80 to 5.27) | flat |
| `HOLLOW_BOOSTER / -` | 8 | 0.05 (0.02 to 0.09) | 0.05 (0.02 to 0.09) | 12 | 0.08 (0.04 to 0.13) | 0.08 (0.04 to 0.13) | 1.49 (0.61 to 4.47) | flat |
| `TRICOLON / tricolon` | 626 | 4.21 (3.85 to 4.55) | 4.28 (3.91 to 4.65) | 909 | 6.06 (5.63 to 6.49) | 6.13 (5.69 to 6.59) | 1.44 (1.29 to 1.61) | rose |
| `CONSULTANT_REGISTER / -` | 245 | 1.65 (1.41 to 1.89) | 1.66 (1.42 to 1.90) | 336 | 2.24 (1.98 to 2.51) | 2.30 (2.03 to 2.59) | 1.36 (1.13 to 1.64) | rose |
| `LLM_DICTION / -` | 440 | 2.96 (2.63 to 3.30) | 3.02 (2.66 to 3.38) | 541 | 3.61 (3.28 to 3.95) | 3.76 (3.40 to 4.12) | 1.22 (1.06 to 1.42) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 103 | 0.69 (0.55 to 0.85) | 0.67 (0.53 to 0.83) | 123 | 0.82 (0.67 to 0.97) | 0.82 (0.66 to 0.98) | 1.19 (0.89 to 1.56) | flat |
| `BORROWED_RIGOUR / -` | 46 | 0.31 (0.22 to 0.41) | 0.30 (0.22 to 0.40) | 51 | 0.34 (0.24 to 0.44) | 0.33 (0.24 to 0.43) | 1.10 (0.70 to 1.68) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 85 | 0.57 (0.45 to 0.70) | 0.59 (0.46 to 0.73) | 82 | 0.55 (0.43 to 0.68) | 0.52 (0.41 to 0.65) | 0.96 (0.70 to 1.32) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 19 | 0.13 (0.07 to 0.19) | 0.12 (0.07 to 0.17) | 18 | 0.12 (0.07 to 0.18) | 0.13 (0.07 to 0.19) | 0.94 (0.48 to 1.83) | flat |
| `VAGUE_QUANTIFIER / -` | 135 | 0.91 (0.76 to 1.06) | 0.86 (0.72 to 1.02) | 113 | 0.75 (0.62 to 0.89) | 0.79 (0.65 to 0.96) | 0.83 (0.65 to 1.05) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 29 | 0.19 (0.13 to 0.27) | 0.20 (0.12 to 0.29) | 22 | 0.15 (0.09 to 0.21) | 0.15 (0.09 to 0.21) | 0.75 (0.42 to 1.32) | flat |

### introduction

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 142 | 0.21 (0.15 to 0.29) | 0.20 (0.15 to 0.27) | 611 | 1.12 (0.93 to 1.30) | 1.11 (0.94 to 1.29) | 5.23 (3.68 to 7.69) | rose |
| `PARTICIPIAL_TAIL` | 1055 | 1.59 (1.45 to 1.73) | 1.62 (1.48 to 1.76) | 2851 | 5.21 (4.94 to 5.48) | 5.27 (5.00 to 5.56) | 3.28 (2.96 to 3.66) | rose |
| `HOLLOW_BOOSTER` | 44 | 0.07 (0.05 to 0.09) | 0.06 (0.04 to 0.09) | 64 | 0.12 (0.09 to 0.15) | 0.11 (0.08 to 0.15) | 1.77 (1.20 to 2.62) | rose |
| `LLM_DICTION` | 1496 | 2.25 (2.08 to 2.42) | 2.35 (2.16 to 2.53) | 1919 | 3.51 (3.28 to 3.74) | 3.52 (3.28 to 3.76) | 1.56 (1.41 to 1.72) | rose |
| `CONSULTANT_REGISTER` | 866 | 1.30 (1.16 to 1.44) | 1.35 (1.21 to 1.49) | 1092 | 2.00 (1.83 to 2.15) | 2.01 (1.84 to 2.19) | 1.53 (1.34 to 1.76) | rose |
| `GAPPED_ANTITHESIS` | 4 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.01) | 1.52 (0.34 to 10.56) | too few |
| `TRICOLON` | 2612 | 3.93 (3.73 to 4.13) | 4.08 (3.87 to 4.30) | 3115 | 5.69 (5.39 to 5.99) | 5.93 (5.61 to 6.26) | 1.45 (1.35 to 1.56) | rose |
| `ABSTRACT_ADVERB` | 501 | 0.75 (0.67 to 0.84) | 0.76 (0.67 to 0.85) | 555 | 1.01 (0.92 to 1.12) | 1.02 (0.92 to 1.12) | 1.35 (1.16 to 1.56) | rose |
| `CORRECTIVE_CONTRAST` | 219 | 0.33 (0.28 to 0.38) | 0.31 (0.26 to 0.37) | 242 | 0.44 (0.38 to 0.50) | 0.46 (0.39 to 0.54) | 1.34 (1.08 to 1.67) | rose |
| `VAGUE_QUANTIFIER` | 405 | 0.61 (0.54 to 0.68) | 0.62 (0.55 to 0.70) | 400 | 0.73 (0.66 to 0.81) | 0.76 (0.68 to 0.84) | 1.20 (1.03 to 1.38) | rose |
| `ALTERNATIVE_FRAMING` | 570 | 0.86 (0.76 to 0.96) | 0.86 (0.76 to 0.96) | 540 | 0.99 (0.89 to 1.08) | 0.91 (0.82 to 1.01) | 1.15 (0.98 to 1.34) | flat |
| `EMPHATIC_REFLEXIVE` | 84 | 0.13 (0.10 to 0.16) | 0.13 (0.09 to 0.16) | 77 | 0.14 (0.11 to 0.17) | 0.14 (0.10 to 0.17) | 1.11 (0.79 to 1.54) | flat |
| `CLOSER` | 82 | 0.12 (0.10 to 0.15) | 0.12 (0.09 to 0.15) | 68 | 0.12 (0.10 to 0.15) | 0.12 (0.09 to 0.14) | 1.01 (0.72 to 1.39) | flat |
| `BORROWED_RIGOUR` | 240 | 0.36 (0.30 to 0.43) | 0.37 (0.30 to 0.43) | 176 | 0.32 (0.26 to 0.39) | 0.31 (0.25 to 0.37) | 0.89 (0.68 to 1.17) | flat |
| `HEDGE_STACK` | 6 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 3 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.61 (0.00 to 3.21) | too few |
| `EMPTY_FRAME` | 38 | 0.06 (0.04 to 0.08) | 0.06 (0.04 to 0.08) | 14 | 0.03 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 0.45 (0.21 to 0.80) | fell |
| `FRAME_MARKER` | 46 | 0.07 (0.05 to 0.09) | 0.07 (0.05 to 0.10) | 15 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.04) | 0.40 (0.20 to 0.71) | fell |
| `NEG_ESCALATION` | 7 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 2 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.35 (0.00 to 1.45) | too few |
| `DISGUISE_METAPHOR` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 142 | 0.21 (0.15 to 0.29) | 0.20 (0.15 to 0.27) | 611 | 1.12 (0.93 to 1.30) | 1.11 (0.94 to 1.29) | 5.23 (3.68 to 7.69) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than` | 74 | 0.11 (0.08 to 0.14) | 0.11 (0.08 to 0.15) | 246 | 0.45 (0.39 to 0.51) | 0.43 (0.36 to 0.49) | 4.04 (3.09 to 5.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 1055 | 1.59 (1.45 to 1.73) | 1.62 (1.48 to 1.76) | 2851 | 5.21 (4.94 to 5.48) | 5.27 (5.00 to 5.56) | 3.28 (2.96 to 3.66) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 13 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 21 | 0.04 (0.02 to 0.06) | 0.04 (0.02 to 0.05) | 1.96 (0.98 to 4.20) | flat |
| `HOLLOW_BOOSTER / -` | 44 | 0.07 (0.05 to 0.09) | 0.06 (0.04 to 0.09) | 64 | 0.12 (0.09 to 0.15) | 0.11 (0.08 to 0.15) | 1.77 (1.20 to 2.62) | rose |
| `LLM_DICTION / -` | 1496 | 2.25 (2.08 to 2.42) | 2.35 (2.16 to 2.53) | 1919 | 3.51 (3.28 to 3.74) | 3.52 (3.28 to 3.76) | 1.56 (1.41 to 1.72) | rose |
| `CONSULTANT_REGISTER / -` | 866 | 1.30 (1.16 to 1.44) | 1.35 (1.21 to 1.49) | 1092 | 2.00 (1.83 to 2.15) | 2.01 (1.84 to 2.19) | 1.53 (1.34 to 1.76) | rose |
| `TRICOLON / tricolon` | 2612 | 3.93 (3.73 to 4.13) | 4.08 (3.87 to 4.30) | 3115 | 5.69 (5.39 to 5.99) | 5.93 (5.61 to 6.26) | 1.45 (1.35 to 1.56) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 176 | 0.26 (0.22 to 0.31) | 0.26 (0.21 to 0.31) | 201 | 0.37 (0.31 to 0.42) | 0.39 (0.32 to 0.46) | 1.39 (1.11 to 1.75) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 501 | 0.75 (0.67 to 0.84) | 0.76 (0.67 to 0.85) | 555 | 1.01 (0.92 to 1.12) | 1.02 (0.92 to 1.12) | 1.35 (1.16 to 1.56) | rose |
| `VAGUE_QUANTIFIER / -` | 405 | 0.61 (0.54 to 0.68) | 0.62 (0.55 to 0.70) | 400 | 0.73 (0.66 to 0.81) | 0.76 (0.68 to 0.84) | 1.20 (1.03 to 1.38) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 84 | 0.13 (0.10 to 0.16) | 0.13 (0.09 to 0.16) | 77 | 0.14 (0.11 to 0.17) | 0.14 (0.10 to 0.17) | 1.11 (0.79 to 1.54) | flat |
| `CLOSER / -` | 82 | 0.12 (0.10 to 0.15) | 0.12 (0.09 to 0.15) | 68 | 0.12 (0.10 to 0.15) | 0.12 (0.09 to 0.14) | 1.01 (0.72 to 1.39) | flat |
| `BORROWED_RIGOUR / -` | 240 | 0.36 (0.30 to 0.43) | 0.37 (0.30 to 0.43) | 176 | 0.32 (0.26 to 0.39) | 0.31 (0.25 to 0.37) | 0.89 (0.68 to 1.17) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 107 | 0.16 (0.13 to 0.19) | 0.15 (0.12 to 0.19) | 76 | 0.14 (0.11 to 0.17) | 0.12 (0.09 to 0.15) | 0.86 (0.62 to 1.19) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 389 | 0.58 (0.50 to 0.67) | 0.60 (0.51 to 0.69) | 218 | 0.40 (0.33 to 0.47) | 0.37 (0.31 to 0.43) | 0.68 (0.54 to 0.85) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 22 | 0.03 (0.02 to 0.05) | 0.03 (0.02 to 0.04) | 10 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 0.55 (0.22 to 1.15) | flat |
| `EMPTY_FRAME / -` | 38 | 0.06 (0.04 to 0.08) | 0.06 (0.04 to 0.08) | 14 | 0.03 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 0.45 (0.21 to 0.80) | fell |
| `FRAME_MARKER / -` | 46 | 0.07 (0.05 to 0.09) | 0.07 (0.05 to 0.10) | 15 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.04) | 0.40 (0.20 to 0.71) | fell |

### body

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 505 | 0.14 (0.10 to 0.19) | 0.14 (0.10 to 0.19) | 2537 | 0.93 (0.76 to 1.12) | 0.81 (0.70 to 0.94) | 6.61 (4.72 to 9.80) | rose |
| `HOLLOW_BOOSTER` | 166 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 451 | 0.17 (0.15 to 0.19) | 0.18 (0.15 to 0.20) | 3.58 (2.89 to 4.56) | rose |
| `PARTICIPIAL_TAIL` | 4277 | 1.19 (1.11 to 1.28) | 1.18 (1.10 to 1.27) | 11535 | 4.24 (4.05 to 4.44) | 4.47 (4.28 to 4.68) | 3.55 (3.26 to 3.89) | rose |
| `ABSTRACT_ADVERB` | 1690 | 0.47 (0.44 to 0.51) | 0.45 (0.41 to 0.49) | 2104 | 0.77 (0.72 to 0.83) | 0.79 (0.73 to 0.85) | 1.64 (1.48 to 1.83) | rose |
| `CORRECTIVE_CONTRAST` | 910 | 0.25 (0.23 to 0.28) | 0.23 (0.21 to 0.26) | 1064 | 0.39 (0.34 to 0.44) | 0.38 (0.33 to 0.42) | 1.54 (1.31 to 1.79) | rose |
| `CONSULTANT_REGISTER` | 2407 | 0.67 (0.60 to 0.75) | 0.66 (0.60 to 0.72) | 2638 | 0.97 (0.89 to 1.06) | 0.98 (0.90 to 1.07) | 1.44 (1.25 to 1.67) | rose |
| `BORROWED_RIGOUR` | 694 | 0.19 (0.16 to 0.23) | 0.21 (0.17 to 0.26) | 748 | 0.27 (0.24 to 0.31) | 0.27 (0.24 to 0.31) | 1.42 (1.18 to 1.73) | rose |
| `TRICOLON` | 11012 | 3.07 (2.95 to 3.21) | 3.09 (2.97 to 3.21) | 11584 | 4.25 (4.04 to 4.47) | 4.28 (4.10 to 4.46) | 1.38 (1.29 to 1.48) | rose |
| `LLM_DICTION` | 4426 | 1.24 (1.14 to 1.34) | 1.19 (1.09 to 1.29) | 4341 | 1.59 (1.47 to 1.73) | 1.64 (1.53 to 1.76) | 1.29 (1.16 to 1.45) | rose |
| `CLOSER` | 214 | 0.06 (0.05 to 0.07) | 0.07 (0.05 to 0.08) | 194 | 0.07 (0.06 to 0.08) | 0.06 (0.05 to 0.07) | 1.19 (0.93 to 1.53) | flat |
| `EMPHATIC_REFLEXIVE` | 400 | 0.11 (0.10 to 0.13) | 0.11 (0.10 to 0.13) | 355 | 0.13 (0.11 to 0.15) | 0.11 (0.10 to 0.13) | 1.17 (0.95 to 1.45) | flat |
| `GAPPED_ANTITHESIS` | 68 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 59 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 1.14 (0.78 to 1.61) | flat |
| `ALTERNATIVE_FRAMING` | 3741 | 1.04 (0.99 to 1.10) | 1.06 (1.00 to 1.12) | 3135 | 1.15 (1.08 to 1.24) | 1.12 (1.05 to 1.19) | 1.10 (1.01 to 1.21) | rose |
| `VAGUE_QUANTIFIER` | 539 | 0.15 (0.13 to 0.17) | 0.14 (0.12 to 0.16) | 394 | 0.14 (0.12 to 0.16) | 0.14 (0.12 to 0.16) | 0.96 (0.79 to 1.17) | flat |
| `DISGUISE_METAPHOR` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.79 (0.00 to 3.96) | too few |
| `NEG_ESCALATION` | 18 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.73 (0.27 to 1.64) | flat |
| `FRAME_MARKER` | 263 | 0.07 (0.06 to 0.09) | 0.07 (0.06 to 0.09) | 138 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 0.69 (0.53 to 0.88) | fell |
| `EMPTY_FRAME` | 363 | 0.10 (0.09 to 0.12) | 0.11 (0.09 to 0.13) | 177 | 0.07 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 0.64 (0.50 to 0.81) | fell |
| `HEDGE_STACK` | 51 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.34 (0.15 to 0.61) | fell |
| `HOUSE_STYLE` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 505 | 0.14 (0.10 to 0.19) | 0.14 (0.10 to 0.19) | 2537 | 0.93 (0.76 to 1.12) | 0.81 (0.70 to 0.94) | 6.61 (4.72 to 9.80) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 56 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 246 | 0.09 (0.07 to 0.12) | 0.08 (0.06 to 0.11) | 5.78 (3.78 to 8.67) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than` | 352 | 0.10 (0.08 to 0.11) | 0.09 (0.08 to 0.11) | 1462 | 0.54 (0.47 to 0.61) | 0.51 (0.46 to 0.57) | 5.47 (4.48 to 6.68) | rose |
| `HOLLOW_BOOSTER / -` | 166 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 451 | 0.17 (0.15 to 0.19) | 0.18 (0.15 to 0.20) | 3.58 (2.89 to 4.56) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 4277 | 1.19 (1.11 to 1.28) | 1.18 (1.10 to 1.27) | 11535 | 4.24 (4.05 to 4.44) | 4.47 (4.28 to 4.68) | 3.55 (3.26 to 3.89) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 56 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 2.30 (1.40 to 3.81) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 1690 | 0.47 (0.44 to 0.51) | 0.45 (0.41 to 0.49) | 2104 | 0.77 (0.72 to 0.83) | 0.79 (0.73 to 0.85) | 1.64 (1.48 to 1.83) | rose |
| `CONSULTANT_REGISTER / -` | 2407 | 0.67 (0.60 to 0.75) | 0.66 (0.60 to 0.72) | 2638 | 0.97 (0.89 to 1.06) | 0.98 (0.90 to 1.07) | 1.44 (1.25 to 1.67) | rose |
| `BORROWED_RIGOUR / -` | 694 | 0.19 (0.16 to 0.23) | 0.21 (0.17 to 0.26) | 748 | 0.27 (0.24 to 0.31) | 0.27 (0.24 to 0.31) | 1.42 (1.18 to 1.73) | rose |
| `TRICOLON / tricolon` | 11009 | 3.07 (2.95 to 3.21) | 3.09 (2.97 to 3.21) | 11582 | 4.25 (4.04 to 4.47) | 4.28 (4.10 to 4.46) | 1.38 (1.29 to 1.48) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 685 | 0.19 (0.17 to 0.21) | 0.18 (0.16 to 0.20) | 712 | 0.26 (0.24 to 0.29) | 0.26 (0.23 to 0.29) | 1.37 (1.19 to 1.57) | rose |
| `LLM_DICTION / -` | 4426 | 1.24 (1.14 to 1.34) | 1.19 (1.09 to 1.29) | 4341 | 1.59 (1.47 to 1.73) | 1.64 (1.53 to 1.76) | 1.29 (1.16 to 1.45) | rose |
| `CLOSER / -` | 214 | 0.06 (0.05 to 0.07) | 0.07 (0.05 to 0.08) | 194 | 0.07 (0.06 to 0.08) | 0.06 (0.05 to 0.07) | 1.19 (0.93 to 1.53) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 400 | 0.11 (0.10 to 0.13) | 0.11 (0.10 to 0.13) | 355 | 0.13 (0.11 to 0.15) | 0.11 (0.10 to 0.13) | 1.17 (0.95 to 1.45) | flat |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 68 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 59 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 1.14 (0.78 to 1.61) | flat |
| `VAGUE_QUANTIFIER / -` | 539 | 0.15 (0.13 to 0.17) | 0.14 (0.12 to 0.16) | 394 | 0.14 (0.12 to 0.16) | 0.14 (0.12 to 0.16) | 0.96 (0.79 to 1.17) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 721 | 0.20 (0.18 to 0.22) | 0.20 (0.18 to 0.22) | 478 | 0.18 (0.15 to 0.20) | 0.17 (0.15 to 0.19) | 0.87 (0.74 to 1.02) | flat |
| `NEG_ESCALATION / neg_escalation` | 18 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.73 (0.27 to 1.64) | flat |
| `FRAME_MARKER / -` | 263 | 0.07 (0.06 to 0.09) | 0.07 (0.06 to 0.09) | 138 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 0.69 (0.53 to 0.88) | fell |
| `EMPTY_FRAME / -` | 363 | 0.10 (0.09 to 0.12) | 0.11 (0.09 to 0.13) | 177 | 0.07 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 0.64 (0.50 to 0.81) | fell |
| `ALTERNATIVE_FRAMING / af_less_than` | 2668 | 0.74 (0.70 to 0.79) | 0.76 (0.71 to 0.81) | 1195 | 0.44 (0.40 to 0.48) | 0.43 (0.40 to 0.47) | 0.59 (0.53 to 0.65) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 137 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 50 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 0.48 (0.31 to 0.72) | fell |
| `HEDGE_STACK / -` | 51 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.34 (0.15 to 0.61) | fell |

### related

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `DISGUISE_METAPHOR` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | inf (inf to inf) | too few |
| `EM_DASH` | 105 | 0.19 (0.11 to 0.28) | 0.18 (0.11 to 0.26) | 430 | 0.98 (0.80 to 1.19) | 0.92 (0.75 to 1.10) | 5.27 (3.38 to 9.23) | rose |
| `HOLLOW_BOOSTER` | 23 | 0.04 (0.02 to 0.06) | 0.05 (0.02 to 0.08) | 68 | 0.16 (0.12 to 0.19) | 0.16 (0.12 to 0.21) | 3.81 (2.35 to 6.59) | rose |
| `PARTICIPIAL_TAIL` | 727 | 1.29 (1.15 to 1.44) | 1.22 (1.07 to 1.37) | 2026 | 4.63 (4.35 to 4.94) | 5.01 (4.66 to 5.38) | 3.59 (3.16 to 4.08) | rose |
| `HEDGE_STACK` | 3 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.04) | 6 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 2.58 (0.64 to inf) | too few |
| `TRICOLON` | 1896 | 3.37 (3.17 to 3.60) | 3.64 (3.38 to 3.92) | 2165 | 4.95 (4.63 to 5.28) | 5.35 (4.99 to 5.73) | 1.47 (1.34 to 1.61) | rose |
| `LLM_DICTION` | 906 | 1.61 (1.42 to 1.84) | 1.60 (1.44 to 1.76) | 1015 | 2.32 (2.10 to 2.55) | 2.49 (2.22 to 2.78) | 1.44 (1.22 to 1.69) | rose |
| `CONSULTANT_REGISTER` | 734 | 1.30 (1.17 to 1.47) | 1.46 (1.29 to 1.64) | 782 | 1.79 (1.61 to 1.97) | 1.82 (1.63 to 2.03) | 1.37 (1.17 to 1.59) | rose |
| `ABSTRACT_ADVERB` | 360 | 0.64 (0.55 to 0.73) | 0.60 (0.51 to 0.69) | 379 | 0.87 (0.77 to 0.97) | 0.87 (0.75 to 1.00) | 1.36 (1.13 to 1.64) | rose |
| `VAGUE_QUANTIFIER` | 173 | 0.31 (0.26 to 0.36) | 0.36 (0.29 to 0.43) | 182 | 0.42 (0.35 to 0.49) | 0.42 (0.33 to 0.51) | 1.35 (1.07 to 1.69) | rose |
| `EMPHATIC_REFLEXIVE` | 91 | 0.16 (0.13 to 0.20) | 0.16 (0.12 to 0.21) | 93 | 0.21 (0.17 to 0.26) | 0.21 (0.16 to 0.27) | 1.32 (0.95 to 1.83) | flat |
| `ALTERNATIVE_FRAMING` | 475 | 0.84 (0.76 to 0.94) | 0.82 (0.72 to 0.92) | 468 | 1.07 (0.96 to 1.18) | 1.10 (0.97 to 1.26) | 1.27 (1.09 to 1.48) | rose |
| `CORRECTIVE_CONTRAST` | 221 | 0.39 (0.33 to 0.45) | 0.40 (0.33 to 0.47) | 203 | 0.46 (0.40 to 0.54) | 0.47 (0.39 to 0.55) | 1.18 (0.95 to 1.46) | flat |
| `FRAME_MARKER` | 16 | 0.03 (0.01 to 0.05) | 0.03 (0.01 to 0.05) | 14 | 0.03 (0.02 to 0.05) | 0.04 (0.01 to 0.07) | 1.13 (0.52 to 2.46) | flat |
| `GAPPED_ANTITHESIS` | 8 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 6 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 0.97 (0.26 to 2.86) | too few |
| `CLOSER` | 34 | 0.06 (0.04 to 0.08) | 0.06 (0.04 to 0.09) | 23 | 0.05 (0.03 to 0.08) | 0.03 (0.02 to 0.05) | 0.87 (0.49 to 1.50) | flat |
| `BORROWED_RIGOUR` | 264 | 0.47 (0.38 to 0.56) | 0.41 (0.34 to 0.50) | 167 | 0.38 (0.32 to 0.45) | 0.41 (0.33 to 0.50) | 0.81 (0.64 to 1.07) | flat |
| `EMPTY_FRAME` | 30 | 0.05 (0.03 to 0.08) | 0.04 (0.02 to 0.07) | 16 | 0.04 (0.02 to 0.06) | 0.02 (0.01 to 0.03) | 0.69 (0.32 to 1.44) | flat |
| `NEG_ESCALATION` | 9 | 0.02 (0.01 to 0.03) | 0.02 (0.00 to 0.04) | 4 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 0.57 (0.11 to 2.33) | too few |
| `HOUSE_STYLE` | 3 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.01) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `ALTERNATIVE_FRAMING / af_rather_than` | 65 | 0.12 (0.08 to 0.15) | 0.12 (0.08 to 0.15) | 269 | 0.62 (0.52 to 0.71) | 0.66 (0.56 to 0.77) | 5.33 (3.99 to 7.49) | rose |
| `EM_DASH / -` | 105 | 0.19 (0.11 to 0.28) | 0.18 (0.11 to 0.26) | 430 | 0.98 (0.80 to 1.19) | 0.92 (0.75 to 1.10) | 5.27 (3.38 to 9.23) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 7 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 27 | 0.06 (0.04 to 0.09) | 0.06 (0.03 to 0.09) | 4.97 (2.21 to 15.99) | rose |
| `HOLLOW_BOOSTER / -` | 23 | 0.04 (0.02 to 0.06) | 0.05 (0.02 to 0.08) | 68 | 0.16 (0.12 to 0.19) | 0.16 (0.12 to 0.21) | 3.81 (2.35 to 6.59) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 727 | 1.29 (1.15 to 1.44) | 1.22 (1.07 to 1.37) | 2026 | 4.63 (4.35 to 4.94) | 5.01 (4.66 to 5.38) | 3.59 (3.16 to 4.08) | rose |
| `TRICOLON / tricolon` | 1896 | 3.37 (3.17 to 3.60) | 3.64 (3.38 to 3.92) | 2165 | 4.95 (4.63 to 5.28) | 5.35 (4.99 to 5.73) | 1.47 (1.34 to 1.61) | rose |
| `LLM_DICTION / -` | 906 | 1.61 (1.42 to 1.84) | 1.60 (1.44 to 1.76) | 1015 | 2.32 (2.10 to 2.55) | 2.49 (2.22 to 2.78) | 1.44 (1.22 to 1.69) | rose |
| `CONSULTANT_REGISTER / -` | 734 | 1.30 (1.17 to 1.47) | 1.46 (1.29 to 1.64) | 782 | 1.79 (1.61 to 1.97) | 1.82 (1.63 to 2.03) | 1.37 (1.17 to 1.59) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 360 | 0.64 (0.55 to 0.73) | 0.60 (0.51 to 0.69) | 379 | 0.87 (0.77 to 0.97) | 0.87 (0.75 to 1.00) | 1.36 (1.13 to 1.64) | rose |
| `VAGUE_QUANTIFIER / -` | 173 | 0.31 (0.26 to 0.36) | 0.36 (0.29 to 0.43) | 182 | 0.42 (0.35 to 0.49) | 0.42 (0.33 to 0.51) | 1.35 (1.07 to 1.69) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 91 | 0.16 (0.13 to 0.20) | 0.16 (0.12 to 0.21) | 93 | 0.21 (0.17 to 0.26) | 0.21 (0.16 to 0.27) | 1.32 (0.95 to 1.83) | flat |
| `FRAME_MARKER / -` | 16 | 0.03 (0.01 to 0.05) | 0.03 (0.01 to 0.05) | 14 | 0.03 (0.02 to 0.05) | 0.04 (0.01 to 0.07) | 1.13 (0.52 to 2.46) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 198 | 0.35 (0.29 to 0.41) | 0.37 (0.30 to 0.45) | 165 | 0.38 (0.32 to 0.44) | 0.39 (0.32 to 0.47) | 1.07 (0.85 to 1.35) | flat |
| `CLOSER / -` | 34 | 0.06 (0.04 to 0.08) | 0.06 (0.04 to 0.09) | 23 | 0.05 (0.03 to 0.08) | 0.03 (0.02 to 0.05) | 0.87 (0.49 to 1.50) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 124 | 0.22 (0.18 to 0.26) | 0.26 (0.20 to 0.32) | 81 | 0.19 (0.14 to 0.23) | 0.16 (0.12 to 0.21) | 0.84 (0.60 to 1.13) | flat |
| `BORROWED_RIGOUR / -` | 264 | 0.47 (0.38 to 0.56) | 0.41 (0.34 to 0.50) | 167 | 0.38 (0.32 to 0.45) | 0.41 (0.33 to 0.50) | 0.81 (0.64 to 1.07) | flat |
| `EMPTY_FRAME / -` | 30 | 0.05 (0.03 to 0.08) | 0.04 (0.02 to 0.07) | 16 | 0.04 (0.02 to 0.06) | 0.02 (0.01 to 0.03) | 0.69 (0.32 to 1.44) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 286 | 0.51 (0.44 to 0.58) | 0.44 (0.38 to 0.52) | 118 | 0.27 (0.22 to 0.32) | 0.28 (0.19 to 0.40) | 0.53 (0.40 to 0.66) | fell |

### conclusion

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 19 | 0.12 (0.05 to 0.19) | 0.14 (0.05 to 0.26) | 173 | 1.42 (1.07 to 1.80) | 1.28 (0.99 to 1.58) | 12.29 (6.93 to 26.99) | rose |
| `PARTICIPIAL_TAIL` | 238 | 1.45 (1.23 to 1.69) | 1.50 (1.26 to 1.75) | 585 | 4.82 (4.41 to 5.23) | 5.08 (4.61 to 5.55) | 3.32 (2.78 to 4.02) | rose |
| `HOLLOW_BOOSTER` | 7 | 0.04 (0.01 to 0.08) | 0.04 (0.01 to 0.07) | 15 | 0.12 (0.06 to 0.19) | 0.09 (0.04 to 0.15) | 2.89 (1.23 to 9.03) | rose |
| `CLOSER` | 16 | 0.10 (0.05 to 0.15) | 0.09 (0.04 to 0.16) | 22 | 0.18 (0.11 to 0.26) | 0.20 (0.11 to 0.30) | 1.86 (0.95 to 3.79) | flat |
| `TRICOLON` | 594 | 3.62 (3.28 to 4.00) | 3.63 (3.26 to 4.02) | 710 | 5.85 (5.34 to 6.34) | 5.81 (5.28 to 6.30) | 1.61 (1.41 to 1.83) | rose |
| `CORRECTIVE_CONTRAST` | 58 | 0.35 (0.25 to 0.47) | 0.30 (0.20 to 0.43) | 67 | 0.55 (0.42 to 0.69) | 0.43 (0.31 to 0.56) | 1.56 (1.02 to 2.40) | rose |
| `CONSULTANT_REGISTER` | 260 | 1.59 (1.33 to 1.86) | 1.88 (1.58 to 2.20) | 291 | 2.40 (2.10 to 2.73) | 2.60 (2.25 to 2.96) | 1.51 (1.22 to 1.88) | rose |
| `GAPPED_ANTITHESIS` | 1 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.01) | 1 | 0.01 (0.00 to 0.03) | 0.00 (0.00 to 0.00) | 1.35 (0.00 to inf) | too few |
| `ALTERNATIVE_FRAMING` | 143 | 0.87 (0.70 to 1.04) | 0.80 (0.64 to 0.98) | 134 | 1.10 (0.90 to 1.34) | 0.83 (0.67 to 1.01) | 1.27 (0.96 to 1.67) | flat |
| `LLM_DICTION` | 455 | 2.78 (2.47 to 3.07) | 2.90 (2.55 to 3.26) | 409 | 3.37 (2.99 to 3.77) | 3.52 (3.09 to 3.95) | 1.21 (1.03 to 1.43) | rose |
| `EMPHATIC_REFLEXIVE` | 17 | 0.10 (0.03 to 0.20) | 0.04 (0.02 to 0.08) | 15 | 0.12 (0.06 to 0.19) | 0.08 (0.04 to 0.13) | 1.19 (0.49 to 4.25) | flat |
| `ABSTRACT_ADVERB` | 111 | 0.68 (0.55 to 0.81) | 0.53 (0.39 to 0.67) | 87 | 0.72 (0.56 to 0.87) | 0.63 (0.48 to 0.79) | 1.06 (0.78 to 1.42) | flat |
| `VAGUE_QUANTIFIER` | 86 | 0.52 (0.39 to 0.67) | 0.47 (0.34 to 0.60) | 49 | 0.40 (0.30 to 0.52) | 0.38 (0.27 to 0.51) | 0.77 (0.51 to 1.13) | flat |
| `BORROWED_RIGOUR` | 72 | 0.44 (0.31 to 0.59) | 0.46 (0.32 to 0.61) | 38 | 0.31 (0.21 to 0.42) | 0.29 (0.18 to 0.40) | 0.71 (0.44 to 1.11) | flat |
| `FRAME_MARKER` | 10 | 0.06 (0.03 to 0.10) | 0.07 (0.02 to 0.14) | 5 | 0.04 (0.01 to 0.08) | 0.04 (0.01 to 0.09) | 0.68 (0.13 to 1.96) | too few |
| `HEDGE_STACK` | 2 | 0.01 (0.00 to 0.04) | 0.01 (0.00 to 0.04) | 1 | 0.01 (0.00 to 0.03) | 0.00 (0.00 to 0.00) | 0.68 (0.00 to inf) | too few |
| `EMPTY_FRAME` | 5 | 0.03 (0.01 to 0.06) | 0.02 (0.00 to 0.05) | 1 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 0.27 (0.00 to 1.77) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 19 | 0.12 (0.05 to 0.19) | 0.14 (0.05 to 0.26) | 173 | 1.42 (1.07 to 1.80) | 1.28 (0.99 to 1.58) | 12.29 (6.93 to 26.99) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than` | 18 | 0.11 (0.05 to 0.18) | 0.09 (0.04 to 0.14) | 68 | 0.56 (0.41 to 0.73) | 0.38 (0.28 to 0.49) | 5.10 (2.80 to 11.31) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 238 | 1.45 (1.23 to 1.69) | 1.50 (1.26 to 1.75) | 585 | 4.82 (4.41 to 5.23) | 5.08 (4.61 to 5.55) | 3.32 (2.78 to 4.02) | rose |
| `HOLLOW_BOOSTER / -` | 7 | 0.04 (0.01 to 0.08) | 0.04 (0.01 to 0.07) | 15 | 0.12 (0.06 to 0.19) | 0.09 (0.04 to 0.15) | 2.89 (1.23 to 9.03) | rose |
| `CLOSER / -` | 16 | 0.10 (0.05 to 0.15) | 0.09 (0.04 to 0.16) | 22 | 0.18 (0.11 to 0.26) | 0.20 (0.11 to 0.30) | 1.86 (0.95 to 3.79) | flat |
| `TRICOLON / tricolon` | 594 | 3.62 (3.28 to 4.00) | 3.63 (3.26 to 4.02) | 710 | 5.85 (5.34 to 6.34) | 5.81 (5.28 to 6.30) | 1.61 (1.41 to 1.83) | rose |
| `CONSULTANT_REGISTER / -` | 260 | 1.59 (1.33 to 1.86) | 1.88 (1.58 to 2.20) | 291 | 2.40 (2.10 to 2.73) | 2.60 (2.25 to 2.96) | 1.51 (1.22 to 1.88) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 51 | 0.31 (0.21 to 0.42) | 0.25 (0.15 to 0.37) | 55 | 0.45 (0.34 to 0.58) | 0.38 (0.27 to 0.50) | 1.46 (0.93 to 2.31) | flat |
| `LLM_DICTION / -` | 455 | 2.78 (2.47 to 3.07) | 2.90 (2.55 to 3.26) | 409 | 3.37 (2.99 to 3.77) | 3.52 (3.09 to 3.95) | 1.21 (1.03 to 1.43) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 17 | 0.10 (0.03 to 0.20) | 0.04 (0.02 to 0.08) | 15 | 0.12 (0.06 to 0.19) | 0.08 (0.04 to 0.13) | 1.19 (0.49 to 4.25) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 111 | 0.68 (0.55 to 0.81) | 0.53 (0.39 to 0.67) | 87 | 0.72 (0.56 to 0.87) | 0.63 (0.48 to 0.79) | 1.06 (0.78 to 1.42) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 101 | 0.62 (0.48 to 0.76) | 0.58 (0.43 to 0.74) | 59 | 0.49 (0.37 to 0.63) | 0.42 (0.30 to 0.56) | 0.79 (0.56 to 1.12) | flat |
| `VAGUE_QUANTIFIER / -` | 86 | 0.52 (0.39 to 0.67) | 0.47 (0.34 to 0.60) | 49 | 0.40 (0.30 to 0.52) | 0.38 (0.27 to 0.51) | 0.77 (0.51 to 1.13) | flat |
| `BORROWED_RIGOUR / -` | 72 | 0.44 (0.31 to 0.59) | 0.46 (0.32 to 0.61) | 38 | 0.31 (0.21 to 0.42) | 0.29 (0.18 to 0.40) | 0.71 (0.44 to 1.11) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 24 | 0.15 (0.07 to 0.23) | 0.13 (0.07 to 0.21) | 7 | 0.06 (0.02 to 0.11) | 0.03 (0.01 to 0.06) | 0.39 (0.11 to 1.00) | flat |

### all

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 771 | 0.15 (0.11 to 0.20) | 0.15 (0.11 to 0.20) | 3751 | 0.98 (0.82 to 1.15) | 0.88 (0.77 to 1.01) | 6.32 (4.61 to 8.96) | rose |
| `PARTICIPIAL_TAIL` | 6297 | 1.27 (1.18 to 1.35) | 1.26 (1.18 to 1.34) | 16997 | 4.44 (4.26 to 4.64) | 4.66 (4.48 to 4.86) | 3.51 (3.25 to 3.82) | rose |
| `HOLLOW_BOOSTER` | 240 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 598 | 0.16 (0.14 to 0.17) | 0.16 (0.14 to 0.18) | 3.24 (2.69 to 3.96) | rose |
| `ABSTRACT_ADVERB` | 2662 | 0.54 (0.50 to 0.57) | 0.52 (0.48 to 0.56) | 3125 | 0.82 (0.77 to 0.87) | 0.84 (0.79 to 0.89) | 1.53 (1.39 to 1.68) | rose |
| `CONSULTANT_REGISTER` | 4267 | 0.86 (0.78 to 0.94) | 0.85 (0.78 to 0.92) | 4803 | 1.25 (1.17 to 1.34) | 1.28 (1.18 to 1.37) | 1.46 (1.31 to 1.65) | rose |
| `CORRECTIVE_CONTRAST` | 1408 | 0.28 (0.26 to 0.31) | 0.27 (0.24 to 0.29) | 1576 | 0.41 (0.37 to 0.45) | 0.40 (0.36 to 0.44) | 1.45 (1.28 to 1.65) | rose |
| `TRICOLON` | 16114 | 3.24 (3.12 to 3.37) | 3.30 (3.19 to 3.41) | 17574 | 4.59 (4.39 to 4.80) | 4.69 (4.51 to 4.87) | 1.42 (1.34 to 1.50) | rose |
| `LLM_DICTION` | 7283 | 1.46 (1.37 to 1.56) | 1.45 (1.36 to 1.55) | 7684 | 2.01 (1.88 to 2.13) | 2.12 (1.99 to 2.25) | 1.37 (1.25 to 1.50) | rose |
| `EMPHATIC_REFLEXIVE` | 592 | 0.12 (0.10 to 0.13) | 0.12 (0.10 to 0.14) | 540 | 0.14 (0.12 to 0.16) | 0.13 (0.11 to 0.14) | 1.19 (0.99 to 1.42) | flat |
| `BORROWED_RIGOUR` | 1270 | 0.26 (0.22 to 0.29) | 0.28 (0.23 to 0.34) | 1129 | 0.29 (0.27 to 0.33) | 0.29 (0.26 to 0.33) | 1.16 (0.99 to 1.35) | flat |
| `CLOSER` | 346 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.09) | 307 | 0.08 (0.07 to 0.09) | 0.07 (0.06 to 0.08) | 1.15 (0.94 to 1.39) | flat |
| `GAPPED_ANTITHESIS` | 81 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 71 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.14 (0.80 to 1.55) | flat |
| `ALTERNATIVE_FRAMING` | 4929 | 0.99 (0.95 to 1.04) | 1.00 (0.95 to 1.06) | 4277 | 1.12 (1.05 to 1.19) | 1.07 (1.01 to 1.14) | 1.13 (1.05 to 1.23) | rose |
| `VAGUE_QUANTIFIER` | 1203 | 0.24 (0.22 to 0.26) | 0.24 (0.22 to 0.26) | 1025 | 0.27 (0.25 to 0.29) | 0.28 (0.25 to 0.30) | 1.11 (0.98 to 1.25) | flat |
| `DISGUISE_METAPHOR` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.87 (0.13 to 3.55) | too few |
| `FRAME_MARKER` | 335 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 172 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.05) | 0.67 (0.53 to 0.84) | fell |
| `EMPTY_FRAME` | 436 | 0.09 (0.08 to 0.10) | 0.09 (0.08 to 0.10) | 208 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 0.62 (0.50 to 0.77) | fell |
| `NEG_ESCALATION` | 34 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.61 (0.30 to 1.13) | flat |
| `HEDGE_STACK` | 62 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.48 (0.27 to 0.84) | fell |
| `HOUSE_STYLE` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 771 | 0.15 (0.11 to 0.20) | 0.15 (0.11 to 0.20) | 3751 | 0.98 (0.82 to 1.15) | 0.88 (0.77 to 1.01) | 6.32 (4.61 to 8.96) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than` | 509 | 0.10 (0.09 to 0.12) | 0.10 (0.09 to 0.11) | 2045 | 0.53 (0.48 to 0.60) | 0.51 (0.47 to 0.56) | 5.22 (4.37 to 6.23) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 78 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 300 | 0.08 (0.06 to 0.10) | 0.07 (0.06 to 0.09) | 5.00 (3.45 to 7.07) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 6297 | 1.27 (1.18 to 1.35) | 1.26 (1.18 to 1.34) | 16997 | 4.44 (4.26 to 4.64) | 4.66 (4.48 to 4.86) | 3.51 (3.25 to 3.82) | rose |
| `HOLLOW_BOOSTER / -` | 240 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 598 | 0.16 (0.14 to 0.17) | 0.16 (0.14 to 0.18) | 3.24 (2.69 to 3.96) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 44 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 76 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 2.24 (1.44 to 3.49) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 2662 | 0.54 (0.50 to 0.57) | 0.52 (0.48 to 0.56) | 3125 | 0.82 (0.77 to 0.87) | 0.84 (0.79 to 0.89) | 1.53 (1.39 to 1.68) | rose |
| `CONSULTANT_REGISTER / -` | 4267 | 0.86 (0.78 to 0.94) | 0.85 (0.78 to 0.92) | 4803 | 1.25 (1.17 to 1.34) | 1.28 (1.18 to 1.37) | 1.46 (1.31 to 1.65) | rose |
| `TRICOLON / tricolon` | 16111 | 3.24 (3.12 to 3.37) | 3.30 (3.19 to 3.41) | 17572 | 4.59 (4.39 to 4.79) | 4.69 (4.51 to 4.87) | 1.42 (1.34 to 1.50) | rose |
| `LLM_DICTION / -` | 7283 | 1.46 (1.37 to 1.56) | 1.45 (1.36 to 1.55) | 7684 | 2.01 (1.88 to 2.13) | 2.12 (1.99 to 2.25) | 1.37 (1.25 to 1.50) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 1110 | 0.22 (0.20 to 0.24) | 0.21 (0.19 to 0.23) | 1133 | 0.30 (0.27 to 0.32) | 0.30 (0.27 to 0.33) | 1.33 (1.18 to 1.49) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 592 | 0.12 (0.10 to 0.13) | 0.12 (0.10 to 0.14) | 540 | 0.14 (0.12 to 0.16) | 0.13 (0.11 to 0.14) | 1.19 (0.99 to 1.42) | flat |
| `BORROWED_RIGOUR / -` | 1270 | 0.26 (0.22 to 0.29) | 0.28 (0.23 to 0.34) | 1129 | 0.29 (0.27 to 0.33) | 0.29 (0.26 to 0.33) | 1.16 (0.99 to 1.35) | flat |
| `CLOSER / -` | 346 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.09) | 307 | 0.08 (0.07 to 0.09) | 0.07 (0.06 to 0.08) | 1.15 (0.94 to 1.39) | flat |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 81 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 71 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.14 (0.80 to 1.55) | flat |
| `VAGUE_QUANTIFIER / -` | 1203 | 0.24 (0.22 to 0.26) | 0.24 (0.22 to 0.26) | 1025 | 0.27 (0.25 to 0.29) | 0.28 (0.25 to 0.30) | 1.11 (0.98 to 1.25) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of` | 976 | 0.20 (0.18 to 0.21) | 0.20 (0.18 to 0.22) | 642 | 0.17 (0.15 to 0.19) | 0.16 (0.14 to 0.17) | 0.85 (0.74 to 0.98) | fell |
| `FRAME_MARKER / -` | 335 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 172 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.05) | 0.67 (0.53 to 0.84) | fell |
| `EMPTY_FRAME / -` | 436 | 0.09 (0.08 to 0.10) | 0.09 (0.08 to 0.10) | 208 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 0.62 (0.50 to 0.77) | fell |
| `NEG_ESCALATION / neg_escalation` | 34 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.61 (0.30 to 1.13) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 3444 | 0.69 (0.66 to 0.73) | 0.70 (0.66 to 0.75) | 1590 | 0.42 (0.38 to 0.45) | 0.41 (0.37 to 0.44) | 0.60 (0.54 to 0.66) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 176 | 0.04 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 67 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 0.49 (0.34 to 0.70) | fell |
| `HEDGE_STACK / -` | 62 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.48 (0.27 to 0.84) | fell |

### body, subtypes with at least 20 findings

| subtype | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB / abstract_adverb / syntactically` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 40 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / necessitate` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 25 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / average` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enhance` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 43 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 56.59 (15.78 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / preserve` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 52.64 (14.84 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / underscore` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 31 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 40.80 (11.07 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / retain` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 35.54 (8.95 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reflect` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 128 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 33.69 (16.78 to 175.41) | rose |
| `PARTICIPIAL_TAIL / participial_tail / capture` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 44 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 28.95 (10.17 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / extend` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 26.32 (6.60 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / ensure` | 20 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 362 | 0.13 (0.11 to 0.15) | 0.14 (0.12 to 0.16) | 23.82 (15.30 to 44.29) | rose |
| `PARTICIPIAL_TAIL / participial_tail / align` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 32 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 21.06 (7.40 to inf) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / structurally` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 85 | 0.03 (0.02 to 0.04) | 0.04 (0.02 to 0.05) | 18.64 (8.28 to 99.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / confirm` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 157 | 0.06 (0.05 to 0.07) | 0.07 (0.05 to 0.08) | 15.89 (8.31 to 48.69) | rose |
| `PARTICIPIAL_TAIL / participial_tail / highlight` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 120 | 0.04 (0.04 to 0.05) | 0.06 (0.04 to 0.08) | 15.79 (8.84 to 40.21) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cover` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 48 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 15.79 (6.93 to 73.84) | rose |
| `PARTICIPIAL_TAIL / participial_tail / exceed` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 34 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 14.92 (5.94 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / complete` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 12.72 (5.10 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / raise` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 12.50 (3.95 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / yield` | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 194 | 0.07 (0.06 to 0.08) | 0.08 (0.07 to 0.09) | 11.61 (7.17 to 21.85) | rose |
| `PARTICIPIAL_TAIL / participial_tail / demonstrate` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 225 | 0.08 (0.07 to 0.09) | 0.10 (0.08 to 0.12) | 10.21 (6.73 to 17.31) | rose |
| `PARTICIPIAL_TAIL / participial_tail / incorporate` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 31 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 10.20 (4.24 to 52.66) | rose |
| `PARTICIPIAL_TAIL / participial_tail / establish` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 9.54 (4.07 to 47.50) | rose |
| `PARTICIPIAL_TAIL / participial_tail / match` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 61 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 8.92 (4.78 to 24.60) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enable` | 101 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 683 | 0.25 (0.22 to 0.28) | 0.27 (0.24 to 0.31) | 8.90 (6.87 to 11.98) | rose |
| `PARTICIPIAL_TAIL / participial_tail / support` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 74 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 8.85 (5.01 to 19.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / produce` | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 121 | 0.04 (0.04 to 0.05) | 0.04 (0.03 to 0.05) | 8.85 (5.46 to 17.15) | rose |
| `PARTICIPIAL_TAIL / participial_tail / maintain` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 47 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 8.84 (4.76 to 26.82) | rose |
| `PARTICIPIAL_TAIL / participial_tail / prevent` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 92 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 8.65 (5.30 to 17.07) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / semantically` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 39 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 8.55 (3.84 to 29.11) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / intentionally` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 36 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 7.90 (3.66 to 27.84) | rose |
| `PARTICIPIAL_TAIL / participial_tail / address` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7.90 (2.87 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / offer` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 77 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 7.80 (4.23 to 19.05) | rose |
| `PARTICIPIAL_TAIL / participial_tail / employ` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 7.63 (2.81 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / motivate` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 7.63 (3.38 to 35.72) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / numerically` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.02) | 7.57 (2.93 to 39.55) | rose |
| `EM_DASH / - / paired aside` | 256 | 0.07 (0.04 to 0.11) | 0.07 (0.05 to 0.11) | 1417 | 0.52 (0.42 to 0.63) | 0.44 (0.37 to 0.52) | 7.28 (4.51 to 12.54) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reveal` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7.24 (2.89 to 37.15) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leverage` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 59 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 7.06 (3.88 to 18.04) | rose |
| `PARTICIPIAL_TAIL / participial_tail / feature` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6.91 (2.70 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / suggest` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 72 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 6.77 (3.73 to 15.15) | rose |
| `PARTICIPIAL_TAIL / participial_tail / achieve` | 50 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 252 | 0.09 (0.08 to 0.11) | 0.11 (0.09 to 0.13) | 6.63 (4.74 to 9.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / account` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 44 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 6.43 (3.38 to 17.65) | rose |
| `PARTICIPIAL_TAIL / participial_tail / introduce` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 44 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 6.43 (3.49 to 16.35) | rose |
| `PARTICIPIAL_TAIL / participial_tail / deliver` | 8 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 39 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 6.42 (2.17 to 61.68) | rose |
| `PARTICIPIAL_TAIL / participial_tail / utilize` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 39 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 6.42 (2.96 to 24.14) | rose |
| `EM_DASH / - / pivot (not X — Y)` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 34 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 6.39 (2.60 to 22.79) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reach` | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 92 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 6.37 (3.88 to 12.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / eliminate` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 116 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.06) | 6.36 (4.10 to 11.59) | rose |
| `PARTICIPIAL_TAIL / participial_tail / validate` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 6.14 (2.69 to 30.80) | rose |
| `PARTICIPIAL_TAIL / participial_tail / expose` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6.05 (2.29 to 34.36) | rose |
| `EM_DASH / - / single break` | 231 | 0.06 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 1049 | 0.39 (0.32 to 0.46) | 0.36 (0.30 to 0.41) | 5.98 (4.33 to 8.64) | rose |
| `PARTICIPIAL_TAIL / participial_tail / assign` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.79 (2.40 to 27.59) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition / X, not Y` | 56 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 246 | 0.09 (0.07 to 0.12) | 0.08 (0.06 to 0.11) | 5.78 (3.78 to 8.67) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leave` | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 140 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 5.76 (3.93 to 9.15) | rose |
| `PARTICIPIAL_TAIL / participial_tail / force` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 35 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 5.76 (2.77 to 18.52) | rose |
| `PARTICIPIAL_TAIL / participial_tail / optimize` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 5.70 (2.56 to 22.24) | rose |
| `PARTICIPIAL_TAIL / participial_tail / operate` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 5.64 (2.62 to 16.44) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than / rather than` | 352 | 0.10 (0.08 to 0.11) | 0.09 (0.08 to 0.11) | 1462 | 0.54 (0.47 to 0.61) | 0.51 (0.46 to 0.57) | 5.47 (4.48 to 6.68) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / substantially` | 42 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 172 | 0.06 (0.05 to 0.07) | 0.07 (0.05 to 0.08) | 5.39 (3.48 to 9.07) | rose |
| `PARTICIPIAL_TAIL / participial_tail / create` | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 80 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 5.26 (3.00 to 10.27) | rose |
| `PARTICIPIAL_TAIL / participial_tail / apply` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.26 (2.01 to 30.51) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / historically` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5.26 (1.90 to 28.92) | rose |
| `PARTICIPIAL_TAIL / participial_tail / contribute` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.26 (1.99 to 27.92) | rose |
| `PARTICIPIAL_TAIL / participial_tail / illustrate` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5.26 (1.96 to 32.34) | rose |
| `PARTICIPIAL_TAIL / participial_tail / present` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.26 (2.07 to 28.38) | rose |
| `PARTICIPIAL_TAIL / participial_tail / limit` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 65 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 5.03 (2.99 to 9.90) | rose |
| `PARTICIPIAL_TAIL / participial_tail / maximize` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 4.89 (2.19 to 17.81) | rose |
| `PARTICIPIAL_TAIL / participial_tail / facilitate` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 4.77 (2.17 to 14.24) | rose |
| `PARTICIPIAL_TAIL / participial_tail / indicate` | 96 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 342 | 0.13 (0.11 to 0.14) | 0.14 (0.12 to 0.17) | 4.69 (3.63 to 6.21) | rose |
| `PARTICIPIAL_TAIL / participial_tail / outperform` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 38 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 4.55 (2.36 to 11.41) | rose |
| `EM_DASH / - / pivot (— it's Y)` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 37 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.43 (1.93 to 17.08) | rose |
| `PARTICIPIAL_TAIL / participial_tail / allow` | 171 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 571 | 0.21 (0.19 to 0.23) | 0.23 (0.20 to 0.25) | 4.39 (3.50 to 5.63) | rose |
| `PARTICIPIAL_TAIL / participial_tail / span` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 4.28 (2.10 to 12.88) | rose |
| `PARTICIPIAL_TAIL / participial_tail / focus` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 45 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 4.23 (2.45 to 8.64) | rose |
| `PARTICIPIAL_TAIL / participial_tail / place` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 4.17 (1.94 to 14.23) | rose |
| `PARTICIPIAL_TAIL / participial_tail / execute` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 22 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.02) | 4.14 (2.03 to 12.86) | rose |
| `PARTICIPIAL_TAIL / participial_tail / make` | 188 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 581 | 0.21 (0.19 to 0.23) | 0.21 (0.19 to 0.23) | 4.07 (3.24 to 5.28) | rose |
| `PARTICIPIAL_TAIL / participial_tail / form` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 43 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 4.04 (2.26 to 8.76) | rose |
| `PARTICIPIAL_TAIL / participial_tail / minimize` | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 46 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 4.04 (2.25 to 8.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail / give` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 71 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 3.89 (2.40 to 6.82) | rose |
| `PARTICIPIAL_TAIL / participial_tail / remove` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.78 (1.73 to 11.14) | rose |
| `HOLLOW_BOOSTER / - / -` | 166 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 451 | 0.17 (0.15 to 0.19) | 0.18 (0.15 to 0.20) | 3.58 (2.89 to 4.56) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / functionally` | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 95 | 0.03 (0.02 to 0.05) | 0.04 (0.03 to 0.06) | 3.57 (2.10 to 6.41) | rose |
| `PARTICIPIAL_TAIL / participial_tail / correspond` | 50 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 134 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 3.53 (2.42 to 5.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / improve` | 31 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 83 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 3.52 (2.32 to 5.89) | rose |
| `PARTICIPIAL_TAIL / participial_tail / replace` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.51 (1.42 to 12.21) | rose |
| `PARTICIPIAL_TAIL / participial_tail / combine` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.45 (1.52 to 11.25) | rose |
| `PARTICIPIAL_TAIL / participial_tail / keep` | 17 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 44 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 3.41 (1.98 to 6.44) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / formally` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 62 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 3.40 (1.56 to 9.37) | rose |
| `PARTICIPIAL_TAIL / participial_tail / avoid` | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 100 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 3.29 (2.22 to 5.13) | rose |
| `PARTICIPIAL_TAIL / participial_tail / render` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 3.23 (1.40 to 11.91) | rose |
| `PARTICIPIAL_TAIL / participial_tail / provide` | 95 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 232 | 0.09 (0.07 to 0.10) | 0.09 (0.07 to 0.11) | 3.21 (2.40 to 4.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reduce` | 115 | 0.03 (0.03 to 0.04) | 0.03 (0.02 to 0.04) | 278 | 0.10 (0.09 to 0.12) | 0.11 (0.09 to 0.13) | 3.18 (2.54 to 4.11) | rose |
| `PARTICIPIAL_TAIL / participial_tail / compare` | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 36 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 3.16 (1.68 to 7.92) | rose |
| `PARTICIPIAL_TAIL / participial_tail / add` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 59 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.03) | 3.11 (1.76 to 6.33) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / statistically` | 16 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 37 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 3.04 (1.56 to 6.84) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / fundamentally` | 31 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 71 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 3.01 (1.83 to 5.39) | rose |
| `PARTICIPIAL_TAIL / participial_tail / require` | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 143 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 2.99 (2.15 to 4.22) | rose |
| `PARTICIPIAL_TAIL / participial_tail / represent` | 30 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 68 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 2.98 (1.94 to 4.90) | rose |
| `PARTICIPIAL_TAIL / participial_tail / bring` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 2.96 (1.38 to 8.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / bypass` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.92 (1.27 to 10.32) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / proportionally` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.90 (1.37 to 7.32) | rose |
| `PARTICIPIAL_TAIL / participial_tail / perform` | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 26 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 2.85 (1.44 to 6.16) | rose |
| `PARTICIPIAL_TAIL / participial_tail / scale` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 15 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.82 (1.12 to 12.31) | rose |
| `PARTICIPIAL_TAIL / participial_tail / show` | 58 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 121 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 2.75 (1.97 to 3.95) | rose |
| `PARTICIPIAL_TAIL / participial_tail / incur` | 20 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.63 (1.28 to 7.70) | rose |
| `PARTICIPIAL_TAIL / participial_tail / comprise` | 15 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.63 (1.26 to 6.71) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / mutually` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.63 (1.28 to 6.24) | rose |
| `PARTICIPIAL_TAIL / participial_tail / select` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.63 (1.01 to 8.92) | rose |
| `PARTICIPIAL_TAIL / participial_tail / target` | 16 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 32 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 2.63 (1.43 to 5.69) | rose |
| `PARTICIPIAL_TAIL / participial_tail / update` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.63 (1.06 to 8.86) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cause` | 65 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 126 | 0.05 (0.04 to 0.06) | 0.04 (0.03 to 0.05) | 2.55 (1.79 to 3.69) | rose |
| `PARTICIPIAL_TAIL / participial_tail / contain` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.51 (1.21 to 5.97) | rose |
| `PARTICIPIAL_TAIL / participial_tail / aim` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.49 (1.08 to 9.28) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / empirically` | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 49 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 2.48 (1.46 to 4.74) | rose |
| `PARTICIPIAL_TAIL / participial_tail / generate` | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 41 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2.45 (1.42 to 4.40) | rose |
| `PARTICIPIAL_TAIL / participial_tail / process` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.44 (0.92 to 8.66) | flat |
| `PARTICIPIAL_TAIL / participial_tail / result` | 221 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.08) | 407 | 0.15 (0.13 to 0.17) | 0.17 (0.15 to 0.20) | 2.42 (1.99 to 2.96) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / architecturally` | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.41 (1.09 to 6.15) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling / X, not Y` | 29 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 53 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 2.41 (1.45 to 4.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / range` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 42 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 2.30 (1.35 to 4.05) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / systematically` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.27 (0.74 to 10.05) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / additionally` | 85 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 130 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 2.01 (1.43 to 2.91) | rose |
| `PARTICIPIAL_TAIL / participial_tail / compute` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 12 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.97 (0.73 to 6.93) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / specifically` | 128 | 0.04 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 181 | 0.07 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 1.86 (1.40 to 2.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / move` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.84 (0.68 to 5.26) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lead` | 224 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 307 | 0.11 (0.10 to 0.13) | 0.12 (0.10 to 0.13) | 1.80 (1.44 to 2.27) | rose |
| `PARTICIPIAL_TAIL / participial_tail / set` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 15 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.79 (0.80 to 4.87) | flat |
| `PARTICIPIAL_TAIL / participial_tail / obtain` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.75 (0.67 to 4.74) | flat |
| `PARTICIPIAL_TAIL / participial_tail / exploit` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 1.72 (0.78 to 4.32) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consume` | 14 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.69 (0.82 to 3.88) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / logically` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 29 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 1.59 (0.85 to 3.38) | flat |
| `PARTICIPIAL_TAIL / participial_tail / increase` | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 76 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 1.59 (1.12 to 2.30) | rose |
| `GAPPED_ANTITHESIS / gapped_antithesis / before/after` | 34 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 41 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.59 (0.99 to 2.60) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / experimentally` | 15 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.58 (0.67 to 3.97) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / mathematically` | 15 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.58 (0.73 to 3.48) | flat |
| `TRICOLON / tricolon / enumeration` | 3321 | 0.93 (0.87 to 0.99) | 0.92 (0.87 to 0.98) | 3737 | 1.37 (1.28 to 1.46) | 1.39 (1.32 to 1.47) | 1.48 (1.35 to 1.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / store` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.48 (0.73 to 3.46) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / computationally` | 99 | 0.03 (0.02 to 0.04) | 0.02 (0.02 to 0.03) | 109 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 1.45 (1.02 to 2.12) | rose |
| `CONSULTANT_REGISTER / - / -` | 2407 | 0.67 (0.60 to 0.75) | 0.66 (0.60 to 0.72) | 2638 | 0.97 (0.89 to 1.06) | 0.98 (0.90 to 1.07) | 1.44 (1.25 to 1.67) | rose |
| `BORROWED_RIGOUR / - / -` | 694 | 0.19 (0.16 to 0.23) | 0.21 (0.17 to 0.26) | 748 | 0.27 (0.24 to 0.31) | 0.27 (0.24 to 0.31) | 1.42 (1.18 to 1.73) | rose |
| `PARTICIPIAL_TAIL / participial_tail / start` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 29 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 1.41 (0.81 to 2.49) | flat |
| `PARTICIPIAL_TAIL / participial_tail / implement` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.40 (0.52 to 3.40) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / virtually` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.39 (0.58 to 3.17) | flat |
| `TRICOLON / tricolon / list-like` | 6286 | 1.75 (1.69 to 1.83) | 1.76 (1.69 to 1.83) | 6579 | 2.42 (2.29 to 2.54) | 2.43 (2.32 to 2.54) | 1.38 (1.29 to 1.47) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated / not X but Y` | 685 | 0.19 (0.17 to 0.21) | 0.18 (0.16 to 0.20) | 712 | 0.26 (0.24 to 0.29) | 0.26 (0.23 to 0.29) | 1.37 (1.19 to 1.57) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / essentially` | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 27 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 1.37 (0.75 to 2.61) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consist` | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 23 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 1.32 (0.72 to 2.37) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / maximally` | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.32 (0.36 to 4.49) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lower` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.32 (0.61 to 2.88) | flat |
| `LLM_DICTION / - / -` | 4426 | 1.24 (1.14 to 1.34) | 1.19 (1.09 to 1.29) | 4341 | 1.59 (1.47 to 1.73) | 1.64 (1.53 to 1.76) | 1.29 (1.16 to 1.45) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / practically` | 31 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.27 (0.74 to 2.27) | flat |
| `PARTICIPIAL_TAIL / participial_tail / assume` | 52 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 49 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.24 (0.77 to 1.97) | flat |
| `PARTICIPIAL_TAIL / participial_tail / mean` | 85 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 80 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 1.24 (0.85 to 1.83) | flat |
| `PARTICIPIAL_TAIL / participial_tail / use` | 336 | 0.09 (0.08 to 0.11) | 0.09 (0.08 to 0.11) | 316 | 0.12 (0.10 to 0.13) | 0.12 (0.10 to 0.14) | 1.24 (1.01 to 1.49) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / temporally` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 1.21 (0.58 to 2.69) | flat |
| `PARTICIPIAL_TAIL / participial_tail / save` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 10 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.20 (0.44 to 2.96) | flat |
| `CLOSER / - / -` | 214 | 0.06 (0.05 to 0.07) | 0.07 (0.05 to 0.08) | 194 | 0.07 (0.06 to 0.08) | 0.06 (0.05 to 0.07) | 1.19 (0.93 to 1.53) | flat |
| `TRICOLON / tricolon / figure` | 1402 | 0.39 (0.36 to 0.43) | 0.40 (0.37 to 0.44) | 1266 | 0.46 (0.43 to 0.50) | 0.46 (0.42 to 0.49) | 1.19 (1.06 to 1.34) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / naturally` | 49 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 44 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.18 (0.70 to 1.94) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / itself` | 331 | 0.09 (0.08 to 0.11) | 0.09 (0.08 to 0.11) | 296 | 0.11 (0.09 to 0.13) | 0.10 (0.08 to 0.11) | 1.18 (0.94 to 1.49) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / themselves` | 68 | 0.02 (0.01 to 0.02) | 0.02 (0.02 to 0.03) | 59 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.02) | 1.14 (0.78 to 1.66) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / marginally` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 13 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.07 (0.39 to 2.74) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / spatially` | 57 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 45 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.04 (0.53 to 2.14) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / incrementally` | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0.99 (0.32 to 3.04) | flat |
| `VAGUE_QUANTIFIER / - / -` | 539 | 0.15 (0.13 to 0.17) | 0.14 (0.12 to 0.16) | 394 | 0.14 (0.12 to 0.16) | 0.14 (0.12 to 0.16) | 0.96 (0.79 to 1.17) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / dramatically` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0.91 (0.30 to 2.31) | flat |
| `PARTICIPIAL_TAIL / participial_tail / exhibit` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.90 (0.31 to 3.03) | flat |
| `PARTICIPIAL_TAIL / participial_tail / run` | 28 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.89 (0.48 to 1.58) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / thermally` | 18 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 12 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.88 (0.27 to 5.07) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of / instead of` | 721 | 0.20 (0.18 to 0.22) | 0.20 (0.18 to 0.22) | 478 | 0.18 (0.15 to 0.20) | 0.17 (0.15 to 0.19) | 0.87 (0.74 to 1.02) | flat |
| `PARTICIPIAL_TAIL / participial_tail / take` | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.86 (0.45 to 1.52) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / theoretically` | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.86 (0.40 to 1.63) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / periodically` | 19 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.83 (0.33 to 1.82) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / partially` | 120 | 0.03 (0.02 to 0.05) | 0.03 (0.02 to 0.05) | 71 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 0.78 (0.47 to 1.39) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / commercially` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 14 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.74 (0.31 to 1.55) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / gradually` | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.73 (0.28 to 1.70) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / vertically` | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.72 (0.35 to 1.69) | flat |
| `GAPPED_ANTITHESIS / gapped_antithesis / opposed verbs` | 34 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.70 (0.34 to 1.26) | flat |
| `NEG_ESCALATION / neg_escalation / modal` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.70 (0.24 to 1.63) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / conceptually` | 19 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.69 (0.28 to 1.69) | flat |
| `FRAME_MARKER / - / -` | 263 | 0.07 (0.06 to 0.09) | 0.07 (0.06 to 0.09) | 138 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 0.69 (0.53 to 0.88) | fell |
| `PARTICIPIAL_TAIL / participial_tail / consider` | 47 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 23 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 0.64 (0.37 to 1.08) | flat |
| `EMPTY_FRAME / - / -` | 363 | 0.10 (0.09 to 0.12) | 0.11 (0.09 to 0.13) | 177 | 0.07 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 0.64 (0.50 to 0.81) | fell |
| `PARTICIPIAL_TAIL / participial_tail / imply` | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.63 (0.25 to 1.80) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / traditionally` | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 15 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.62 (0.29 to 1.17) | flat |
| `ALTERNATIVE_FRAMING / af_less_than / more...than` | 1726 | 0.48 (0.45 to 0.51) | 0.49 (0.45 to 0.53) | 793 | 0.29 (0.26 to 0.32) | 0.29 (0.26 to 0.32) | 0.60 (0.54 to 0.68) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft` | 44 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.60 (0.29 to 1.15) | flat |
| `PARTICIPIAL_TAIL / participial_tail / be` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.58 (0.25 to 1.23) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / potentially` | 138 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 60 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.02) | 0.57 (0.37 to 0.81) | fell |
| `ALTERNATIVE_FRAMING / af_less_than / less...than` | 942 | 0.26 (0.24 to 0.29) | 0.27 (0.24 to 0.30) | 402 | 0.15 (0.13 to 0.17) | 0.15 (0.13 to 0.17) | 0.56 (0.48 to 0.65) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / drastically` | 24 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 8 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0.44 (0.14 to 0.99) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft, across sentences` | 93 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 0.42 (0.25 to 0.66) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / basically` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 0.41 (0.09 to 1.18) | flat |
| `HEDGE_STACK / - / -` | 51 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.34 (0.15 to 0.61) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / horizontally` | 22 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.30 (0.07 to 1.16) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / ideally` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.29 (0.08 to 0.65) | fell |
| `PARTICIPIAL_TAIL / participial_tail / have` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.27 (0.06 to 0.65) | fell |

With 23 body pattern rows at 95%, a few `rose` or `fell` verdicts near an interval edge are expected by chance.

### all, subtypes with at least 20 findings

| subtype | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB / abstract_adverb / syntactically` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 52 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / guide` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / necessitate` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 49 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 63.68 (17.92 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / underscore` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 48 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 62.38 (16.99 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / emphasize` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 45.48 (12.53 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enhance` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 68 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 44.18 (16.29 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / retain` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 36.39 (9.20 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / average` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 29.89 (7.93 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / encompass` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 28.59 (7.21 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reflect` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 136 | 0.04 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 25.25 (13.50 to 81.21) | rose |
| `PARTICIPIAL_TAIL / participial_tail / ensure` | 24 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 444 | 0.12 (0.10 to 0.13) | 0.12 (0.10 to 0.14) | 24.04 (15.97 to 41.24) | rose |
| `PARTICIPIAL_TAIL / participial_tail / preserve` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 52 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 22.53 (9.42 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / balance` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 17.54 (6.12 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / align` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 40 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 17.33 (6.98 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / capture` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 53 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 17.22 (7.87 to 89.98) | rose |
| `PARTICIPIAL_TAIL / participial_tail / highlight` | 15 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 188 | 0.05 (0.04 to 0.06) | 0.06 (0.05 to 0.07) | 16.29 (10.16 to 32.19) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / structurally` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 112 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 16.17 (8.20 to 46.17) | rose |
| `PARTICIPIAL_TAIL / participial_tail / confirm` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 172 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 15.97 (8.65 to 43.90) | rose |
| `PARTICIPIAL_TAIL / participial_tail / complete` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 15.16 (6.04 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / establish` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 56 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 14.56 (7.22 to 72.61) | rose |
| `PARTICIPIAL_TAIL / participial_tail / drive` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 14.30 (4.94 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / prove` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 13.00 (4.37 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / surpass` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 13.00 (3.29 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reuse` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 12.35 (4.23 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / extend` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 36 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 11.70 (4.95 to 54.13) | rose |
| `PARTICIPIAL_TAIL / participial_tail / hinder` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 11.70 (3.83 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / overlap` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 11.70 (3.61 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / showcase` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 11.70 (4.42 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / address` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 51 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 11.05 (5.44 to 34.52) | rose |
| `PARTICIPIAL_TAIL / participial_tail / exceed` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 39 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 10.14 (4.67 to 52.50) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reveal` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 39 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 10.14 (4.57 to 49.52) | rose |
| `PARTICIPIAL_TAIL / participial_tail / incorporate` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 46 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 9.96 (4.92 to 34.86) | rose |
| `PARTICIPIAL_TAIL / participial_tail / convert` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 9.53 (3.49 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / restrict` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 9.42 (4.01 to 47.51) | rose |
| `PARTICIPIAL_TAIL / participial_tail / demonstrate` | 49 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 351 | 0.09 (0.08 to 0.10) | 0.11 (0.09 to 0.12) | 9.31 (6.64 to 14.26) | rose |
| `PARTICIPIAL_TAIL / participial_tail / maintain` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 60 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 8.66 (4.85 to 21.22) | rose |
| `PARTICIPIAL_TAIL / participial_tail / motivate` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 73 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 8.62 (4.67 to 20.36) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enable` | 174 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.04) | 1133 | 0.30 (0.27 to 0.32) | 0.32 (0.29 to 0.36) | 8.46 (6.88 to 10.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / match` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 8.19 (4.43 to 21.54) | rose |
| `PARTICIPIAL_TAIL / participial_tail / offer` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 180 | 0.05 (0.04 to 0.06) | 0.06 (0.05 to 0.07) | 8.07 (5.41 to 13.44) | rose |
| `PARTICIPIAL_TAIL / participial_tail / yield` | 39 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 235 | 0.06 (0.05 to 0.07) | 0.07 (0.06 to 0.08) | 7.83 (5.17 to 13.00) | rose |
| `PARTICIPIAL_TAIL / participial_tail / prevent` | 21 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 126 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.04) | 7.80 (4.94 to 14.18) | rose |
| `PARTICIPIAL_TAIL / participial_tail / validate` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 42 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 7.80 (3.59 to 29.33) | rose |
| `PARTICIPIAL_TAIL / participial_tail / support` | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 111 | 0.03 (0.02 to 0.04) | 0.04 (0.03 to 0.05) | 7.59 (4.70 to 13.86) | rose |
| `PARTICIPIAL_TAIL / participial_tail / fail` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 7.36 (2.54 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cover` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 62 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 7.32 (3.97 to 17.20) | rose |
| `PARTICIPIAL_TAIL / participial_tail / produce` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 161 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 7.21 (4.68 to 12.69) | rose |
| `PARTICIPIAL_TAIL / participial_tail / suggest` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 97 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 7.00 (4.18 to 14.08) | rose |
| `PARTICIPIAL_TAIL / participial_tail / expose` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 37 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 6.87 (3.12 to 23.35) | rose |
| `PARTICIPIAL_TAIL / participial_tail / achieve` | 85 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 442 | 0.12 (0.10 to 0.13) | 0.13 (0.12 to 0.15) | 6.76 (5.22 to 8.90) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / semantically` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 57 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 6.73 (3.35 to 17.65) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / intentionally` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 41 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 6.66 (3.28 to 17.91) | rose |
| `EM_DASH / - / paired aside` | 415 | 0.08 (0.05 to 0.12) | 0.08 (0.05 to 0.11) | 2093 | 0.55 (0.45 to 0.66) | 0.48 (0.41 to 0.56) | 6.55 (4.27 to 10.62) | rose |
| `PARTICIPIAL_TAIL / participial_tail / serve` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6.50 (2.82 to 33.97) | rose |
| `PARTICIPIAL_TAIL / participial_tail / eliminate` | 34 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 168 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 6.42 (4.45 to 10.10) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leave` | 50 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 244 | 0.06 (0.05 to 0.07) | 0.07 (0.06 to 0.08) | 6.34 (4.73 to 9.10) | rose |
| `PARTICIPIAL_TAIL / participial_tail / assign` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6.24 (2.68 to 30.36) | rose |
| `EM_DASH / - / single break` | 331 | 0.07 (0.05 to 0.08) | 0.07 (0.05 to 0.08) | 1563 | 0.41 (0.34 to 0.48) | 0.38 (0.33 to 0.44) | 6.14 (4.60 to 8.40) | rose |
| `PARTICIPIAL_TAIL / participial_tail / form` | 15 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 70 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 6.06 (3.60 to 12.29) | rose |
| `PARTICIPIAL_TAIL / participial_tail / facilitate` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 50 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 5.91 (3.14 to 14.39) | rose |
| `PARTICIPIAL_TAIL / participial_tail / map` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.85 (2.28 to 32.19) | rose |
| `PARTICIPIAL_TAIL / participial_tail / deliver` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 71 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 5.77 (2.88 to 15.04) | rose |
| `PARTICIPIAL_TAIL / participial_tail / pose` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.72 (2.27 to 36.37) | rose |
| `PARTICIPIAL_TAIL / participial_tail / raise` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.72 (2.45 to 26.22) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reach` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 107 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 5.56 (3.47 to 10.31) | rose |
| `PARTICIPIAL_TAIL / participial_tail / break` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5.52 (2.02 to 28.83) | rose |
| `PARTICIPIAL_TAIL / participial_tail / utilize` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 59 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 5.48 (2.99 to 12.77) | rose |
| `PARTICIPIAL_TAIL / participial_tail / present` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 5.38 (2.41 to 20.55) | rose |
| `ALTERNATIVE_FRAMING / af_rather_than / rather than` | 509 | 0.10 (0.09 to 0.12) | 0.10 (0.09 to 0.11) | 2045 | 0.53 (0.48 to 0.60) | 0.51 (0.47 to 0.56) | 5.22 (4.37 to 6.23) | rose |
| `PARTICIPIAL_TAIL / participial_tail / illustrate` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.20 (2.15 to 24.46) | rose |
| `PARTICIPIAL_TAIL / participial_tail / simplify` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5.20 (2.19 to 24.24) | rose |
| `EM_DASH / - / pivot (not X — Y)` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 47 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 5.09 (2.52 to 12.08) | rose |
| `PARTICIPIAL_TAIL / participial_tail / combine` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 43 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 5.08 (2.63 to 13.39) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition / X, not Y` | 78 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 300 | 0.08 (0.06 to 0.10) | 0.07 (0.06 to 0.09) | 5.00 (3.45 to 7.07) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leverage` | 28 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 106 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 4.92 (3.22 to 8.49) | rose |
| `PARTICIPIAL_TAIL / participial_tail / feature` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 4.87 (2.31 to 14.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / create` | 35 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 131 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 4.86 (3.23 to 7.74) | rose |
| `EM_DASH / - / pivot (— it's Y)` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 48 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.80 (2.28 to 14.66) | rose |
| `PARTICIPIAL_TAIL / participial_tail / indicate` | 105 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 386 | 0.10 (0.09 to 0.12) | 0.11 (0.10 to 0.13) | 4.78 (3.71 to 6.22) | rose |
| `PARTICIPIAL_TAIL / participial_tail / force` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 51 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.73 (2.43 to 11.54) | rose |
| `PARTICIPIAL_TAIL / participial_tail / optimize` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 43 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.66 (2.44 to 11.04) | rose |
| `PARTICIPIAL_TAIL / participial_tail / account` | 16 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.63 (2.70 to 8.99) | rose |
| `PARTICIPIAL_TAIL / participial_tail / introduce` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 70 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 4.55 (2.74 to 8.52) | rose |
| `PARTICIPIAL_TAIL / participial_tail / span` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 42 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 4.55 (2.48 to 9.87) | rose |
| `PARTICIPIAL_TAIL / participial_tail / make` | 296 | 0.06 (0.05 to 0.07) | 0.05 (0.05 to 0.06) | 1032 | 0.27 (0.25 to 0.29) | 0.29 (0.26 to 0.31) | 4.53 (3.75 to 5.61) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / numerically` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 4.48 (1.64 to 35.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / integrate` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 31 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 4.48 (2.30 to 11.32) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / exceptionally` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 4.42 (1.76 to 20.97) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / economically` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 4.33 (0.99 to 25.22) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / substantially` | 71 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 234 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 4.28 (2.97 to 6.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / limit` | 48 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 158 | 0.04 (0.03 to 0.05) | 0.04 (0.04 to 0.05) | 4.28 (3.02 to 6.38) | rose |
| `PARTICIPIAL_TAIL / participial_tail / give` | 28 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 90 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 4.18 (2.66 to 7.24) | rose |
| `PARTICIPIAL_TAIL / participial_tail / operate` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 4.13 (2.18 to 9.13) | rose |
| `PARTICIPIAL_TAIL / participial_tail / outperform` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 57 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 4.12 (2.27 to 8.75) | rose |
| `PARTICIPIAL_TAIL / participial_tail / remove` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 4.04 (1.98 to 10.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail / shift` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.90 (1.84 to 11.63) | rose |
| `PARTICIPIAL_TAIL / participial_tail / prioritize` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.90 (1.64 to 18.73) | rose |
| `PARTICIPIAL_TAIL / participial_tail / turn` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.90 (1.46 to 17.98) | rose |
| `PARTICIPIAL_TAIL / participial_tail / employ` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 3.79 (1.91 to 9.45) | rose |
| `PARTICIPIAL_TAIL / participial_tail / place` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 3.78 (2.04 to 8.73) | rose |
| `PARTICIPIAL_TAIL / participial_tail / allow` | 264 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 765 | 0.20 (0.18 to 0.22) | 0.21 (0.19 to 0.23) | 3.77 (3.13 to 4.63) | rose |
| `PARTICIPIAL_TAIL / participial_tail / execute` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.75 (1.88 to 9.88) | rose |
| `PARTICIPIAL_TAIL / participial_tail / rely` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.64 (1.79 to 8.99) | rose |
| `PARTICIPIAL_TAIL / participial_tail / minimize` | 23 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 64 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 3.62 (2.24 to 6.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / report` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.57 (1.60 to 9.78) | rose |
| `PARTICIPIAL_TAIL / participial_tail / contribute` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.53 (1.57 to 12.64) | rose |
| `PARTICIPIAL_TAIL / participial_tail / handle` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.53 (1.33 to 11.86) | rose |
| `PARTICIPIAL_TAIL / participial_tail / bring` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.51 (1.76 to 8.88) | rose |
| `PARTICIPIAL_TAIL / participial_tail / replace` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.51 (1.76 to 8.88) | rose |
| `PARTICIPIAL_TAIL / participial_tail / focus` | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 67 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 3.48 (2.22 to 5.94) | rose |
| `PARTICIPIAL_TAIL / participial_tail / maximize` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 3.47 (1.79 to 8.03) | rose |
| `PARTICIPIAL_TAIL / participial_tail / scale` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.41 (1.50 to 12.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail / push` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.34 (1.46 to 10.35) | rose |
| `PARTICIPIAL_TAIL / participial_tail / correspond` | 55 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 141 | 0.04 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 3.33 (2.32 to 5.15) | rose |
| `PARTICIPIAL_TAIL / participial_tail / avoid` | 51 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 130 | 0.03 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 3.31 (2.31 to 4.93) | rose |
| `PARTICIPIAL_TAIL / participial_tail / identify` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 3.31 (1.64 to 8.88) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / geometrically` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.25 (1.08 to 15.39) | rose |
| `HOLLOW_BOOSTER / - / -` | 240 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 598 | 0.16 (0.14 to 0.17) | 0.16 (0.14 to 0.18) | 3.24 (2.69 to 3.96) | rose |
| `PARTICIPIAL_TAIL / participial_tail / aim` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 39 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 3.17 (1.67 to 8.31) | rose |
| `PARTICIPIAL_TAIL / participial_tail / apply` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.14 (1.57 to 7.56) | rose |
| `PARTICIPIAL_TAIL / participial_tail / provide` | 150 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.03) | 361 | 0.09 (0.08 to 0.11) | 0.10 (0.09 to 0.11) | 3.13 (2.48 to 4.11) | rose |
| `PARTICIPIAL_TAIL / participial_tail / improve` | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 137 | 0.04 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 3.12 (2.23 to 4.56) | rose |
| `PARTICIPIAL_TAIL / participial_tail / represent` | 35 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 84 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 3.12 (2.11 to 5.01) | rose |
| `PARTICIPIAL_TAIL / participial_tail / comprise` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 43 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 3.10 (1.67 to 6.93) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reduce` | 177 | 0.04 (0.03 to 0.04) | 0.04 (0.03 to 0.04) | 413 | 0.11 (0.10 to 0.12) | 0.12 (0.10 to 0.13) | 3.03 (2.49 to 3.79) | rose |
| `PARTICIPIAL_TAIL / participial_tail / mitigate` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 14 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.03 (1.17 to 12.75) | rose |
| `PARTICIPIAL_TAIL / participial_tail / total` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 3.03 (1.14 to 14.69) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / proportionally` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.99 (1.39 to 7.33) | rose |
| `PARTICIPIAL_TAIL / participial_tail / require` | 98 | 0.02 (0.02 to 0.02) | 0.02 (0.01 to 0.02) | 225 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 2.98 (2.27 to 4.02) | rose |
| `PARTICIPIAL_TAIL / participial_tail / add` | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 71 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 2.98 (1.75 to 5.47) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / functionally` | 64 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 145 | 0.04 (0.03 to 0.05) | 0.05 (0.03 to 0.06) | 2.94 (1.87 to 4.87) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / biologically` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.92 (0.75 to 10.36) | flat |
| `PARTICIPIAL_TAIL / participial_tail / compare` | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 42 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 2.87 (1.57 to 6.33) | rose |
| `PARTICIPIAL_TAIL / participial_tail / update` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.73 (1.23 to 7.77) | rose |
| `PARTICIPIAL_TAIL / participial_tail / generate` | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 64 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2.68 (1.69 to 4.38) | rose |
| `PARTICIPIAL_TAIL / participial_tail / show` | 84 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 173 | 0.05 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 2.68 (2.00 to 3.59) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cause` | 91 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 184 | 0.05 (0.04 to 0.06) | 0.04 (0.04 to 0.05) | 2.63 (1.92 to 3.68) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / analytically` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.60 (0.89 to 9.98) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lack` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.60 (0.99 to 15.06) | flat |
| `PARTICIPIAL_TAIL / participial_tail / vary` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.60 (0.88 to 8.24) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / statistically` | 24 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 48 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.60 (1.39 to 5.28) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / fundamentally` | 84 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 168 | 0.04 (0.04 to 0.05) | 0.04 (0.03 to 0.05) | 2.60 (1.81 to 3.76) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / formally` | 40 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 79 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 2.57 (1.29 to 5.82) | rose |
| `PARTICIPIAL_TAIL / participial_tail / render` | 22 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 43 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 2.54 (1.34 to 5.99) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / historically` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.52 (1.27 to 5.63) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / empirically` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.47 (1.47 to 4.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / perform` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 2.45 (1.31 to 4.84) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / diagonally` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.41 (0.21 to 14.11) | flat |
| `PARTICIPIAL_TAIL / participial_tail / keep` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 53 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 2.38 (1.45 to 4.04) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling / X, not Y` | 40 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 73 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 2.37 (1.51 to 3.80) | rose |
| `PARTICIPIAL_TAIL / participial_tail / process` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.34 (1.00 to 6.71) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / systematically` | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.32 (0.87 to 9.60) | flat |
| `PARTICIPIAL_TAIL / participial_tail / select` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.31 (0.95 to 6.56) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / mutually` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.23 (1.13 to 4.73) | rose |
| `PARTICIPIAL_TAIL / participial_tail / bypass` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.23 (1.10 to 5.11) | rose |
| `PARTICIPIAL_TAIL / participial_tail / guarantee` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.21 (1.01 to 5.09) | rose |
| `PARTICIPIAL_TAIL / participial_tail / result` | 334 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 567 | 0.15 (0.13 to 0.16) | 0.16 (0.14 to 0.18) | 2.21 (1.85 to 2.63) | rose |
| `PARTICIPIAL_TAIL / participial_tail / contain` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.20 (1.07 to 5.05) | rose |
| `PARTICIPIAL_TAIL / participial_tail / target` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 45 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.17 (1.27 to 3.97) | rose |
| `PARTICIPIAL_TAIL / participial_tail / incur` | 37 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 61 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.14 (1.24 to 4.16) | rose |
| `PARTICIPIAL_TAIL / participial_tail / set` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.06 (0.95 to 5.12) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lead` | 318 | 0.06 (0.05 to 0.08) | 0.06 (0.05 to 0.07) | 494 | 0.13 (0.11 to 0.15) | 0.13 (0.12 to 0.15) | 2.02 (1.65 to 2.49) | rose |
| `PARTICIPIAL_TAIL / participial_tail / compute` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.01 (0.89 to 5.03) | flat |
| `PARTICIPIAL_TAIL / participial_tail / explore` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 1.95 (0.75 to 5.64) | flat |
| `PARTICIPIAL_TAIL / participial_tail / hold` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.95 (0.75 to 6.14) | flat |
| `PARTICIPIAL_TAIL / participial_tail / store` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.91 (1.01 to 4.29) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / additionally` | 118 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 173 | 0.05 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 1.91 (1.39 to 2.67) | rose |
| `PARTICIPIAL_TAIL / participial_tail / translate` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 19 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.90 (0.87 to 4.03) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / architecturally` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.88 (0.85 to 5.03) | flat |
| `PARTICIPIAL_TAIL / participial_tail / define` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.88 (0.75 to 5.04) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / specifically` | 193 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 274 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 1.84 (1.45 to 2.31) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / maximally` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.82 (0.58 to 6.42) | flat |
| `PARTICIPIAL_TAIL / participial_tail / range` | 46 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 64 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.81 (1.19 to 2.70) | rose |
| `PARTICIPIAL_TAIL / participial_tail / move` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.76 (0.82 to 3.90) | flat |
| `PARTICIPIAL_TAIL / participial_tail / pave` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.73 (0.63 to 7.53) | flat |
| `PARTICIPIAL_TAIL / participial_tail / involve` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.73 (0.77 to 3.95) | flat |
| `PARTICIPIAL_TAIL / participial_tail / evaluate` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.62 (0.72 to 4.10) | flat |
| `PARTICIPIAL_TAIL / participial_tail / analyze` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 1.59 (0.53 to 4.54) | flat |
| `PARTICIPIAL_TAIL / participial_tail / implement` | 21 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.55 (0.71 to 3.27) | flat |
| `GAPPED_ANTITHESIS / gapped_antithesis / before/after` | 43 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 50 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.51 (0.99 to 2.27) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / logically` | 35 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 40 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 1.49 (0.84 to 2.76) | flat |
| `TRICOLON / tricolon / enumeration` | 4870 | 0.98 (0.92 to 1.03) | 0.98 (0.94 to 1.04) | 5556 | 1.45 (1.37 to 1.53) | 1.48 (1.41 to 1.56) | 1.48 (1.37 to 1.60) | rose |
| `CONSULTANT_REGISTER / - / -` | 4267 | 0.86 (0.78 to 0.94) | 0.85 (0.78 to 0.92) | 4803 | 1.25 (1.17 to 1.34) | 1.28 (1.18 to 1.37) | 1.46 (1.31 to 1.65) | rose |
| `PARTICIPIAL_TAIL / participial_tail / exploit` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 33 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 1.43 (0.81 to 2.63) | flat |
| `TRICOLON / tricolon / list-like` | 9200 | 1.85 (1.78 to 1.92) | 1.89 (1.82 to 1.95) | 10103 | 2.64 (2.52 to 2.76) | 2.70 (2.58 to 2.81) | 1.43 (1.35 to 1.51) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / temporally` | 31 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 34 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 1.43 (0.75 to 2.89) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consume` | 21 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.42 (0.75 to 2.70) | flat |
| `PARTICIPIAL_TAIL / participial_tail / increase` | 88 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 95 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 1.40 (1.03 to 1.97) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / mathematically` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.40 (0.80 to 2.55) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consist` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 1.39 (0.83 to 2.33) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / dramatically` | 16 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.38 (0.64 to 2.96) | flat |
| `LLM_DICTION / - / -` | 7283 | 1.46 (1.37 to 1.56) | 1.45 (1.36 to 1.55) | 7684 | 2.01 (1.88 to 2.13) | 2.12 (1.99 to 2.25) | 1.37 (1.25 to 1.50) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / spatially` | 81 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 83 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 1.33 (0.73 to 2.47) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated / not X but Y` | 1110 | 0.22 (0.20 to 0.24) | 0.21 (0.19 to 0.23) | 1133 | 0.30 (0.27 to 0.32) | 0.30 (0.27 to 0.33) | 1.33 (1.18 to 1.49) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / computationally` | 199 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 200 | 0.05 (0.04 to 0.06) | 0.06 (0.05 to 0.07) | 1.31 (0.99 to 1.77) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lower` | 22 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.30 (0.66 to 2.55) | flat |
| `PARTICIPIAL_TAIL / participial_tail / exhibit` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.30 (0.53 to 4.12) | flat |
| `PARTICIPIAL_TAIL / participial_tail / find` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.30 (0.55 to 3.01) | flat |
| `PARTICIPIAL_TAIL / participial_tail / ignore` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.30 (0.52 to 3.19) | flat |
| `PARTICIPIAL_TAIL / participial_tail / obtain` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.30 (0.52 to 3.24) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / intrinsically` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 1.30 (0.56 to 3.07) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / visually` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.30 (0.46 to 3.60) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / practically` | 44 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 43 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.27 (0.78 to 2.10) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / itself` | 479 | 0.10 (0.08 to 0.11) | 0.10 (0.08 to 0.11) | 456 | 0.12 (0.10 to 0.14) | 0.11 (0.09 to 0.12) | 1.24 (1.02 to 1.50) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / naturally` | 67 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.22 (0.82 to 1.84) | flat |
| `TRICOLON / tricolon / figure` | 2041 | 0.41 (0.38 to 0.44) | 0.43 (0.39 to 0.46) | 1913 | 0.50 (0.47 to 0.53) | 0.51 (0.48 to 0.55) | 1.22 (1.10 to 1.35) | rose |
| `PARTICIPIAL_TAIL / participial_tail / mean` | 110 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 103 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 1.22 (0.87 to 1.73) | flat |
| `PARTICIPIAL_TAIL / participial_tail / use` | 444 | 0.09 (0.08 to 0.10) | 0.09 (0.08 to 0.10) | 411 | 0.11 (0.10 to 0.12) | 0.11 (0.09 to 0.12) | 1.20 (1.02 to 1.42) | rose |
| `BORROWED_RIGOUR / - / -` | 1270 | 0.26 (0.22 to 0.29) | 0.28 (0.23 to 0.34) | 1129 | 0.29 (0.27 to 0.33) | 0.29 (0.26 to 0.33) | 1.16 (0.99 to 1.35) | flat |
| `CLOSER / - / -` | 346 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.09) | 307 | 0.08 (0.07 to 0.09) | 0.07 (0.06 to 0.08) | 1.15 (0.94 to 1.39) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / conventionally` | 16 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.14 (0.45 to 2.54) | flat |
| `VAGUE_QUANTIFIER / - / -` | 1203 | 0.24 (0.22 to 0.26) | 0.24 (0.22 to 0.26) | 1025 | 0.27 (0.25 to 0.29) | 0.28 (0.25 to 0.30) | 1.11 (0.98 to 1.25) | flat |
| `PARTICIPIAL_TAIL / participial_tail / start` | 39 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 33 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 1.10 (0.67 to 1.82) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / essentially` | 39 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 32 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 1.07 (0.59 to 1.84) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / hierarchically` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.06 (0.35 to 2.77) | flat |
| `PARTICIPIAL_TAIL / participial_tail / decrease` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.06 (0.35 to 2.95) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / commercially` | 49 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 1.06 (0.57 to 2.00) | flat |
| `PARTICIPIAL_TAIL / participial_tail / run` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.04 (0.60 to 1.78) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / virtually` | 34 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.03 (0.43 to 2.28) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / incrementally` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.02 (0.38 to 2.99) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / marginally` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.01 (0.36 to 2.40) | flat |
| `PARTICIPIAL_TAIL / participial_tail / assume` | 74 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.00 (0.66 to 1.50) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / themselves` | 111 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 84 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.02) | 0.98 (0.72 to 1.35) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / experimentally` | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.97 (0.46 to 1.87) | flat |
| `PARTICIPIAL_TAIL / participial_tail / save` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.94 (0.42 to 1.99) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / gradually` | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.89 (0.38 to 1.93) | flat |
| `PARTICIPIAL_TAIL / participial_tail / take` | 45 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.87 (0.49 to 1.42) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / identically` | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.87 (0.28 to 2.58) | flat |
| `ALTERNATIVE_FRAMING / af_instead_of / instead of` | 976 | 0.20 (0.18 to 0.21) | 0.20 (0.18 to 0.22) | 642 | 0.17 (0.15 to 0.19) | 0.16 (0.14 to 0.17) | 0.85 (0.74 to 0.98) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / exponentially` | 17 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 0.84 (0.32 to 2.36) | flat |
| `PARTICIPIAL_TAIL / participial_tail / wait` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.84 (0.27 to 2.03) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / vertically` | 50 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 32 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.83 (0.42 to 1.84) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consider` | 56 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 35 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 0.81 (0.51 to 1.26) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / critically` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.81 (0.33 to 1.90) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / thermally` | 26 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.75 (0.24 to 2.74) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / theoretically` | 40 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.75 (0.39 to 1.33) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / traditionally` | 76 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 43 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 0.74 (0.49 to 1.09) | flat |
| `GAPPED_ANTITHESIS / gapped_antithesis / opposed verbs` | 38 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.72 (0.37 to 1.23) | flat |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft` | 58 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.69 (0.38 to 1.18) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / periodically` | 34 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.69 (0.33 to 1.33) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / partially` | 189 | 0.04 (0.02 to 0.06) | 0.04 (0.02 to 0.05) | 100 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 0.69 (0.42 to 1.17) | flat |
| `FRAME_MARKER / - / -` | 335 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 172 | 0.04 (0.04 to 0.05) | 0.05 (0.04 to 0.05) | 0.67 (0.53 to 0.84) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / drastically` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.65 (0.30 to 1.28) | flat |
| `PARTICIPIAL_TAIL / participial_tail / imply` | 24 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 12 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.65 (0.26 to 1.84) | flat |
| `EMPTY_FRAME / - / -` | 436 | 0.09 (0.08 to 0.10) | 0.09 (0.08 to 0.10) | 208 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 0.62 (0.50 to 0.77) | fell |
| `ALTERNATIVE_FRAMING / af_less_than / more...than` | 2286 | 0.46 (0.43 to 0.49) | 0.46 (0.43 to 0.50) | 1076 | 0.28 (0.26 to 0.31) | 0.27 (0.25 to 0.30) | 0.61 (0.55 to 0.68) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / conceptually` | 35 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.59 (0.29 to 1.13) | flat |
| `NEG_ESCALATION / neg_escalation / modal` | 33 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.59 (0.27 to 1.12) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / potentially` | 199 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.04) | 90 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.59 (0.42 to 0.80) | fell |
| `ALTERNATIVE_FRAMING / af_less_than / less...than` | 1158 | 0.23 (0.21 to 0.26) | 0.24 (0.22 to 0.26) | 514 | 0.13 (0.12 to 0.15) | 0.13 (0.12 to 0.15) | 0.58 (0.49 to 0.66) | fell |
| `PARTICIPIAL_TAIL / participial_tail / be` | 34 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.54 (0.26 to 1.03) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / minimally` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.51 (0.09 to 1.99) | flat |
| `HEDGE_STACK / - / -` | 62 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.48 (0.27 to 0.84) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / ideally` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.43 (0.19 to 0.85) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / trivially` | 19 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.41 (0.06 to 1.04) | flat |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft, across sentences` | 118 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 36 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 0.40 (0.25 to 0.59) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / basically` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.36 (0.07 to 0.98) | fell |
| `PARTICIPIAL_TAIL / participial_tail / waste` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.31 (0.05 to 0.88) | fell |
| `PARTICIPIAL_TAIL / participial_tail / have` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.30 (0.09 to 0.64) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / horizontally` | 28 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.23 (0.05 to 0.78) | fell |

## Phrase-list matches

Every phrase-list construction, keyed by matched text, lowercased (one lemma entry gives a row per word form). Rows with at least 20 findings in both windows together.

### all

| phrase | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `LLM_DICTION / underscore` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 53 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 68.88 (19.18 to inf) | rose |
| `LLM_DICTION / underscores` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 60 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 38.99 (14.11 to inf) | rose |
| `LLM_DICTION / underscoring` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 53 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 34.44 (9.42 to inf) | rose |
| `CONSULTANT_REGISTER / streamlining` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 16.89 (4.80 to inf) | rose |
| `CONSULTANT_REGISTER / stakeholders` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 14.30 (0.00 to inf) | flat |
| `CONSULTANT_REGISTER / streamline` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 13.00 (5.04 to inf) | rose |
| `LLM_DICTION / navigating` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 11.70 (3.76 to inf) | rose |
| `CONSULTANT_REGISTER / actionable` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 40 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 10.40 (3.80 to inf) | rose |
| `HOLLOW_BOOSTER / critically,` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 44 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 9.53 (4.00 to 63.78) | rose |
| `BORROWED_RIGOUR / step function` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 21 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 6.82 (2.06 to 43.37) | rose |
| `HOLLOW_BOOSTER / crucially,` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 79 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 6.04 (3.67 to 11.51) | rose |
| `BORROWED_RIGOUR / failure mode` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 43 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 5.59 (1.94 to 18.14) | rose |
| `LLM_DICTION / landscape` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 116 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 5.58 (3.36 to 10.12) | rose |
| `LLM_DICTION / seamless` | 30 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 117 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 5.07 (3.15 to 8.99) | rose |
| `HOLLOW_BOOSTER / notably,` | 76 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 293 | 0.08 (0.07 to 0.09) | 0.08 (0.07 to 0.09) | 5.01 (3.53 to 7.68) | rose |
| `LLM_DICTION / intricate` | 15 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 52 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.51 (2.58 to 9.50) | rose |
| `LLM_DICTION / pivotal` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 4.48 (1.91 to 13.85) | rose |
| `CONSULTANT_REGISTER / unlocking` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 34 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 4.02 (1.61 to 12.75) | rose |
| `LLM_DICTION / orchestrated` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 38 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 3.80 (1.93 to 8.00) | rose |
| `LLM_DICTION / harness` | 61 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 154 | 0.04 (0.02 to 0.06) | 0.05 (0.02 to 0.08) | 3.28 (1.28 to 10.89) | rose |
| `CONSULTANT_REGISTER / at scale` | 27 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 68 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 3.27 (1.79 to 7.49) | rose |
| `LLM_DICTION / cornerstone` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.25 (1.56 to 8.01) | rose |
| `LLM_DICTION / navigate` | 22 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 54 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 3.19 (1.79 to 6.22) | rose |
| `CONSULTANT_REGISTER / unlock` | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 67 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.05) | 3.11 (1.32 to 7.11) | rose |
| `BORROWED_RIGOUR / canonical` | 58 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 123 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 2.76 (1.39 to 6.22) | rose |
| `LLM_DICTION / innovative` | 32 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 67 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2.72 (1.67 to 4.89) | rose |
| `BORROWED_RIGOUR / by construction` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 60 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.69 (1.43 to 5.65) | rose |
| `LLM_DICTION / comprehensive` | 305 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 617 | 0.16 (0.13 to 0.20) | 0.17 (0.14 to 0.21) | 2.63 (2.01 to 3.45) | rose |
| `CONSULTANT_REGISTER / synergy` | 13 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.60 (1.28 to 6.18) | rose |
| `VAGUE_QUANTIFIER / increasingly` | 248 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 471 | 0.12 (0.11 to 0.14) | 0.13 (0.11 to 0.15) | 2.47 (1.99 to 3.11) | rose |
| `LLM_DICTION / orchestrates` | 26 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 47 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.35 (1.39 to 4.15) | rose |
| `LLM_DICTION / harnesses` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.34 (0.94 to 10.42) | flat |
| `LLM_DICTION / dynamics` | 132 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 237 | 0.06 (0.04 to 0.08) | 0.06 (0.04 to 0.09) | 2.33 (1.43 to 4.01) | rose |
| `CONSULTANT_REGISTER / leverages` | 280 | 0.06 (0.05 to 0.07) | 0.05 (0.04 to 0.06) | 464 | 0.12 (0.11 to 0.14) | 0.12 (0.10 to 0.13) | 2.15 (1.70 to 2.76) | rose |
| `LLM_DICTION / essential` | 335 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.09) | 547 | 0.14 (0.13 to 0.16) | 0.16 (0.14 to 0.18) | 2.12 (1.70 to 2.69) | rose |
| `LLM_DICTION / robust` | 264 | 0.05 (0.04 to 0.07) | 0.05 (0.04 to 0.07) | 423 | 0.11 (0.09 to 0.13) | 0.12 (0.10 to 0.15) | 2.08 (1.53 to 2.88) | rose |
| `FRAME_MARKER / at its core` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 16 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 2.08 (0.94 to 5.56) | flat |
| `CLOSER / ultimately,` | 21 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 33 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 2.04 (1.18 to 3.98) | rose |
| `CONSULTANT_REGISTER / unlocks` | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.02 (0.84 to 5.82) | flat |
| `LLM_DICTION / crucial` | 232 | 0.05 (0.04 to 0.06) | 0.04 (0.04 to 0.05) | 348 | 0.09 (0.08 to 0.10) | 0.10 (0.08 to 0.11) | 1.95 (1.53 to 2.52) | rose |
| `LLM_DICTION / versatile` | 43 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 1.90 (1.04 to 3.78) | rose |
| `CONSULTANT_REGISTER / leveraging` | 418 | 0.08 (0.06 to 0.11) | 0.08 (0.06 to 0.09) | 604 | 0.16 (0.14 to 0.18) | 0.16 (0.14 to 0.18) | 1.88 (1.43 to 2.50) | rose |
| `CONSULTANT_REGISTER / optimizes` | 156 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 225 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 1.87 (1.42 to 2.50) | rose |
| `BORROWED_RIGOUR / well-defined` | 35 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 49 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.82 (1.12 to 3.05) | rose |
| `CONSULTANT_REGISTER / optimizing` | 331 | 0.07 (0.06 to 0.08) | 0.06 (0.05 to 0.07) | 461 | 0.12 (0.10 to 0.14) | 0.12 (0.11 to 0.14) | 1.81 (1.47 to 2.26) | rose |
| `HOLLOW_BOOSTER / importantly,` | 136 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 173 | 0.05 (0.04 to 0.05) | 0.05 (0.04 to 0.06) | 1.65 (1.28 to 2.16) | rose |
| `CONSULTANT_REGISTER / holistic` | 77 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.04) | 97 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 1.64 (0.99 to 2.76) | flat |
| `CLOSER / in conclusion` | 16 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.62 (0.81 to 3.46) | flat |
| `CONSULTANT_REGISTER / paradigm shift` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.62 (0.71 to 4.39) | flat |
| `BORROWED_RIGOUR / search space` | 147 | 0.03 (0.02 to 0.04) | 0.04 (0.02 to 0.07) | 182 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 1.61 (1.01 to 2.62) | rose |
| `LLM_DICTION / harnessing` | 15 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 18 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.56 (0.65 to 5.10) | flat |
| `LLM_DICTION / orchestrating` | 15 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.47 (0.66 to 3.56) | flat |
| `LLM_DICTION / paradigms` | 79 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 83 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.03) | 1.37 (0.77 to 2.53) | flat |
| `VAGUE_QUANTIFIER / numerous` | 186 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 187 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 1.31 (1.01 to 1.70) | rose |
| `LLM_DICTION / foster` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 14 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 1.30 (0.58 to 3.67) | flat |
| `LLM_DICTION / delve` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1.30 (0.42 to 4.19) | flat |
| `CONSULTANT_REGISTER / optimized` | 1369 | 0.28 (0.24 to 0.31) | 0.28 (0.25 to 0.31) | 1347 | 0.35 (0.31 to 0.39) | 0.36 (0.32 to 0.40) | 1.28 (1.09 to 1.50) | rose |
| `BORROWED_RIGOUR / ground truth` | 80 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 78 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 1.27 (0.70 to 2.61) | flat |
| `CONSULTANT_REGISTER / optimize` | 684 | 0.14 (0.12 to 0.16) | 0.14 (0.13 to 0.16) | 661 | 0.17 (0.15 to 0.19) | 0.19 (0.16 to 0.21) | 1.26 (1.05 to 1.53) | rose |
| `BORROWED_RIGOUR / orthogonal` | 187 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 180 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 1.25 (0.94 to 1.68) | flat |
| `LLM_DICTION / paradigm` | 393 | 0.08 (0.05 to 0.12) | 0.08 (0.05 to 0.11) | 374 | 0.10 (0.08 to 0.12) | 0.10 (0.08 to 0.12) | 1.24 (0.80 to 2.02) | flat |
| `CLOSER / in summary` | 202 | 0.04 (0.03 to 0.05) | 0.04 (0.04 to 0.05) | 188 | 0.05 (0.04 to 0.06) | 0.04 (0.03 to 0.05) | 1.21 (0.94 to 1.56) | flat |
| `CLOSER / in short` | 31 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.01) | 28 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.17 (0.66 to 2.07) | flat |
| `LLM_DICTION / dynamic` | 2080 | 0.42 (0.36 to 0.48) | 0.42 (0.36 to 0.49) | 1795 | 0.47 (0.41 to 0.52) | 0.48 (0.42 to 0.53) | 1.12 (0.93 to 1.34) | flat |
| `EMPTY_FRAME / it is important to note` | 62 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 53 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.11 (0.70 to 1.74) | flat |
| `BORROWED_RIGOUR / state space` | 55 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 47 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.11 (0.53 to 2.62) | flat |
| `EMPTY_FRAME / it is worth noting` | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 48 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.09 (0.68 to 1.80) | flat |
| `FRAME_MARKER / it is worth noting` | 57 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 48 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.09 (0.68 to 1.80) | flat |
| `LLM_DICTION / orchestrate` | 46 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 36 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 1.02 (0.60 to 1.68) | flat |
| `CONSULTANT_REGISTER / leverage` | 651 | 0.13 (0.11 to 0.15) | 0.12 (0.11 to 0.14) | 478 | 0.12 (0.11 to 0.14) | 0.12 (0.10 to 0.13) | 0.95 (0.77 to 1.17) | flat |
| `BORROWED_RIGOUR / non-trivial` | 138 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 97 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.91 (0.66 to 1.27) | flat |
| `LLM_DICTION / significant` | 2879 | 0.58 (0.53 to 0.62) | 0.55 (0.52 to 0.59) | 1963 | 0.51 (0.47 to 0.55) | 0.55 (0.51 to 0.60) | 0.89 (0.79 to 0.99) | fell |
| `BORROWED_RIGOUR / degrees of freedom` | 15 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0.87 (0.15 to 2.45) | flat |
| `CLOSER / fundamentally,` | 14 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.84 (0.30 to 2.18) | flat |
| `BORROWED_RIGOUR / order of magnitude` | 158 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 97 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.80 (0.56 to 1.10) | flat |
| `VAGUE_QUANTIFIER / a wide range of` | 334 | 0.07 (0.06 to 0.08) | 0.06 (0.05 to 0.07) | 205 | 0.05 (0.04 to 0.06) | 0.06 (0.05 to 0.07) | 0.80 (0.63 to 1.01) | flat |
| `LLM_DICTION / vital` | 63 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 38 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 0.78 (0.44 to 1.25) | flat |
| `HEDGE_STACK / is not necessarily` | 22 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.77 (0.35 to 1.67) | flat |
| `CLOSER / in essence` | 32 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.73 (0.36 to 1.39) | flat |
| `BORROWED_RIGOUR / solution space` | 69 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 38 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 0.72 (0.24 to 2.75) | flat |
| `CONSULTANT_REGISTER / leveraged` | 132 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.03) | 63 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 0.62 (0.40 to 0.94) | fell |
| `FRAME_MARKER / it is important to` | 181 | 0.04 (0.03 to 0.04) | 0.04 (0.03 to 0.04) | 84 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.60 (0.43 to 0.81) | fell |
| `HEDGE_STACK / are not necessarily` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.52 (0.18 to 1.12) | flat |
| `VAGUE_QUANTIFIER / a variety of` | 338 | 0.07 (0.06 to 0.08) | 0.07 (0.06 to 0.08) | 131 | 0.03 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 0.50 (0.38 to 0.64) | fell |
| `LLM_DICTION / profound` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.46 (0.11 to 1.26) | flat |
| `VAGUE_QUANTIFIER / a significant number of` | 27 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.43 (0.17 to 0.93) | fell |
| `BORROWED_RIGOUR / threat model` | 61 | 0.01 (0.01 to 0.02) | 0.02 (0.00 to 0.05) | 20 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.43 (0.14 to 1.17) | flat |
| `EMPTY_FRAME / in other words` | 288 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.07) | 93 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.42 (0.31 to 0.55) | fell |
| `VAGUE_QUANTIFIER / vast majority` | 64 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.32 (0.16 to 0.55) | fell |
| `BORROWED_RIGOUR / phase change` | 45 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.32 (0.10 to 0.72) | fell |
| `CLOSER / essentially,` | 29 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.31 (0.07 to 0.74) | fell |
| `BORROWED_RIGOUR / state of the art` | 110 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.31 (0.17 to 0.51) | fell |
| `LLM_DICTION / plethora` | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.25 (0.05 to 0.60) | fell |
| `BORROWED_RIGOUR / idempotent` | 18 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.14 (0.00 to 1.66) | flat |
| `FRAME_MARKER / in today's` | 50 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.13 (0.03 to 0.27) | fell |
| `HEDGE_STACK / may or may not` | 20 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.13 (0.00 to 0.46) | fell |

### body

| phrase | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `CONSULTANT_REGISTER / actionable` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 22 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | inf (inf to inf) | rose |
| `LLM_DICTION / underscore` | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 39.48 (10.02 to inf) | rose |
| `LLM_DICTION / underscores` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 36 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 23.69 (8.05 to inf) | rose |
| `LLM_DICTION / underscoring` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 34 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 22.37 (6.17 to inf) | rose |
| `BORROWED_RIGOUR / failure mode` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 30 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.03) | 19.74 (5.85 to inf) | rose |
| `HOLLOW_BOOSTER / crucially,` | 10 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 60 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 7.90 (4.18 to 22.32) | rose |
| `BORROWED_RIGOUR / step function` | 3 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7.90 (2.01 to inf) | rose |
| `HOLLOW_BOOSTER / critically,` | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 7.90 (2.71 to inf) | rose |
| `LLM_DICTION / seamless` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 73 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 7.39 (3.89 to 18.78) | rose |
| `LLM_DICTION / orchestrated` | 5 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 26 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 6.84 (2.88 to 34.15) | rose |
| `LLM_DICTION / landscape` | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 57 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 6.82 (3.33 to 19.99) | rose |
| `LLM_DICTION / intricate` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 6.14 (2.76 to 20.06) | rose |
| `HOLLOW_BOOSTER / notably,` | 57 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.04) | 237 | 0.09 (0.07 to 0.10) | 0.09 (0.08 to 0.11) | 5.47 (3.75 to 8.76) | rose |
| `BORROWED_RIGOUR / canonical` | 26 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 97 | 0.04 (0.02 to 0.05) | 0.04 (0.02 to 0.05) | 4.91 (2.71 to 10.15) | rose |
| `CONSULTANT_REGISTER / at scale` | 10 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 33 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 4.34 (2.05 to 14.80) | rose |
| `LLM_DICTION / pivotal` | 6 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 17 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 3.73 (1.09 to 19.47) | rose |
| `LLM_DICTION / harness` | 44 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 116 | 0.04 (0.02 to 0.07) | 0.05 (0.02 to 0.09) | 3.47 (1.17 to 15.94) | rose |
| `LLM_DICTION / comprehensive` | 131 | 0.04 (0.03 to 0.04) | 0.03 (0.03 to 0.04) | 336 | 0.12 (0.09 to 0.17) | 0.12 (0.10 to 0.15) | 3.38 (2.26 to 5.10) | rose |
| `BORROWED_RIGOUR / by construction` | 21 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 49 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 3.07 (1.49 to 7.64) | rose |
| `LLM_DICTION / innovative` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.02) | 2.99 (1.44 to 7.10) | rose |
| `CLOSER / ultimately,` | 11 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 24 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 2.87 (1.43 to 7.20) | rose |
| `LLM_DICTION / orchestrates` | 18 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 39 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2.85 (1.62 to 5.40) | rose |
| `LLM_DICTION / navigate` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 28 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 2.83 (1.41 to 6.23) | rose |
| `CONSULTANT_REGISTER / synergy` | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 15 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 2.82 (1.05 to 9.39) | rose |
| `CONSULTANT_REGISTER / leverages` | 120 | 0.03 (0.03 to 0.04) | 0.03 (0.02 to 0.04) | 254 | 0.09 (0.08 to 0.11) | 0.09 (0.07 to 0.11) | 2.79 (2.06 to 3.84) | rose |
| `VAGUE_QUANTIFIER / increasingly` | 67 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 141 | 0.05 (0.04 to 0.07) | 0.05 (0.04 to 0.06) | 2.77 (1.82 to 4.58) | rose |
| `LLM_DICTION / dynamics` | 76 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 148 | 0.05 (0.04 to 0.07) | 0.05 (0.04 to 0.07) | 2.56 (1.51 to 4.66) | rose |
| `LLM_DICTION / versatile` | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 25 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 2.53 (1.16 to 6.66) | rose |
| `LLM_DICTION / robust` | 151 | 0.04 (0.03 to 0.06) | 0.04 (0.03 to 0.05) | 276 | 0.10 (0.08 to 0.13) | 0.11 (0.09 to 0.13) | 2.41 (1.67 to 3.54) | rose |
| `BORROWED_RIGOUR / well-defined` | 19 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 32 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 2.22 (1.16 to 4.68) | rose |
| `CONSULTANT_REGISTER / unlocking` | 8 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 13 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.03) | 2.14 (0.21 to 12.89) | flat |
| `CONSULTANT_REGISTER / unlock` | 19 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 30 | 0.01 (0.00 to 0.02) | 0.02 (0.00 to 0.05) | 2.08 (0.62 to 6.15) | flat |
| `BORROWED_RIGOUR / orthogonal` | 65 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 97 | 0.04 (0.03 to 0.05) | 0.03 (0.02 to 0.04) | 1.96 (1.25 to 3.31) | rose |
| `LLM_DICTION / essential` | 217 | 0.06 (0.05 to 0.07) | 0.06 (0.04 to 0.07) | 303 | 0.11 (0.09 to 0.13) | 0.11 (0.09 to 0.13) | 1.84 (1.38 to 2.48) | rose |
| `CONSULTANT_REGISTER / optimizes` | 79 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 110 | 0.04 (0.03 to 0.05) | 0.04 (0.03 to 0.05) | 1.83 (1.28 to 2.65) | rose |
| `CONSULTANT_REGISTER / optimizing` | 182 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 246 | 0.09 (0.08 to 0.11) | 0.09 (0.07 to 0.11) | 1.78 (1.38 to 2.36) | rose |
| `HOLLOW_BOOSTER / importantly,` | 91 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 123 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 1.78 (1.30 to 2.49) | rose |
| `LLM_DICTION / crucial` | 148 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 200 | 0.07 (0.06 to 0.09) | 0.08 (0.06 to 0.09) | 1.78 (1.28 to 2.51) | rose |
| `CONSULTANT_REGISTER / leveraging` | 229 | 0.06 (0.04 to 0.09) | 0.05 (0.04 to 0.07) | 304 | 0.11 (0.10 to 0.13) | 0.11 (0.10 to 0.13) | 1.75 (1.23 to 2.56) | rose |
| `BORROWED_RIGOUR / search space` | 112 | 0.03 (0.02 to 0.05) | 0.03 (0.02 to 0.05) | 133 | 0.05 (0.04 to 0.06) | 0.05 (0.03 to 0.06) | 1.56 (0.94 to 2.60) | flat |
| `CONSULTANT_REGISTER / optimized` | 856 | 0.24 (0.21 to 0.27) | 0.24 (0.21 to 0.27) | 901 | 0.33 (0.29 to 0.38) | 0.33 (0.29 to 0.38) | 1.39 (1.15 to 1.68) | rose |
| `CLOSER / in short` | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 18 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.32 (0.60 to 2.89) | flat |
| `VAGUE_QUANTIFIER / numerous` | 68 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 68 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 1.32 (0.89 to 1.97) | flat |
| `LLM_DICTION / paradigms` | 34 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 34 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.32 (0.63 to 2.89) | flat |
| `EMPTY_FRAME / it is worth noting` | 44 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 43 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.29 (0.79 to 2.20) | flat |
| `FRAME_MARKER / it is worth noting` | 44 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 43 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.29 (0.79 to 2.20) | flat |
| `CLOSER / in summary` | 121 | 0.03 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 115 | 0.04 (0.03 to 0.05) | 0.03 (0.03 to 0.04) | 1.25 (0.89 to 1.77) | flat |
| `BORROWED_RIGOUR / ground truth` | 72 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 63 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 1.15 (0.62 to 2.44) | flat |
| `CONSULTANT_REGISTER / holistic` | 41 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.04) | 35 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.12 (0.59 to 2.30) | flat |
| `EMPTY_FRAME / it is important to note` | 57 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 48 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 1.11 (0.69 to 1.75) | flat |
| `LLM_DICTION / dynamic` | 1316 | 0.37 (0.32 to 0.42) | 0.37 (0.31 to 0.45) | 1102 | 0.40 (0.35 to 0.46) | 0.41 (0.36 to 0.47) | 1.10 (0.90 to 1.33) | flat |
| `CONSULTANT_REGISTER / optimize` | 397 | 0.11 (0.09 to 0.13) | 0.11 (0.09 to 0.13) | 332 | 0.12 (0.10 to 0.14) | 0.14 (0.11 to 0.16) | 1.10 (0.87 to 1.40) | flat |
| `LLM_DICTION / orchestrate` | 30 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 23 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1.01 (0.53 to 1.84) | flat |
| `CLOSER / in conclusion` | 12 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.99 (0.36 to 2.70) | flat |
| `BORROWED_RIGOUR / non-trivial` | 78 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 58 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.03) | 0.98 (0.64 to 1.51) | flat |
| `CONSULTANT_REGISTER / leverage` | 347 | 0.10 (0.08 to 0.12) | 0.09 (0.07 to 0.10) | 245 | 0.09 (0.07 to 0.11) | 0.08 (0.07 to 0.10) | 0.93 (0.70 to 1.23) | flat |
| `CLOSER / in essence` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 16 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.88 (0.39 to 1.87) | flat |
| `BORROWED_RIGOUR / order of magnitude` | 92 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.04) | 61 | 0.02 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.87 (0.58 to 1.28) | flat |
| `LLM_DICTION / paradigm` | 199 | 0.06 (0.03 to 0.10) | 0.05 (0.03 to 0.08) | 125 | 0.05 (0.03 to 0.06) | 0.04 (0.03 to 0.06) | 0.83 (0.41 to 1.92) | flat |
| `LLM_DICTION / vital` | 34 | 0.01 (0.01 to 0.01) | 0.01 (0.01 to 0.01) | 20 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.77 (0.37 to 1.42) | flat |
| `LLM_DICTION / significant` | 1856 | 0.52 (0.47 to 0.56) | 0.49 (0.45 to 0.53) | 1091 | 0.40 (0.36 to 0.44) | 0.44 (0.39 to 0.48) | 0.77 (0.68 to 0.88) | fell |
| `BORROWED_RIGOUR / state space` | 42 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.75 (0.32 to 2.13) | flat |
| `HEDGE_STACK / is not necessarily` | 16 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.74 (0.27 to 1.73) | flat |
| `VAGUE_QUANTIFIER / a wide range of` | 178 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 98 | 0.04 (0.03 to 0.04) | 0.04 (0.03 to 0.05) | 0.72 (0.52 to 0.98) | fell |
| `BORROWED_RIGOUR / solution space` | 44 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.01 to 0.02) | 0.72 (0.23 to 3.27) | flat |
| `VAGUE_QUANTIFIER / a significant number of` | 18 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 9 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 0.66 (0.25 to 1.49) | flat |
| `FRAME_MARKER / it is important to` | 158 | 0.04 (0.04 to 0.05) | 0.04 (0.03 to 0.05) | 72 | 0.03 (0.02 to 0.03) | 0.03 (0.02 to 0.03) | 0.60 (0.41 to 0.84) | fell |
| `BORROWED_RIGOUR / threat model` | 27 | 0.01 (0.00 to 0.01) | 0.02 (0.00 to 0.06) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.54 (0.10 to 2.07) | flat |
| `VAGUE_QUANTIFIER / a variety of` | 163 | 0.05 (0.04 to 0.06) | 0.04 (0.03 to 0.06) | 62 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.03) | 0.50 (0.36 to 0.69) | fell |
| `CLOSER / essentially,` | 19 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 7 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.48 (0.11 to 1.22) | flat |
| `CONSULTANT_REGISTER / leveraged` | 75 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.02) | 25 | 0.01 (0.01 to 0.01) | 0.01 (0.00 to 0.01) | 0.44 (0.24 to 0.79) | fell |
| `VAGUE_QUANTIFIER / vast majority` | 41 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.01) | 13 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.42 (0.19 to 0.77) | fell |
| `EMPTY_FRAME / in other words` | 246 | 0.07 (0.06 to 0.08) | 0.08 (0.06 to 0.09) | 73 | 0.03 (0.02 to 0.03) | 0.02 (0.02 to 0.03) | 0.39 (0.28 to 0.53) | fell |
| `BORROWED_RIGOUR / state of the art` | 40 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 11 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0.36 (0.15 to 0.73) | fell |
| `HEDGE_STACK / are not necessarily` | 17 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 4 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.31 (0.05 to 0.78) | fell |
| `FRAME_MARKER / in today's` | 24 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 1 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.05 (0.00 to 0.19) | fell |

## `ALTERNATIVE_FRAMING` by pattern

The TF-007 split: `af_rather_than` and `af_instead_of` apart, per text type, rows with at least 20 findings.

| text type | pattern | pre n | post n | ratio (95% CI) | verdict |
|---|---|---|---|---|---|
| abstract | `af_instead_of` | 19 | 18 | 0.94 (0.48 to 1.83) | flat |
| abstract | `af_less_than` | 85 | 82 | 0.96 (0.70 to 1.32) | flat |
| abstract | `af_rather_than` | 13 | 38 | 2.90 (1.54 to 6.48) | rose |
| introduction | `af_instead_of` | 107 | 76 | 0.86 (0.62 to 1.19) | flat |
| introduction | `af_less_than` | 389 | 218 | 0.68 (0.54 to 0.85) | fell |
| introduction | `af_rather_than` | 74 | 246 | 4.04 (3.09 to 5.48) | rose |
| body | `af_instead_of` | 721 | 478 | 0.87 (0.74 to 1.02) | flat |
| body | `af_less_than` | 2668 | 1195 | 0.59 (0.53 to 0.65) | fell |
| body | `af_rather_than` | 352 | 1462 | 5.47 (4.48 to 6.68) | rose |
| related | `af_instead_of` | 124 | 81 | 0.84 (0.60 to 1.13) | flat |
| related | `af_less_than` | 286 | 118 | 0.53 (0.40 to 0.66) | fell |
| related | `af_rather_than` | 65 | 269 | 5.33 (3.99 to 7.49) | rose |
| conclusion | `af_instead_of` | 24 | 7 | 0.39 (0.11 to 1.00) | flat |
| conclusion | `af_less_than` | 101 | 59 | 0.79 (0.56 to 1.12) | flat |
| conclusion | `af_rather_than` | 18 | 68 | 5.10 (2.80 to 11.31) | rose |
| all | `af_instead_of` | 976 | 642 | 0.85 (0.74 to 0.98) | fell |
| all | `af_less_than` | 3444 | 1590 | 0.60 (0.54 to 0.66) | fell |
| all | `af_rather_than` | 509 | 2045 | 5.22 (4.37 to 6.23) | rose |
