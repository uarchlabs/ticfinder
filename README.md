# ticfinder

Finds recurring LLM prose constructions in markdown or plain text, so a human
can decide what to cut.

ticfinder is not a grammar checker. Everything it flags is legitimate English.
The premise is that these constructions *cluster* in LLM generated prose, and
the clustering is what breaks reader flow.

## Install

```bash
pip install spacy
python3 -m spacy download en_core_web_md
```

Use `md`, not `sm`. On `a bug wrapped in an excuse trenchcoat`, the small model
attaches `trenchcoat` as `advmod` of `excuse`; `md` gets the compound right.
Parse quality is upstream of every structural detector. `en_core_web_trf` is
better still if you can afford the install.

## Use

```bash
python3 ticfinder.py article.md
python3 ticfinder.py posts/*.md --stats
python3 ticfinder.py article.md --only NEG_ANTITHESIS,PARTICIPIAL_TAIL
python3 ticfinder.py article.md --model sm     # sm/md/lg/trf shorthand
python3 ticfinder.py posts/*.md --json findings.json
python3 ticfinder.py posts/*.md --summary       # counts only, no findings
```

Findings are colour-coded by confidence: red = high, yellow = medium,
grey = low. Read the high ones, skim the rest.

Colour is ANSI escapes, and it switches off automatically when stdout is not a
terminal, so `> out.log` and `| less` come out clean. `NO_COLOR` and
`TERM=dumb` are honoured too. `--plain` forces it off, `--colour` forces it on.

Note that `--ascii` does *not* remove colour: escape codes are themselves
ASCII. The two flags do different jobs -- `--ascii` handles the text, `--plain`
handles the formatting.

## What it looks for

Structural (dependency parse):

| id | what |
|---|---|
| `CORRECTIVE_CONTRAST` | rejects X, asserts Y — six surface forms |
| `NEG_ESCALATION` | didn't X, and couldn't have |
| `ABSTRACT_ADVERB` | structurally unable, fundamentally different |
| `EMPHATIC_REFLEXIVE` | the document itself |
| `PARTICIPIAL_TAIL` | `, making it easier to…` tacked on the end |
| `TRICOLON` | three-part coordination |
| `DISGUISE_METAPHOR` | X wrapped in / wearing / masquerading as Y |

Phrasal (token patterns):

| id | what |
|---|---|
| `FRAME_MARKER` | throat-clearing, advance organizers |
| `HOLLOW_BOOSTER` | unearned assertions of importance |
| `CLOSER` | summative wrap-ups |
| `TECH_METAPHOR` | load-bearing, blast radius, heavy lifting |
| `ELEVATED_DICTION` | delve, tapestry, realm, testament |
| `HEDGE_STACK` | two hedges on one claim |
| `EM_DASH` | split by function; pivot uses ranked high |

## Output encoding

By default output is UTF-8, and flagged em dashes appear as em dashes. Pass
`--ascii` for 7-bit output: the tool's own separators become ASCII and quoted
source text is transliterated (em dash to `--`, curly quotes to straight, and
so on), with anything unmapped escaped rather than dropped.

ASCII mode also switches on automatically when `sys.stdout.encoding` isn't
UTF-8, which is what happens under `PYTHONIOENCODING=ascii`, some CI runners,
and slim Docker images. Without that guard, printing a flagged em dash raises
`UnicodeEncodeError` and kills the run.

`--json` always writes UTF-8 to disk; `--ascii` additionally sets
`ensure_ascii` so the file itself stays 7-bit.

## HTML report

```bash
python3 ticfinder.py posts/*.md --html report/
```

Writes one self-contained HTML file per article: source on the left with
findings highlighted in place, list on the right. Click either side to jump to
the other. Uncheck a construction in the legend to hide it everywhere, which is
how you read past a noisy detector without editing config.

Highlight colour is confidence, not severity: rust = high, amber = medium,
grey = low.

Overlapping spans are resolved rather than nested -- highest confidence wins,
then longest. The header reports how many were suppressed, so a large number
there means two detectors are firing on the same text and one of them probably
should not be.

Single file, no JS dependencies, no network. Opens from `file://`.

## Reading the output

Each file gets a header, an aligned count table sorted by frequency, then the
findings themselves. Output wraps to your terminal width (clamped 60-120), so
nothing runs off the screen or into a hard-to-read wrap.

Findings are **grouped by construction**, most frequent first, so each header
and note is printed once rather than once per hit. In positional order a note
reprints every time its construction recurs -- on a real 3,500-word article
that was 21% of the whole report.

