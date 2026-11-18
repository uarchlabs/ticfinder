  I've drafted both task files from the template, and both pass
  validate_and_extract.py. The Date fields are still YYYY.MM.DD for you to fill in when
  you run them.

  prompts/TF-003.md covers masking fixes and TRICOLON licensing, in two phases with a
  commit between them.
  - Phase 1:
    - The indented-code rule applies only to markdown files. In plain text the code
      masker judges indented lines.
    - Code lines with a trailing # or // comment are judged on the code part.
    - name : value.call(arg) DSL lines are masked.
    - Each fix has test rows first, using invented examples and nothing copied from the
      specs.
    - Harvest is expected to be identical. If any finding changes, the task stops.
    - The specs aggregates and spot-checks are redone, then it stops for your commit.
  - Phase 2:
    - It starts with an offline test on labels.jsonl. Each list member is scored as a
      referent (identifier, proper noun, quantity, a phrase that recurs) or a quality,
      and the score is compared between accepted and rewritten findings. If it doesn't
      separate them, that's a null result and no code goes in.
    - If it does separate them, the task stops and asks you to choose. Option (a) is a
      new subtype label: no waiver goes stale, but you can't mute it on its own. Option
      (b) is a new pattern: you can mute it with --off, but every waiver for a moved
      finding goes stale, because the fingerprint hashes the pattern. The task counts
      those waivers before asking.
    - Harvest gets a --by-subtype option. The main measure is how many of the 84
      accepted and 19 rewritten findings move to the new label.
  - Results go in roadmap section 10.

  prompts/TF-004.md covers arXiv cs.AR abstracts before and after LLMs.
  - Script: a new eval/arxiv_rates.py with fetch and analyse subcommands.
  - Windows: 2018–2021 against 2025–2026, by first-version date, primary category only.
    Each window is capped at 3,000 papers with a fixed seed.
  - Fetching: the arXiv API with 3 seconds between requests, a generic User-Agent, and
    no personal details in requests. The cache goes in private/arxiv/, and the task
    checks that private/ is still git-ignored before writing.
  - Masking: inline LaTeX is masked inside the script, so ticfinder itself is
    untouched.
  - Statistics: rates per 1,000 words, with bootstrap intervals over papers and
    post/pre ratios. Sanity checks cover abstract length and 20 hand-checked findings
    for each of the three biggest movers.
  - Output: only aggregates are committed, with no abstract text, titles or paper ids.
    Results go in roadmap section 11.

  Running both at once. The two tasks are kept from colliding:
  - Code: TF-004 must not edit ticfinder.py or tests.py. If it needs a change there, it
    stops and asks.
  - Roadmap: each task edits only its own results section and its own step in
    section 7.
  - Working copy: run them in separate sessions, ideally in a git worktree.

  Before you run them, check two choices I made that you may want differently:
  - TF-004 sample cap: 3,000 papers per window.
  - TF-003 phase 2 option (b): it's there for when the referent signal is strong enough
    that you'd want to mute those lists separately.

  Both task files go with this work. Add this line to the commit message body:

  Add prompts/TF-003.md (masking fixes, TRICOLON licensing) and
  prompts/TF-004.md (arXiv cs.AR rates before and after LLMs).

