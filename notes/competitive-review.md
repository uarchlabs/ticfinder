# Competitive review and feature backlog

Date: 2026-09-08
Source: reading four competing Vale style packages at the commit
current on that date, plus the prose-linting and AI-detection
literature. Rule counts are from the cloned repositories, not their
READMEs.

## The field

| project | rules | detection |
|---|---|---|
| vale-ai-tells | 130 + 16 experimental | 142 existence, 9 script (Tengo), 7 sequence (POS), 3 metric, 2 substitution, 2 occurrence, 1 capitalization |
| deslop | 34 | 28 existence, 4 occurrence, 2 substitution |
| vale-llm-slop | 19 | 19 existence, 4 occurrence, 3 sequence, 2 substitution |
| slopster | 6 + agent skill + slop-diff | 5 existence, 1 substitution |
| ticfinder | 12 constructions, 6 phrase groups | spaCy dependency parse + Matcher |

Roughly 85% of the largest ruleset is `existence`, which is regex.
Vale has twelve extension points and only `sequence` touches
linguistics, reading POS tags one sentence at a time. Nothing in the
field parses dependencies.

Repos:
- https://github.com/tbhb/vale-ai-tells
- https://github.com/JMill/deslop
- https://github.com/Syntaf/vale-llm-slop
- https://github.com/t0ddharris/slopster

## Convergent taxonomy

Independently arrived at, which is evidence the constructions are real
rather than one editor's preferences.

| ticfinder | elsewhere |
|---|---|
| BORROWED_RIGOUR | deslop `BorrowedRigor` (same name) |
| CORRECTIVE_CONTRAST | ai-tells `ContrastiveNegation`, `ContrastiveFormulas`, `NegatedPair`; deslop `AntitheticalPair`, `NotJustScaffold`; llm-slop `NegativeParallelism`; slopster `AISlop` |
| TRICOLON | ai-tells `VerbTricolon`, `VerbTricolonDensity`; llm-slop `Tricolon` |
| HEDGE_STACK | deslop `HedgeCascade`; ai-tells `StackedHedges` |
| CLOSER | deslop `HollowCloser`; ai-tells `ClosingPleasantries`, `ConclusionMarkers` |
| FRAME_MARKER | deslop `OpenerCliche`, `AssistantOpener`; ai-tells `OpeningCliches` |
| EM_DASH | all four |
| LLM_DICTION | all four |

## Backlog, ranked

### 1. Document-level uniformity statistics

The one whole category ticfinder lacks. vale-ai-tells measures
sentence-length variance, paragraph-length variance, sentence-start
entropy, sentence-start repetition, transition repetition and content
duplication, in Tengo scripts that split a document by heading first
so format diversity across sections does not mask uniformity within
one.

The signal is the absence of variance, not the presence of a
construction, and it is the best-supported signal in the stylometry
literature. ticfinder already computes `mean_sentence_len` and
`sentence_len_stdev` and emits them in the JSON header; nothing reads
them. This is the highest-value addition and much of the groundwork
exists.

Note their preprocessing: strip code fences, HTML comments, MDX
expressions, import/export lines, frontmatter, JSX tags, then drop
list items, checklist items and table rows before measuring. Markdown
masking already covers most of that.

CAVEAT, and it is the reason this is not simply worth building. Every
one of these metrics assumes an essayistic register, where varied
sentence length and varied openings are evidence of a human hand.
Specification prose is not that register. It is deliberately even:
one fact per sentence, in order, subject-verb-object, and often four
or five consecutive sentences opening on "The". That is not a tell.
It is what makes a spec readable, and it is the register Pacino's
documentation will be written in.

Worked example, the opening paragraph of "Why this exists" in
BLOG_tools_1_ticfinder.md, which is deliberately spec-like:

    12  The previous posts in the Pacino series concern LLM-based ...
    15  The methodology in RTL generation uses an LLM to draft ...
     8  The designer reviews this RTL against planning documents.
    11  The record of this review is captured in the task file.
    18  The documented review and the unit test suites provide ...

    n=5  mean=12.8  sd=3.4  range=8-18

