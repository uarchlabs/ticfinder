```
 FILE:    CLAUDE.md
 SOURCE:  various
 STATUS:  WORKING
 UPDATED: 2026-11-17
 CONTACT: Jeff Nye
```

# Project: ticfinder

You are assisting with the development of a process for detection and
classification of LLM prose constructs. The tool is called ticfinder.

ticfinder finds recurring LLM prose constructions in markdown so a human editor
can decide what to cut. It parses with spaCy and reports named constructions,
per-1k-word rates, and content-hash waivers.

The current work reduces false positives and adds novel internals. Read
`eval/TICFINDER_ROADMAP.md` before starting; it holds the plan, the
baseline numbers, and the open bugs. `eval/eval-baseline-2026-11-17.md`
is the reference measurement.

## Layout

- `tools/ticfinder.py`: everything (masking, detectors, phrase layer,
      waivers, report, HTML). Detectors are registered with `@construction`
      and `@pattern`.
- `tools/ticfinder-phrases.json`: phrase-list constructions.
- `tools/tests.py`: regression suite (registry, detectors, masking, spans,
      waivers, cli).
- `tools/setup.sh`: sets the session environment variables (see Setup).
- `tools/html_report.py`: standalone HTML report generator. Not imported
      by `ticfinder.py`.
- `tools/masktest.py`, `tools/spantest.py`: older standalone masking and
      span checks. The `masking` and `spans` sections of `tests.py` cover
      the same ground.
- `tools/validate_and_extract.py`: validates a task file against the
      template and extracts its PROMPT section.
- `tools/run_time.py`: reports active and wall-clock time of the last
      `/run` task in a Claude Code session transcript.

- `eval/harvest.py`  : labels findings from the pacino edit history and
      reports precision per pattern.
- `eval/labels.jsonl`: harvested labels.

- `notes/`     : bug notes and the competitive review.
- `waivers/`   : all waiver files, for documents in this repo and for
      external documents such as the pacino blogs.
- `prompts/`   : task files and prompts.
- `reports/`   : report output (git-ignored).
- `samples/`   : writing samples committed to the repo.
- `templates/` : task file and other standard file forms.
- `images/`    : documentation images.
- `versions/`  : previous versions of files (git-ignored). Do not reference.

## Setup

The user provides the environment before the session starts:

```
pip install spacy
python3 -m spacy download en_core_web_md   # en_core_web_trf for parse-agreement work
. tools/setup.sh
```

`md` is used, not `sm`. Parse quality is the ceiling on precision.

`tools/setup.sh` sets these variables. It does not install anything.

```bash
PACINO=<some path>           # absolute path to the local pacino checkout
WRITING_SAMPLES=<some path>  # absolute path to non-LLM writing samples
SPACY_INSTALLED=yes|no       # yes if `python3 -c 'import spacy'` succeeds
                             # when setup.sh runs, otherwise no
```

## Restrictions

- Do not run git commands that change repository state, including
  commits and pushes. Read-only commands (`status`, `log`, `diff`,
  `show`) are fine.

## Commands

```bash
make regress                   # ./tools/tests.py, must pass before any commit
./tools/tests.py detectors -v  # one section, verbose
make                           # run ticfinder on README.md with HTML to reports/
make notes                     # run ticfinder on notes/*.md with HTML to reports/
make f2                        # run ticfinder on $PACINO/blogs/BLOG_bpu_14_directed_validation.md

python3 eval/harvest.py $PACINO --waiver-dir waivers --docs <blogs>   # see roadmap s.4
```

`harvest.py` needs the full git history of `$PACINO`.

## How to work

- **Measure every detector change.** Run `make regress` and `harvest.py`
  before and after. Report the change in per-pattern precision
  (`prec*`) and in accepted/rewritten counts. A change that cuts findings
  without that comparison is not done.
- **Test row first.** When a miss or a false positive turns up, add the
  sentence to the `detectors` section of `tests.py` as an expected
  yes/no row before changing code. Negative rows are what stop a detector
  being loosened until it fires on ordinary English.
- **Report null results.** If a hypothesis doesn't separate accepted from
  rewritten findings, record it in the roadmap or `notes/` and keep the
  code out. The first licensing test was null; see roadmap s.4.
- At the end of each step, stop and summarize the files changed, the
  `make regress` result and the harvest numbers, and suggest a commit
  message. The user commits.

## Conventions

- A **construction** is a stable id: what users mute and what counts are
  reported against. A **pattern** is one executable query for one surface
  form. When phrasing drifts, add patterns and keep the id.
- **Group ids by measured precision.** Two constructions that look
  alike rhetorically get separate ids when their precision differs.
  Anything a user would want to mute separately needs its own id or
  pattern.
- A pattern may override its construction's confidence. Once calibration
  lands (roadmap 5.3), confidence comes from measured likelihood ratios,
  not judgement.
- The `note` field says what to check, not "this is bad". Every
  construction is legitimate somewhere.
- Detectors return `(span, subtype)` or `(span, subtype, confidence)`.
  Never emit empty, inverted or zero-width spans.
- Masking must preserve character offsets: blank in place, never delete.
  Inline code keeps its text and only the backticks are blanked.
- Fingerprints hash construction, pattern, matched text and sentence
  (whitespace-normalised). Never include line numbers or offsets. Any
  change to the hash invalidates every existing waiver: call it out
  explicitly and provide a migration or a note.
- A normal run never writes waiver files; only `--waive`, `--unwaive`,
  `--gen-waivers` and `--prune-stale` do.
- Keep it a single dependency-light script unless there is a clear reason
  to split it.

## Data handling

- The author's pre-LLM specifications are private. They are in
  `$WRITING_SAMPLES`, mixed in with the other non-LLM writing samples,
  so treat every file there as private. Never copy them into this repo,
  commit them, or quote them in notes or commit messages. Report
  aggregates only.
- arXiv full texts carry mixed licenses: use them for counts, don't
  commit them. Cache corpora outside the repo or under a git-ignored
  directory.

## Writing

Docs in this repo are run through ticfinder. After editing README.md,
run `make`. After editing a notes file, run `make notes`. Fix or justify new findings; don't add waivers without being asked.
Write plainly: no em dashes, no "not X but Y" framing, no throat-clearing.
