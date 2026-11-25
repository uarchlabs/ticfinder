# ticfinder construction rates in public pre-2022 design and specification documents

Generated 2026-11-25 by `eval/spec_baseline.py` (TF-009). Aggregates only: no document text, titles, file names or document numbers, and for the author's specifications no per-file figures. Ratios here compare two corpora (or one source with the pool). They are not likelihood ratios; those are step 8.

## Setup

| item | value |
|---|---|
| sources | Python PEPs, IETF RFCs, Rust RFCs, the RISC-V ISA manuals and the OpenTitan hardware docs, each as of its last commit (or index entry) before 2022-01-01, with documents dated 2018 to 2021 (the TF-004 pre window) |
| sample | every dated document, except a source over 1,500,000 raw words, which is shuffled with seed `20261121-<source>` and walked until the cap |
| exclusions | per source, in place (`selftest` holds the rows): boilerplate, front matter, references, acknowledgements, headings, page furniture, figures, tables, code, markup and generated regions; then ticfinder's own masking |
| ticfinder | `tools/ticfinder.py` at 494e4dd (sha256 f0fc55a44f37); defaults: `en_core_web_md`, code masker on, `ticfinder-phrases.json`; Rust and OpenTitan kept text analysed as `.md`, the others as `.txt` |
| arXiv side | TF-008 full-run per-paper tables, pre window, all sections, 778 papers, written at sha256 f0fc55a44f37 |
| author side | the author's specification files in `$WRITING_SAMPLES`, read in place as in TF-003 (the `.docx` skipped), 36 files; construction and pattern counts only |
| bootstrap | 2000 draws over documents, seed 9009; one index matrix per source, for the arXiv papers and for the author's files; percentile 95% intervals, nearest rank for ratios |
| rates | findings per 1,000 words. Words are ticfinder's count (alphabetic spaCy tokens of the masked text). Pooled by words: total findings over total words of the five sources. Equal-weight: the mean of the five source rates |
| rows | at least 20 findings in the pool; comparisons need at least 20 findings on both sides |

## Sample and masking

| source | documents | raw words | kept words (ticfinder) | median masked share | documents over 40% masked |
|---|---|---|---|---|---|
| PEPs | 123 | 360,029 | 285,161 | 28.4% | 28 |
| IETF RFCs | 177 | 1,511,288 | 1,017,707 | 33.4% | 59 |
| Rust RFCs | 153 | 352,699 | 253,255 | 31.8% | 37 |
| RISC-V | 44 | 141,171 | 97,174 | 31.7% | 14 |
| OpenTitan | 105 | 232,486 | 163,521 | 31.5% | 32 |
| pool | 602 | 2,597,673 | 1,816,818 | | |

Comparison corpora: arXiv pre-window bodies 4,975,688 words in 778 papers; the author's specifications 80,788 words by ticfinder's count in 36 files (89,371 by the TF-003 measure, runs of ASCII letters after code masking).

## Which pooled rate

IETF RFCs hold 56% of the pool's words, so the rate pooled by words mostly measures one source's house style. Requirements 13 to 15 use the equal-weight pool, which counts each source as one sample of the register. Both are in the rate tables. The intervals resample documents within each source, so they cover the choice of documents and not the choice of sources.

## Rates

Rows with at least 20 findings in the pool, sorted by the equal-weight rate. Source cells are findings, then rate (95% CI). Phrase rows are phrase-list constructions keyed by the matched text, lowercased.

### construction

| construction | n | documents | pooled by words (95% CI) | equal-weight (95% CI) | PEPs | IETF RFCs | Rust RFCs | RISC-V | OpenTitan |
|---|---|---|---|---|---|---|---|---|---|
| `TRICOLON` | 4575 | 515 | 2.52 (2.39 to 2.67) | 2.83 (2.67 to 2.99) | 772, 2.71 (2.29 to 3.26) | 2418, 2.38 (2.23 to 2.53) | 510, 2.01 (1.75 to 2.30) | 408, 4.20 (3.67 to 4.67) | 467, 2.86 (2.61 to 3.15) |
| `PARTICIPIAL_TAIL` | 1182 | 342 | 0.65 (0.60 to 0.71) | 0.71 (0.64 to 0.79) | 237, 0.83 (0.70 to 0.95) | 568, 0.56 (0.49 to 0.64) | 195, 0.77 (0.64 to 0.90) | 69, 0.71 (0.52 to 0.98) | 113, 0.69 (0.49 to 0.90) |
| `ALTERNATIVE_FRAMING` | 934 | 314 | 0.51 (0.45 to 0.59) | 0.65 (0.58 to 0.72) | 335, 1.17 (0.98 to 1.42) | 263, 0.26 (0.22 to 0.30) | 243, 0.96 (0.81 to 1.12) | 66, 0.68 (0.52 to 0.88) | 27, 0.17 (0.09 to 0.24) |
| `ABSTRACT_ADVERB` | 947 | 309 | 0.52 (0.46 to 0.60) | 0.63 (0.56 to 0.70) | 207, 0.73 (0.56 to 0.89) | 391, 0.38 (0.32 to 0.47) | 204, 0.81 (0.67 to 0.95) | 85, 0.87 (0.62 to 1.12) | 60, 0.37 (0.25 to 0.48) |
| `LLM_DICTION` | 1058 | 301 | 0.58 (0.47 to 0.71) | 0.62 (0.51 to 0.75) | 228, 0.80 (0.53 to 1.11) | 546, 0.54 (0.38 to 0.73) | 133, 0.53 (0.40 to 0.64) | 77, 0.79 (0.44 to 1.25) | 74, 0.45 (0.28 to 0.66) |
| `EMPHATIC_REFLEXIVE` | 576 | 234 | 0.32 (0.28 to 0.36) | 0.32 (0.28 to 0.36) | 118, 0.41 (0.32 to 0.51) | 285, 0.28 (0.23 to 0.35) | 114, 0.45 (0.36 to 0.55) | 19, 0.20 (0.10 to 0.30) | 40, 0.24 (0.16 to 0.33) |
| `CORRECTIVE_CONTRAST` | 473 | 242 | 0.26 (0.23 to 0.29) | 0.29 (0.26 to 0.33) | 154, 0.54 (0.43 to 0.65) | 179, 0.18 (0.15 to 0.21) | 98, 0.39 (0.31 to 0.47) | 23, 0.24 (0.15 to 0.34) | 19, 0.12 (0.06 to 0.18) |
| `BORROWED_RIGOUR` | 244 | 118 | 0.13 (0.10 to 0.16) | 0.17 (0.13 to 0.23) | 55, 0.19 (0.14 to 0.25) | 105, 0.10 (0.05 to 0.15) | 44, 0.17 (0.11 to 0.24) | 34, 0.35 (0.16 to 0.63) | 6, 0.04 (0.01 to 0.06) |
| `CONSULTANT_REGISTER` | 258 | 129 | 0.14 (0.11 to 0.18) | 0.15 (0.12 to 0.19) | 31, 0.11 (0.06 to 0.17) | 138, 0.14 (0.09 to 0.19) | 49, 0.19 (0.13 to 0.28) | 17, 0.17 (0.07 to 0.31) | 23, 0.14 (0.08 to 0.21) |
| `EM_DASH` | 139 | 39 | 0.08 (0.05 to 0.12) | 0.13 (0.08 to 0.18) | 72, 0.25 (0.11 to 0.42) | 0, 0.00 (0.00 to 0.00) | 48, 0.19 (0.07 to 0.34) | 19, 0.20 (0.10 to 0.32) | 0, 0.00 (0.00 to 0.00) |
| `EMPTY_FRAME` | 180 | 110 | 0.10 (0.08 to 0.12) | 0.11 (0.08 to 0.15) | 42, 0.15 (0.09 to 0.22) | 77, 0.08 (0.06 to 0.09) | 41, 0.16 (0.10 to 0.22) | 10, 0.10 (0.01 to 0.26) | 10, 0.06 (0.02 to 0.10) |
| `VAGUE_QUANTIFIER` | 113 | 75 | 0.06 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 23, 0.08 (0.05 to 0.12) | 56, 0.06 (0.04 to 0.08) | 24, 0.09 (0.05 to 0.15) | 3, 0.03 (0.00 to 0.08) | 7, 0.04 (0.01 to 0.08) |
| `FRAME_MARKER` | 106 | 80 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.08) | 21, 0.07 (0.04 to 0.11) | 48, 0.05 (0.03 to 0.06) | 26, 0.10 (0.06 to 0.15) | 3, 0.03 (0.00 to 0.08) | 8, 0.05 (0.02 to 0.09) |
| `HEDGE_STACK` | 79 | 55 | 0.04 (0.03 to 0.06) | 0.05 (0.03 to 0.06) | 9, 0.03 (0.01 to 0.05) | 40, 0.04 (0.03 to 0.06) | 21, 0.08 (0.04 to 0.13) | 5, 0.05 (0.01 to 0.10) | 4, 0.02 (0.00 to 0.06) |
| `HOLLOW_BOOSTER` | 51 | 42 | 0.03 (0.02 to 0.04) | 0.04 (0.03 to 0.05) | 21, 0.07 (0.04 to 0.11) | 8, 0.01 (0.00 to 0.01) | 18, 0.07 (0.03 to 0.11) | 4, 0.04 (0.00 to 0.09) | 0, 0.00 (0.00 to 0.00) |
| `CLOSER` | 56 | 49 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 14, 0.05 (0.03 to 0.08) | 23, 0.02 (0.01 to 0.03) | 16, 0.06 (0.03 to 0.10) | 1, 0.01 (0.00 to 0.04) | 2, 0.01 (0.00 to 0.04) |
| `GAPPED_ANTITHESIS` | 36 | 23 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 6, 0.02 (0.00 to 0.04) | 17, 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 2, 0.02 (0.00 to 0.04) | 9, 0.06 (0.01 to 0.13) |