The lengths are fine. Four of the five openings are identical, so
SentenceStartEntropy and SentenceStartRepetition would both fire, and
both would be wrong. I asserted this paragraph was uniform in length
before measuring it, and the numbers said otherwise -- which is itself
the argument for not shipping a metric that reports a number nobody
checks.

So this feature needs the same escape hatch as the domain vocabulary
in item 6: a register setting, or a per-file exemption, before any of
it fires on a specification. It is the same class of error as the
`figure` label on a list of bare identifiers -- a scorer tuned for
English prose meeting a document that is not written in it.

### 2. Anthropomorphism

"The module wants to", "the parser knows about", "the FSM tries to".
llm-slop has `Anthropomorphism`; ai-tells has three rules. For
hardware documentation this is a precision defect before it is a
stylistic tell, which makes it more valuable here than in general
prose. Dependency-shaped: an animate-agent verb with an inanimate
nsubj.

### 3. Chat-artifact tells

`AssistantOpener`, `AssistantCloser`, `SycophancyMarkers`,
`PerformedCandor`, `CalibrationTheatre`, `HollowAcknowledgment`.
These leak whenever an assistant drafts specification text and a
human pastes it in. Mostly phrase-list work, so cheap.

### 4. Constructions they do by regex that suit a parse better

`PseudoCleft`, `ShellNounCopula`, `SummativeAppositive`,
`StackedAnaphora`, `ParallelStaccato`, `CataphoricForecasting`,
`ColonDrumroll`, `WithheldPayoff`. Each is a dependency shape. This is
where the parse advantage compounds: one detector per construction
instead of one regex per surface form.

### 5. Heading rules

ai-tells has six: `AnnouncementHeadings`, `ExplainerHeadings`,
`MarketingHeadings`, `MicDropHeadings`, `WrapUpHeadings`,
`StructureAnnouncements`. ticfinder ignores headings entirely. Matters
for documentation, less for prose.

### 6. Domain vocabulary exemptions

ai-tells disables its fall-metaphor rules for aviation prose. Every
hardware document here waives `mutually exclusive` (ABSTRACT_ADVERB)
and `by construction` (BORROWED_RIGOUR) by hand. A domain profile that
mutes named terms per project would remove that recurring cost. The
least sophisticated item on the list and the most immediately useful.

### 7. Rule-level density variants

`VerbTricolonDensity`, `NegationDensity`, `PassiveDensity` fire on
rate within a section rather than on a single instance. ticfinder does
rates at the report level only. A per-construction threshold would let
a construction stay silent until it clusters, which is the stated
premise of the tool.

## What not to copy

Flat rule sets with everything at `level: error`. vale-ai-tells sets
every rule to error and has no confidence tiers, which is why it needs
per-file disabling as the primary escape hatch.

Per-line matching. The `VerbTricolon` comment records that Vale
flattens a document to one string before matching, so three clauses
from three separate sentences once read as a series and reported a
tricolon that did not exist. Their fix was to exclude terminal
punctuation from every inter-item gap. The parse makes the problem
absent rather than fixed.

## What ticfinder keeps

- Dependency parsing, and the construction/pattern hierarchy it allows
- Per-pattern confidence overriding the construction's
- The waiver ledger. None of the four has one. slopster's `slop-diff`
  is nearest: it compares a branch against main and reports only new
  findings, ignoring line shifts. That answers what changed. The
  ledger answers what a human accepted, which is the question that
  matters for a document reviewed repeatedly by different people.
- Rate framing with an author-controlled denominator, and no verdict

Content-hash baselines are not novel in software generally -- Psalm,
Android Lint, PVS-Studio, detekt, SonarQube and Semgrep all hash
warning fields because line numbers shift. The contribution is
bringing that to prose, which nobody in this niche had done.
