# TF-002 summary: what ticfinder can do now, and why

## Where this fits

The roadmap's long-term aim is to stop guessing which findings matter. A
construction is worth reporting when it is more common in LLM text than in
human text of the same register. Measuring that needs a human baseline in
the target register, and the best one available is the author's pre-LLM
specifications (roadmap 5.3).

Those specs are full of code that markdown cannot see: netlists, DSL
statements, port lists and register tables written as plain lines. Until
TF-002, ticfinder parsed all of it as English. Any rate measured on the
specs would have counted code as human prose, and the human baseline would
have come out polluted in an unknown direction. TF-002 is the step that
has to come before the specs can be used.

There was a second hope. Unmarked code in the blogs might explain some of
the `TRICOLON` false positives, since comma-separated identifiers look
like a list. Removing it would then raise precision directly.

## What changed in capability

### 1. ticfinder reports how much of a file it read

Before, the masked percentage was effectively broken. It compared lengths,
and masking blanks text in place without changing the length, so the
figure moved only when masked text sat at the very start or end of a file.
Files with a fifth to a third of their text masked reported about zero,
and the 40% warning could never fire.

Now the figure counts non-whitespace characters and leaves out regions the
author deliberately switched off. It is split in two:

- **markdown-masked**: fences, indented code, tables, quotes, link targets
- **code-masked**: unmarked code found by the new masker

Both appear in `--stats` and `--json`. The tool can now tell you how much
of a document it ignored, and for which reason. That turns the masked
percentage into a usable quality check on a corpus: a file at 55% masked
is either mostly code or being misread, and you can now see which.

### 2. ticfinder recognises code that is not marked up

A new line-level masker blanks lines that read as code. It scores each
line on:

- density of code symbols (`;{}()=[]<>`), balanced pairs only
- share of identifier-shaped tokens (`foo_bar`, `pc_p1`, `[31:0]`,
  `0x04`, `3'b011`)
- port, declaration and register keywords (`input`, `logic`, `assign`,
  `RW`)
- a guard on the share of ordinary words, so prose that mentions code
  stays prose

It also looks at where a line sits. A code-like line is blanked only when
it cannot be the middle of a sentence: it starts a block, follows a line
that ends a sentence or a colon, or follows another code line. A line that
is very dense in symbols and ends the way code lines end (`;`, `)`, `{`)
is blanked anywhere. That case covers netlist instances, which follow
unpunctuated labels in plain-text specs.

It deliberately leaves alone:

- **Inline code.** Backticked text stays as text, as it did before. A line
  that contains any inline code is never code-masked, because the author
  has already marked up the code there.
- **Identifier runs inside a wrapped prose sentence.** Blanking one line
  of a paragraph would leave a hole the parser reads across, which is the
  failure that made inline code keep its text in the first place.

### 3. The masker can be switched off for comparison

`--no-code-mask` runs with markdown masking only. Any document can be
compared with and without the new masker, so its effect can be measured
on any document, including ones outside the harvest set.

### What did not change

- The fingerprint formula. No waiver ids moved and no waiver went stale.
- The detectors. Every construction and pattern is as it was.
- Inline-code handling and the offset rules: masking still blanks in
  place, and character offsets and newlines are preserved.
- The default run: the code masker is on by default.

## Outcome

### Blogs: a null result

The masker changed nothing in the harvest. Labels and per-pattern
precision are identical before and after, and no blog finding was
removed. Over the whole public corpus (all pacino blogs and their drafts, plus
the notes and README) it blanks three lines, all genuine expressions in a post outside the harvest set.

The blogs put their code in fences and backticks, so there was no unmarked
code to remove. The `TRICOLON` false positives in the blogs are prose
lists of real things, and a masker cannot reach them. That narrows the
next step: precision on `TRICOLON` will come from the role-specific
licensing check in roadmap 5.2 (are the list members referents or
qualities?), and further masking work will not help it.

### Specs: needed, and not yet sufficient

On the 36 spec and sample files the masker removes about 6% of the words
that markdown masking leaves. Spot checks show it is accurate when it
fires (39 of 40 sampled blanked lines were code). It still misses code in
about 10 files, and the kinds it misses are known:

- DSL statements of the form `name : value.call(arg)`
- code lines that end in a prose comment
- XML attribute lines, bit-encoding table rows and comment rule lines

The spot check also found a larger problem in the existing markdown
masking. The 4-space indented-code rule treats indented prose in plain
text files as code, and blanks about 530 lines of the author's own prose
across 6 files. All three files over the 40% warning are over it for this
reason. This is the opposite error to the one TF-002 set out to fix: it
removes human prose from the baseline.

The split percentages from capability 1 are what exposed this. With a
single broken figure it would not have been visible.

## Direction after TF-002

1. **Finish corpus preparation before measuring base rates.** Three fixes,
   each with test rows: keep the indented-code rule away from plain text,
   score code lines with trailing comments on the code part, and add the
   DSL form. Then recheck the per-file masked percentages on the specs.
2. **Move `TRICOLON` work to licensing.** The blogs show that its false
   positives are a question of meaning, and masking cannot fix them.
3. **Use the masked percentage as a gate.** Any corpus fed to 5.3 should be
   checked file by file for markdown and code share before its counts are
   trusted.

Roadmap section 9 has the full measurements and thresholds. The RESULTS
block of `prompts/TF-002.md` records the test rows and decisions.

# Interactive Q&A

1. Why wouldnt the pre-2020 arxiv papers be a more substantial body for the human       
  baseline

```
  For volume, it would be. The issue is which comparison the baseline feeds.
  
  The likelihood ratio needs matched registers. Roadmap 5.3 defines it as the rate in
  LLM text of register R over the rate in human text of the same register R. Academic
  papers have their own construction rates: dense coordination, hedging, "rather than"
  for comparing methods, and set phrases like "in this paper, we". If you divide
  pacino's LLM-written specs or blogs by pre-2020 arXiv rates, part of the ratio is
  genre: academic paper against design spec or narrative blog. A huge corpus in the
  wrong register gives a very precise estimate of the wrong quantity.

  The edits being predicted are about one author's voice. The labels come from you
  rewriting or waiving findings in your own documents. A construction is a tic when
  it's unusual for this author in this register. Your specs measure that directly, and
  arXiv measures what academics in general write.

  arXiv full text is harder to clean than the specs. It comes as LaTeX or PDF, so math,
  \cite, figures, tables, algorithm blocks and PDF extraction errors would all need
  masking. That's the same problem TF-002 just hit, but larger. Abstracts are clean,
  but they're a compressed sub-register with their own rates. The licenses also allow
  counting only, with no redistribution.

  The specs do have a real weakness: size. After masking they are about 82k words. A
  construction at 0.5 per 1,000 words gives about 40 instances, so the confidence
  interval is wide. For rare constructions the specs can't separate a ratio of 1.5 from
  3, and arXiv can.

  Where arXiv is the stronger design is pre against post. Roadmap section 6 compares
  cs.AR from 2018 to 2021 with 2025 to 2026. Both sides are arXiv in the same subfield,
  so genre cancels and the change over time is mostly LLM influence. That's a cleaner
  experiment than either corpus against pacino, and it uses arXiv's size well.

  So I'd give each corpus its own job:

  - arXiv pre against post: which constructions rose after LLMs, with tight intervals,
    independent of author.
  - Specs against pacino LLM specs: the per-author, per-register ratio that drives
    confidence in ticfinder.
  - Combined: use the arXiv estimates as a prior and update them with the spec counts
    (empirical Bayes). Rare constructions then borrow strength from arXiv, and common
    ones are set by your own data. Where the two disagree, the difference is a measure
    of the register effect, which is useful in itself.

  One correction on dates: the roadmap uses 2021 as the cutoff (ChatGPT launched in
  November 2022), so pre-2022 is safe and pre-2020 gives up two years of data for
  little gain.
```

2. what is the issue with licenses                                                      