### pattern

| pattern | n | documents | pooled by words (95% CI) | equal-weight (95% CI) | PEPs | IETF RFCs | Rust RFCs | RISC-V | OpenTitan |
|---|---|---|---|---|---|---|---|---|---|
| `TRICOLON / tricolon` | 4569 | 515 | 2.51 (2.39 to 2.66) | 2.83 (2.66 to 2.99) | 772, 2.71 (2.29 to 3.26) | 2413, 2.37 (2.23 to 2.52) | 509, 2.01 (1.75 to 2.30) | 408, 4.20 (3.67 to 4.67) | 467, 2.86 (2.61 to 3.15) |
| `PARTICIPIAL_TAIL / participial_tail` | 1182 | 342 | 0.65 (0.60 to 0.71) | 0.71 (0.64 to 0.79) | 237, 0.83 (0.70 to 0.95) | 568, 0.56 (0.49 to 0.64) | 195, 0.77 (0.64 to 0.90) | 69, 0.71 (0.52 to 0.98) | 113, 0.69 (0.49 to 0.90) |
| `ABSTRACT_ADVERB / abstract_adverb` | 947 | 309 | 0.52 (0.46 to 0.60) | 0.63 (0.56 to 0.70) | 207, 0.73 (0.56 to 0.89) | 391, 0.38 (0.32 to 0.47) | 204, 0.81 (0.67 to 0.95) | 85, 0.87 (0.62 to 1.12) | 60, 0.37 (0.25 to 0.48) |
| `LLM_DICTION / -` | 1058 | 301 | 0.58 (0.47 to 0.71) | 0.62 (0.51 to 0.75) | 228, 0.80 (0.53 to 1.11) | 546, 0.54 (0.38 to 0.73) | 133, 0.53 (0.40 to 0.64) | 77, 0.79 (0.44 to 1.25) | 74, 0.45 (0.28 to 0.66) |
| `ALTERNATIVE_FRAMING / af_rather_than` | 477 | 177 | 0.26 (0.22 to 0.32) | 0.32 (0.27 to 0.38) | 198, 0.69 (0.50 to 0.92) | 140, 0.14 (0.10 to 0.17) | 95, 0.38 (0.28 to 0.48) | 35, 0.36 (0.22 to 0.51) | 9, 0.06 (0.01 to 0.12) |
| `ALTERNATIVE_FRAMING / af_instead_of` | 451 | 223 | 0.25 (0.21 to 0.29) | 0.32 (0.27 to 0.37) | 135, 0.47 (0.37 to 0.58) | 121, 0.12 (0.10 to 0.15) | 146, 0.58 (0.45 to 0.72) | 31, 0.32 (0.16 to 0.51) | 18, 0.11 (0.05 to 0.18) |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive` | 576 | 234 | 0.32 (0.28 to 0.36) | 0.32 (0.28 to 0.36) | 118, 0.41 (0.32 to 0.51) | 285, 0.28 (0.23 to 0.35) | 114, 0.45 (0.36 to 0.55) | 19, 0.20 (0.10 to 0.30) | 40, 0.24 (0.16 to 0.33) |
| `BORROWED_RIGOUR / -` | 244 | 118 | 0.13 (0.10 to 0.16) | 0.17 (0.13 to 0.23) | 55, 0.19 (0.14 to 0.25) | 105, 0.10 (0.05 to 0.15) | 44, 0.17 (0.11 to 0.24) | 34, 0.35 (0.16 to 0.63) | 6, 0.04 (0.01 to 0.06) |
| `CONSULTANT_REGISTER / -` | 258 | 129 | 0.14 (0.11 to 0.18) | 0.15 (0.12 to 0.19) | 31, 0.11 (0.06 to 0.17) | 138, 0.14 (0.09 to 0.19) | 49, 0.19 (0.13 to 0.28) | 17, 0.17 (0.07 to 0.31) | 23, 0.14 (0.08 to 0.21) |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 220 | 147 | 0.12 (0.10 to 0.14) | 0.13 (0.11 to 0.16) | 56, 0.20 (0.14 to 0.25) | 88, 0.09 (0.06 to 0.11) | 56, 0.22 (0.17 to 0.28) | 10, 0.10 (0.04 to 0.19) | 10, 0.06 (0.02 to 0.12) |
| `EM_DASH / -` | 139 | 39 | 0.08 (0.05 to 0.12) | 0.13 (0.08 to 0.18) | 72, 0.25 (0.11 to 0.42) | 0, 0.00 (0.00 to 0.00) | 48, 0.19 (0.07 to 0.34) | 19, 0.20 (0.10 to 0.32) | 0, 0.00 (0.00 to 0.00) |
| `EMPTY_FRAME / -` | 180 | 110 | 0.10 (0.08 to 0.12) | 0.11 (0.08 to 0.15) | 42, 0.15 (0.09 to 0.22) | 77, 0.08 (0.06 to 0.09) | 41, 0.16 (0.10 to 0.22) | 10, 0.10 (0.01 to 0.26) | 10, 0.06 (0.02 to 0.10) |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 132 | 97 | 0.07 (0.06 to 0.09) | 0.08 (0.06 to 0.09) | 48, 0.17 (0.12 to 0.22) | 53, 0.05 (0.04 to 0.07) | 22, 0.09 (0.05 to 0.13) | 6, 0.06 (0.02 to 0.11) | 3, 0.02 (0.00 to 0.04) |
| `VAGUE_QUANTIFIER / -` | 113 | 75 | 0.06 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 23, 0.08 (0.05 to 0.12) | 56, 0.06 (0.04 to 0.08) | 24, 0.09 (0.05 to 0.15) | 3, 0.03 (0.00 to 0.08) | 7, 0.04 (0.01 to 0.08) |
| `FRAME_MARKER / -` | 106 | 80 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.08) | 21, 0.07 (0.04 to 0.11) | 48, 0.05 (0.03 to 0.06) | 26, 0.10 (0.06 to 0.15) | 3, 0.03 (0.00 to 0.08) | 8, 0.05 (0.02 to 0.09) |
| `HEDGE_STACK / -` | 79 | 55 | 0.04 (0.03 to 0.06) | 0.05 (0.03 to 0.06) | 9, 0.03 (0.01 to 0.05) | 40, 0.04 (0.03 to 0.06) | 21, 0.08 (0.04 to 0.13) | 5, 0.05 (0.01 to 0.10) | 4, 0.02 (0.00 to 0.06) |
| `HOLLOW_BOOSTER / -` | 51 | 42 | 0.03 (0.02 to 0.04) | 0.04 (0.03 to 0.05) | 21, 0.07 (0.04 to 0.11) | 8, 0.01 (0.00 to 0.01) | 18, 0.07 (0.03 to 0.11) | 4, 0.04 (0.00 to 0.09) | 0, 0.00 (0.00 to 0.00) |
| `CORRECTIVE_CONTRAST / cc_additive` | 61 | 46 | 0.03 (0.02 to 0.05) | 0.04 (0.02 to 0.05) | 26, 0.09 (0.04 to 0.15) | 20, 0.02 (0.01 to 0.03) | 10, 0.04 (0.02 to 0.07) | 2, 0.02 (0.00 to 0.05) | 3, 0.02 (0.00 to 0.04) |
| `CLOSER / -` | 56 | 49 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 14, 0.05 (0.03 to 0.08) | 23, 0.02 (0.01 to 0.03) | 16, 0.06 (0.03 to 0.10) | 1, 0.01 (0.00 to 0.04) | 2, 0.01 (0.00 to 0.04) |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 37 | 31 | 0.02 (0.01 to 0.03) | 0.03 (0.02 to 0.04) | 18, 0.06 (0.03 to 0.10) | 8, 0.01 (0.00 to 0.01) | 5, 0.02 (0.00 to 0.04) | 5, 0.05 (0.01 to 0.10) | 1, 0.01 (0.00 to 0.02) |
| `GAPPED_ANTITHESIS / gapped_antithesis` | 36 | 23 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 6, 0.02 (0.00 to 0.04) | 17, 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 2, 0.02 (0.00 to 0.04) | 9, 0.06 (0.01 to 0.13) |
| `CORRECTIVE_CONTRAST / cc_cleft` | 23 | 21 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 6, 0.02 (0.00 to 0.04) | 10, 0.01 (0.00 to 0.02) | 5, 0.02 (0.00 to 0.04) | 0, 0.00 (0.00 to 0.00) | 2, 0.01 (0.00 to 0.03) |

### subtype

| subtype | n | documents | pooled by words (95% CI) | equal-weight (95% CI) | PEPs | IETF RFCs | Rust RFCs | RISC-V | OpenTitan |
|---|---|---|---|---|---|---|---|---|---|
| `TRICOLON / tricolon / list-like` | 2722 | 479 | 1.50 (1.41 to 1.60) | 1.76 (1.65 to 1.86) | 464, 1.63 (1.32 to 2.01) | 1348, 1.32 (1.22 to 1.42) | 351, 1.39 (1.20 to 1.59) | 246, 2.53 (2.24 to 2.81) | 313, 1.91 (1.72 to 2.18) |
| `TRICOLON / tricolon / enumeration` | 1366 | 336 | 0.75 (0.70 to 0.81) | 0.77 (0.69 to 0.85) | 206, 0.72 (0.56 to 0.91) | 829, 0.81 (0.74 to 0.90) | 101, 0.40 (0.32 to 0.48) | 118, 1.21 (0.91 to 1.51) | 112, 0.68 (0.54 to 0.83) |
| `LLM_DICTION / - / -` | 1058 | 301 | 0.58 (0.47 to 0.71) | 0.62 (0.51 to 0.75) | 228, 0.80 (0.53 to 1.11) | 546, 0.54 (0.38 to 0.73) | 133, 0.53 (0.40 to 0.64) | 77, 0.79 (0.44 to 1.25) | 74, 0.45 (0.28 to 0.66) |
| `ALTERNATIVE_FRAMING / af_rather_than / rather than` | 477 | 177 | 0.26 (0.22 to 0.32) | 0.32 (0.27 to 0.38) | 198, 0.69 (0.50 to 0.92) | 140, 0.14 (0.10 to 0.17) | 95, 0.38 (0.28 to 0.48) | 35, 0.36 (0.22 to 0.51) | 9, 0.06 (0.01 to 0.12) |
| `ALTERNATIVE_FRAMING / af_instead_of / instead of` | 451 | 223 | 0.25 (0.21 to 0.29) | 0.32 (0.27 to 0.37) | 135, 0.47 (0.37 to 0.58) | 121, 0.12 (0.10 to 0.15) | 146, 0.58 (0.45 to 0.72) | 31, 0.32 (0.16 to 0.51) | 18, 0.11 (0.05 to 0.18) |
| `TRICOLON / tricolon / figure` | 481 | 219 | 0.26 (0.23 to 0.30) | 0.30 (0.25 to 0.36) | 102, 0.36 (0.28 to 0.44) | 236, 0.23 (0.19 to 0.27) | 57, 0.23 (0.15 to 0.31) | 44, 0.45 (0.25 to 0.65) | 42, 0.26 (0.17 to 0.36) |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / itself` | 448 | 204 | 0.25 (0.21 to 0.28) | 0.24 (0.21 to 0.28) | 83, 0.29 (0.21 to 0.37) | 232, 0.23 (0.19 to 0.28) | 87, 0.34 (0.26 to 0.42) | 16, 0.16 (0.07 to 0.25) | 30, 0.18 (0.12 to 0.25) |
| `BORROWED_RIGOUR / - / -` | 244 | 118 | 0.13 (0.10 to 0.16) | 0.17 (0.13 to 0.23) | 55, 0.19 (0.14 to 0.25) | 105, 0.10 (0.05 to 0.15) | 44, 0.17 (0.11 to 0.24) | 34, 0.35 (0.16 to 0.63) | 6, 0.04 (0.01 to 0.06) |
| `CONSULTANT_REGISTER / - / -` | 258 | 129 | 0.14 (0.11 to 0.18) | 0.15 (0.12 to 0.19) | 31, 0.11 (0.06 to 0.17) | 138, 0.14 (0.09 to 0.19) | 49, 0.19 (0.13 to 0.28) | 17, 0.17 (0.07 to 0.31) | 23, 0.14 (0.08 to 0.21) |
| `CORRECTIVE_CONTRAST / cc_coordinated / not X but Y` | 220 | 147 | 0.12 (0.10 to 0.14) | 0.13 (0.11 to 0.16) | 56, 0.20 (0.14 to 0.25) | 88, 0.09 (0.06 to 0.11) | 56, 0.22 (0.17 to 0.28) | 10, 0.10 (0.04 to 0.19) | 10, 0.06 (0.02 to 0.12) |
| `EMPTY_FRAME / - / -` | 180 | 110 | 0.10 (0.08 to 0.12) | 0.11 (0.08 to 0.15) | 42, 0.15 (0.09 to 0.22) | 77, 0.08 (0.06 to 0.09) | 41, 0.16 (0.10 to 0.22) | 10, 0.10 (0.01 to 0.26) | 10, 0.06 (0.02 to 0.10) |
| `EM_DASH / - / single break` | 93 | 34 | 0.05 (0.03 to 0.08) | 0.08 (0.05 to 0.12) | 40, 0.14 (0.06 to 0.23) | 0, 0.00 (0.00 to 0.00) | 42, 0.17 (0.06 to 0.31) | 11, 0.11 (0.04 to 0.19) | 0, 0.00 (0.00 to 0.00) |
| `CORRECTIVE_CONTRAST / cc_negated_apposition / X, not Y` | 132 | 97 | 0.07 (0.06 to 0.09) | 0.08 (0.06 to 0.09) | 48, 0.17 (0.12 to 0.22) | 53, 0.05 (0.04 to 0.07) | 22, 0.09 (0.05 to 0.13) | 6, 0.06 (0.02 to 0.11) | 3, 0.02 (0.00 to 0.04) |
| `EMPHATIC_REFLEXIVE / emphatic_reflexive / themselves` | 127 | 87 | 0.07 (0.06 to 0.09) | 0.07 (0.06 to 0.09) | 34, 0.12 (0.07 to 0.16) | 53, 0.05 (0.04 to 0.07) | 27, 0.11 (0.06 to 0.16) | 3, 0.03 (0.00 to 0.06) | 10, 0.06 (0.02 to 0.10) |
| `ABSTRACT_ADVERB / abstract_adverb / potentially` | 131 | 84 | 0.07 (0.06 to 0.09) | 0.07 (0.05 to 0.08) | 37, 0.13 (0.08 to 0.18) | 64, 0.06 (0.04 to 0.10) | 22, 0.09 (0.05 to 0.12) | 4, 0.04 (0.00 to 0.08) | 4, 0.02 (0.00 to 0.06) |
| `ABSTRACT_ADVERB / abstract_adverb / naturally` | 36 | 17 | 0.02 (0.01 to 0.03) | 0.07 (0.03 to 0.10) | 2, 0.01 (0.00 to 0.02) | 0, 0.00 (0.00 to 0.00) | 3, 0.01 (0.00 to 0.03) | 31, 0.32 (0.15 to 0.50) | 0, 0.00 (0.00 to 0.00) |
| `VAGUE_QUANTIFIER / - / -` | 113 | 75 | 0.06 (0.05 to 0.08) | 0.06 (0.05 to 0.08) | 23, 0.08 (0.05 to 0.12) | 56, 0.06 (0.04 to 0.08) | 24, 0.09 (0.05 to 0.15) | 3, 0.03 (0.00 to 0.08) | 7, 0.04 (0.01 to 0.08) |
| `FRAME_MARKER / - / -` | 106 | 80 | 0.06 (0.05 to 0.07) | 0.06 (0.05 to 0.08) | 21, 0.07 (0.04 to 0.11) | 48, 0.05 (0.03 to 0.06) | 26, 0.10 (0.06 to 0.15) | 3, 0.03 (0.00 to 0.08) | 8, 0.05 (0.02 to 0.09) |
| `PARTICIPIAL_TAIL / participial_tail / make` | 82 | 61 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.07) | 22, 0.08 (0.05 to 0.11) | 29, 0.03 (0.02 to 0.04) | 25, 0.10 (0.06 to 0.14) | 4, 0.04 (0.00 to 0.10) | 2, 0.01 (0.00 to 0.03) |
| `PARTICIPIAL_TAIL / participial_tail / allow` | 90 | 59 | 0.05 (0.04 to 0.06) | 0.05 (0.04 to 0.06) | 20, 0.07 (0.03 to 0.12) | 42, 0.04 (0.02 to 0.06) | 21, 0.08 (0.05 to 0.12) | 2, 0.02 (0.00 to 0.05) | 5, 0.03 (0.01 to 0.05) |
| `PARTICIPIAL_TAIL / participial_tail / use` | 123 | 85 | 0.07 (0.05 to 0.08) | 0.05 (0.04 to 0.06) | 14, 0.05 (0.03 to 0.07) | 88, 0.09 (0.07 to 0.11) | 15, 0.06 (0.03 to 0.09) | 3, 0.03 (0.00 to 0.06) | 3, 0.02 (0.00 to 0.04) |
| `HEDGE_STACK / - / -` | 79 | 55 | 0.04 (0.03 to 0.06) | 0.05 (0.03 to 0.06) | 9, 0.03 (0.01 to 0.05) | 40, 0.04 (0.03 to 0.06) | 21, 0.08 (0.04 to 0.13) | 5, 0.05 (0.01 to 0.10) | 4, 0.02 (0.00 to 0.06) |
| `PARTICIPIAL_TAIL / participial_tail / mean` | 49 | 40 | 0.03 (0.02 to 0.04) | 0.04 (0.03 to 0.06) | 7, 0.02 (0.01 to 0.05) | 10, 0.01 (0.00 to 0.02) | 15, 0.06 (0.03 to 0.09) | 2, 0.02 (0.00 to 0.08) | 15, 0.09 (0.05 to 0.14) |
| `HOLLOW_BOOSTER / - / -` | 51 | 42 | 0.03 (0.02 to 0.04) | 0.04 (0.03 to 0.05) | 21, 0.07 (0.04 to 0.11) | 8, 0.01 (0.00 to 0.01) | 18, 0.07 (0.03 to 0.11) | 4, 0.04 (0.00 to 0.09) | 0, 0.00 (0.00 to 0.00) |
| `CORRECTIVE_CONTRAST / cc_additive / not only X but also Y` | 61 | 46 | 0.03 (0.02 to 0.05) | 0.04 (0.02 to 0.05) | 26, 0.09 (0.04 to 0.15) | 20, 0.02 (0.01 to 0.03) | 10, 0.04 (0.02 to 0.07) | 2, 0.02 (0.00 to 0.05) | 3, 0.02 (0.00 to 0.04) |
| `ABSTRACT_ADVERB / abstract_adverb / specifically` | 74 | 56 | 0.04 (0.03 to 0.05) | 0.04 (0.02 to 0.05) | 11, 0.04 (0.02 to 0.07) | 46, 0.05 (0.03 to 0.06) | 8, 0.03 (0.01 to 0.05) | 2, 0.02 (0.00 to 0.06) | 7, 0.04 (0.01 to 0.08) |
| `EM_DASH / - / paired aside` | 35 | 13 | 0.02 (0.01 to 0.03) | 0.03 (0.02 to 0.06) | 24, 0.08 (0.03 to 0.15) | 0, 0.00 (0.00 to 0.00) | 4, 0.02 (0.00 to 0.04) | 7, 0.07 (0.00 to 0.17) | 0, 0.00 (0.00 to 0.00) |
| `ABSTRACT_ADVERB / abstract_adverb / additionally` | 45 | 38 | 0.02 (0.02 to 0.03) | 0.03 (0.02 to 0.05) | 12, 0.04 (0.02 to 0.07) | 14, 0.01 (0.01 to 0.02) | 11, 0.04 (0.02 to 0.07) | 5, 0.05 (0.01 to 0.10) | 3, 0.02 (0.00 to 0.05) |
| `CLOSER / - / -` | 56 | 49 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 14, 0.05 (0.03 to 0.08) | 23, 0.02 (0.01 to 0.03) | 16, 0.06 (0.03 to 0.10) | 1, 0.01 (0.00 to 0.04) | 2, 0.01 (0.00 to 0.04) |
| `ABSTRACT_ADVERB / abstract_adverb / mutually` | 46 | 26 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 15, 0.05 (0.01 to 0.10) | 18, 0.02 (0.01 to 0.03) | 6, 0.02 (0.00 to 0.05) | 3, 0.03 (0.00 to 0.06) | 4, 0.02 (0.00 to 0.06) |
| `ABSTRACT_ADVERB / abstract_adverb / partially` | 38 | 29 | 0.02 (0.01 to 0.03) | 0.03 (0.02 to 0.04) | 3, 0.01 (0.00 to 0.03) | 12, 0.01 (0.01 to 0.02) | 15, 0.06 (0.03 to 0.10) | 3, 0.03 (0.00 to 0.08) | 5, 0.03 (0.00 to 0.07) |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling / X, not Y` | 33 | 29 | 0.02 (0.01 to 0.03) | 0.03 (0.02 to 0.04) | 17, 0.06 (0.03 to 0.09) | 6, 0.01 (0.00 to 0.01) | 4, 0.02 (0.00 to 0.03) | 5, 0.05 (0.01 to 0.10) | 1, 0.01 (0.00 to 0.02) |
| `ABSTRACT_ADVERB / abstract_adverb / semantically` | 37 | 21 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.04) | 8, 0.03 (0.01 to 0.05) | 15, 0.01 (0.00 to 0.03) | 11, 0.04 (0.01 to 0.08) | 3, 0.03 (0.00 to 0.10) | 0, 0.00 (0.00 to 0.00) |
| `ABSTRACT_ADVERB / abstract_adverb / intentionally` | 34 | 27 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 8, 0.03 (0.01 to 0.05) | 16, 0.02 (0.01 to 0.03) | 7, 0.03 (0.01 to 0.05) | 3, 0.03 (0.00 to 0.08) | 0, 0.00 (0.00 to 0.00) |
| `GAPPED_ANTITHESIS / gapped_antithesis / opposed verbs` | 29 | 18 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.04) | 5, 0.02 (0.00 to 0.03) | 14, 0.01 (0.00 to 0.03) | 1, 0.00 (0.00 to 0.01) | 2, 0.02 (0.00 to 0.04) | 7, 0.04 (0.00 to 0.12) |
| `PARTICIPIAL_TAIL / participial_tail / indicate` | 33 | 21 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 23, 0.02 (0.01 to 0.04) | 0, 0.00 (0.00 to 0.00) | 3, 0.03 (0.00 to 0.06) | 5, 0.03 (0.01 to 0.06) |
| `PARTICIPIAL_TAIL / participial_tail / require` | 22 | 21 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 4, 0.01 (0.00 to 0.03) | 6, 0.01 (0.00 to 0.01) | 8, 0.03 (0.01 to 0.05) | 3, 0.03 (0.00 to 0.06) | 1, 0.01 (0.00 to 0.02) |
| `PARTICIPIAL_TAIL / participial_tail / lead` | 24 | 19 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 9, 0.03 (0.01 to 0.05) | 9, 0.01 (0.00 to 0.02) | 1, 0.00 (0.00 to 0.01) | 3, 0.03 (0.00 to 0.08) | 2, 0.01 (0.00 to 0.03) |
| `PARTICIPIAL_TAIL / participial_tail / result` | 34 | 21 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 4, 0.01 (0.00 to 0.03) | 23, 0.02 (0.01 to 0.04) | 0, 0.00 (0.00 to 0.00) | 1, 0.01 (0.00 to 0.04) | 6, 0.04 (0.00 to 0.09) |
| `ABSTRACT_ADVERB / abstract_adverb / logically` | 20 | 15 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 7, 0.01 (0.00 to 0.01) | 1, 0.00 (0.00 to 0.01) | 1, 0.01 (0.00 to 0.04) | 9, 0.06 (0.01 to 0.10) |
| `ABSTRACT_ADVERB / abstract_adverb / technically` | 25 | 19 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 9, 0.03 (0.01 to 0.06) | 4, 0.00 (0.00 to 0.01) | 12, 0.05 (0.02 to 0.08) | 0, 0.00 (0.00 to 0.00) | 0, 0.00 (0.00 to 0.00) |
| `PARTICIPIAL_TAIL / participial_tail / leave` | 23 | 17 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 3, 0.01 (0.00 to 0.02) | 13, 0.01 (0.01 to 0.02) | 2, 0.01 (0.00 to 0.02) | 5, 0.05 (0.01 to 0.11) | 0, 0.00 (0.00 to 0.00) |
| `ABSTRACT_ADVERB / abstract_adverb / formally` | 24 | 17 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 9, 0.03 (0.00 to 0.07) | 6, 0.01 (0.00 to 0.01) | 7, 0.03 (0.01 to 0.05) | 0, 0.00 (0.00 to 0.00) | 2, 0.01 (0.00 to 0.03) |
| `ABSTRACT_ADVERB / abstract_adverb / historically` | 20 | 17 | 0.01 (0.01 to 0.02) | 0.01 (0.01 to 0.02) | 9, 0.03 (0.01 to 0.05) | 5, 0.00 (0.00 to 0.01) | 6, 0.02 (0.00 to 0.05) | 0, 0.00 (0.00 to 0.00) | 0, 0.00 (0.00 to 0.00) |
| `PARTICIPIAL_TAIL / participial_tail / cause` | 21 | 16 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 2, 0.01 (0.00 to 0.02) | 13, 0.01 (0.01 to 0.02) | 3, 0.01 (0.00 to 0.03) | 0, 0.00 (0.00 to 0.00) | 3, 0.02 (0.00 to 0.05) |
| `ABSTRACT_ADVERB / abstract_adverb / cryptographically` | 24 | 17 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.02) | 0, 0.00 (0.00 to 0.00) | 20, 0.02 (0.01 to 0.04) | 0, 0.00 (0.00 to 0.00) | 0, 0.00 (0.00 to 0.00) | 4, 0.02 (0.00 to 0.05) |
| `PARTICIPIAL_TAIL / participial_tail / provide` | 20 | 16 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 4, 0.01 (0.00 to 0.03) | 12, 0.01 (0.00 to 0.02) | 3, 0.01 (0.00 to 0.03) | 0, 0.00 (0.00 to 0.00) | 1, 0.01 (0.00 to 0.02) |

### phrase

| phrase | n | documents | pooled by words (95% CI) | equal-weight (95% CI) | PEPs | IETF RFCs | Rust RFCs | RISC-V | OpenTitan |
|---|---|---|---|---|---|---|---|---|---|
| `LLM_DICTION / significant` | 330 | 151 | 0.18 (0.15 to 0.22) | 0.22 (0.17 to 0.28) | 49, 0.17 (0.11 to 0.24) | 159, 0.16 (0.11 to 0.22) | 53, 0.21 (0.14 to 0.28) | 38, 0.39 (0.21 to 0.60) | 31, 0.19 (0.06 to 0.37) |
| `LLM_DICTION / dynamic` | 353 | 123 | 0.19 (0.13 to 0.28) | 0.22 (0.15 to 0.30) | 89, 0.31 (0.10 to 0.56) | 182, 0.18 (0.09 to 0.32) | 15, 0.06 (0.03 to 0.09) | 32, 0.33 (0.13 to 0.64) | 35, 0.21 (0.14 to 0.32) |
| `EMPTY_FRAME / in other words` | 111 | 73 | 0.06 (0.05 to 0.08) | 0.07 (0.05 to 0.10) | 30, 0.11 (0.06 to 0.17) | 47, 0.05 (0.03 to 0.06) | 22, 0.09 (0.05 to 0.13) | 7, 0.07 (0.00 to 0.18) | 5, 0.03 (0.00 to 0.07) |
| `BORROWED_RIGOUR / canonical` | 57 | 30 | 0.03 (0.02 to 0.05) | 0.06 (0.03 to 0.11) | 19, 0.07 (0.03 to 0.11) | 13, 0.01 (0.00 to 0.03) | 6, 0.02 (0.00 to 0.05) | 19, 0.20 (0.05 to 0.47) | 0, 0.00 (0.00 to 0.00) |
| `LLM_DICTION / underscore` | 50 | 23 | 0.03 (0.02 to 0.04) | 0.04 (0.02 to 0.06) | 31, 0.11 (0.05 to 0.18) | 5, 0.00 (0.00 to 0.01) | 10, 0.04 (0.01 to 0.08) | 4, 0.04 (0.00 to 0.15) | 0, 0.00 (0.00 to 0.00) |
| `CONSULTANT_REGISTER / optimized` | 51 | 32 | 0.03 (0.02 to 0.04) | 0.04 (0.02 to 0.06) | 4, 0.01 (0.00 to 0.03) | 23, 0.02 (0.01 to 0.04) | 16, 0.06 (0.03 to 0.11) | 7, 0.07 (0.00 to 0.18) | 1, 0.01 (0.00 to 0.02) |
| `CONSULTANT_REGISTER / optimize` | 59 | 44 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 7, 0.02 (0.01 to 0.05) | 30, 0.03 (0.02 to 0.04) | 16, 0.06 (0.03 to 0.10) | 4, 0.04 (0.01 to 0.08) | 2, 0.01 (0.00 to 0.03) |
| `FRAME_MARKER / it is important to` | 62 | 43 | 0.03 (0.03 to 0.04) | 0.03 (0.02 to 0.05) | 10, 0.04 (0.01 to 0.07) | 36, 0.04 (0.02 to 0.05) | 8, 0.03 (0.01 to 0.06) | 3, 0.03 (0.00 to 0.08) | 5, 0.03 (0.01 to 0.06) |
| `HEDGE_STACK / may or may not` | 52 | 35 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.05) | 1, 0.00 (0.00 to 0.01) | 30, 0.03 (0.02 to 0.05) | 12, 0.05 (0.01 to 0.09) | 5, 0.05 (0.01 to 0.10) | 4, 0.02 (0.00 to 0.06) |
| `LLM_DICTION / robust` | 57 | 39 | 0.03 (0.02 to 0.04) | 0.03 (0.02 to 0.04) | 15, 0.05 (0.02 to 0.10) | 26, 0.03 (0.02 to 0.04) | 14, 0.06 (0.01 to 0.12) | 0, 0.00 (0.00 to 0.00) | 2, 0.01 (0.00 to 0.03) |
| `BORROWED_RIGOUR / idempotent` | 55 | 5 | 0.03 (0.00 to 0.07) | 0.03 (0.00 to 0.06) | 2, 0.01 (0.00 to 0.02) | 44, 0.04 (0.00 to 0.10) | 0, 0.00 (0.00 to 0.00) | 9, 0.09 (0.00 to 0.22) | 0, 0.00 (0.00 to 0.00) |
| `BORROWED_RIGOUR / well-defined` | 38 | 27 | 0.02 (0.01 to 0.03) | 0.03 (0.01 to 0.04) | 9, 0.03 (0.01 to 0.05) | 11, 0.01 (0.00 to 0.02) | 16, 0.06 (0.02 to 0.12) | 2, 0.02 (0.00 to 0.04) | 0, 0.00 (0.00 to 0.00) |
| `LLM_DICTION / essential` | 43 | 32 | 0.02 (0.02 to 0.03) | 0.02 (0.01 to 0.03) | 7, 0.02 (0.01 to 0.05) | 26, 0.03 (0.01 to 0.04) | 7, 0.03 (0.01 to 0.05) | 2, 0.02 (0.00 to 0.06) | 1, 0.01 (0.00 to 0.02) |
| `VAGUE_QUANTIFIER / a variety of` | 38 | 31 | 0.02 (0.01 to 0.03) | 0.02 (0.01 to 0.03) | 4, 0.01 (0.00 to 0.03) | 20, 0.02 (0.01 to 0.03) | 7, 0.03 (0.01 to 0.05) | 0, 0.00 (0.00 to 0.00) | 7, 0.04 (0.01 to 0.08) |
| `BORROWED_RIGOUR / non-trivial` | 23 | 19 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 14, 0.05 (0.02 to 0.08) | 1, 0.00 (0.00 to 0.00) | 4, 0.02 (0.00 to 0.04) | 3, 0.03 (0.00 to 0.08) | 1, 0.01 (0.00 to 0.02) |
| `HOLLOW_BOOSTER / notably,` | 25 | 22 | 0.01 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 8, 0.03 (0.01 to 0.05) | 4, 0.00 (0.00 to 0.01) | 10, 0.04 (0.02 to 0.07) | 3, 0.03 (0.00 to 0.07) | 0, 0.00 (0.00 to 0.00) |
| `VAGUE_QUANTIFIER / numerous` | 30 | 22 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 16, 0.02 (0.01 to 0.03) | 10, 0.04 (0.01 to 0.07) | 2, 0.02 (0.00 to 0.06) | 0, 0.00 (0.00 to 0.00) |
| `LLM_DICTION / comprehensive` | 28 | 23 | 0.02 (0.01 to 0.02) | 0.02 (0.01 to 0.02) | 9, 0.03 (0.00 to 0.07) | 12, 0.01 (0.01 to 0.02) | 4, 0.02 (0.00 to 0.04) | 0, 0.00 (0.00 to 0.00) | 3, 0.02 (0.00 to 0.04) |
| `CONSULTANT_REGISTER / leverage` | 33 | 29 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 6, 0.02 (0.01 to 0.04) | 22, 0.02 (0.01 to 0.03) | 2, 0.01 (0.00 to 0.02) | 1, 0.01 (0.00 to 0.04) | 2, 0.01 (0.00 to 0.03) |
| `CONSULTANT_REGISTER / leverages` | 34 | 21 | 0.02 (0.01 to 0.03) | 0.01 (0.01 to 0.02) | 2, 0.01 (0.00 to 0.02) | 25, 0.02 (0.01 to 0.04) | 2, 0.01 (0.00 to 0.02) | 0, 0.00 (0.00 to 0.00) | 5, 0.03 (0.01 to 0.07) |
| `LLM_DICTION / crucial` | 20 | 18 | 0.01 (0.01 to 0.02) | 0.01 (0.00 to 0.01) | 4, 0.01 (0.00 to 0.03) | 12, 0.01 (0.01 to 0.02) | 4, 0.02 (0.00 to 0.03) | 0, 0.00 (0.00 to 0.00) | 0, 0.00 (0.00 to 0.00) |
| `LLM_DICTION / seamless` | 24 | 8 | 0.01 (0.00 to 0.03) | 0.01 (0.00 to 0.01) | 1, 0.00 (0.00 to 0.01) | 22, 0.02 (0.00 to 0.06) | 0, 0.00 (0.00 to 0.00) | 0, 0.00 (0.00 to 0.00) | 1, 0.01 (0.00 to 0.02) |

## Pool against arXiv pre-window bodies (H2)

Construction and pattern rows with at least 20 findings in the pool and in the arXiv pre-window bodies (all sections). A pattern that is its construction's only pattern is left out (same counts as the construction row). The ratio is the equal-weight pool rate over the arXiv rate.

| row | pool n | pool rate (95% CI) | arXiv n | arXiv rate (95% CI) | pool over arXiv (95% CI) | interval |
|---|---|---|---|---|---|---|
| `HEDGE_STACK` | 79 | 0.05 (0.03 to 0.06) | 62 | 0.01 (0.01 to 0.02) | 3.69 (2.16 to 6.17) | above 1 |
| `EMPHATIC_REFLEXIVE` | 576 | 0.32 (0.28 to 0.36) | 592 | 0.12 (0.10 to 0.13) | 2.66 (2.24 to 3.17) | above 1 |
| `ALTERNATIVE_FRAMING` | 934 | 0.65 (0.58 to 0.72) | 1491 | 0.30 (0.28 to 0.32) | 2.16 (1.91 to 2.44) | above 1 |
| `CORRECTIVE_CONTRAST` | 473 | 0.29 (0.26 to 0.33) | 749 | 0.15 (0.14 to 0.16) | 1.93 (1.65 to 2.25) | above 1 |
| `GAPPED_ANTITHESIS` | 36 | 0.02 (0.01 to 0.04) | 81 | 0.02 (0.01 to 0.02) | 1.49 (0.70 to 2.55) | spans 1 |
| `EMPTY_FRAME` | 180 | 0.11 (0.08 to 0.15) | 436 | 0.09 (0.08 to 0.10) | 1.25 (0.90 to 1.72) | spans 1 |
| `ABSTRACT_ADVERB` | 947 | 0.63 (0.56 to 0.70) | 2662 | 0.54 (0.50 to 0.57) | 1.18 (1.03 to 1.34) | above 1 |
| `FRAME_MARKER` | 106 | 0.06 (0.05 to 0.08) | 335 | 0.07 (0.06 to 0.08) | 0.90 (0.67 to 1.19) | spans 1 |
| `TRICOLON` | 4575 | 2.83 (2.67 to 2.99) | 16114 | 3.24 (3.12 to 3.37) | 0.87 (0.81 to 0.93) | below 1 |
| `EM_DASH` | 139 | 0.13 (0.08 to 0.18) | 771 | 0.15 (0.11 to 0.21) | 0.82 (0.50 to 1.29) | spans 1 |
| `HOLLOW_BOOSTER` | 51 | 0.04 (0.03 to 0.05) | 240 | 0.05 (0.04 to 0.06) | 0.80 (0.52 to 1.14) | spans 1 |
| `BORROWED_RIGOUR` | 244 | 0.17 (0.13 to 0.23) | 1270 | 0.26 (0.23 to 0.29) | 0.67 (0.49 to 0.90) | below 1 |
| `PARTICIPIAL_TAIL` | 1182 | 0.71 (0.64 to 0.79) | 6297 | 1.27 (1.18 to 1.36) | 0.56 (0.49 to 0.64) | below 1 |
| `CLOSER` | 56 | 0.03 (0.02 to 0.04) | 346 | 0.07 (0.06 to 0.08) | 0.45 (0.31 to 0.64) | below 1 |
| `LLM_DICTION` | 1058 | 0.62 (0.51 to 0.75) | 7283 | 1.46 (1.37 to 1.56) | 0.42 (0.35 to 0.51) | below 1 |
| `VAGUE_QUANTIFIER` | 113 | 0.06 (0.05 to 0.08) | 1203 | 0.24 (0.22 to 0.26) | 0.25 (0.19 to 0.33) | below 1 |
| `CONSULTANT_REGISTER` | 258 | 0.15 (0.12 to 0.19) | 4267 | 0.86 (0.78 to 0.94) | 0.18 (0.14 to 0.22) | below 1 |
| `CORRECTIVE_CONTRAST / cc_negated_apposition` | 132 | 0.08 (0.06 to 0.09) | 78 | 0.02 (0.01 to 0.02) | 4.94 (3.56 to 7.06) | above 1 |
| `CORRECTIVE_CONTRAST / cc_parallel_sibling` | 37 | 0.03 (0.02 to 0.04) | 44 | 0.01 (0.01 to 0.01) | 3.35 (1.89 to 5.40) | above 1 |
| `ALTERNATIVE_FRAMING / af_rather_than` | 477 | 0.32 (0.27 to 0.38) | 509 | 0.10 (0.09 to 0.12) | 3.17 (2.55 to 3.90) | above 1 |
| `CORRECTIVE_CONTRAST / cc_coordinated` | 220 | 0.13 (0.11 to 0.16) | 256 | 0.05 (0.04 to 0.06) | 2.60 (2.08 to 3.24) | above 1 |
| `ALTERNATIVE_FRAMING / af_instead_of` | 451 | 0.32 (0.27 to 0.37) | 976 | 0.20 (0.18 to 0.21) | 1.63 (1.33 to 1.96) | above 1 |
| `TRICOLON / tricolon` | 4569 | 2.83 (2.66 to 2.99) | 16111 | 3.24 (3.12 to 3.37) | 0.87 (0.81 to 0.93) | below 1 |
| `CORRECTIVE_CONTRAST / cc_additive` | 61 | 0.04 (0.02 to 0.05) | 363 | 0.07 (0.06 to 0.08) | 0.52 (0.32 to 0.74) | below 1 |

19 of 24 rows have a pool over arXiv interval that excludes 1 (10 above, 9 below). H2 needs at least a quarter: holds.

## Author against pool (H3)

Construction and pattern rows with at least 20 findings in the author's specifications and in the pool. The ratio is the author's rate over the equal-weight pool rate; the author side resamples the author's files.

| row | author n | author rate (95% CI) | pool n | pool rate (95% CI) | author over pool (95% CI) | interval |
|---|---|---|---|---|---|---|
| `EM_DASH` | 133 | 1.65 (0.54 to 2.75) | 139 | 0.13 (0.08 to 0.18) | 12.91 (3.92 to 25.57) | above 1 |
| `TRICOLON` | 272 | 3.37 (2.76 to 3.97) | 4575 | 2.83 (2.67 to 2.99) | 1.19 (0.97 to 1.42) | spans 1 |
| `PARTICIPIAL_TAIL` | 65 | 0.80 (0.54 to 1.25) | 1182 | 0.71 (0.64 to 0.79) | 1.13 (0.73 to 1.78) | spans 1 |
| `LLM_DICTION` | 36 | 0.45 (0.18 to 0.85) | 1058 | 0.62 (0.51 to 0.75) | 0.72 (0.29 to 1.43) | spans 1 |
| `ABSTRACT_ADVERB` | 33 | 0.41 (0.24 to 0.62) | 947 | 0.63 (0.56 to 0.70) | 0.65 (0.37 to 1.00) | below 1 |
| `ALTERNATIVE_FRAMING` | 20 | 0.25 (0.13 to 0.37) | 934 | 0.65 (0.58 to 0.72) | 0.38 (0.20 to 0.58) | below 1 |
| `TRICOLON / tricolon` | 272 | 3.37 (2.76 to 3.97) | 4569 | 2.83 (2.66 to 2.99) | 1.19 (0.97 to 1.42) | spans 1 |

7 construction and pattern rows reach 20 findings in the author's specifications; 7 of them also reach 20 in the pool. 4 of 7 author over pool intervals contain 1. H3 needs at least three quarters: fails.

## Sources against the pool (H4)

Constructions with at least 20 findings in every source. Each source cell is rate (95% CI); the last column names the sources whose interval excludes the equal-weight pooled rate.

| construction | equal-weight pool (95% CI) | PEPs | IETF RFCs | Rust RFCs | RISC-V | OpenTitan | outside |
|---|---|---|---|---|---|---|---|
| `ABSTRACT_ADVERB` | 0.63 (0.56 to 0.70) | 0.73 (0.56 to 0.89) | 0.38 (0.32 to 0.47) | 0.81 (0.67 to 0.95) | 0.87 (0.62 to 1.12) | 0.37 (0.25 to 0.48) | IETF RFCs, Rust RFCs, OpenTitan |
| `ALTERNATIVE_FRAMING` | 0.65 (0.58 to 0.72) | 1.17 (0.98 to 1.42) | 0.26 (0.22 to 0.30) | 0.96 (0.81 to 1.12) | 0.68 (0.52 to 0.88) | 0.17 (0.09 to 0.24) | PEPs, IETF RFCs, Rust RFCs, OpenTitan |
| `LLM_DICTION` | 0.62 (0.51 to 0.75) | 0.80 (0.53 to 1.11) | 0.54 (0.38 to 0.73) | 0.53 (0.40 to 0.64) | 0.79 (0.44 to 1.25) | 0.45 (0.28 to 0.66) | none |
| `PARTICIPIAL_TAIL` | 0.71 (0.64 to 0.79) | 0.83 (0.70 to 0.95) | 0.56 (0.49 to 0.64) | 0.77 (0.64 to 0.90) | 0.71 (0.52 to 0.98) | 0.69 (0.49 to 0.90) | IETF RFCs |
| `TRICOLON` | 2.83 (2.67 to 2.99) | 2.71 (2.29 to 3.26) | 2.38 (2.23 to 2.53) | 2.01 (1.75 to 2.30) | 4.20 (3.67 to 4.67) | 2.86 (2.61 to 3.15) | IETF RFCs, Rust RFCs, RISC-V |

4 of 5 constructions have at least one source outside the pooled rate. H4 needs at least half: holds.
