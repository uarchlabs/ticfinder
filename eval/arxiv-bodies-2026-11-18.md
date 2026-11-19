# ticfinder construction rates in arXiv cs.AR paper bodies, a pilot

Generated 2026-11-18 by `eval/arxiv_bodies.py` (TF-005). Aggregates only: no paper text, titles or ids.

## Setup

| item | value |
|---|---|
| papers | TF-004 primary `cs.AR` sets (month manifests); windows by v1 date: pre 2018-01-01 to 2021-12-31, post 2025-01-01 to the latest TF-004 date |
| sample | each window's ids shuffled with seed `20261118-bodies-<window>`; walked in order, the first 200 with usable LaTeX source kept |
| source | `export.arxiv.org/e-print/<id>v1` (the v1 source, so a body cannot hold a later revision), 3.5 s between requests |
| abstracts | the same papers' API abstracts (latest version, as in TF-004), masked with the TF-004 masker |
| ticfinder | `tools/ticfinder.py` at 69e1743 (sha256 c1c7d5943a28); defaults: `en_core_web_md`, code masker on, `ticfinder-phrases.json`; text analysed as `.txt` |
| LaTeX masker | `arxiv_bodies.py`, blanks in place: preamble, comments, back matter (bibliography and appendices), math, floats and code with captions, references, labels, URLs, footnotes, headings, command names (text commands keep their argument), `\item` markers, the abstract and acknowledgements. TeX `---` becomes U+2014 and two spaces. `selftest` holds its rows |
| sections | A section runs from its \section heading to the next one. The first section, or any heading containing "introduction", is introduction. Otherwise a heading containing "conclusion", "summary" or "future work" is conclusion, and one containing "related work", "background" or "prior work" is related. Everything else is body. Matching ignores case. Text between \begin{document} and the first \section (after the title, abstract and keywords are masked) counts as introduction, since an unheaded opening is the introduction; a paper with no \section is all introduction. Findings are assigned to a section by offset |
| bootstrap | 2000 draws over papers, seed 5005; one index matrix per window shared by every text type, so comparisons between text types are paired; percentile 95% intervals (nearest rank for ratios) |
| rates | pooled: total findings / total words x 1,000; mean: the mean of per-paper rates over papers with words in that text type. Words are alphabetic spaCy tokens after masking |

## Sample and masking

| measure | pre | post |
|---|---|---|
| TF-004 primary papers | 955 | 2627 |
| walked / kept | 246 / 200 | 223 / 200 |
| skipped: no source | 0 | 0 |
| skipped: PDF only | 41 | 13 |
| skipped: no main file found | 0 | 8 |
| skipped: unpack error | 0 | 0 |
| skipped: other format | 0 | 0 |
| skipped: too little text | 4 | 2 |
| skipped: placeholder text | 1 | 0 |
| masked share, all non-space characters | min 17.8%, median 47.6%, max 95.3%; 141 over 40% | min 20.2%, median 48.5%, max 94.1%; 152 over 40% |
| masked share inside the kept body | min 12.3%, median 29.9%, max 93.8%; 39 over 40% | min 13.3%, median 33.8%, max 93.6%; 56 over 40% |
| several main-file candidates (longest expanded text kept) | 13 | 4 |
| papers with no `\section` | 1 | 0 |
| unresolved `\input` / `\include` | 23 | 4 |
| TeX `---` in kept text | 259 | 350 |
| spaced ` -- ` in kept text | 219 | 195 |
| Unicode em dash in kept text | 1 | 433 |
| Unicode en dash in kept text | 12 | 260 |
| ticfinder masked_pct, mean per paper | 0.06% | 0.03% |
| findings outside any section | 0 | 0 |
| papers where section words do not sum to ticfinder's count | 0 | 0 |

## Words per text type

| text type | pre words | pre papers with text | post words | post papers with text |
|---|---|---|---|---|
| abstract | 38,478 | 200 | 37,794 | 200 |
| introduction | 167,582 | 199 | 135,717 | 200 |
| body | 917,673 | 198 | 658,473 | 200 |
| related | 166,586 | 141 | 104,882 | 140 |
| conclusion | 46,202 | 184 | 32,221 | 194 |
| all | 1,298,043 | 200 | 931,293 | 200 |

Mean paper length, all sections, words (95% interval): pre 6,490 (5,743 to 7,462), post 4,656 (4,334 to 4,981).

Mean abstract length, words (95% interval): pre 192 (184 to 201), post 189 (182 to 196).

## `EM_DASH` per text type

| text type | pre n | pre rate (95% CI) | post n | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|
| abstract | 0 | 0.00 (0.00 to 0.00) | 0 | 0.00 (0.00 to 0.00) | - (- to -) | too few |
| introduction | 55 | 0.33 (0.15 to 0.56) | 158 | 1.16 (0.86 to 1.52) | 3.55 (1.91 to 7.98) | rose |
| body | 165 | 0.18 (0.09 to 0.30) | 625 | 0.95 (0.67 to 1.29) | 5.28 (2.87 to 10.98) | rose |
| related | 38 | 0.23 (0.06 to 0.45) | 109 | 1.04 (0.73 to 1.40) | 4.56 (2.12 to 16.10) | rose |
| conclusion | 9 | 0.19 (0.04 to 0.42) | 55 | 1.71 (0.94 to 2.69) | 8.76 (3.22 to 42.35) | rose |
| all | 267 | 0.21 (0.11 to 0.34) | 947 | 1.02 (0.75 to 1.33) | 4.94 (2.77 to 9.81) | rose |

## Abstract against body

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | body n pre / post | body ratio (95% CI) | body over abstract (95% CI) | body ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 35 / 32 | 0.93 (0.54 to 1.60) | 429 / 567 | 1.84 (1.50 to 2.25) | 1.98 (1.21 to 3.34) | no |
| `ALTERNATIVE_FRAMING` | 37 / 40 | 1.10 (0.67 to 1.85) | 950 / 798 | 1.17 (1.02 to 1.34) | 1.06 (0.64 to 1.73) | yes |
| `CONSULTANT_REGISTER` | 65 / 74 | 1.16 (0.79 to 1.73) | 594 / 646 | 1.52 (1.19 to 1.96) | 1.31 (0.89 to 1.94) | yes |
| `LLM_DICTION` | 115 / 136 | 1.20 (0.90 to 1.60) | 1254 / 1165 | 1.29 (1.03 to 1.63) | 1.08 (0.81 to 1.44) | yes |
| `PARTICIPIAL_TAIL` | 67 / 218 | 3.31 (2.51 to 4.53) | 1035 / 3012 | 4.06 (3.46 to 4.74) | 1.22 (0.88 to 1.61) | yes |
| `TRICOLON` | 144 / 254 | 1.80 (1.48 to 2.23) | 2792 / 2831 | 1.41 (1.27 to 1.57) | 0.79 (0.63 to 0.95) | no |
| `VAGUE_QUANTIFIER` | 34 / 32 | 0.96 (0.61 to 1.53) | 126 / 99 | 1.10 (0.74 to 1.56) | 1.14 (0.66 to 1.97) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 30 / 26 | 0.88 (0.49 to 1.57) | 680 / 312 | 0.64 (0.53 to 0.78) | 0.72 (0.40 to 1.31) | yes |
| `TRICOLON / tricolon` | 144 / 254 | 1.80 (1.48 to 2.23) | 2792 / 2830 | 1.41 (1.27 to 1.57) | 0.79 (0.63 to 0.95) | no |

6 of 9 rows have the body ratio inside the abstract interval.

## Introduction against body

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | introduction n pre / post | introduction ratio (95% CI) | body n pre / post | body ratio (95% CI) | body over introduction (95% CI) | body ratio inside introduction interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 145 / 140 | 1.19 (0.90 to 1.59) | 429 / 567 | 1.84 (1.50 to 2.25) | 1.54 (1.15 to 2.07) | no |
| `ALTERNATIVE_FRAMING` | 126 / 128 | 1.25 (0.95 to 1.65) | 950 / 798 | 1.17 (1.02 to 1.34) | 0.93 (0.71 to 1.22) | yes |
| `BORROWED_RIGOUR` | 67 / 37 | 0.68 (0.42 to 1.07) | 147 / 169 | 1.60 (1.16 to 2.18) | 2.35 (1.48 to 3.87) | no |
| `CONSULTANT_REGISTER` | 227 / 264 | 1.44 (1.11 to 1.88) | 594 / 646 | 1.52 (1.19 to 1.96) | 1.06 (0.79 to 1.38) | yes |
| `CORRECTIVE_CONTRAST` | 54 / 63 | 1.44 (0.96 to 2.11) | 262 / 266 | 1.41 (1.06 to 1.91) | 0.98 (0.63 to 1.50) | yes |
| `EM_DASH` | 55 / 158 | 3.55 (1.91 to 7.98) | 165 / 625 | 5.28 (2.87 to 10.98) | 1.49 (0.71 to 2.79) | yes |
| `LLM_DICTION` | 395 / 493 | 1.54 (1.27 to 1.85) | 1254 / 1165 | 1.29 (1.03 to 1.63) | 0.84 (0.69 to 1.04) | yes |
| `PARTICIPIAL_TAIL` | 270 / 786 | 3.59 (2.99 to 4.37) | 1035 / 3012 | 4.06 (3.46 to 4.74) | 1.13 (0.93 to 1.36) | yes |
| `TRICOLON` | 620 / 779 | 1.55 (1.34 to 1.79) | 2792 / 2831 | 1.41 (1.27 to 1.57) | 0.91 (0.79 to 1.05) | yes |
| `VAGUE_QUANTIFIER` | 99 / 105 | 1.31 (0.96 to 1.79) | 126 / 99 | 1.10 (0.74 to 1.56) | 0.84 (0.50 to 1.32) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 79 / 43 | 0.67 (0.45 to 0.97) | 680 / 312 | 0.64 (0.53 to 0.78) | 0.95 (0.63 to 1.42) | yes |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 47 / 85 | 2.23 (1.53 to 3.39) | 270 / 486 | 2.51 (2.01 to 3.14) | 1.12 (0.73 to 1.66) | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 39 / 56 | 1.77 (1.12 to 2.74) | 187 / 167 | 1.24 (0.95 to 1.63) | 0.70 (0.44 to 1.13) | yes |
| `TRICOLON / tricolon` | 620 / 779 | 1.55 (1.34 to 1.79) | 2792 / 2830 | 1.41 (1.27 to 1.57) | 0.91 (0.79 to 1.05) | yes |

12 of 14 rows have the body ratio inside the introduction interval.

## Abstract against introduction

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | introduction n pre / post | introduction ratio (95% CI) | introduction over abstract (95% CI) | introduction ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 35 / 32 | 0.93 (0.54 to 1.60) | 145 / 140 | 1.19 (0.90 to 1.59) | 1.28 (0.76 to 2.23) | yes |
| `ALTERNATIVE_FRAMING` | 37 / 40 | 1.10 (0.67 to 1.85) | 126 / 128 | 1.25 (0.95 to 1.65) | 1.14 (0.67 to 1.92) | yes |
| `CONSULTANT_REGISTER` | 65 / 74 | 1.16 (0.79 to 1.73) | 227 / 264 | 1.44 (1.11 to 1.88) | 1.24 (0.87 to 1.80) | yes |
| `LLM_DICTION` | 115 / 136 | 1.20 (0.90 to 1.60) | 395 / 493 | 1.54 (1.27 to 1.85) | 1.28 (0.96 to 1.69) | yes |
| `PARTICIPIAL_TAIL` | 67 / 218 | 3.31 (2.51 to 4.53) | 270 / 786 | 3.59 (2.99 to 4.37) | 1.09 (0.80 to 1.44) | yes |
| `TRICOLON` | 144 / 254 | 1.80 (1.48 to 2.23) | 620 / 779 | 1.55 (1.34 to 1.79) | 0.86 (0.70 to 1.05) | yes |
| `VAGUE_QUANTIFIER` | 34 / 32 | 0.96 (0.61 to 1.53) | 99 / 105 | 1.31 (0.96 to 1.79) | 1.37 (0.82 to 2.28) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 30 / 26 | 0.88 (0.49 to 1.57) | 79 / 43 | 0.67 (0.45 to 0.97) | 0.76 (0.43 to 1.35) | yes |
| `TRICOLON / tricolon` | 144 / 254 | 1.80 (1.48 to 2.23) | 620 / 779 | 1.55 (1.34 to 1.79) | 0.86 (0.70 to 1.05) | yes |

