# ticfinder construction rates in arXiv cs.AR abstracts, before and after LLMs

Generated 2026-11-18 by `eval/arxiv_rates.py` (TF-004). Aggregates only: no abstract text, titles or paper ids.

## Setup

| item | value |
|---|---|
| source | arXiv API, `cat:cs.AR`, primary category cs.AR only; metadata is CC0 |
| pre window | first version 2018-01-01 to 2021-12-31 (analysed papers span 2018-01-01 to 2021-12-30) |
| post window | first version 2025-01-01 to the latest date available, 2026-11-17 (analysed papers from 2025-01-01) |
| pre papers | 955 primary cs.AR; all analysed, no sampling; 797 cross-listed papers excluded |
| post papers | 2627 primary cs.AR; all analysed, no sampling; 1307 cross-listed papers excluded |
| ticfinder | `tools/ticfinder.py` at 69e1743 (sha256 c1c7d5943a28); defaults: `en_core_web_md`, code masker on, `ticfinder-phrases.json`; abstracts analysed as plain text (`.txt`) |
| bootstrap | 2000 draws over papers, seed 4004; percentile 95% intervals (nearest rank for ratios, so draws with a zero pre rate give inf, not nan); the ratio interval resamples both windows independently |
| rate | findings per 1,000 words, pooled over papers (total findings / total words); words are alphabetic tokens after masking |

## Sanity measures

| measure | pre | post |
|---|---|---|
| papers analysed | 955 | 2627 |
| words analysed | 179,136 | 500,093 |
| mean abstract length, words (95% interval) | 187.6 (183.9 to 191.2) | 190.4 (188.5 to 192.2) |
| LaTeX-masked share of non-space characters | 0.21% | 0.46% |
| abstracts with any LaTeX masked | 12.1% | 23.2% |
| ticfinder masked_pct, mean per abstract | 0.00% | 0.00% |
| Unicode em and en dashes in the abstracts | 0 | 0 |
| em dash proxy (TeX `---` and spaced ` -- `), n | 43 | 158 |
| em dash proxy per 1k words (95% CI) | 0.24 (0.15 to 0.34) | 0.32 (0.24 to 0.40) |
| em dash proxy ratio, post over pre (95% CI) | 1.32 (0.85 to 2.25) | |

## Rates per construction

Sorted by ratio. `n` is findings in both windows; `papers` is abstracts with at least one finding. Verdict: `rose` when the ratio interval is above 1, `fell` when below, `flat` when it spans 1, `too few` under 20 findings in total.