| flag | effect |
|---|---|
| `--compact` | one line per finding: id, line, construction, text |
| `--by-position` | document order instead of grouped |
| `--context` | show the surrounding sentence, windowed on the match |
| `--explain` | full note per construction, not just its first line |
| `--summary` | count table only, no findings |

By default only the first sentence of each note is shown; `--explain` gives the
rest. Context is off by default because file and line already point your editor
at it. When shown, the sentence is windowed *around* the match rather than
truncated from its start, so the flagged text stays visible.

Pass more than one file and a combined `ALL FILES` table is printed at the end
with percentage shares. That is the view that tells you which two or three
constructions dominate your writing -- which is where editing effort actually
pays off.

## Rates, not counts

A single tricolon is good writing. Six on a page is a tic. Use `--stats` and
watch `per_1000_words`. On a planted sample this scores ~109/1k; on plain human
technical prose, ~9/1k. Your own numbers will differ — calibrate on your
pre-LLM writing if you have any.

## Waivers

Findings carry a short id. Review a document, fix what needs fixing, waive the
rest:

```bash
./tools/tic_finder.py posts/BLOG_bpu_13.md --waive 46df5f,b695e7
```

Waived findings are hidden on later runs, so the reported count is work you
have not looked at yet. Zero means covered.

```
posts/BLOG_bpu_13.md
  1,240 words * 4 findings (3.2 per 1k words)
  3 waived, 1 stale (no longer in the text) [posts/BLOG_bpu_13.waivers.json]
```

| flag | effect |
|---|---|
| `--waive IDS` | waive by id, or `all` for everything shown |
| `--unwaive IDS` | remove waivers, or `all` |
| `--show-waived` | include waived findings in output |
| `--waiver-dir DIR` | keep waiver files in DIR instead of beside the source |
| `--waiver-file F` | explicit path; single input file only |
| `--no-waivers` | ignore waiver files entirely |

The waiver path is derived from the source stem -- `BLOG_bpu_13.md` becomes
`BLOG_bpu_13.waivers.json` -- so there is nothing to type and nothing to
mistype. A mistyped explicit path would silently create an empty baseline and
look exactly like lost work.

### The waiver file

```json
{
  "generated_by": "ticfinder",
  "source": "posts/BLOG_bpu_13.md",
  "waivers": {
    "46df5f": {
      "construction": "TRICOLON",
      "line_when_waived": 1,
      "pattern": "tricolon",
      "text": "fast, correct, and easy to extend"
    },
    "b695e7": {
      "construction": "BORROWED_RIGOUR",
      "line_when_waived": 4,
      "pattern": "",
      "text": "ground truth"
    }
  }
}
```

Only the keys of `waivers` are load-bearing -- they are the finding ids, and
matching is done on those alone. Everything inside each entry is there so the
file is readable six months later: `construction` and `pattern` say which rule
fired, `text` shows what was waived, and `line_when_waived` records where it
was at the time. That line number is **not** used for matching and will go
stale as the document changes; it is a breadcrumb, not a key.

`source` is checked on load and warns on mismatch. `pattern` is empty for
findings that come from phrase lists rather than structural detectors.

The file is safe to hand-edit -- delete an entry to unwaive it, or add one if
you know the id. An empty `waivers` object is written rather than the file
being removed, because "reviewed, nothing waived" and "never looked at" are
different states.

### Why ids are content hashes

The id hashes the construction, pattern, matched text and surrounding
sentence, whitespace-normalised. It deliberately excludes line and character
offsets, so:

- editing one paragraph does not invalidate waivers in another
- rewrapping a paragraph keeps its waivers
- actually changing a flagged sentence *does* drop the waiver, which is right --
  it is a different sentence now

Waivers whose text has since disappeared are reported as **stale** rather than
deleted, so the file does not silently accumulate dead entries.

The waiver file records the source path it was written for and warns on
mismatch, which covers the case of two directories holding the same filename.

## When a rule is too noisy

Three levers, in order of bluntness.

**Mute an id.** `--off ALTERNATIVE_FRAMING` drops it entirely. Repeatable as a
comma list.

**Mute one pattern.** `--off af_less_than` drops a single pattern and leaves
the rest of its construction working.

**Find out what to mute.** `--patterns` reports hits per pattern rather than
per construction. A pattern with a large share is the first thing to check
when the tool feels noisy -- it is usually one weak query, not the whole
inventory.

Patterns can carry their own confidence, overriding their construction's,
because base rates inside one rhetorical family vary enormously. `not X but Y`
is rare and diagnostic; a bare `rather than` is ordinary English. Reporting
them at the same confidence makes the good rules look unreliable.