9 of 9 rows have the introduction ratio inside the abstract interval.

## Abstract against all sections

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | all n pre / post | all ratio (95% CI) | all over abstract (95% CI) | all ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 35 / 32 | 0.93 (0.54 to 1.60) | 737 / 832 | 1.57 (1.31 to 1.89) | 1.69 (1.03 to 2.86) | yes |
| `ALTERNATIVE_FRAMING` | 37 / 40 | 1.10 (0.67 to 1.85) | 1224 / 1082 | 1.23 (1.08 to 1.40) | 1.12 (0.68 to 1.82) | yes |
| `CONSULTANT_REGISTER` | 65 / 74 | 1.16 (0.79 to 1.73) | 1113 / 1161 | 1.45 (1.20 to 1.76) | 1.25 (0.88 to 1.77) | yes |
| `LLM_DICTION` | 115 / 136 | 1.20 (0.90 to 1.60) | 2047 / 2044 | 1.39 (1.17 to 1.67) | 1.16 (0.88 to 1.52) | yes |
| `PARTICIPIAL_TAIL` | 67 / 218 | 3.31 (2.51 to 4.53) | 1559 / 4505 | 4.03 (3.49 to 4.62) | 1.22 (0.89 to 1.57) | yes |
| `TRICOLON` | 144 / 254 | 1.80 (1.48 to 2.23) | 4148 / 4386 | 1.47 (1.32 to 1.63) | 0.82 (0.67 to 0.99) | no |
| `VAGUE_QUANTIFIER` | 34 / 32 | 0.96 (0.61 to 1.53) | 302 / 268 | 1.24 (0.98 to 1.54) | 1.29 (0.81 to 2.06) | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 30 / 26 | 0.88 (0.49 to 1.57) | 844 / 398 | 0.66 (0.55 to 0.79) | 0.74 (0.41 to 1.31) | yes |
| `TRICOLON / tricolon` | 144 / 254 | 1.80 (1.48 to 2.23) | 4148 / 4385 | 1.47 (1.32 to 1.63) | 0.82 (0.67 to 0.99) | no |

7 of 9 rows have the all ratio inside the abstract interval.

## Abstract against related work

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | related n pre / post | related ratio (95% CI) | related over abstract (95% CI) | related ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 35 / 32 | 0.93 (0.54 to 1.60) | 124 / 99 | 1.27 (0.90 to 1.77) | 1.36 (0.74 to 2.54) | yes |
| `ALTERNATIVE_FRAMING` | 37 / 40 | 1.10 (0.67 to 1.85) | 112 / 122 | 1.73 (1.33 to 2.24) | 1.57 (0.89 to 2.69) | yes |
| `CONSULTANT_REGISTER` | 65 / 74 | 1.16 (0.79 to 1.73) | 228 / 176 | 1.23 (0.95 to 1.59) | 1.06 (0.68 to 1.59) | yes |
| `LLM_DICTION` | 115 / 136 | 1.20 (0.90 to 1.60) | 265 / 264 | 1.58 (1.21 to 2.06) | 1.31 (0.93 to 1.88) | yes |
| `PARTICIPIAL_TAIL` | 67 / 218 | 3.31 (2.51 to 4.53) | 205 / 526 | 4.08 (3.29 to 5.11) | 1.23 (0.88 to 1.67) | yes |
| `TRICOLON` | 144 / 254 | 1.80 (1.48 to 2.23) | 589 / 579 | 1.56 (1.28 to 1.90) | 0.87 (0.69 to 1.09) | yes |
| `VAGUE_QUANTIFIER` | 34 / 32 | 0.96 (0.61 to 1.53) | 48 / 51 | 1.69 (1.11 to 2.58) | 1.76 (0.94 to 3.24) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 30 / 26 | 0.88 (0.49 to 1.57) | 64 / 31 | 0.77 (0.49 to 1.18) | 0.87 (0.41 to 1.72) | yes |
| `TRICOLON / tricolon` | 144 / 254 | 1.80 (1.48 to 2.23) | 589 / 579 | 1.56 (1.28 to 1.90) | 0.87 (0.69 to 1.09) | yes |

8 of 9 rows have the related ratio inside the abstract interval.

## Body against related work

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | body n pre / post | body ratio (95% CI) | related n pre / post | related ratio (95% CI) | related over body (95% CI) | related ratio inside body interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 429 / 567 | 1.84 (1.50 to 2.25) | 124 / 99 | 1.27 (0.90 to 1.77) | 0.69 (0.51 to 0.94) | no |
| `ALTERNATIVE_FRAMING` | 950 / 798 | 1.17 (1.02 to 1.34) | 112 / 122 | 1.73 (1.33 to 2.24) | 1.48 (1.11 to 1.95) | no |
| `BORROWED_RIGOUR` | 147 / 169 | 1.60 (1.16 to 2.18) | 87 / 46 | 0.84 (0.52 to 1.44) | 0.52 (0.30 to 0.97) | no |
| `CONSULTANT_REGISTER` | 594 / 646 | 1.52 (1.19 to 1.96) | 228 / 176 | 1.23 (0.95 to 1.59) | 0.81 (0.57 to 1.14) | yes |
| `CORRECTIVE_CONTRAST` | 262 / 266 | 1.41 (1.06 to 1.91) | 70 / 49 | 1.11 (0.75 to 1.68) | 0.79 (0.51 to 1.23) | yes |
| `EMPHATIC_REFLEXIVE` | 106 / 77 | 1.01 (0.70 to 1.51) | 21 / 24 | 1.82 (0.88 to 3.89) | 1.79 (0.83 to 3.78) | no |
| `EM_DASH` | 165 / 625 | 5.28 (2.87 to 10.98) | 38 / 109 | 4.56 (2.12 to 16.10) | 0.86 (0.52 to 2.10) | yes |
| `LLM_DICTION` | 1254 / 1165 | 1.29 (1.03 to 1.63) | 265 / 264 | 1.58 (1.21 to 2.06) | 1.22 (0.92 to 1.63) | yes |
| `PARTICIPIAL_TAIL` | 1035 / 3012 | 4.06 (3.46 to 4.74) | 205 / 526 | 4.08 (3.29 to 5.11) | 1.00 (0.82 to 1.25) | yes |
| `TRICOLON` | 2792 / 2831 | 1.41 (1.27 to 1.57) | 589 / 579 | 1.56 (1.28 to 1.90) | 1.10 (0.93 to 1.32) | yes |
| `VAGUE_QUANTIFIER` | 126 / 99 | 1.10 (0.74 to 1.56) | 48 / 51 | 1.69 (1.11 to 2.58) | 1.54 (0.94 to 2.60) | no |
| `ALTERNATIVE_FRAMING / af_less_than` | 680 / 312 | 0.64 (0.53 to 0.78) | 64 / 31 | 0.77 (0.49 to 1.18) | 1.20 (0.75 to 1.91) | yes |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 270 / 486 | 2.51 (2.01 to 3.14) | 48 / 91 | 3.01 (2.05 to 4.73) | 1.20 (0.79 to 1.98) | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 187 / 167 | 1.24 (0.95 to 1.63) | 63 / 42 | 1.06 (0.68 to 1.67) | 0.85 (0.53 to 1.39) | yes |
| `TRICOLON / tricolon` | 2792 / 2830 | 1.41 (1.27 to 1.57) | 589 / 579 | 1.56 (1.28 to 1.90) | 1.11 (0.93 to 1.32) | yes |

10 of 15 rows have the related ratio inside the body interval.

## Abstract against conclusion

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | abstract n pre / post | abstract ratio (95% CI) | conclusion n pre / post | conclusion ratio (95% CI) | conclusion over abstract (95% CI) | conclusion ratio inside abstract interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 35 / 32 | 0.93 (0.54 to 1.60) | 39 / 26 | 0.96 (0.55 to 1.63) | 1.03 (0.50 to 2.07) | yes |
| `ALTERNATIVE_FRAMING` | 37 / 40 | 1.10 (0.67 to 1.85) | 36 / 34 | 1.35 (0.84 to 2.26) | 1.23 (0.66 to 2.39) | yes |
| `CONSULTANT_REGISTER` | 65 / 74 | 1.16 (0.79 to 1.73) | 64 / 75 | 1.68 (1.09 to 2.64) | 1.45 (0.86 to 2.41) | yes |
| `LLM_DICTION` | 115 / 136 | 1.20 (0.90 to 1.60) | 133 / 122 | 1.32 (0.96 to 1.74) | 1.09 (0.76 to 1.56) | yes |
| `PARTICIPIAL_TAIL` | 67 / 218 | 3.31 (2.51 to 4.53) | 49 / 181 | 5.30 (3.78 to 7.55) | 1.60 (1.05 to 2.41) | no |
| `TRICOLON` | 144 / 254 | 1.80 (1.48 to 2.23) | 147 / 197 | 1.92 (1.48 to 2.46) | 1.07 (0.80 to 1.40) | yes |
| `TRICOLON / tricolon` | 144 / 254 | 1.80 (1.48 to 2.23) | 147 / 197 | 1.92 (1.48 to 2.46) | 1.07 (0.80 to 1.40) | yes |

6 of 7 rows have the conclusion ratio inside the abstract interval.

## Body against conclusion

Construction and pattern rows with at least 20 findings in both windows of both text types. A ratio is post rate over pre rate. The ratio of ratios uses the same bootstrap draws for both text types (paired).

| row | body n pre / post | body ratio (95% CI) | conclusion n pre / post | conclusion ratio (95% CI) | conclusion over body (95% CI) | conclusion ratio inside body interval |
|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 429 / 567 | 1.84 (1.50 to 2.25) | 39 / 26 | 0.96 (0.55 to 1.63) | 0.52 (0.29 to 0.88) | no |
| `ALTERNATIVE_FRAMING` | 950 / 798 | 1.17 (1.02 to 1.34) | 36 / 34 | 1.35 (0.84 to 2.26) | 1.16 (0.72 to 1.90) | no |
| `CONSULTANT_REGISTER` | 594 / 646 | 1.52 (1.19 to 1.96) | 64 / 75 | 1.68 (1.09 to 2.64) | 1.11 (0.74 to 1.65) | yes |
| `LLM_DICTION` | 1254 / 1165 | 1.29 (1.03 to 1.63) | 133 / 122 | 1.32 (0.96 to 1.74) | 1.02 (0.74 to 1.35) | yes |
| `PARTICIPIAL_TAIL` | 1035 / 3012 | 4.06 (3.46 to 4.74) | 49 / 181 | 5.30 (3.78 to 7.55) | 1.31 (0.94 to 1.85) | no |
| `TRICOLON` | 2792 / 2831 | 1.41 (1.27 to 1.57) | 147 / 197 | 1.92 (1.48 to 2.46) | 1.36 (1.07 to 1.72) | no |
| `TRICOLON / tricolon` | 2792 / 2830 | 1.41 (1.27 to 1.57) | 147 / 197 | 1.92 (1.48 to 2.46) | 1.36 (1.07 to 1.72) | no |

2 of 7 rows have the conclusion ratio inside the body interval.

## Check against TF-004

The sample's abstract ratio against the TF-004 interval for the full abstract sets (955 and 2,627 papers), for rows with at least 20 findings in TF-004.