| construction | pre n | pre papers | pre rate (95% CI) | post n | post papers | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `NEG_ESCALATION` | 0 | 0 | 0.00 (0.00 to 0.00) | 2 | 2 | 0.00 (0.00 to 0.01) | inf (inf to inf) | too few |
| `GAPPED_ANTITHESIS` | 0 | 0 | 0.00 (0.00 to 0.00) | 1 | 1 | 0.00 (0.00 to 0.01) | inf (inf to inf) | too few |
| `CLOSER` | 1 | 1 | 0.01 (0.00 to 0.02) | 11 | 11 | 0.02 (0.01 to 0.04) | 3.94 (0.91 to inf) | too few |
| `PARTICIPIAL_TAIL` | 324 | 250 | 1.81 (1.60 to 2.01) | 2836 | 1658 | 5.67 (5.46 to 5.88) | 3.14 (2.79 to 3.57) | rose |
| `DISGUISE_METAPHOR` | 3 | 3 | 0.02 (0.00 to 0.04) | 24 | 24 | 0.05 (0.03 to 0.07) | 2.87 (1.10 to inf) | rose |
| `TRICOLON` | 760 | 500 | 4.24 (3.95 to 4.55) | 3055 | 1676 | 6.11 (5.87 to 6.34) | 1.44 (1.32 to 1.56) | rose |
| `HOLLOW_BOOSTER` | 10 | 10 | 0.06 (0.02 to 0.09) | 40 | 40 | 0.08 (0.06 to 0.11) | 1.43 (0.79 to 3.56) | flat |
| `CONSULTANT_REGISTER` | 295 | 216 | 1.65 (1.43 to 1.88) | 1177 | 869 | 2.35 (2.21 to 2.50) | 1.43 (1.23 to 1.67) | rose |
| `EMPHATIC_REFLEXIVE` | 13 | 13 | 0.07 (0.04 to 0.11) | 47 | 46 | 0.09 (0.07 to 0.12) | 1.30 (0.74 to 2.63) | flat |
| `LLM_DICTION` | 535 | 346 | 2.99 (2.69 to 3.30) | 1903 | 1200 | 3.81 (3.61 to 4.00) | 1.27 (1.14 to 1.44) | rose |
| `ABSTRACT_ADVERB` | 124 | 111 | 0.69 (0.57 to 0.84) | 439 | 380 | 0.88 (0.79 to 0.97) | 1.27 (1.02 to 1.59) | rose |
| `ALTERNATIVE_FRAMING` | 137 | 123 | 0.76 (0.63 to 0.90) | 471 | 405 | 0.94 (0.85 to 1.03) | 1.23 (1.02 to 1.51) | rose |
| `CORRECTIVE_CONTRAST` | 38 | 36 | 0.21 (0.14 to 0.28) | 110 | 102 | 0.22 (0.18 to 0.26) | 1.04 (0.71 to 1.57) | flat |
| `BORROWED_RIGOUR` | 55 | 49 | 0.31 (0.22 to 0.40) | 156 | 139 | 0.31 (0.26 to 0.37) | 1.02 (0.74 to 1.45) | flat |
| `VAGUE_QUANTIFIER` | 155 | 140 | 0.87 (0.73 to 1.01) | 366 | 346 | 0.73 (0.66 to 0.81) | 0.85 (0.70 to 1.03) | flat |
| `HEDGE_STACK` | 2 | 2 | 0.01 (0.00 to 0.03) | 4 | 3 | 0.01 (0.00 to 0.02) | 0.72 (0.00 to inf) | too few |
| `EMPTY_FRAME` | 2 | 2 | 0.01 (0.00 to 0.03) | 2 | 2 | 0.00 (0.00 to 0.01) | 0.36 (0.00 to inf) | too few |
| `FRAME_MARKER` | 16 | 16 | 0.09 (0.05 to 0.13) | 12 | 12 | 0.02 (0.01 to 0.04) | 0.27 (0.12 to 0.56) | fell |

## Rates per pattern

Sorted by ratio. `n` is findings in both windows; `papers` is abstracts with at least one finding. Verdict: `rose` when the ratio interval is above 1, `fell` when below, `flat` when it spans 1, `too few` under 20 findings in total.