That is also why `rather than` / `instead of` / `less...than` live under
`ALTERNATIVE_FRAMING` rather than `CORRECTIVE_CONTRAST`. Same rhetorical
family, completely different base rate. **Group ids by precision, not by
rhetorical neatness** -- an id is the unit you mute, so anything you would want
to mute separately needs its own id.

## Skipping regions

Boilerplate you never edit -- author bios, licence blocks, standard footers --
can be fenced off:

```markdown
<!-- ticfinder_off -->
*Jeff Nye is a microprocessor architect with 35 years of experience spanning
performance modeling, RTL implementation, and architecture...*
<!-- ticfinder_on -->
```

Everything between the markers is invisible to the tool: no findings, and the
text does not count toward the per-1000-word denominator either. Line numbers
outside the region stay correct, because the region is blanked in place rather
than removed.

`<!-- ticfinder_skip -->` skips just the next blank-line-delimited block, which
is less typing for a single paragraph. An unclosed `ticfinder_off` runs to the
end of the file -- useful when all your boilerplate is at the bottom.

`ticfinder_off`, `ticfinder-off` and `ticfinder off` are all accepted, in any
case. The header reports how many regions were skipped, so a fence you forgot
to close is visible rather than silent.

## Phrase lists

Word and phrase lists live in JSON, not in the code. Drop
`ticfinder-phrases.json` in the working directory or beside the script and it
is picked up automatically; `--phrases FILE` overrides (repeatable),
`--no-phrases` disables.

```json
{"constructions": [
  {"id": "BORROWED_RIGOUR",
   "label": "Borrowed technical rigour",
   "note": "Ask whether the technical sense is actually intended.",
   "confidence": "low",
   "match_lemma": false,
   "phrases": ["ground truth", "threat model", "non-trivial"]}
]}
```

Two shorthands are accepted: a bare list of strings (everything becomes
`OVERUSED_PHRASE`), or a mapping of id to phrase list.

`match_lemma: true` matches inflected forms, so `leverage` also catches
`leveraged` and `leveraging`. It costs a full parse of each phrase at startup,
so use it for single words and leave it off for fixed multi-word phrases.

Group by *why* a phrase is a problem rather than alphabetically. Each group is
its own construction id with its own row in the summary and its own mute, so
the grouping determines what you can act on. The shipped file has five:
`BORROWED_RIGOUR`, `CONSULTANT_REGISTER`, `LLM_DICTION`, `EMPTY_FRAME`,
`VAGUE_QUANTIFIER`.

## Adding a construction

Structural ones are a function returning `(span, subtype)` pairs:

```python
@construction("MY_TIC", "Human-readable label",
              "What to check before cutting it.", "high")
def my_tic(doc, nlp):
    out = []
    for tok in doc:
        if tok.dep_ == "advcl" and tok.lemma_ == "suggest":
            out.append((doc[tok.left_edge.i:tok.right_edge.i + 1], "variant"))
    return out
```

Phrasal ones are entries in `PHRASE_PATTERNS` using spaCy `Matcher` syntax.

### Constructions vs patterns

A **construction** is a rhetorical move with a stable id. A **pattern** is one
executable query that finds one of its surface forms. One construction owns
many patterns:

```python
@construction("CORRECTIVE_CONTRAST", "Corrective contrast", "...", "high")
def cc_coordinated(doc, nlp): ...      # not X but Y

@pattern("CORRECTIVE_CONTRAST")
def cc_parallel_sibling(doc, nlp): ... # X, not Y
```

`CORRECTIVE_CONTRAST` currently has six patterns because the same move parses
six different ways -- coordinated with `but`, two-clause cleft (including
across a sentence boundary), asyndetic sibling phrases, negated apposition,
`rather than` / `instead of`, and `less...than`. Findings report which pattern
fired in brackets, so a subtype that turns out to be noisy can be removed
without touching the id.

This split is the point. When phrasing drifts, add patterns and keep the id --
counts, mutes and history all stay continuous.

Two rules worth keeping:
- The **note** field says what to check, not "this is bad". Every construction
  is legitimate somewhere.
- One construction, many patterns. When surface forms drift, add patterns and
  keep the id. The id is what you report on and what you mute.

## Known limits

- Markdown masking blanks code blocks, inline code, link targets, tables,
  blockquotes and HTML, preserving offsets so line numbers stay accurate.
- `TRICOLON` and `ELEVATED_DICTION` are noisy by design; they are rate signals.
- Licensing checks are not implemented. `NEG_ANTITHESIS` cannot yet tell you
  whether X was ever actually claimed earlier in the document. That check is
  the obvious next thing to build and the thing that would most improve
  precision.