| row | TF-004 ratio (95% CI) | sample abstract n pre / post | sample abstract ratio (95% CI) | sample ratio inside TF-004 interval | TF-004 ratio inside sample interval |
|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 1.27 (1.02 to 1.59) | 35 / 32 | 0.93 (0.54 to 1.60) | no | yes |
| `ALTERNATIVE_FRAMING` | 1.23 (1.02 to 1.51) | 37 / 40 | 1.10 (0.67 to 1.85) | yes | yes |
| `BORROWED_RIGOUR` | 1.02 (0.74 to 1.45) | 16 / 13 | 0.83 (0.36 to 1.92) | yes | yes |
| `CONSULTANT_REGISTER` | 1.43 (1.23 to 1.67) | 65 / 74 | 1.16 (0.79 to 1.73) | no | yes |
| `CORRECTIVE_CONTRAST` | 1.04 (0.71 to 1.57) | 11 / 5 | 0.46 (0.09 to 1.44) | no | yes |
| `DISGUISE_METAPHOR` | 2.87 (1.10 to inf) | 1 / 1 | 1.02 (0.00 to inf) | no | yes |
| `EMPHATIC_REFLEXIVE` | 1.30 (0.74 to 2.63) | 4 / 3 | 0.76 (0.00 to 5.09) | yes | yes |
| `FRAME_MARKER` | 0.27 (0.12 to 0.56) | 5 / 0 | 0.00 (0.00 to 0.00) | no | no |
| `HOLLOW_BOOSTER` | 1.43 (0.79 to 3.56) | 1 / 3 | 3.05 (0.00 to inf) | yes | yes |
| `LLM_DICTION` | 1.27 (1.14 to 1.44) | 115 / 136 | 1.20 (0.90 to 1.60) | yes | yes |
| `PARTICIPIAL_TAIL` | 3.14 (2.79 to 3.57) | 67 / 218 | 3.31 (2.51 to 4.53) | yes | yes |
| `TRICOLON` | 1.44 (1.32 to 1.56) | 144 / 254 | 1.80 (1.48 to 2.23) | no | no |
| `VAGUE_QUANTIFIER` | 0.85 (0.70 to 1.03) | 34 / 32 | 0.96 (0.61 to 1.53) | yes | yes |
| `ALTERNATIVE_FRAMING / af_less_than` | 0.90 (0.72 to 1.17) | 30 / 26 | 0.88 (0.49 to 1.57) | yes | yes |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 2.15 (1.56 to 3.29) | 7 / 14 | 2.04 (0.88 to 5.92) | yes | yes |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 1.00 (0.69 to 1.57) | 9 / 4 | 0.45 (0.08 to 1.48) | no | yes |
| `TRICOLON / tricolon` | 1.44 (1.32 to 1.56) | 144 / 254 | 1.80 (1.48 to 2.23) | no | no |

9 of 17 sample abstract ratios lie inside the TF-004 interval; the TF-004 ratio lies inside the sample interval for 14 of 17. The sample's abstract counts equal the TF-004 per-paper counts for the same papers (same abstracts, same ticfinder), so the differences come from drawing 200 papers, and from keeping only papers with usable LaTeX. A 200-paper interval is two to three times as wide as the TF-004 one, so about half of the sample points are expected inside the narrower TF-004 interval by sampling alone.

## Rates per text type

Sorted by ratio. `n` is findings; the verdict is `rose` when the ratio interval is above 1, `fell` below, `flat` when it spans 1, `too few` under 20 findings in both windows together. Construction tables list every row with a finding; pattern tables list rows with at least 20.

### abstract

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `NEG_ESCALATION` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1 | 0.03 (0.00 to 0.08) | 0.02 (0.00 to 0.06) | inf (inf to inf) | too few |
| `PARTICIPIAL_TAIL` | 67 | 1.74 (1.31 to 2.19) | 1.65 (1.23 to 2.10) | 218 | 5.77 (5.02 to 6.53) | 5.88 (5.08 to 6.72) | 3.31 (2.51 to 4.53) | rose |
| `HOLLOW_BOOSTER` | 1 | 0.03 (0.00 to 0.10) | 0.03 (0.00 to 0.10) | 3 | 0.08 (0.00 to 0.18) | 0.08 (0.00 to 0.18) | 3.05 (0.00 to inf) | too few |
| `TRICOLON` | 144 | 3.74 (3.12 to 4.37) | 3.84 (3.15 to 4.50) | 254 | 6.72 (5.92 to 7.54) | 6.88 (6.01 to 7.74) | 1.80 (1.48 to 2.23) | rose |
| `LLM_DICTION` | 115 | 2.99 (2.36 to 3.67) | 3.03 (2.38 to 3.75) | 136 | 3.60 (2.94 to 4.27) | 3.79 (3.08 to 4.49) | 1.20 (0.90 to 1.60) | flat |
| `CONSULTANT_REGISTER` | 65 | 1.69 (1.22 to 2.16) | 1.59 (1.15 to 2.04) | 74 | 1.96 (1.49 to 2.47) | 2.05 (1.54 to 2.61) | 1.16 (0.79 to 1.73) | flat |
| `ALTERNATIVE_FRAMING` | 37 | 0.96 (0.64 to 1.31) | 0.92 (0.60 to 1.27) | 40 | 1.06 (0.73 to 1.43) | 0.99 (0.67 to 1.38) | 1.10 (0.67 to 1.85) | flat |
| `CLOSER` | 1 | 0.03 (0.00 to 0.08) | 0.05 (0.00 to 0.15) | 1 | 0.03 (0.00 to 0.08) | 0.02 (0.00 to 0.07) | 1.02 (0.00 to inf) | too few |
| `DISGUISE_METAPHOR` | 1 | 0.03 (0.00 to 0.08) | 0.02 (0.00 to 0.07) | 1 | 0.03 (0.00 to 0.08) | 0.02 (0.00 to 0.06) | 1.02 (0.00 to inf) | too few |
| `VAGUE_QUANTIFIER` | 34 | 0.88 (0.59 to 1.18) | 0.78 (0.52 to 1.06) | 32 | 0.85 (0.59 to 1.12) | 0.95 (0.61 to 1.35) | 0.96 (0.61 to 1.53) | flat |
| `ABSTRACT_ADVERB` | 35 | 0.91 (0.58 to 1.29) | 0.77 (0.49 to 1.09) | 32 | 0.85 (0.55 to 1.15) | 0.82 (0.51 to 1.16) | 0.93 (0.54 to 1.60) | flat |
| `BORROWED_RIGOUR` | 16 | 0.42 (0.20 to 0.67) | 0.39 (0.19 to 0.63) | 13 | 0.34 (0.18 to 0.53) | 0.37 (0.17 to 0.58) | 0.83 (0.36 to 1.92) | flat |
| `EMPHATIC_REFLEXIVE` | 4 | 0.10 (0.03 to 0.21) | 0.14 (0.02 to 0.30) | 3 | 0.08 (0.00 to 0.18) | 0.08 (0.00 to 0.18) | 0.76 (0.00 to 5.09) | too few |
| `CORRECTIVE_CONTRAST` | 11 | 0.29 (0.11 to 0.48) | 0.33 (0.13 to 0.58) | 5 | 0.13 (0.03 to 0.26) | 0.13 (0.02 to 0.25) | 0.46 (0.09 to 1.44) | too few |
| `FRAME_MARKER` | 5 | 0.13 (0.03 to 0.26) | 0.14 (0.03 to 0.28) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |
| `EMPTY_FRAME` | 2 | 0.05 (0.00 to 0.13) | 0.05 (0.00 to 0.13) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |
| `HEDGE_STACK` | 1 | 0.03 (0.00 to 0.08) | 0.02 (0.00 to 0.07) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `PARTICIPIAL_TAIL / participial_tail` | 67 | 1.74 (1.31 to 2.19) | 1.65 (1.23 to 2.10) | 218 | 5.77 (5.02 to 6.53) | 5.88 (5.08 to 6.72) | 3.31 (2.51 to 4.53) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 7 | 0.18 (0.08 to 0.33) | 0.18 (0.07 to 0.33) | 14 | 0.37 (0.20 to 0.56) | 0.35 (0.18 to 0.53) | 2.04 (0.88 to 5.92) | flat |
| `TRICOLON / tricolon` | 144 | 3.74 (3.12 to 4.37) | 3.84 (3.15 to 4.50) | 254 | 6.72 (5.92 to 7.54) | 6.88 (6.01 to 7.74) | 1.80 (1.48 to 2.23) | rose |
| `LLM_DICTION / -` | 115 | 2.99 (2.36 to 3.67) | 3.03 (2.38 to 3.75) | 136 | 3.60 (2.94 to 4.27) | 3.79 (3.08 to 4.49) | 1.20 (0.90 to 1.60) | flat |
| `CONSULTANT_REGISTER / -` | 65 | 1.69 (1.22 to 2.16) | 1.59 (1.15 to 2.04) | 74 | 1.96 (1.49 to 2.47) | 2.05 (1.54 to 2.61) | 1.16 (0.79 to 1.73) | flat |
| `VAGUE_QUANTIFIER / -` | 34 | 0.88 (0.59 to 1.18) | 0.78 (0.52 to 1.06) | 32 | 0.85 (0.59 to 1.12) | 0.95 (0.61 to 1.35) | 0.96 (0.61 to 1.53) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 35 | 0.91 (0.58 to 1.29) | 0.77 (0.49 to 1.09) | 32 | 0.85 (0.55 to 1.15) | 0.82 (0.51 to 1.16) | 0.93 (0.54 to 1.60) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 30 | 0.78 (0.51 to 1.08) | 0.74 (0.47 to 1.03) | 26 | 0.69 (0.43 to 0.98) | 0.64 (0.40 to 0.93) | 0.88 (0.49 to 1.57) | flat |
| `BORROWED_RIGOUR / -` | 16 | 0.42 (0.20 to 0.67) | 0.39 (0.19 to 0.63) | 13 | 0.34 (0.18 to 0.53) | 0.37 (0.17 to 0.58) | 0.83 (0.36 to 1.92) | flat |