| construction / pattern | pre n | pre papers | pre rate (95% CI) | post n | post papers | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 0 | 0 | 0.00 (0.00 to 0.00) | 6 | 6 | 0.01 (0.00 to 0.02) | inf (inf to inf) | too few |
| `NEG_ESCALATION / neg_escalation` | 0 | 0 | 0.00 (0.00 to 0.00) | 2 | 2 | 0.00 (0.00 to 0.01) | inf (inf to inf) | too few |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 0 | 0 | 0.00 (0.00 to 0.00) | 1 | 1 | 0.00 (0.00 to 0.01) | inf (inf to inf) | too few |
| `CLOSER / -` | 1 | 1 | 0.01 (0.00 to 0.02) | 11 | 11 | 0.02 (0.01 to 0.04) | 3.94 (0.91 to inf) | too few |
| `PARTICIPIAL_TAIL / participial_tail` | 324 | 250 | 1.81 (1.60 to 2.01) | 2836 | 1658 | 5.67 (5.46 to 5.88) | 3.14 (2.79 to 3.57) | rose |
| `DISGUISE_METAPHOR / disguise_metaphor` | 3 | 3 | 0.02 (0.00 to 0.04) | 24 | 24 | 0.05 (0.03 to 0.07) | 2.87 (1.10 to inf) | rose |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 2 | 2 | 0.01 (0.00 to 0.03) | 13 | 11 | 0.03 (0.01 to 0.04) | 2.33 (0.71 to inf) | too few |
| `ALTERNATIVE_FRAMING / af_rather_instead` | 36 | 35 | 0.20 (0.14 to 0.27) | 216 | 193 | 0.43 (0.37 to 0.49) | 2.15 (1.56 to 3.29) | rose |
| `TRICOLON / tricolon` | 760 | 500 | 4.24 (3.95 to 4.55) | 3055 | 1676 | 6.11 (5.87 to 6.34) | 1.44 (1.32 to 1.56) | rose |
| `HOLLOW_BOOSTER / -` | 10 | 10 | 0.06 (0.02 to 0.09) | 40 | 40 | 0.08 (0.06 to 0.11) | 1.43 (0.79 to 3.56) | flat |
| `CONSULTANT_REGISTER / -` | 295 | 216 | 1.65 (1.43 to 1.88) | 1177 | 869 | 2.35 (2.21 to 2.50) | 1.43 (1.23 to 1.67) | rose |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 13 | 13 | 0.07 (0.04 to 0.11) | 47 | 46 | 0.09 (0.07 to 0.12) | 1.30 (0.74 to 2.63) | flat |
| `LLM_DICTION / -` | 535 | 346 | 2.99 (2.69 to 3.30) | 1903 | 1200 | 3.81 (3.61 to 4.00) | 1.27 (1.14 to 1.44) | rose |
| `ABSTRACT_ADVERB / abstract_adverb` | 124 | 111 | 0.69 (0.57 to 0.84) | 439 | 380 | 0.88 (0.79 to 0.97) | 1.27 (1.02 to 1.59) | rose |
| `BORROWED_RIGOUR / -` | 55 | 49 | 0.31 (0.22 to 0.40) | 156 | 139 | 0.31 (0.26 to 0.37) | 1.02 (0.74 to 1.45) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 32 | 31 | 0.18 (0.11 to 0.24) | 89 | 89 | 0.18 (0.14 to 0.22) | 1.00 (0.69 to 1.57) | flat |
| `ALTERNATIVE_FRAMING / af_less_than` | 101 | 92 | 0.56 (0.45 to 0.68) | 255 | 230 | 0.51 (0.44 to 0.58) | 0.90 (0.72 to 1.17) | flat |
| `VAGUE_QUANTIFIER / -` | 155 | 140 | 0.87 (0.73 to 1.01) | 366 | 346 | 0.73 (0.66 to 0.81) | 0.85 (0.70 to 1.03) | flat |
| `HEDGE_STACK / -` | 2 | 2 | 0.01 (0.00 to 0.03) | 4 | 3 | 0.01 (0.00 to 0.02) | 0.72 (0.00 to inf) | too few |
| `EMPTY_FRAME / -` | 2 | 2 | 0.01 (0.00 to 0.03) | 2 | 2 | 0.00 (0.00 to 0.01) | 0.36 (0.00 to inf) | too few |
| `FRAME_MARKER / -` | 16 | 16 | 0.09 (0.05 to 0.13) | 12 | 12 | 0.02 (0.01 to 0.04) | 0.27 (0.12 to 0.56) | fell |
| `CORRECTIVE_CONTRAST / cc_cleft` | 4 | 4 | 0.02 (0.01 to 0.05) | 2 | 2 | 0.00 (0.00 to 0.01) | 0.18 (0.00 to 1.42) | too few |

## Rates per subtype, at least 20 findings

Sorted by ratio. `n` is findings in both windows; `papers` is abstracts with at least one finding. Verdict: `rose` when the ratio interval is above 1, `fell` when below, `flat` when it spans 1, `too few` under 20 findings in total.

