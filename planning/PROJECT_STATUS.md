<!-- SPDX-License-Identifier: Apache-2.0                        -->
<!-- Copyright (c) 2026 Jeff Nye, uarchlabs.com                 -->
<!-- SPDX-FileCopyrightText: 2026 Jeff Nye <jeff@uarchlabs.com> -->
# Project Status -- ticfinder
```
 FILE:    PROJECT_STATUS.md
 SOURCE:  various
 STATUS:  DRAFT
 UPDATED: 2026-11-27
 CONTACT: Jeff Nye
```

This contains status and technical debt for the ticfinder 
development. For the most part this is soley technical
debt.

So far there are no PA sessions associated w/ ticfinder, this is a Claude Code
only development.

---

## Module Status

This is a placeholder at present.

| Module  | Status      | Tests             | Notes                            |
|---------|-------------|-------------------|----------------------------------|
|         |             |                   |                                  |


---

## Technical Debt

Closed rows are in CLOSED_TECH_DEBT.md, with their numbers; a row
moves there in the planning update that closes it.

| #   | Item                   | Comments                                              |
|-----|------------------------|-------------------------------------------------------|
| 1   | specs under-masking | Code the masker still keeps in `$WRITING_SAMPLES` after TF-003 phase 1: whole-line comment and rule lines (`//...`, `# ----`, about half of the remaining misses), assembly lines, bit-encoding rows, pseudocode. About 190 code lines came back with the restored indented prose (estimate from 7 of 40 sampled). Blocks trusting spec counts for the LRs in roadmap 5.3. Evidence: roadmap s.10, phase 1. Close with test rows written without quoting the specs, then a respot-check. |
| 2   | unverified citation in `tricolon()` | The isocolon comment cites "Morari's threshold" (matching POS pairs over 55% of the span). Source not confirmed. Check it or remove the attribution before any published write-up uses it. |
| 3   | `harvest.py` has no `--no-code-mask` | It follows `ticfinder.CODE_MASK`, so a harvest with the code masker off needs a code edit. Deferred in TF-002. |
| 4   | `trf` parser and GPU use unmeasured | TF-015 H5: `en_core_web_trf` gives the relative-clause arc on 29 of 33 positive `OBJECT_RELATIVE` and `TRAILING_LIGHT_VERB` test rows, `md` on 19. Evidence is short test rows only. On the README, on one CPU thread, `trf` took 117 s and `md` 13 s, about 10 times slower per word; the arXiv run would take about 20 hours. Only 5 of the 24 README findings keep their fingerprint under `trf`, so making it the run model would stale most waivers and void every measured LR and level. This machine has no NVIDIA GPU. A GPU path needs the CUDA build of PyTorch and `spacy.prefer_gpu()`, and CPU and GPU parses are not checked for equality. Close in order: (1) parse the TF-015 phase 2 readings with `trf` on the CPU and count the false hits it rejects and the real ones it keeps; (2) if it helps, an optional `trf` check on `OBJECT_RELATIVE` candidates only, with `md` still running the document, so fingerprints and levels stay; (3) a `--gpu` option only if `trf` becomes the whole-document model, after a CPU and GPU parse comparison on the test rows and one blog. Or record a null result. Evidence: roadmap s.22, phase 3. |

---

## Open Items

| Priority | Item                                    | Status              |
|----------|-----------------------------------------|---------------------|
| low | clause-list hypothesis (`TRICOLON`): rewritten findings are mostly lists of clauses, accepted ones mostly lists of noun phrases. Found post hoc in TF-003 phase 2. Clause series: 15 of 19 rewritten, 44 of 84 accepted (prec* 0.25). Noun-phrase series: 4 rewritten, 40 accepted (prec* 0.09; only 4 rewritten, so weak). Evidence: `notes/tricolon-referent-null-2026-11-18.md`, roadmap s.10. | Untested. Test on labels harvested after 2026-11-18, with the cut fixed before looking. If it holds: a `[clausal]` subtype (no waiver moves) or a `tricolon_clausal` pattern (mutable on its own, moved waivers go stale), as in TF-003 options (a)/(b). If not: record a null result and close. |
| -   | `harvest.py --by-subtype` | Closed: delivered in TF-004 with `--summary-only` (roadmap s.11). |

---

---

---

## Prompt Generation Guide

These do not exist yet for ticfinder, they will in the near future

See PROJECT_CORE.md, Prompt generation rules.
For known failure modes see ANTIPATTERNS.md.

---

### Shared planning documents

planning/PROJECT_STATUS.md    this file