### introduction

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `DISGUISE_METAPHOR` | 1 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 5 | 0.04 (0.01 to 0.07) | 0.03 (0.01 to 0.05) | 6.17 (1.18 to inf) | too few |
| `HEDGE_STACK` | 1 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.01) | 3 | 0.02 (0.00 to 0.05) | 0.02 (0.00 to 0.06) | 3.70 (0.00 to inf) | too few |
| `PARTICIPIAL_TAIL` | 270 | 1.61 (1.36 to 1.88) | 1.60 (1.33 to 1.89) | 786 | 5.79 (5.24 to 6.34) | 5.72 (5.14 to 6.26) | 3.59 (2.99 to 4.37) | rose |
| `EM_DASH` | 55 | 0.33 (0.15 to 0.56) | 0.29 (0.14 to 0.49) | 158 | 1.16 (0.86 to 1.52) | 1.16 (0.87 to 1.49) | 3.55 (1.91 to 7.98) | rose |
| `TRICOLON` | 620 | 3.70 (3.33 to 4.08) | 3.91 (3.50 to 4.33) | 779 | 5.74 (5.10 to 6.35) | 6.30 (5.56 to 7.07) | 1.55 (1.34 to 1.79) | rose |
| `LLM_DICTION` | 395 | 2.36 (2.04 to 2.68) | 2.46 (2.11 to 2.81) | 493 | 3.63 (3.17 to 4.10) | 3.55 (3.09 to 4.02) | 1.54 (1.27 to 1.85) | rose |
| `CORRECTIVE_CONTRAST` | 54 | 0.32 (0.25 to 0.40) | 0.32 (0.22 to 0.41) | 63 | 0.46 (0.33 to 0.62) | 0.56 (0.37 to 0.78) | 1.44 (0.96 to 2.11) | flat |
| `CONSULTANT_REGISTER` | 227 | 1.35 (1.11 to 1.61) | 1.31 (1.07 to 1.55) | 264 | 1.95 (1.60 to 2.31) | 1.91 (1.58 to 2.25) | 1.44 (1.11 to 1.88) | rose |
| `HOLLOW_BOOSTER` | 14 | 0.08 (0.04 to 0.13) | 0.07 (0.04 to 0.11) | 15 | 0.11 (0.06 to 0.17) | 0.10 (0.05 to 0.16) | 1.32 (0.60 to 2.87) | flat |
| `VAGUE_QUANTIFIER` | 99 | 0.59 (0.46 to 0.73) | 0.60 (0.46 to 0.75) | 105 | 0.77 (0.63 to 0.93) | 0.86 (0.68 to 1.06) | 1.31 (0.96 to 1.79) | flat |
| `ALTERNATIVE_FRAMING` | 126 | 0.75 (0.61 to 0.90) | 0.86 (0.65 to 1.10) | 128 | 0.94 (0.77 to 1.12) | 0.89 (0.71 to 1.07) | 1.25 (0.95 to 1.65) | flat |
| `GAPPED_ANTITHESIS` | 2 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.03) | 2 | 0.01 (0.00 to 0.04) | 0.01 (0.00 to 0.02) | 1.23 (0.00 to inf) | too few |
| `ABSTRACT_ADVERB` | 145 | 0.87 (0.69 to 1.04) | 0.86 (0.67 to 1.06) | 140 | 1.03 (0.85 to 1.21) | 1.01 (0.81 to 1.21) | 1.19 (0.90 to 1.59) | flat |
| `EMPHATIC_REFLEXIVE` | 22 | 0.13 (0.07 to 0.20) | 0.13 (0.07 to 0.20) | 18 | 0.13 (0.08 to 0.20) | 0.12 (0.07 to 0.18) | 1.01 (0.51 to 2.16) | flat |
| `CLOSER` | 24 | 0.14 (0.09 to 0.20) | 0.13 (0.08 to 0.19) | 18 | 0.13 (0.07 to 0.20) | 0.11 (0.06 to 0.16) | 0.93 (0.47 to 1.64) | flat |
| `FRAME_MARKER` | 8 | 0.05 (0.01 to 0.09) | 0.05 (0.01 to 0.08) | 6 | 0.04 (0.01 to 0.08) | 0.04 (0.01 to 0.08) | 0.93 (0.25 to 3.54) | too few |
| `EMPTY_FRAME` | 11 | 0.07 (0.03 to 0.11) | 0.08 (0.03 to 0.14) | 8 | 0.06 (0.02 to 0.10) | 0.05 (0.02 to 0.10) | 0.90 (0.31 to 2.34) | too few |
| `BORROWED_RIGOUR` | 67 | 0.40 (0.28 to 0.52) | 0.39 (0.27 to 0.52) | 37 | 0.27 (0.18 to 0.37) | 0.28 (0.18 to 0.39) | 0.68 (0.42 to 1.07) | flat |
| `NEG_ESCALATION` | 1 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `PARTICIPIAL_TAIL / participial_tail` | 270 | 1.61 (1.36 to 1.88) | 1.60 (1.33 to 1.89) | 786 | 5.79 (5.24 to 6.34) | 5.72 (5.14 to 6.26) | 3.59 (2.99 to 4.37) | rose |
| `EM_DASH / -` | 55 | 0.33 (0.15 to 0.56) | 0.29 (0.14 to 0.49) | 158 | 1.16 (0.86 to 1.52) | 1.16 (0.87 to 1.49) | 3.55 (1.91 to 7.98) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 47 | 0.28 (0.20 to 0.37) | 0.26 (0.17 to 0.38) | 85 | 0.63 (0.48 to 0.78) | 0.56 (0.42 to 0.70) | 2.23 (1.53 to 3.39) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 39 | 0.23 (0.17 to 0.30) | 0.24 (0.16 to 0.32) | 56 | 0.41 (0.29 to 0.56) | 0.50 (0.32 to 0.71) | 1.77 (1.12 to 2.74) | rose |
| `TRICOLON / tricolon` | 620 | 3.70 (3.33 to 4.08) | 3.91 (3.50 to 4.33) | 779 | 5.74 (5.10 to 6.35) | 6.30 (5.56 to 7.07) | 1.55 (1.34 to 1.79) | rose |
| `LLM_DICTION / -` | 395 | 2.36 (2.04 to 2.68) | 2.46 (2.11 to 2.81) | 493 | 3.63 (3.17 to 4.10) | 3.55 (3.09 to 4.02) | 1.54 (1.27 to 1.85) | rose |
| `CONSULTANT_REGISTER / -` | 227 | 1.35 (1.11 to 1.61) | 1.31 (1.07 to 1.55) | 264 | 1.95 (1.60 to 2.31) | 1.91 (1.58 to 2.25) | 1.44 (1.11 to 1.88) | rose |
| `HOLLOW_BOOSTER / -` | 14 | 0.08 (0.04 to 0.13) | 0.07 (0.04 to 0.11) | 15 | 0.11 (0.06 to 0.17) | 0.10 (0.05 to 0.16) | 1.32 (0.60 to 2.87) | flat |
| `VAGUE_QUANTIFIER / -` | 99 | 0.59 (0.46 to 0.73) | 0.60 (0.46 to 0.75) | 105 | 0.77 (0.63 to 0.93) | 0.86 (0.68 to 1.06) | 1.31 (0.96 to 1.79) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 145 | 0.87 (0.69 to 1.04) | 0.86 (0.67 to 1.06) | 140 | 1.03 (0.85 to 1.21) | 1.01 (0.81 to 1.21) | 1.19 (0.90 to 1.59) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 22 | 0.13 (0.07 to 0.20) | 0.13 (0.07 to 0.20) | 18 | 0.13 (0.08 to 0.20) | 0.12 (0.07 to 0.18) | 1.01 (0.51 to 2.16) | flat |
| `CLOSER / -` | 24 | 0.14 (0.09 to 0.20) | 0.13 (0.08 to 0.19) | 18 | 0.13 (0.07 to 0.20) | 0.11 (0.06 to 0.16) | 0.93 (0.47 to 1.64) | flat |
| `BORROWED_RIGOUR / -` | 67 | 0.40 (0.28 to 0.52) | 0.39 (0.27 to 0.52) | 37 | 0.27 (0.18 to 0.37) | 0.28 (0.18 to 0.39) | 0.68 (0.42 to 1.07) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 79 | 0.47 (0.37 to 0.59) | 0.60 (0.40 to 0.83) | 43 | 0.32 (0.23 to 0.41) | 0.34 (0.24 to 0.45) | 0.67 (0.45 to 0.97) | fell |

### body

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 165 | 0.18 (0.09 to 0.30) | 0.22 (0.12 to 0.34) | 625 | 0.95 (0.67 to 1.29) | 0.89 (0.67 to 1.15) | 5.28 (2.87 to 10.98) | rose |
| `PARTICIPIAL_TAIL` | 1035 | 1.13 (0.98 to 1.29) | 1.10 (0.95 to 1.26) | 3012 | 4.57 (4.16 to 4.99) | 4.69 (4.26 to 5.11) | 4.06 (3.46 to 4.74) | rose |
| `HOLLOW_BOOSTER` | 51 | 0.06 (0.04 to 0.07) | 0.06 (0.04 to 0.09) | 121 | 0.18 (0.14 to 0.22) | 0.19 (0.14 to 0.24) | 3.31 (2.25 to 4.93) | rose |
| `NEG_ESCALATION` | 5 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 7 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 1.95 (0.50 to 9.67) | too few |
| `ABSTRACT_ADVERB` | 429 | 0.47 (0.40 to 0.54) | 0.47 (0.38 to 0.57) | 567 | 0.86 (0.75 to 0.97) | 0.84 (0.72 to 0.95) | 1.84 (1.50 to 2.25) | rose |
| `GAPPED_ANTITHESIS` | 15 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 18 | 0.03 (0.01 to 0.04) | 0.04 (0.02 to 0.06) | 1.67 (0.76 to 3.50) | flat |
| `BORROWED_RIGOUR` | 147 | 0.16 (0.12 to 0.20) | 0.20 (0.14 to 0.26) | 169 | 0.26 (0.21 to 0.31) | 0.25 (0.19 to 0.30) | 1.60 (1.16 to 2.18) | rose |
| `CONSULTANT_REGISTER` | 594 | 0.65 (0.52 to 0.78) | 0.59 (0.49 to 0.71) | 646 | 0.98 (0.83 to 1.14) | 0.98 (0.82 to 1.15) | 1.52 (1.19 to 1.96) | rose |
| `CORRECTIVE_CONTRAST` | 262 | 0.29 (0.23 to 0.34) | 0.23 (0.19 to 0.28) | 266 | 0.40 (0.32 to 0.50) | 0.43 (0.33 to 0.54) | 1.41 (1.06 to 1.91) | rose |
| `TRICOLON` | 2792 | 3.04 (2.84 to 3.27) | 3.05 (2.83 to 3.27) | 2831 | 4.30 (3.94 to 4.67) | 4.51 (4.13 to 4.88) | 1.41 (1.27 to 1.57) | rose |
| `DISGUISE_METAPHOR` | 17 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 17 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.05) | 1.39 (0.60 to 3.44) | flat |
| `LLM_DICTION` | 1254 | 1.37 (1.17 to 1.57) | 1.37 (1.15 to 1.62) | 1165 | 1.77 (1.49 to 2.08) | 1.77 (1.53 to 1.99) | 1.29 (1.03 to 1.63) | rose |
| `ALTERNATIVE_FRAMING` | 950 | 1.04 (0.94 to 1.14) | 1.06 (0.94 to 1.18) | 798 | 1.21 (1.09 to 1.34) | 1.19 (1.06 to 1.34) | 1.17 (1.02 to 1.34) | rose |
| `VAGUE_QUANTIFIER` | 126 | 0.14 (0.11 to 0.17) | 0.15 (0.11 to 0.20) | 99 | 0.15 (0.11 to 0.20) | 0.14 (0.10 to 0.18) | 1.10 (0.74 to 1.56) | flat |
| `EMPHATIC_REFLEXIVE` | 106 | 0.12 (0.08 to 0.15) | 0.11 (0.07 to 0.14) | 77 | 0.12 (0.09 to 0.15) | 0.11 (0.08 to 0.14) | 1.01 (0.70 to 1.51) | flat |
| `CLOSER` | 56 | 0.06 (0.04 to 0.09) | 0.06 (0.04 to 0.09) | 37 | 0.06 (0.03 to 0.08) | 0.06 (0.03 to 0.08) | 0.92 (0.51 to 1.57) | flat |
| `FRAME_MARKER` | 79 | 0.09 (0.06 to 0.11) | 0.08 (0.06 to 0.11) | 38 | 0.06 (0.04 to 0.08) | 0.07 (0.04 to 0.09) | 0.67 (0.40 to 1.08) | flat |
| `EMPTY_FRAME` | 104 | 0.11 (0.08 to 0.15) | 0.12 (0.08 to 0.15) | 46 | 0.07 (0.05 to 0.10) | 0.07 (0.05 to 0.10) | 0.62 (0.39 to 0.96) | fell |
| `HEDGE_STACK` | 22 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 4 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.25 (0.05 to 0.73) | fell |
| `HOUSE_STYLE` | 2 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 165 | 0.18 (0.09 to 0.30) | 0.22 (0.12 to 0.34) | 625 | 0.95 (0.67 to 1.29) | 0.89 (0.67 to 1.15) | 5.28 (2.87 to 10.98) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 18 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 64 | 0.10 (0.06 to 0.14) | 0.12 (0.06 to 0.18) | 4.96 (2.37 to 11.53) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 1035 | 1.13 (0.98 to 1.29) | 1.10 (0.95 to 1.26) | 3012 | 4.57 (4.16 to 4.99) | 4.69 (4.26 to 5.11) | 4.06 (3.46 to 4.74) | rose |
| `HOLLOW_BOOSTER / -` | 51 | 0.06 (0.04 to 0.07) | 0.06 (0.04 to 0.09) | 121 | 0.18 (0.14 to 0.22) | 0.19 (0.14 to 0.24) | 3.31 (2.25 to 4.93) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 270 | 0.29 (0.25 to 0.34) | 0.27 (0.23 to 0.32) | 486 | 0.74 (0.63 to 0.85) | 0.72 (0.61 to 0.83) | 2.51 (2.01 to 3.14) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 10 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 15 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 2.09 (0.88 to 5.30) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 429 | 0.47 (0.40 to 0.54) | 0.47 (0.38 to 0.57) | 567 | 0.86 (0.75 to 0.97) | 0.84 (0.72 to 0.95) | 1.84 (1.50 to 2.25) | rose |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 15 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 18 | 0.03 (0.01 to 0.04) | 0.04 (0.02 to 0.06) | 1.67 (0.76 to 3.50) | flat |
| `BORROWED_RIGOUR / -` | 147 | 0.16 (0.12 to 0.20) | 0.20 (0.14 to 0.26) | 169 | 0.26 (0.21 to 0.31) | 0.25 (0.19 to 0.30) | 1.60 (1.16 to 2.18) | rose |
| `CONSULTANT_REGISTER / -` | 594 | 0.65 (0.52 to 0.78) | 0.59 (0.49 to 0.71) | 646 | 0.98 (0.83 to 1.14) | 0.98 (0.82 to 1.15) | 1.52 (1.19 to 1.96) | rose |
| `TRICOLON / tricolon` | 2792 | 3.04 (2.84 to 3.27) | 3.05 (2.83 to 3.27) | 2830 | 4.30 (3.94 to 4.67) | 4.51 (4.13 to 4.88) | 1.41 (1.27 to 1.57) | rose |
| `DISGUISE_METAPHOR / disguise_metaphor` | 17 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 17 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.05) | 1.39 (0.60 to 3.44) | flat |
| `LLM_DICTION / -` | 1254 | 1.37 (1.17 to 1.57) | 1.37 (1.15 to 1.62) | 1165 | 1.77 (1.49 to 2.08) | 1.77 (1.53 to 1.99) | 1.29 (1.03 to 1.63) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 187 | 0.20 (0.17 to 0.24) | 0.17 (0.13 to 0.20) | 167 | 0.25 (0.21 to 0.31) | 0.26 (0.21 to 0.33) | 1.24 (0.95 to 1.63) | flat |
| `VAGUE_QUANTIFIER / -` | 126 | 0.14 (0.11 to 0.17) | 0.15 (0.11 to 0.20) | 99 | 0.15 (0.11 to 0.20) | 0.14 (0.10 to 0.18) | 1.10 (0.74 to 1.56) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 106 | 0.12 (0.08 to 0.15) | 0.11 (0.07 to 0.14) | 77 | 0.12 (0.09 to 0.15) | 0.11 (0.08 to 0.14) | 1.01 (0.70 to 1.51) | flat |
| `CLOSER / -` | 56 | 0.06 (0.04 to 0.09) | 0.06 (0.04 to 0.09) | 37 | 0.06 (0.03 to 0.08) | 0.06 (0.03 to 0.08) | 0.92 (0.51 to 1.57) | flat |
| `FRAME_MARKER / -` | 79 | 0.09 (0.06 to 0.11) | 0.08 (0.06 to 0.11) | 38 | 0.06 (0.04 to 0.08) | 0.07 (0.04 to 0.09) | 0.67 (0.40 to 1.08) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 680 | 0.74 (0.65 to 0.84) | 0.79 (0.68 to 0.90) | 312 | 0.47 (0.40 to 0.55) | 0.48 (0.40 to 0.55) | 0.64 (0.53 to 0.78) | fell |
| `EMPTY_FRAME / -` | 104 | 0.11 (0.08 to 0.15) | 0.12 (0.08 to 0.15) | 46 | 0.07 (0.05 to 0.10) | 0.07 (0.05 to 0.10) | 0.62 (0.39 to 0.96) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 47 | 0.05 (0.03 to 0.08) | 0.04 (0.02 to 0.05) | 20 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.04) | 0.59 (0.27 to 1.27) | flat |
| `HEDGE_STACK / -` | 22 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 4 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.25 (0.05 to 0.73) | fell |