| construction / pattern / subtype | pre n | pre papers | pre rate (95% CI) | post n | post papers | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `PARTICIPIAL_TAIL / participial_tail / leave` | 0 | 0 | 0.00 (0.00 to 0.00) | 48 | 48 | 0.10 (0.07 to 0.12) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / highlight` | 0 | 0 | 0.00 (0.00 to 0.00) | 45 | 44 | 0.09 (0.06 to 0.12) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / create` | 0 | 0 | 0.00 (0.00 to 0.00) | 25 | 25 | 0.05 (0.03 to 0.07) | inf (inf to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / outperform` | 1 | 1 | 0.01 (0.00 to 0.02) | 30 | 29 | 0.06 (0.04 to 0.08) | 10.75 (2.88 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / eliminate` | 2 | 2 | 0.01 (0.00 to 0.03) | 46 | 45 | 0.09 (0.07 to 0.12) | 8.24 (2.97 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / yield` | 1 | 1 | 0.01 (0.00 to 0.02) | 23 | 22 | 0.05 (0.03 to 0.07) | 8.24 (2.16 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / demonstrate` | 5 | 5 | 0.03 (0.01 to 0.06) | 113 | 112 | 0.23 (0.19 to 0.27) | 8.10 (3.95 to 37.68) | rose |
| `PARTICIPIAL_TAIL / participial_tail / offer` | 3 | 3 | 0.02 (0.00 to 0.04) | 58 | 58 | 0.12 (0.09 to 0.15) | 6.93 (3.01 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / enable` | 13 | 13 | 0.07 (0.03 to 0.11) | 238 | 232 | 0.48 (0.42 to 0.54) | 6.56 (4.15 to 13.89) | rose |
| `PARTICIPIAL_TAIL / participial_tail / deliver` | 2 | 2 | 0.01 (0.00 to 0.03) | 34 | 34 | 0.07 (0.05 to 0.09) | 6.09 (2.13 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / leverage` | 2 | 2 | 0.01 (0.00 to 0.03) | 30 | 30 | 0.06 (0.04 to 0.08) | 5.37 (1.82 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / ensure` | 3 | 3 | 0.02 (0.00 to 0.04) | 40 | 38 | 0.08 (0.06 to 0.11) | 4.78 (1.90 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / require` | 3 | 3 | 0.02 (0.00 to 0.04) | 40 | 40 | 0.08 (0.06 to 0.11) | 4.78 (1.97 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / cause` | 2 | 2 | 0.01 (0.00 to 0.03) | 26 | 26 | 0.05 (0.03 to 0.07) | 4.66 (1.56 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / achieve` | 14 | 14 | 0.08 (0.04 to 0.12) | 174 | 160 | 0.35 (0.29 to 0.41) | 4.45 (2.80 to 8.96) | rose |
| `PARTICIPIAL_TAIL / participial_tail / limit` | 5 | 5 | 0.03 (0.01 to 0.05) | 57 | 57 | 0.11 (0.09 to 0.14) | 4.08 (2.06 to 19.75) | rose |
| `ALTERNATIVE_FRAMING / af_rather_instead / rather than` | 14 | 13 | 0.08 (0.04 to 0.12) | 150 | 134 | 0.30 (0.25 to 0.35) | 3.84 (2.29 to 8.06) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / spatially` | 2 | 2 | 0.01 (0.00 to 0.03) | 20 | 19 | 0.04 (0.02 to 0.06) | 3.58 (1.14 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / focus` | 2 | 2 | 0.01 (0.00 to 0.03) | 19 | 19 | 0.04 (0.02 to 0.06) | 3.40 (1.11 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / support` | 2 | 2 | 0.01 (0.00 to 0.03) | 19 | 18 | 0.04 (0.02 to 0.06) | 3.40 (1.08 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / combine` | 2 | 2 | 0.01 (0.00 to 0.03) | 18 | 18 | 0.04 (0.02 to 0.05) | 3.22 (1.06 to inf) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / specifically` | 6 | 6 | 0.03 (0.01 to 0.06) | 51 | 51 | 0.10 (0.08 to 0.13) | 3.04 (1.51 to 10.81) | rose |
| `PARTICIPIAL_TAIL / participial_tail / reduce` | 12 | 12 | 0.07 (0.03 to 0.11) | 101 | 92 | 0.20 (0.16 to 0.25) | 3.01 (1.80 to 6.55) | rose |
| `PARTICIPIAL_TAIL / participial_tail / lead` | 11 | 11 | 0.06 (0.03 to 0.10) | 91 | 90 | 0.18 (0.15 to 0.22) | 2.96 (1.72 to 6.81) | rose |
| `PARTICIPIAL_TAIL / participial_tail / show` | 6 | 6 | 0.03 (0.01 to 0.06) | 48 | 46 | 0.10 (0.07 to 0.12) | 2.87 (1.40 to 9.22) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / functionally` | 4 | 3 | 0.02 (0.00 to 0.05) | 32 | 29 | 0.06 (0.04 to 0.09) | 2.87 (1.10 to inf) | rose |
| `PARTICIPIAL_TAIL / participial_tail / make` | 27 | 26 | 0.15 (0.09 to 0.21) | 181 | 178 | 0.36 (0.31 to 0.41) | 2.40 (1.65 to 3.85) | rose |
| `DISGUISE_METAPHOR / disguise_metaphor / pose` | 3 | 3 | 0.02 (0.00 to 0.04) | 19 | 19 | 0.04 (0.02 to 0.05) | 2.27 (0.85 to inf) | flat |
| `PARTICIPIAL_TAIL / participial_tail / improve` | 6 | 6 | 0.03 (0.01 to 0.06) | 37 | 37 | 0.07 (0.05 to 0.10) | 2.21 (1.05 to 7.09) | rose |
| `PARTICIPIAL_TAIL / participial_tail / provide` | 12 | 12 | 0.07 (0.03 to 0.11) | 61 | 61 | 0.12 (0.09 to 0.15) | 1.82 (1.08 to 3.79) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / substantially` | 5 | 5 | 0.03 (0.01 to 0.06) | 25 | 25 | 0.05 (0.03 to 0.07) | 1.79 (0.76 to 8.28) | flat |
| `TRICOLON / tricolon / list-like` | 426 | 345 | 2.38 (2.16 to 2.59) | 1854 | 1268 | 3.71 (3.53 to 3.88) | 1.56 (1.41 to 1.74) | rose |
| `TRICOLON / tricolon / enumeration` | 196 | 168 | 1.09 (0.94 to 1.27) | 817 | 637 | 1.63 (1.52 to 1.75) | 1.49 (1.27 to 1.77) | rose |
| `PARTICIPIAL_TAIL / participial_tail / allow` | 14 | 14 | 0.08 (0.04 to 0.12) | 58 | 58 | 0.12 (0.09 to 0.15) | 1.48 (0.87 to 3.12) | flat |
| `HOLLOW_BOOSTER / - / -` | 10 | 10 | 0.06 (0.02 to 0.09) | 40 | 40 | 0.08 (0.06 to 0.11) | 1.43 (0.79 to 3.56) | flat |
| `CONSULTANT_REGISTER / - / -` | 295 | 216 | 1.65 (1.43 to 1.88) | 1177 | 869 | 2.35 (2.21 to 2.50) | 1.43 (1.23 to 1.67) | rose |
| `ABSTRACT_ADVERB / abstract_adverb / fundamentally` | 9 | 9 | 0.05 (0.02 to 0.08) | 35 | 34 | 0.07 (0.05 to 0.09) | 1.39 (0.72 to 3.69) | flat |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / itself` | 11 | 11 | 0.06 (0.03 to 0.10) | 40 | 39 | 0.08 (0.06 to 0.11) | 1.30 (0.71 to 2.97) | flat |
| `LLM_DICTION / - / -` | 535 | 346 | 2.99 (2.69 to 3.30) | 1903 | 1200 | 3.81 (3.61 to 4.00) | 1.27 (1.14 to 1.44) | rose |
| `ALTERNATIVE_FRAMING / af_less_than / less...than` | 28 | 26 | 0.16 (0.10 to 0.22) | 94 | 91 | 0.19 (0.15 to 0.23) | 1.20 (0.80 to 1.96) | flat |
| `PARTICIPIAL_TAIL / participial_tail / use` | 18 | 18 | 0.10 (0.06 to 0.15) | 55 | 55 | 0.11 (0.08 to 0.14) | 1.09 (0.67 to 2.00) | flat |
| `ALTERNATIVE_FRAMING / af_rather_instead / instead of` | 22 | 22 | 0.12 (0.07 to 0.17) | 66 | 63 | 0.13 (0.10 to 0.17) | 1.07 (0.68 to 1.90) | flat |
| `BORROWED_RIGOUR / - / -` | 55 | 49 | 0.31 (0.22 to 0.40) | 156 | 139 | 0.31 (0.26 to 0.37) | 1.02 (0.74 to 1.45) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / computationally` | 16 | 15 | 0.09 (0.04 to 0.14) | 45 | 44 | 0.09 (0.06 to 0.12) | 1.01 (0.58 to 2.02) | flat |
| `TRICOLON / tricolon / figure` | 138 | 123 | 0.77 (0.65 to 0.91) | 384 | 353 | 0.77 (0.69 to 0.85) | 1.00 (0.82 to 1.22) | flat |
| `CORRECTIVE_CONTRAST / cc_coordinated / not X but Y` | 32 | 31 | 0.18 (0.11 to 0.24) | 89 | 89 | 0.18 (0.14 to 0.22) | 1.00 (0.69 to 1.57) | flat |
| `PARTICIPIAL_TAIL / participial_tail / result` | 23 | 21 | 0.13 (0.07 to 0.19) | 59 | 59 | 0.12 (0.09 to 0.15) | 0.92 (0.57 to 1.63) | flat |
| `VAGUE_QUANTIFIER / - / -` | 155 | 140 | 0.87 (0.73 to 1.01) | 366 | 346 | 0.73 (0.66 to 0.81) | 0.85 (0.70 to 1.03) | flat |
| `ALTERNATIVE_FRAMING / af_less_than / more...than` | 73 | 69 | 0.41 (0.32 to 0.51) | 161 | 148 | 0.32 (0.27 to 0.38) | 0.79 (0.60 to 1.08) | flat |
| `ABSTRACT_ADVERB / abstract_adverb / traditionally` | 7 | 7 | 0.04 (0.01 to 0.07) | 14 | 14 | 0.03 (0.01 to 0.04) | 0.72 (0.30 to 2.34) | flat |
| `FRAME_MARKER / - / -` | 16 | 16 | 0.09 (0.05 to 0.13) | 12 | 12 | 0.02 (0.01 to 0.04) | 0.27 (0.12 to 0.56) | fell |

## Phrase-list matches, at least 20 findings

Sorted by ratio. `n` is findings in both windows; `papers` is abstracts with at least one finding. Verdict: `rose` when the ratio interval is above 1, `fell` when below, `flat` when it spans 1, `too few` under 20 findings in total.

| construction / matched phrase | pre n | pre papers | pre rate (95% CI) | post n | post papers | post rate (95% CI) | ratio (95% CI) | verdict |
|---|---|---|---|---|---|---|---|---|
| `LLM_DICTION / landscape` | 2 | 2 | 0.01 (0.00 to 0.03) | 26 | 22 | 0.05 (0.03 to 0.08) | 4.66 (1.62 to inf) | rose |
| `CONSULTANT_REGISTER / leverages` | 17 | 16 | 0.09 (0.05 to 0.15) | 168 | 166 | 0.34 (0.29 to 0.39) | 3.54 (2.25 to 6.84) | rose |
| `LLM_DICTION / seamless` | 3 | 3 | 0.02 (0.00 to 0.04) | 21 | 20 | 0.04 (0.02 to 0.06) | 2.51 (0.95 to inf) | flat |
| `BORROWED_RIGOUR / search space` | 4 | 4 | 0.02 (0.01 to 0.05) | 23 | 20 | 0.05 (0.03 to 0.07) | 2.06 (0.81 to 10.76) | flat |
| `LLM_DICTION / innovative` | 5 | 5 | 0.03 (0.01 to 0.06) | 28 | 28 | 0.06 (0.04 to 0.08) | 2.01 (0.88 to 8.97) | flat |
| `VAGUE_QUANTIFIER / increasingly` | 46 | 46 | 0.26 (0.19 to 0.33) | 255 | 249 | 0.51 (0.45 to 0.57) | 1.99 (1.49 to 2.73) | rose |
| `LLM_DICTION / essential` | 28 | 28 | 0.16 (0.10 to 0.21) | 148 | 145 | 0.30 (0.25 to 0.34) | 1.89 (1.33 to 3.00) | rose |
| `CONSULTANT_REGISTER / leveraging` | 35 | 33 | 0.20 (0.13 to 0.27) | 184 | 176 | 0.37 (0.32 to 0.42) | 1.88 (1.32 to 2.88) | rose |
| `CONSULTANT_REGISTER / optimizing` | 23 | 23 | 0.13 (0.08 to 0.18) | 116 | 106 | 0.23 (0.19 to 0.28) | 1.81 (1.19 to 2.98) | rose |
| `LLM_DICTION / comprehensive` | 37 | 35 | 0.21 (0.14 to 0.28) | 169 | 162 | 0.34 (0.29 to 0.39) | 1.64 (1.16 to 2.50) | rose |
| `LLM_DICTION / versatile` | 6 | 6 | 0.03 (0.01 to 0.06) | 26 | 25 | 0.05 (0.03 to 0.07) | 1.55 (0.69 to 5.62) | flat |
| `LLM_DICTION / dynamics` | 10 | 6 | 0.06 (0.01 to 0.13) | 42 | 37 | 0.08 (0.06 to 0.11) | 1.50 (0.58 to 8.03) | flat |
| `LLM_DICTION / robust` | 24 | 23 | 0.13 (0.08 to 0.19) | 97 | 95 | 0.19 (0.16 to 0.23) | 1.45 (0.96 to 2.42) | flat |
| `HOLLOW_BOOSTER / notably,` | 4 | 4 | 0.02 (0.01 to 0.05) | 16 | 16 | 0.03 (0.02 to 0.05) | 1.43 (0.54 to 7.50) | flat |
| `CONSULTANT_REGISTER / optimizes` | 20 | 18 | 0.11 (0.06 to 0.17) | 76 | 72 | 0.15 (0.12 to 0.19) | 1.36 (0.85 to 2.51) | flat |
| `CONSULTANT_REGISTER / optimize` | 45 | 43 | 0.25 (0.18 to 0.33) | 156 | 145 | 0.31 (0.26 to 0.37) | 1.24 (0.89 to 1.82) | flat |
| `LLM_DICTION / significant` | 141 | 120 | 0.79 (0.65 to 0.92) | 481 | 443 | 0.96 (0.87 to 1.05) | 1.22 (1.01 to 1.49) | rose |
| `CONSULTANT_REGISTER / optimized` | 90 | 71 | 0.50 (0.39 to 0.63) | 298 | 263 | 0.60 (0.52 to 0.67) | 1.19 (0.92 to 1.59) | flat |
| `LLM_DICTION / crucial` | 31 | 31 | 0.17 (0.11 to 0.24) | 102 | 101 | 0.20 (0.17 to 0.24) | 1.18 (0.82 to 1.86) | flat |
| `LLM_DICTION / paradigms` | 10 | 10 | 0.06 (0.02 to 0.09) | 32 | 29 | 0.06 (0.04 to 0.09) | 1.15 (0.57 to 2.89) | flat |
| `BORROWED_RIGOUR / order of magnitude` | 9 | 9 | 0.05 (0.02 to 0.08) | 27 | 26 | 0.05 (0.03 to 0.08) | 1.07 (0.53 to 2.92) | flat |
| `LLM_DICTION / dynamic` | 136 | 97 | 0.76 (0.60 to 0.93) | 384 | 276 | 0.77 (0.67 to 0.87) | 1.01 (0.79 to 1.30) | flat |
| `CONSULTANT_REGISTER / holistic` | 9 | 9 | 0.05 (0.02 to 0.09) | 24 | 23 | 0.05 (0.03 to 0.07) | 0.96 (0.45 to 2.30) | flat |
| `LLM_DICTION / harness` | 7 | 5 | 0.04 (0.01 to 0.08) | 17 | 15 | 0.03 (0.02 to 0.05) | 0.87 (0.34 to 5.05) | flat |
| `CONSULTANT_REGISTER / leverage` | 26 | 26 | 0.15 (0.09 to 0.20) | 60 | 58 | 0.12 (0.09 to 0.15) | 0.83 (0.53 to 1.34) | flat |
| `VAGUE_QUANTIFIER / numerous` | 17 | 17 | 0.09 (0.05 to 0.14) | 39 | 37 | 0.08 (0.05 to 0.10) | 0.82 (0.47 to 1.58) | flat |
| `LLM_DICTION / paradigm` | 58 | 41 | 0.32 (0.21 to 0.45) | 133 | 121 | 0.27 (0.22 to 0.32) | 0.82 (0.57 to 1.29) | flat |
| `LLM_DICTION / vital` | 8 | 8 | 0.04 (0.02 to 0.08) | 17 | 17 | 0.03 (0.02 to 0.05) | 0.76 (0.35 to 2.16) | flat |
| `BORROWED_RIGOUR / state of the art` | 13 | 11 | 0.07 (0.03 to 0.12) | 18 | 18 | 0.04 (0.02 to 0.05) | 0.50 (0.23 to 1.20) | flat |
| `VAGUE_QUANTIFIER / a wide range of` | 48 | 41 | 0.27 (0.19 to 0.36) | 49 | 49 | 0.10 (0.07 to 0.13) | 0.37 (0.24 to 0.56) | fell |
| `VAGUE_QUANTIFIER / a variety of` | 41 | 37 | 0.23 (0.16 to 0.31) | 18 | 17 | 0.04 (0.02 to 0.05) | 0.16 (0.08 to 0.27) | fell |

With 22 pattern rows at 95%, one or two `rose` or `fell` verdicts near the interval edge are expected by chance.