```
  The issue is redistribution. Analysing the papers is fine.

  Authors choose a license for each paper when they submit it. The options are:

  - arXiv's own non-exclusive distribution license. This is the default and the most
    common. It gives arXiv the right to distribute the paper and gives no rights to
    anyone else. Copyright stays with the authors.
  - Creative Commons licenses: CC BY, CC BY-SA, CC BY-NC-SA, CC BY-NC-ND, or CC0. Each
    has its own conditions on attribution, commercial use and derivative works.

  A corpus of a few thousand cs.AR papers would mix all of these, and most would carry
  the default license, which grants you nothing for redistribution.

  What's generally fine:

  - Analysis. Downloading papers through arXiv's API or bulk-access channels and
    computing statistics on them is text and data mining. Counts, rates and likelihood
    ratios are facts about the text, and they're safe to publish.
  - Metadata and abstracts. arXiv releases its metadata, abstracts included, under CC0.
    That's why the roadmap treats abstracts as unrestricted.

  What's risky:

  - Committing full texts to this repo or pushing them to GitHub.
  - Publishing a derived dataset that contains the text.
  - Quoting at length in a blog post.

  ticfinder has one specific trap here. Every finding stores its full sentence, in
  context for the waiver fingerprint, and harvest.py writes those sentences to
  labels.jsonl. Run on arXiv full texts, the JSON output, the HTML reports, any waiver
  file and any labels file would all hold verbatim sentences from copyrighted papers.
  Kept local or in a git-ignored directory, that's fine. Committed or shared, it
  amounts to redistributing excerpts.

  Two smaller points:

  - NC licenses: if uarchlabs ever uses this work commercially, the papers with
    non-commercial licenses become a question too.
  - Bulk access: arXiv asks that bulk downloads go through its API, with rate limits,
    or its S3 bulk buckets, and not through scraping the website.

  That's why roadmap section 6 says "count only and don't redistribute", and why
  CLAUDE.md says to cache corpora outside the repo or under a git-ignored directory. In
  practice, store the papers under something like corpora/arxiv/, add that to
  .gitignore, and commit only aggregate tables. If you quote example sentences in a
  post, use short excerpts with citations. Text and data mining rules vary by country
  (US fair use, the EU and UK TDM exceptions), so this is a summary of the norms and
  not legal advice.
```

3. Where does the redistribution concern come up ? The intent is not to modify the      
   arxiv papers for re-publication. I guess the question is what would ticfinder do     
   with those is different than what it does with my writing samples ? 

```
  ticfinder would do nothing different with them. It reads a file, parses it and counts
  constructions, the same as with your samples. I overstated the concern. It only
  comes up if verbatim text from a paper ends up in a file that leaves your machine.
  For the arXiv study, which only counts constructions per year, that won't happen by
  default.

  ticfinder writes text in only a few places:

  ┌───────────────────┬──────────────────┬────────────────┬────────────────────────┐
  │      output       │     contains     │  written when  │        at risk?        │
  ├───────────────────┼──────────────────┼────────────────┼────────────────────────┤
  │ terminal output   │ matched text,    │ every run      │ no, it stays on your   │
  │                   │ sentence excerpt │                │ screen                 │
  ├───────────────────┼──────────────────┼────────────────┼────────────────────────┤
  │                   │ the whole        │                │ no, reports/ is        │
  │ reports/*.html    │ document,        │ --html         │ git-ignored            │
  │                   │ highlighted      │                │                        │
  ├───────────────────┼──────────────────┼────────────────┼────────────────────────┤
  │                   │ matched text and │                │ only if you write it   │
  │ --json file       │  full sentence   │ --json         │ into the repo and      │
  │                   │ per finding      │                │ commit it              │
  ├───────────────────┼──────────────────┼────────────────┼────────────────────────┤
  │                   │ matched text     │ --waive,       │ no need to waive arXiv │
  │ waiver files      │ only (text       │ --gen-waivers  │  findings              │
  │                   │ field)           │                │                        │
  ├───────────────────┼──────────────────┼────────────────┼────────────────────────┤
  │                   │                  │                │ doesn't apply: harvest │
  │ eval/labels.jsonl │ full sentences   │ harvest.py     │  needs a git edit      │
  │                   │                  │                │ history, and arXiv     │
  │                   │                  │                │ papers don't have one  │
  └───────────────────┴──────────────────┴────────────────┴────────────────────────┘

  So the arXiv pipeline would be: fetch papers to a local cache, run ticfinder,
  aggregate counts by year and construction, and commit only the table of rates. None
  of that publishes paper text.

  The rule for the arXiv papers is the same one CLAUDE.md already sets for your specs:
  keep the source files out of the repo, and commit aggregates only. The reason
  differs. Your specs are private, and the papers belong to other people. In practice
  the handling is identical.

  Two habits to keep:

  1. Store the papers outside the repo or in a git-ignored directory. .gitignore
     already has private/ and reports/, so private/arxiv/ would work with no change.
  2. Write any --json output from arXiv runs to the same ignored location. That file
     holds full sentences.

  The one way excerpts would get published is quoting example sentences in a blog post
  about the results. Short quotes with a citation are normal academic practice and
  fine.
```