### related

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 38 | 0.23 (0.06 to 0.45) | 0.20 (0.07 to 0.38) | 109 | 1.04 (0.73 to 1.40) | 1.08 (0.74 to 1.46) | 4.56 (2.12 to 16.10) | rose |
| `PARTICIPIAL_TAIL` | 205 | 1.23 (1.00 to 1.46) | 1.14 (0.90 to 1.42) | 526 | 5.02 (4.43 to 5.63) | 5.27 (4.61 to 5.97) | 4.08 (3.29 to 5.11) | rose |
| `HOLLOW_BOOSTER` | 8 | 0.05 (0.01 to 0.09) | 0.04 (0.01 to 0.07) | 18 | 0.17 (0.10 to 0.25) | 0.16 (0.08 to 0.25) | 3.57 (1.49 to 13.60) | rose |
| `NEG_ESCALATION` | 2 | 0.01 (0.00 to 0.03) | 0.00 (0.00 to 0.01) | 4 | 0.04 (0.01 to 0.08) | 0.06 (0.00 to 0.13) | 3.18 (0.51 to inf) | too few |
| `FRAME_MARKER` | 3 | 0.02 (0.00 to 0.04) | 0.01 (0.00 to 0.02) | 5 | 0.05 (0.01 to 0.10) | 0.08 (0.01 to 0.20) | 2.65 (0.52 to inf) | too few |
| `EMPHATIC_REFLEXIVE` | 21 | 0.13 (0.07 to 0.19) | 0.16 (0.06 to 0.29) | 24 | 0.23 (0.12 to 0.35) | 0.23 (0.10 to 0.40) | 1.82 (0.88 to 3.89) | flat |
| `ALTERNATIVE_FRAMING` | 112 | 0.67 (0.56 to 0.80) | 0.67 (0.51 to 0.85) | 122 | 1.16 (0.94 to 1.38) | 1.32 (0.95 to 1.79) | 1.73 (1.33 to 2.24) | rose |
| `VAGUE_QUANTIFIER` | 48 | 0.29 (0.21 to 0.37) | 0.40 (0.23 to 0.61) | 51 | 0.49 (0.36 to 0.62) | 0.45 (0.30 to 0.63) | 1.69 (1.11 to 2.58) | rose |
| `DISGUISE_METAPHOR` | 2 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.02) | 2 | 0.02 (0.00 to 0.05) | 0.02 (0.00 to 0.04) | 1.59 (0.00 to inf) | too few |
| `LLM_DICTION` | 265 | 1.59 (1.30 to 1.90) | 1.79 (1.46 to 2.13) | 264 | 2.52 (2.07 to 2.98) | 2.33 (1.90 to 2.76) | 1.58 (1.21 to 2.06) | rose |
| `TRICOLON` | 589 | 3.54 (3.05 to 4.06) | 4.11 (3.49 to 4.80) | 579 | 5.52 (4.86 to 6.27) | 5.78 (5.07 to 6.54) | 1.56 (1.28 to 1.90) | rose |
| `ABSTRACT_ADVERB` | 124 | 0.74 (0.57 to 0.96) | 0.65 (0.49 to 0.84) | 99 | 0.94 (0.75 to 1.14) | 1.03 (0.77 to 1.31) | 1.27 (0.90 to 1.77) | flat |
| `CLOSER` | 9 | 0.05 (0.02 to 0.09) | 0.05 (0.02 to 0.09) | 7 | 0.07 (0.01 to 0.14) | 0.04 (0.01 to 0.08) | 1.24 (0.22 to 3.94) | too few |
| `CONSULTANT_REGISTER` | 228 | 1.37 (1.12 to 1.64) | 1.55 (1.25 to 1.86) | 176 | 1.68 (1.39 to 1.99) | 1.74 (1.39 to 2.11) | 1.23 (0.95 to 1.59) | flat |
| `CORRECTIVE_CONTRAST` | 70 | 0.42 (0.32 to 0.52) | 0.38 (0.26 to 0.50) | 49 | 0.47 (0.33 to 0.63) | 0.54 (0.36 to 0.77) | 1.11 (0.75 to 1.68) | flat |
| `GAPPED_ANTITHESIS` | 3 | 0.02 (0.00 to 0.04) | 0.02 (0.00 to 0.05) | 2 | 0.02 (0.00 to 0.05) | 0.02 (0.00 to 0.06) | 1.06 (0.00 to inf) | too few |
| `BORROWED_RIGOUR` | 87 | 0.52 (0.33 to 0.74) | 0.38 (0.24 to 0.54) | 46 | 0.44 (0.31 to 0.58) | 0.48 (0.32 to 0.66) | 0.84 (0.52 to 1.44) | flat |
| `EMPTY_FRAME` | 10 | 0.06 (0.02 to 0.10) | 0.06 (0.02 to 0.11) | 5 | 0.05 (0.01 to 0.09) | 0.02 (0.00 to 0.04) | 0.79 (0.17 to 2.28) | too few |
| `HEDGE_STACK` | 2 | 0.01 (0.00 to 0.03) | 0.04 (0.00 to 0.13) | 1 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.03) | 0.79 (0.00 to inf) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 38 | 0.23 (0.06 to 0.45) | 0.20 (0.07 to 0.38) | 109 | 1.04 (0.73 to 1.40) | 1.08 (0.74 to 1.46) | 4.56 (2.12 to 16.10) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 205 | 1.23 (1.00 to 1.46) | 1.14 (0.90 to 1.42) | 526 | 5.02 (4.43 to 5.63) | 5.27 (4.61 to 5.97) | 4.08 (3.29 to 5.11) | rose |
| `HOLLOW_BOOSTER / -` | 8 | 0.05 (0.01 to 0.09) | 0.04 (0.01 to 0.07) | 18 | 0.17 (0.10 to 0.25) | 0.16 (0.08 to 0.25) | 3.57 (1.49 to 13.60) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 48 | 0.29 (0.19 to 0.38) | 0.37 (0.23 to 0.53) | 91 | 0.87 (0.67 to 1.06) | 0.85 (0.64 to 1.09) | 3.01 (2.05 to 4.73) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 21 | 0.13 (0.07 to 0.19) | 0.16 (0.06 to 0.29) | 24 | 0.23 (0.12 to 0.35) | 0.23 (0.10 to 0.40) | 1.82 (0.88 to 3.89) | flat |
| `VAGUE_QUANTIFIER / -` | 48 | 0.29 (0.21 to 0.37) | 0.40 (0.23 to 0.61) | 51 | 0.49 (0.36 to 0.62) | 0.45 (0.30 to 0.63) | 1.69 (1.11 to 2.58) | rose |
| `LLM_DICTION / -` | 265 | 1.59 (1.30 to 1.90) | 1.79 (1.46 to 2.13) | 264 | 2.52 (2.07 to 2.98) | 2.33 (1.90 to 2.76) | 1.58 (1.21 to 2.06) | rose |
| `TRICOLON / tricolon` | 589 | 3.54 (3.05 to 4.06) | 4.11 (3.49 to 4.80) | 579 | 5.52 (4.86 to 6.27) | 5.78 (5.07 to 6.54) | 1.56 (1.28 to 1.90) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 124 | 0.74 (0.57 to 0.96) | 0.65 (0.49 to 0.84) | 99 | 0.94 (0.75 to 1.14) | 1.03 (0.77 to 1.31) | 1.27 (0.90 to 1.77) | flat |
| `CONSULTANT_REGISTER / -` | 228 | 1.37 (1.12 to 1.64) | 1.55 (1.25 to 1.86) | 176 | 1.68 (1.39 to 1.99) | 1.74 (1.39 to 2.11) | 1.23 (0.95 to 1.59) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 63 | 0.38 (0.27 to 0.49) | 0.35 (0.24 to 0.48) | 42 | 0.40 (0.28 to 0.55) | 0.48 (0.31 to 0.68) | 1.06 (0.68 to 1.67) | flat |
| `BORROWED_RIGOUR / -` | 87 | 0.52 (0.33 to 0.74) | 0.38 (0.24 to 0.54) | 46 | 0.44 (0.31 to 0.58) | 0.48 (0.32 to 0.66) | 0.84 (0.52 to 1.44) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 64 | 0.38 (0.29 to 0.48) | 0.31 (0.22 to 0.40) | 31 | 0.30 (0.20 to 0.40) | 0.47 (0.19 to 0.91) | 0.77 (0.49 to 1.18) | flat |