4. i have a question about why my 'voice' matters; because it is less about my writing  
  style than it is finding the LLM prose contructs that are intrusive and break the    
  easy flow of information when reading LLM prose. This is a necessity because I have  
  not made enough of my own pre-LLM text available. Much of my writing is no longer    
  available to me, it is company IP. If there is a good motivation I could mine my     
  emails and other ad hoc text for this purpose. but back to the goal of ticfinder,    
  its initial purpose is to make editing LLM generate prose easier, i have LLMs        
  generate progress and design description now, soon to want to generate true          
  technical specifications, eventually feeding ticfinder into the generation loop.     
  this last bit is well outside the scope right now.                                   
  
● That changes the argument, and it weakens one of my reasons. I treated the baseline
  as "what's unusual for this author". For the goal you describe, it should be "what's
  unusual for competent human technical writing in this register". The labels already
  capture your judgement: harvest records what you, as editor, found intrusive. The
  baseline only has to answer whether a construction is overrepresented in LLM text,
  and any skilled human writer in the same register can supply that.

  What still holds. Register matters a great deal. Academic papers, design documents,
  progress reports and specifications each have different normal rates for
  coordination, hedging, "rather than" and so on. A baseline from the wrong register
  would make spec-normal constructions look like tics, or the reverse.

  What changes. Your own pre-LLM text has no special status. Its value was being
  in-register and certainly pre-LLM. That's why losing access to your old writing (now
  company IP) is less of a problem than I implied.

  Emails would mostly be the wrong register. Email is informal, conversational and
  fragmentary, with its own rhythm. It would make a fair baseline for progress notes at
  most, and it adds privacy work for little gain. I wouldn't mine them for this.

  A better source: public, pre-2022 design and specification documents by many authors.
  These match what you generate now (design descriptions) and what you want next
  (specifications):

  - Python PEPs. Design proposals with motivation, specification and rationale
    sections. Public domain, dated, and hundreds of them before 2022.
  - IETF RFCs. Formal protocol specifications going back decades. They contain a lot of
    ASCII diagrams and packet layouts, so the code masker matters here.
  - Rust RFCs. Design documents with a fixed structure, under MIT or Apache licenses.
  - The RISC-V ISA manuals. Hardware specification prose in your domain, under CC BY
    4.0.
  - Open hardware design docs (OpenTitan, lowRISC, older OpenCores projects).
    Microarchitecture descriptions, the register closest to your specs.

  Most of these are in version control, so the files can be dated precisely to before
  2022. The volume is in the millions of words, which fixes the size problem with your
  specs. Their licenses are also simpler than arXiv's.

  Where that leaves each corpus:

  - Public design and spec documents: the main human baseline for the design and spec
    registers.
  - Your specs: a small, trusted check on that baseline in your exact domain.
  - arXiv before and after LLMs: still the best evidence of which constructions LLMs
    increased, because genre cancels within it.
  - Your harvest labels: what counts as intrusive. The likelihood ratio says whether a
    construction is LLM-typical, and the labels say whether it breaks the reader's
    flow. A construction should be reported with high confidence when both are true.

  The point about flow also supports the density work in roadmap 5.4. One "rather than"
  is fine; four in a paragraph break the reading. A per-construction likelihood ratio
  combined with a density test is close to a direct measure of "intrusive".

  For the generation loop later, this design gives you calibrated per-construction
  scores in place of hand-set confidence. That's what a generator would need as
  feedback, so the current direction doesn't close that off.

  Should I revise roadmap 5.3 and section 6 to match? The "one author's voice" framing
  in 5.3 is now wrong and should go. The public design-doc corpus would be added as the
  primary baseline, with your specs as a check.