### conclusion

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `HEDGE_STACK` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 1 | 0.03 (0.00 to 0.10) | 0.01 (0.00 to 0.02) | inf (inf to inf) | too few |
| `EM_DASH` | 9 | 0.19 (0.04 to 0.42) | 0.24 (0.05 to 0.49) | 55 | 1.71 (0.94 to 2.69) | 1.41 (0.85 to 2.05) | 8.76 (3.22 to 42.35) | rose |
| `HOLLOW_BOOSTER` | 1 | 0.02 (0.00 to 0.05) | 0.00 (0.00 to 0.00) | 4 | 0.12 (0.03 to 0.24) | 0.08 (0.00 to 0.16) | 5.74 (0.83 to inf) | too few |
| `PARTICIPIAL_TAIL` | 49 | 1.06 (0.76 to 1.42) | 1.33 (0.89 to 1.82) | 181 | 5.62 (4.77 to 6.55) | 5.79 (4.78 to 6.81) | 5.30 (3.78 to 7.55) | rose |
| `CLOSER` | 3 | 0.06 (0.00 to 0.15) | 0.06 (0.00 to 0.14) | 8 | 0.25 (0.09 to 0.43) | 0.28 (0.09 to 0.51) | 3.82 (1.12 to inf) | too few |
| `TRICOLON` | 147 | 3.18 (2.61 to 3.89) | 3.76 (2.88 to 4.69) | 197 | 6.11 (5.13 to 7.06) | 6.40 (5.37 to 7.37) | 1.92 (1.48 to 2.46) | rose |
| `CONSULTANT_REGISTER` | 64 | 1.39 (0.94 to 1.96) | 1.76 (1.25 to 2.39) | 75 | 2.33 (1.77 to 2.93) | 2.94 (2.17 to 3.79) | 1.68 (1.09 to 2.64) | rose |
| `GAPPED_ANTITHESIS` | 1 | 0.02 (0.00 to 0.08) | 0.01 (0.00 to 0.03) | 1 | 0.03 (0.00 to 0.09) | 0.01 (0.00 to 0.02) | 1.43 (0.00 to inf) | too few |
| `ALTERNATIVE_FRAMING` | 36 | 0.78 (0.50 to 1.13) | 0.76 (0.44 to 1.17) | 34 | 1.06 (0.76 to 1.38) | 0.79 (0.53 to 1.12) | 1.35 (0.84 to 2.26) | flat |
| `LLM_DICTION` | 133 | 2.88 (2.32 to 3.54) | 3.37 (2.68 to 4.12) | 122 | 3.79 (3.00 to 4.58) | 3.75 (2.96 to 4.58) | 1.32 (0.96 to 1.74) | flat |
| `CORRECTIVE_CONTRAST` | 22 | 0.48 (0.26 to 0.71) | 0.41 (0.17 to 0.70) | 17 | 0.53 (0.27 to 0.81) | 0.47 (0.21 to 0.77) | 1.11 (0.50 to 2.40) | flat |
| `ABSTRACT_ADVERB` | 39 | 0.84 (0.55 to 1.15) | 0.71 (0.40 to 1.09) | 26 | 0.81 (0.50 to 1.15) | 0.85 (0.51 to 1.27) | 0.96 (0.55 to 1.63) | flat |
| `VAGUE_QUANTIFIER` | 29 | 0.63 (0.41 to 0.90) | 0.78 (0.46 to 1.16) | 13 | 0.40 (0.19 to 0.66) | 0.45 (0.19 to 0.74) | 0.64 (0.28 to 1.21) | flat |
| `BORROWED_RIGOUR` | 19 | 0.41 (0.22 to 0.69) | 0.50 (0.25 to 0.82) | 8 | 0.25 (0.06 to 0.47) | 0.23 (0.03 to 0.50) | 0.60 (0.15 to 1.48) | flat |
| `EMPHATIC_REFLEXIVE` | 11 | 0.24 (0.02 to 0.56) | 0.07 (0.01 to 0.15) | 4 | 0.12 (0.03 to 0.25) | 0.07 (0.00 to 0.15) | 0.52 (0.08 to 10.70) | too few |
| `FRAME_MARKER` | 5 | 0.11 (0.02 to 0.20) | 0.07 (0.00 to 0.17) | 1 | 0.03 (0.00 to 0.10) | 0.01 (0.00 to 0.04) | 0.29 (0.00 to 1.95) | too few |
| `EMPTY_FRAME` | 2 | 0.04 (0.00 to 0.12) | 0.03 (0.00 to 0.08) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 9 | 0.19 (0.04 to 0.42) | 0.24 (0.05 to 0.49) | 55 | 1.71 (0.94 to 2.69) | 1.41 (0.85 to 2.05) | 8.76 (3.22 to 42.35) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 49 | 1.06 (0.76 to 1.42) | 1.33 (0.89 to 1.82) | 181 | 5.62 (4.77 to 6.55) | 5.79 (4.78 to 6.81) | 5.30 (3.78 to 7.55) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 15 | 0.32 (0.13 to 0.60) | 0.27 (0.10 to 0.51) | 22 | 0.68 (0.44 to 0.94) | 0.47 (0.28 to 0.71) | 2.10 (1.00 to 5.24) | flat |
| `TRICOLON / tricolon` | 147 | 3.18 (2.61 to 3.89) | 3.76 (2.88 to 4.69) | 197 | 6.11 (5.13 to 7.06) | 6.40 (5.37 to 7.37) | 1.92 (1.48 to 2.46) | rose |
| `CONSULTANT_REGISTER / -` | 64 | 1.39 (0.94 to 1.96) | 1.76 (1.25 to 2.39) | 75 | 2.33 (1.77 to 2.93) | 2.94 (2.17 to 3.79) | 1.68 (1.09 to 2.64) | rose |
| `LLM_DICTION / -` | 133 | 2.88 (2.32 to 3.54) | 3.37 (2.68 to 4.12) | 122 | 3.79 (3.00 to 4.58) | 3.75 (2.96 to 4.58) | 1.32 (0.96 to 1.74) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 39 | 0.84 (0.55 to 1.15) | 0.71 (0.40 to 1.09) | 26 | 0.81 (0.50 to 1.15) | 0.85 (0.51 to 1.27) | 0.96 (0.55 to 1.63) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 20 | 0.43 (0.21 to 0.65) | 0.33 (0.11 to 0.61) | 12 | 0.37 (0.16 to 0.62) | 0.36 (0.14 to 0.61) | 0.86 (0.34 to 2.12) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 21 | 0.45 (0.25 to 0.68) | 0.49 (0.21 to 0.83) | 12 | 0.37 (0.18 to 0.60) | 0.32 (0.14 to 0.55) | 0.82 (0.36 to 1.74) | flat |
| `VAGUE_QUANTIFIER / -` | 29 | 0.63 (0.41 to 0.90) | 0.78 (0.46 to 1.16) | 13 | 0.40 (0.19 to 0.66) | 0.45 (0.19 to 0.74) | 0.64 (0.28 to 1.21) | flat |
| `BORROWED_RIGOUR / -` | 19 | 0.41 (0.22 to 0.69) | 0.50 (0.25 to 0.82) | 8 | 0.25 (0.06 to 0.47) | 0.23 (0.03 to 0.50) | 0.60 (0.15 to 1.48) | flat |

### all

| construction | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH` | 267 | 0.21 (0.11 to 0.34) | 0.24 (0.13 to 0.36) | 947 | 1.02 (0.75 to 1.33) | 0.97 (0.75 to 1.23) | 4.94 (2.77 to 9.81) | rose |
| `PARTICIPIAL_TAIL` | 1559 | 1.20 (1.06 to 1.35) | 1.19 (1.04 to 1.33) | 4505 | 4.84 (4.44 to 5.23) | 4.90 (4.50 to 5.28) | 4.03 (3.49 to 4.62) | rose |
| `HOLLOW_BOOSTER` | 74 | 0.06 (0.04 to 0.07) | 0.06 (0.04 to 0.09) | 158 | 0.17 (0.14 to 0.20) | 0.17 (0.13 to 0.20) | 2.98 (2.12 to 4.25) | rose |
| `NEG_ESCALATION` | 8 | 0.01 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 11 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 1.92 (0.74 to 6.58) | too few |
| `DISGUISE_METAPHOR` | 20 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 24 | 0.03 (0.01 to 0.04) | 0.03 (0.02 to 0.04) | 1.67 (0.83 to 3.84) | flat |
| `ABSTRACT_ADVERB` | 737 | 0.57 (0.49 to 0.65) | 0.57 (0.49 to 0.66) | 832 | 0.89 (0.79 to 0.99) | 0.88 (0.78 to 0.98) | 1.57 (1.31 to 1.89) | rose |
| `GAPPED_ANTITHESIS` | 21 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 23 | 0.02 (0.01 to 0.04) | 0.03 (0.02 to 0.05) | 1.53 (0.79 to 2.93) | flat |
| `TRICOLON` | 4148 | 3.20 (2.97 to 3.43) | 3.30 (3.08 to 3.51) | 4386 | 4.71 (4.33 to 5.09) | 4.93 (4.53 to 5.34) | 1.47 (1.32 to 1.63) | rose |
| `CONSULTANT_REGISTER` | 1113 | 0.86 (0.74 to 0.98) | 0.80 (0.69 to 0.93) | 1161 | 1.25 (1.09 to 1.41) | 1.27 (1.09 to 1.45) | 1.45 (1.20 to 1.76) | rose |
| `LLM_DICTION` | 2047 | 1.58 (1.38 to 1.78) | 1.64 (1.44 to 1.87) | 2044 | 2.19 (1.92 to 2.47) | 2.22 (1.97 to 2.47) | 1.39 (1.17 to 1.67) | rose |
| `CORRECTIVE_CONTRAST` | 408 | 0.31 (0.26 to 0.37) | 0.26 (0.22 to 0.31) | 395 | 0.42 (0.35 to 0.51) | 0.46 (0.37 to 0.57) | 1.35 (1.05 to 1.74) | rose |
| `VAGUE_QUANTIFIER` | 302 | 0.23 (0.20 to 0.27) | 0.26 (0.21 to 0.30) | 268 | 0.29 (0.24 to 0.34) | 0.31 (0.26 to 0.37) | 1.24 (0.98 to 1.54) | flat |
| `ALTERNATIVE_FRAMING` | 1224 | 0.94 (0.86 to 1.02) | 1.00 (0.89 to 1.12) | 1082 | 1.16 (1.05 to 1.28) | 1.13 (1.02 to 1.26) | 1.23 (1.08 to 1.40) | rose |
| `BORROWED_RIGOUR` | 320 | 0.25 (0.20 to 0.29) | 0.27 (0.21 to 0.34) | 260 | 0.28 (0.23 to 0.33) | 0.27 (0.22 to 0.32) | 1.13 (0.86 to 1.47) | flat |
| `EMPHATIC_REFLEXIVE` | 160 | 0.12 (0.09 to 0.16) | 0.12 (0.09 to 0.15) | 123 | 0.13 (0.10 to 0.16) | 0.12 (0.09 to 0.15) | 1.07 (0.75 to 1.58) | flat |
| `CLOSER` | 92 | 0.07 (0.05 to 0.09) | 0.07 (0.05 to 0.10) | 70 | 0.08 (0.06 to 0.10) | 0.08 (0.05 to 0.10) | 1.06 (0.70 to 1.60) | flat |
| `FRAME_MARKER` | 95 | 0.07 (0.05 to 0.10) | 0.07 (0.05 to 0.09) | 50 | 0.05 (0.04 to 0.07) | 0.06 (0.04 to 0.08) | 0.73 (0.46 to 1.15) | flat |
| `EMPTY_FRAME` | 127 | 0.10 (0.07 to 0.13) | 0.10 (0.07 to 0.13) | 59 | 0.06 (0.04 to 0.09) | 0.06 (0.04 to 0.08) | 0.65 (0.42 to 0.99) | fell |
| `HEDGE_STACK` | 25 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 0.50 (0.17 to 1.26) | flat |
| `HOUSE_STYLE` | 2 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.01) | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | too few |

| pattern | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `EM_DASH / -` | 267 | 0.21 (0.11 to 0.34) | 0.24 (0.13 to 0.36) | 947 | 1.02 (0.75 to 1.33) | 0.97 (0.75 to 1.23) | 4.94 (2.77 to 9.81) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 22 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 78 | 0.08 (0.05 to 0.12) | 0.10 (0.06 to 0.16) | 4.94 (2.53 to 10.76) | rose |
| `PARTICIPIAL_TAIL / participial_tail` | 1559 | 1.20 (1.06 to 1.35) | 1.19 (1.04 to 1.33) | 4505 | 4.84 (4.44 to 5.23) | 4.90 (4.50 to 5.28) | 4.03 (3.49 to 4.62) | rose |
| `HOLLOW_BOOSTER / -` | 74 | 0.06 (0.04 to 0.07) | 0.06 (0.04 to 0.09) | 158 | 0.17 (0.14 to 0.20) | 0.17 (0.13 to 0.20) | 2.98 (2.12 to 4.25) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 380 | 0.29 (0.25 to 0.33) | 0.28 (0.24 to 0.33) | 684 | 0.73 (0.63 to 0.84) | 0.70 (0.60 to 0.80) | 2.51 (2.08 to 3.04) | rose |
| `DISGUISE_METAPHOR / disguise_metaphor` | 20 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 24 | 0.03 (0.01 to 0.04) | 0.03 (0.02 to 0.04) | 1.67 (0.83 to 3.84) | flat |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 15 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 17 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 1.58 (0.73 to 3.30) | flat |
| `ABSTRACT_ADVERB / abstract_adverb` | 737 | 0.57 (0.49 to 0.65) | 0.57 (0.49 to 0.66) | 832 | 0.89 (0.79 to 0.99) | 0.88 (0.78 to 0.98) | 1.57 (1.31 to 1.89) | rose |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 21 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 23 | 0.02 (0.01 to 0.04) | 0.03 (0.02 to 0.05) | 1.53 (0.79 to 2.93) | flat |
| `TRICOLON / tricolon` | 4148 | 3.20 (2.97 to 3.43) | 3.30 (3.08 to 3.51) | 4385 | 4.71 (4.33 to 5.09) | 4.93 (4.53 to 5.34) | 1.47 (1.32 to 1.63) | rose |
| `CONSULTANT_REGISTER / -` | 1113 | 0.86 (0.74 to 0.98) | 0.80 (0.69 to 0.93) | 1161 | 1.25 (1.09 to 1.41) | 1.27 (1.09 to 1.45) | 1.45 (1.20 to 1.76) | rose |
| `LLM_DICTION / -` | 2047 | 1.58 (1.38 to 1.78) | 1.64 (1.44 to 1.87) | 2044 | 2.19 (1.92 to 2.47) | 2.22 (1.97 to 2.47) | 1.39 (1.17 to 1.67) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 309 | 0.24 (0.20 to 0.27) | 0.20 (0.16 to 0.23) | 277 | 0.30 (0.25 to 0.35) | 0.32 (0.26 to 0.38) | 1.25 (0.99 to 1.59) | flat |
| `VAGUE_QUANTIFIER / -` | 302 | 0.23 (0.20 to 0.27) | 0.26 (0.21 to 0.30) | 268 | 0.29 (0.24 to 0.34) | 0.31 (0.26 to 0.37) | 1.24 (0.98 to 1.54) | flat |
| `BORROWED_RIGOUR / -` | 320 | 0.25 (0.20 to 0.29) | 0.27 (0.21 to 0.34) | 260 | 0.28 (0.23 to 0.33) | 0.27 (0.22 to 0.32) | 1.13 (0.86 to 1.47) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 160 | 0.12 (0.09 to 0.16) | 0.12 (0.09 to 0.15) | 123 | 0.13 (0.10 to 0.16) | 0.12 (0.09 to 0.15) | 1.07 (0.75 to 1.58) | flat |
| `CLOSER / -` | 92 | 0.07 (0.05 to 0.09) | 0.07 (0.05 to 0.10) | 70 | 0.08 (0.06 to 0.10) | 0.08 (0.05 to 0.10) | 1.06 (0.70 to 1.60) | flat |
| `FRAME_MARKER / -` | 95 | 0.07 (0.05 to 0.10) | 0.07 (0.05 to 0.09) | 50 | 0.05 (0.04 to 0.07) | 0.06 (0.04 to 0.08) | 0.73 (0.46 to 1.15) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 844 | 0.65 (0.58 to 0.72) | 0.72 (0.61 to 0.83) | 398 | 0.43 (0.37 to 0.49) | 0.43 (0.37 to 0.50) | 0.66 (0.55 to 0.79) | fell |
| `EMPTY_FRAME / -` | 127 | 0.10 (0.07 to 0.13) | 0.10 (0.07 to 0.13) | 59 | 0.06 (0.04 to 0.09) | 0.06 (0.04 to 0.08) | 0.65 (0.42 to 0.99) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 62 | 0.05 (0.03 to 0.07) | 0.04 (0.03 to 0.05) | 23 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 0.52 (0.27 to 0.93) | fell |
| `HEDGE_STACK / -` | 25 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 0.50 (0.17 to 1.26) | flat |

### body, subtypes with at least 20 findings

| subtype | pre n | pre pooled (95% CI) | pre mean per paper (95% CI) | post n | post pooled (95% CI) | post mean per paper (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `PARTICIPIAL_TAIL / participial_tail / confirm` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 36 | 0.05 (0.03 to 0.08) | 0.07 (0.03 to 0.13) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / highlight` | 0 | 0.00 (0.00 to 0.00) | 0.00 (0.00 to 0.00) | 28 | 0.04 (0.03 to 0.06) | 0.05 (0.03 to 0.07) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reflect` | 2 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 47 | 0.07 (0.05 to 0.10) | 0.07 (0.04 to 0.09) | 32.75 (11.64 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / ensure` | 7 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 118 | 0.18 (0.13 to 0.23) | 0.19 (0.13 to 0.26) | 23.49 (11.41 to 86.21) | rose |
| `PARTICIPIAL_TAIL / participial_tail / demonstrate` | 4 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 53 | 0.08 (0.06 to 0.11) | 0.08 (0.06 to 0.12) | 18.47 (7.80 to 90.84) | rose |
| `PARTICIPIAL_TAIL / participial_tail / create` | 2 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.00) | 21 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.04) | 14.63 (4.70 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / produce` | 3 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 31 | 0.05 (0.03 to 0.07) | 0.04 (0.02 to 0.07) | 14.40 (5.43 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / suggest` | 3 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 29 | 0.04 (0.03 to 0.06) | 0.06 (0.03 to 0.09) | 13.47 (4.53 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / achieve` | 7 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 65 | 0.10 (0.07 to 0.13) | 0.11 (0.07 to 0.15) | 12.94 (6.39 to 37.11) | rose |
| `PARTICIPIAL_TAIL / participial_tail / match` | 2 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 18 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 12.54 (3.84 to inf) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / structurally` | 3 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 23 | 0.03 (0.01 to 0.06) | 0.04 (0.02 to 0.07) | 10.68 (2.90 to inf) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / semantically` | 3 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 20 | 0.03 (0.01 to 0.05) | 0.03 (0.01 to 0.05) | 9.29 (2.96 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / offer` | 4 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 23 | 0.03 (0.02 to 0.05) | 0.03 (0.02 to 0.05) | 8.01 (2.51 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / support` | 3 | 0.00 (0.00 to 0.01) | 0.00 (0.00 to 0.01) | 17 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.04) | 7.90 (2.50 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / yield` | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 51 | 0.08 (0.06 to 0.10) | 0.09 (0.06 to 0.12) | 7.90 (3.87 to 22.84) | rose |
| `PARTICIPIAL_TAIL / participial_tail / allow` | 26 | 0.03 (0.02 to 0.04) | 0.03 (0.01 to 0.04) | 145 | 0.22 (0.18 to 0.27) | 0.24 (0.19 to 0.30) | 7.77 (5.02 to 13.98) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enable` | 34 | 0.04 (0.02 to 0.05) | 0.03 (0.02 to 0.04) | 168 | 0.26 (0.20 to 0.32) | 0.27 (0.20 to 0.34) | 6.89 (4.48 to 11.82) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reach` | 4 | 0.00 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 19 | 0.03 (0.02 to 0.04) | 0.03 (0.01 to 0.04) | 6.62 (2.16 to inf) | rose |
| `EM_DASH / - / paired aside` | 78 | 0.08 (0.03 to 0.17) | 0.10 (0.04 to 0.18) | 357 | 0.54 (0.35 to 0.79) | 0.44 (0.31 to 0.60) | 6.38 (2.85 to 19.93) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / fundamentally` | 6 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 27 | 0.04 (0.02 to 0.06) | 0.03 (0.02 to 0.05) | 6.27 (2.66 to 21.41) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / substantially` | 11 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 49 | 0.07 (0.05 to 0.10) | 0.06 (0.04 to 0.08) | 6.21 (3.25 to 14.38) | rose |
| `PARTICIPIAL_TAIL / participial_tail / make` | 34 | 0.04 (0.03 to 0.05) | 0.03 (0.02 to 0.05) | 142 | 0.22 (0.18 to 0.25) | 0.21 (0.17 to 0.25) | 5.82 (4.04 to 8.73) | rose |
| `PARTICIPIAL_TAIL / participial_tail / indicate` | 22 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 79 | 0.12 (0.09 to 0.16) | 0.13 (0.09 to 0.18) | 5.00 (3.10 to 9.93) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition / X, not Y` | 18 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 64 | 0.10 (0.06 to 0.14) | 0.12 (0.06 to 0.18) | 4.96 (2.37 to 11.53) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead / rather than` | 114 | 0.12 (0.09 to 0.16) | 0.11 (0.08 to 0.14) | 376 | 0.57 (0.46 to 0.68) | 0.57 (0.46 to 0.68) | 4.60 (3.22 to 6.70) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leave` | 11 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 36 | 0.05 (0.03 to 0.08) | 0.05 (0.03 to 0.07) | 4.56 (2.26 to 11.38) | rose |
| `EM_DASH / - / single break` | 80 | 0.09 (0.05 to 0.14) | 0.11 (0.06 to 0.16) | 256 | 0.39 (0.29 to 0.51) | 0.43 (0.32 to 0.57) | 4.46 (2.57 to 8.53) | rose |
| `PARTICIPIAL_TAIL / participial_tail / eliminate` | 8 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.01) | 25 | 0.04 (0.02 to 0.05) | 0.04 (0.02 to 0.06) | 4.36 (1.98 to 12.97) | rose |
| `PARTICIPIAL_TAIL / participial_tail / correspond` | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.01) | 27 | 0.04 (0.02 to 0.06) | 0.04 (0.02 to 0.06) | 4.18 (2.02 to 14.43) | rose |
| `PARTICIPIAL_TAIL / participial_tail / limit` | 5 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 15 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 4.18 (1.34 to 30.30) | rose |
| `PARTICIPIAL_TAIL / participial_tail / result` | 40 | 0.04 (0.03 to 0.06) | 0.03 (0.02 to 0.05) | 101 | 0.15 (0.12 to 0.19) | 0.16 (0.12 to 0.20) | 3.52 (2.25 to 5.80) | rose |
| `PARTICIPIAL_TAIL / participial_tail / prevent` | 6 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 15 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 3.48 (1.37 to 12.78) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / additionally` | 16 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 40 | 0.06 (0.04 to 0.08) | 0.07 (0.04 to 0.10) | 3.48 (1.62 to 8.84) | rose |
| `PARTICIPIAL_TAIL / participial_tail / require` | 15 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 37 | 0.06 (0.04 to 0.08) | 0.05 (0.03 to 0.07) | 3.44 (1.91 to 7.25) | rose |
| `PARTICIPIAL_TAIL / participial_tail / provide` | 27 | 0.03 (0.02 to 0.04) | 0.03 (0.01 to 0.04) | 66 | 0.10 (0.07 to 0.13) | 0.08 (0.06 to 0.11) | 3.41 (2.10 to 6.12) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cause` | 16 | 0.02 (0.01 to 0.03) | 0.01 (0.00 to 0.02) | 39 | 0.06 (0.03 to 0.09) | 0.05 (0.03 to 0.08) | 3.40 (1.57 to 8.62) | rose |
| `HOLLOW_BOOSTER / - / -` | 51 | 0.06 (0.04 to 0.07) | 0.06 (0.04 to 0.09) | 121 | 0.18 (0.14 to 0.22) | 0.19 (0.14 to 0.24) | 3.31 (2.25 to 4.93) | rose |
| `PARTICIPIAL_TAIL / participial_tail / avoid` | 11 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 26 | 0.04 (0.02 to 0.06) | 0.04 (0.02 to 0.07) | 3.29 (1.58 to 9.27) | rose |
| `PARTICIPIAL_TAIL / participial_tail / target` | 6 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.02) | 14 | 0.02 (0.01 to 0.03) | 0.03 (0.01 to 0.06) | 3.25 (1.21 to 12.33) | rose |
| `PARTICIPIAL_TAIL / participial_tail / represent` | 8 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 18 | 0.03 (0.01 to 0.04) | 0.04 (0.02 to 0.08) | 3.14 (1.30 to 10.96) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reduce` | 29 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.05) | 64 | 0.10 (0.07 to 0.12) | 0.09 (0.06 to 0.13) | 3.08 (1.85 to 5.59) | rose |
| `PARTICIPIAL_TAIL / participial_tail / show` | 14 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 27 | 0.04 (0.03 to 0.06) | 0.05 (0.03 to 0.07) | 2.69 (1.37 to 6.14) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / specifically` | 28 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 51 | 0.08 (0.05 to 0.10) | 0.08 (0.05 to 0.11) | 2.54 (1.51 to 4.48) | rose |
| `PARTICIPIAL_TAIL / participial_tail / give` | 10 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 18 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.05) | 2.51 (1.06 to 8.50) | rose |
| `PARTICIPIAL_TAIL / participial_tail / improve` | 12 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 21 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.05) | 2.44 (1.14 to 5.82) | rose |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling / X, not Y` | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.01) | 15 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.04) | 2.32 (0.99 to 6.05) | flat |
| `PARTICIPIAL_TAIL / participial_tail / add` | 9 | 0.01 (0.00 to 0.02) | 0.00 (0.00 to 0.01) | 15 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 2.32 (0.79 to 24.89) | flat |
| `PARTICIPIAL_TAIL / participial_tail / start` | 8 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 12 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 2.09 (0.79 to 6.19) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / functionally` | 17 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 24 | 0.04 (0.02 to 0.06) | 0.04 (0.01 to 0.06) | 1.97 (0.73 to 6.53) | flat |
| `PARTICIPIAL_TAIL / participial_tail / lead` | 52 | 0.06 (0.04 to 0.08) | 0.06 (0.03 to 0.08) | 68 | 0.10 (0.07 to 0.14) | 0.10 (0.07 to 0.12) | 1.82 (1.10 to 3.11) | rose |
| `BORROWED_RIGOUR / - / -` | 147 | 0.16 (0.12 to 0.20) | 0.20 (0.14 to 0.26) | 169 | 0.26 (0.21 to 0.31) | 0.25 (0.19 to 0.30) | 1.60 (1.16 to 2.18) | rose |
| `TRICOLON / tricolon / enumeration` | 821 | 0.89 (0.81 to 0.98) | 0.87 (0.79 to 0.97) | 925 | 1.40 (1.25 to 1.57) | 1.47 (1.31 to 1.64) | 1.57 (1.35 to 1.83) | rose |
| `CONSULTANT_REGISTER / - / -` | 594 | 0.65 (0.52 to 0.78) | 0.59 (0.49 to 0.71) | 646 | 0.98 (0.83 to 1.14) | 0.98 (0.82 to 1.15) | 1.52 (1.19 to 1.96) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / computationally` | 24 | 0.03 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 26 | 0.04 (0.03 to 0.06) | 0.04 (0.03 to 0.06) | 1.51 (0.85 to 2.91) | flat |
| `PARTICIPIAL_TAIL / participial_tail / increase` | 17 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 18 | 0.03 (0.01 to 0.04) | 0.03 (0.01 to 0.04) | 1.48 (0.70 to 3.22) | flat |
| `TRICOLON / tricolon / list-like` | 1617 | 1.76 (1.63 to 1.91) | 1.75 (1.61 to 1.90) | 1614 | 2.45 (2.24 to 2.68) | 2.58 (2.33 to 2.83) | 1.39 (1.24 to 1.56) | rose |
| `PARTICIPIAL_TAIL / participial_tail / use` | 95 | 0.10 (0.07 to 0.14) | 0.11 (0.07 to 0.15) | 91 | 0.14 (0.10 to 0.18) | 0.15 (0.11 to 0.20) | 1.33 (0.90 to 2.05) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / themselves` | 20 | 0.02 (0.01 to 0.03) | 0.03 (0.01 to 0.04) | 19 | 0.03 (0.02 to 0.04) | 0.03 (0.01 to 0.04) | 1.32 (0.66 to 2.77) | flat |
| `LLM_DICTION / - / -` | 1254 | 1.37 (1.17 to 1.57) | 1.37 (1.15 to 1.62) | 1165 | 1.77 (1.49 to 2.08) | 1.77 (1.53 to 1.99) | 1.29 (1.03 to 1.63) | rose |
| `CORRECTIVE_CONTRAST / cc_coordinated / not X but Y` | 187 | 0.20 (0.17 to 0.24) | 0.17 (0.13 to 0.20) | 167 | 0.25 (0.21 to 0.31) | 0.26 (0.21 to 0.33) | 1.24 (0.95 to 1.63) | flat |
| `DISGUISE_METAPHOR / disguise_metaphor / pass` | 16 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 14 | 0.02 (0.01 to 0.04) | 0.03 (0.01 to 0.04) | 1.22 (0.42 to 3.15) | flat |
| `TRICOLON / tricolon / figure` | 354 | 0.39 (0.33 to 0.45) | 0.42 (0.35 to 0.49) | 291 | 0.44 (0.38 to 0.50) | 0.46 (0.39 to 0.53) | 1.15 (0.93 to 1.40) | flat |
| `VAGUE_QUANTIFIER / - / -` | 126 | 0.14 (0.11 to 0.17) | 0.15 (0.11 to 0.20) | 99 | 0.15 (0.11 to 0.20) | 0.14 (0.10 to 0.18) | 1.10 (0.74 to 1.56) | flat |
| `PARTICIPIAL_TAIL / participial_tail / mean` | 24 | 0.03 (0.01 to 0.05) | 0.03 (0.01 to 0.06) | 17 | 0.03 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 0.99 (0.44 to 2.57) | flat |
| `ALTERNATIVE_FRAMING / af_rather_instead / instead of` | 156 | 0.17 (0.14 to 0.20) | 0.17 (0.13 to 0.21) | 110 | 0.17 (0.13 to 0.21) | 0.15 (0.12 to 0.19) | 0.98 (0.72 to 1.34) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / itself` | 86 | 0.09 (0.06 to 0.12) | 0.08 (0.05 to 0.10) | 58 | 0.09 (0.06 to 0.12) | 0.08 (0.06 to 0.11) | 0.94 (0.61 to 1.50) | flat |
| `CLOSER / - / -` | 56 | 0.06 (0.04 to 0.09) | 0.06 (0.04 to 0.09) | 37 | 0.06 (0.03 to 0.08) | 0.06 (0.03 to 0.08) | 0.92 (0.51 to 1.57) | flat |
| `PARTICIPIAL_TAIL / participial_tail / consider` | 14 | 0.02 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 8 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.03) | 0.80 (0.23 to 1.90) | flat |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft` | 17 | 0.02 (0.01 to 0.03) | 0.01 (0.00 to 0.02) | 9 | 0.01 (0.00 to 0.02) | 0.01 (0.00 to 0.02) | 0.74 (0.22 to 2.17) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / potentially` | 30 | 0.03 (0.02 to 0.05) | 0.03 (0.02 to 0.05) | 15 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 0.70 (0.27 to 1.47) | flat |
| `FRAME_MARKER / - / -` | 79 | 0.09 (0.06 to 0.11) | 0.08 (0.06 to 0.11) | 38 | 0.06 (0.04 to 0.08) | 0.07 (0.04 to 0.09) | 0.67 (0.40 to 1.08) | flat |
| `ALTERNATIVE_FRAMING / af_less_than / more...than` | 428 | 0.47 (0.40 to 0.53) | 0.52 (0.43 to 0.62) | 202 | 0.31 (0.25 to 0.37) | 0.31 (0.26 to 0.37) | 0.66 (0.52 to 0.83) | fell |
| `ABSTRACT_ADVERB / abstract_adverb / spatially` | 30 | 0.03 (0.01 to 0.07) | 0.03 (0.01 to 0.05) | 14 | 0.02 (0.01 to 0.04) | 0.01 (0.00 to 0.03) | 0.65 (0.16 to 2.57) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / partially` | 48 | 0.05 (0.02 to 0.10) | 0.06 (0.02 to 0.14) | 22 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.06) | 0.64 (0.25 to 2.18) | flat |
| `EMPTY_FRAME / - / -` | 104 | 0.11 (0.08 to 0.15) | 0.12 (0.08 to 0.15) | 46 | 0.07 (0.05 to 0.10) | 0.07 (0.05 to 0.10) | 0.62 (0.39 to 0.96) | fell |
| `ALTERNATIVE_FRAMING / af_less_than / less...than` | 252 | 0.27 (0.22 to 0.33) | 0.27 (0.21 to 0.32) | 110 | 0.17 (0.13 to 0.20) | 0.16 (0.13 to 0.20) | 0.61 (0.45 to 0.81) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft / cleft, across sentences` | 30 | 0.03 (0.02 to 0.05) | 0.03 (0.01 to 0.04) | 11 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 0.51 (0.19 to 1.19) | flat |
| `HEDGE_STACK / - / -` | 22 | 0.02 (0.01 to 0.04) | 0.02 (0.01 to 0.03) | 4 | 0.01 (0.00 to 0.01) | 0.01 (0.00 to 0.01) | 0.25 (0.05 to 0.73) | fell |

With 22 body pattern rows at 95%, a few `rose` or `fell` verdicts near an interval edge are expected by chance.
