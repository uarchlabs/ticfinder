#!/usr/bin/env python3
"""ticfinder construction rates in public pre-2022 design and specification
documents: the public baseline for roadmap step 7 (TF-009).

  fetch        clone or rsync the five sources into private/specs/ (a rerun
               fetches only what is missing), extract every document as of
               the last commit on or before 2021-12-31, date it, keep the
               ones dated in the TF-004 pre window (2018 to 2021), and draw
               a seeded sample capped at SOURCE_CAP raw words per source.
               Writes private/specs/docs.jsonl and private/specs/sample.json
               and prints the survey table.
  selftest     expected-output rows for every exclusion rule, written from
               synthetic text only.
  mask-report  per source: documents and words kept, masked shares, and
               random masked sentences printed to the console for a residue
               spot-check. Prints text; writes nothing.
  analyse      ticfinder over the kept text of every sampled document, the
               per-document tables, and the report. --report-only
               --table-sha SHA rebuilds the report from a table written by
               an earlier ticfinder (pinned rebuild). --table-dir DIR,
               --arxiv-table-dir DIR and --arxiv-sha SHA read snapshot
               tables, so an older report can be rebuilt after a rerun.
               --json PATH also writes every report row as JSON (schema:
               roadmap s.15).

Sources (roadmap section 6):

  peps       python/peps, PEP files at the cutoff commit, dated by the
             Created header
  ietf       RFC Editor plain-text RFCs (rsync module rfcs-text-only),
             dated by publication date in rfc-index.xml
  rust       rust-lang/rfcs, text/*.md at the cutoff commit, dated by the
             first-parent commit that added the file at that path (the
             merge that landed it on the main branch)
  riscv      riscv/riscv-isa-manual, the LaTeX chapters the unprivileged
             and privileged manuals \\input at the cutoff commit, dated by
             the last commit that changed the file
  opentitan  lowRISC/opentitan, hw/**/doc/*.md outside hw/vendor/ at the
             cutoff commit (checklist.md sign-off templates left out),
             dated by the commit that added the file, following renames

Nothing this script writes outside private/ holds document text, titles,
file names or document numbers.
"""

import argparse
import hashlib
import json
import math
import random
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import arxiv_rates as AR  # noqa: E402
import arxiv_bodies as AB  # noqa: E402  (mask_tex, Boot, verdicts)

SPECS = AR.ROOT / "private" / "specs"
DOCS = SPECS / "docs.jsonl"
SAMPLE = SPECS / "sample.json"
TEXT = SPECS / "text"              # extracted raw documents
TABLE = SPECS / "per_doc.jsonl"
FINDINGS = SPECS / "findings.jsonl"

CUTOFF = "2022-01-01T00:00:00Z"    # last commit strictly before this
YEARS = (2018, 2021)               # TF-004 pre window
SOURCE_CAP = 1_500_000             # raw words per source
SAMPLE_SEED = 20261121             # shuffle key f"{SAMPLE_SEED}-{source}"
SOURCES = ["peps", "ietf", "rust", "riscv", "opentitan"]

REPOS = {
    "peps": ("https://github.com/python/peps.git", "peps", False),
    "rust": ("https://github.com/rust-lang/rfcs.git", "rust-rfcs", False),
    "riscv": ("https://github.com/riscv/riscv-isa-manual.git", "riscv",
              False),
    "opentitan": ("https://github.com/lowRISC/opentitan.git", "opentitan",
                  True),
}
RFC_DIR = SPECS / "rfc"
RFC_INDEX_URL = "https://www.rfc-editor.org/rfc-index.xml"
RFC_RSYNC = "rsync.rfc-editor.org::rfcs-text-only"
RFC_NS = {"r": "https://www.rfc-editor.org/rfc-index"}

LICENSES = {
    "peps": "public domain or CC0 1.0 (per-PEP Copyright section)",
    "ietf": "IETF Trust Legal Provisions (BCP 78)",
    "rust": "MIT or Apache 2.0",
    "riscv": "CC BY 4.0",
    "opentitan": "Apache 2.0",
}
ORIGIN = {
    "peps": "git repository",
    "ietf": "bulk archive (RFC Editor rsync)",
    "rust": "git repository",
    "riscv": "git repository",
    "opentitan": "git repository (blobless, sparse hw/**/*.md)",
}
DATING = {
    "peps": "Created header",
    "ietf": "publication date (rfc-index.xml)",
    "rust": "first-parent commit adding the file under text/",
    "riscv": "last commit changing the file",
    "opentitan": "commit adding the file, following renames",
}


# ---------------------------------------------------------------- fetch

def git(repo, *a, text=True):
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True,
                       text=text)
    if r.returncode:
        sys.exit(f"git {' '.join(a)} in {repo}: {r.stderr.strip()}")
    return r.stdout


def cutoff_commit(repo):
    return git(repo, "rev-list", "-1", "--first-parent",
               f"--before={CUTOFF}", "HEAD").strip()


def words_of(s):
    return len(s.split())


def doc_id(source, path):
    """Opaque id for a document: no names or numbers in anything derived."""
    return hashlib.sha256(f"{source}:{path}".encode()).hexdigest()[:12]


def fetch_sources():
    SPECS.mkdir(parents=True, exist_ok=True)
    for src, (url, d, blobless) in REPOS.items():
        repo = SPECS / d
        if repo.exists():
            continue
        t0 = time.monotonic()
        cmd = ["git", "clone", "-q"]
        if blobless:
            cmd += ["--filter=blob:none", "--no-checkout"]
        subprocess.run(cmd + [url, str(repo)], check=True)
        if blobless:
            git(repo, "config", "gc.auto", "0")
            git(repo, "sparse-checkout", "set", "--no-cone", "/hw/**/*.md")
            git(repo, "checkout", "-q", cutoff_commit(repo))
        print(f"cloned {src} in {time.monotonic() - t0:.0f} s",
              file=sys.stderr)
    RFC_DIR.mkdir(exist_ok=True)
    idx = RFC_DIR / "rfc-index.xml"
    if not idx.exists():
        import urllib.request
        req = urllib.request.Request(RFC_INDEX_URL,
                                     headers={"User-Agent": AR.USER_AGENT})
        with urllib.request.urlopen(req, timeout=120) as r:
            idx.write_bytes(r.read())
        time.sleep(AR.DELAY)
    want = [f"rfc{n}.txt" for n, _ in rfc_entries()]
    missing = [w for w in want if not (RFC_DIR / "txt" / w).exists()]
    if missing:
        lst = RFC_DIR / "files.txt"
        lst.write_text("\n".join(missing) + "\n")
        subprocess.run(["rsync", "-a", f"--files-from={lst}", RFC_RSYNC,
                        str(RFC_DIR / "txt") + "/"], check=True)


def rfc_entries():
    """(number, date) for RFCs published in the window."""
    t = ET.parse(RFC_DIR / "rfc-index.xml").getroot()
    months = {m: i for i, m in enumerate(
        ["January", "February", "March", "April", "May", "June", "July",
         "August", "September", "October", "November", "December"], 1)}
    out = []
    for e in t.findall("r:rfc-entry", RFC_NS):
        y = int(e.find("r:date/r:year", RFC_NS).text)
        if YEARS[0] <= y <= YEARS[1]:
            m = months[e.find("r:date/r:month", RFC_NS).text]
            out.append((int(e.find("r:doc-id", RFC_NS).text[3:]),
                        f"{y}-{m:02d}"))
    return out


def docs_peps():
    repo = SPECS / "peps"
    c = cutoff_commit(repo)
    for name in git(repo, "ls-tree", "--name-only", c).split():
        if not re.fullmatch(r"pep-\d{4}\.(txt|rst)", name):
            continue
        text = git(repo, "show", f"{c}:{name}")
        m = re.search(r"^Created:\s*(.+)$", text, re.M)
        y = re.search(r"\b(19|20)\d\d\b", m.group(1)) if m else None
        yield name, (y.group(0) if y else None), text, ".rst", c


def docs_ietf():
    for n, date in rfc_entries():
        p = RFC_DIR / "txt" / f"rfc{n}.txt"
        yield p.name, date, p.read_text(encoding="utf-8", errors="replace"), \
            ".txt", None


def added_dates(repo, c, prefix):
    """{path: date of the oldest commit adding it at that path}."""
    out = {}
    cur = None
    for line in git(repo, "log", "--no-renames", "--first-parent",
                    "--diff-merges=first-parent", "--diff-filter=A",
                    "--format=@%cs", "--name-only", c, "--",
                    prefix).splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.strip():
            out[line.strip()] = cur        # log is newest first: keep oldest
    return out


def docs_rust():
    repo = SPECS / "rust-rfcs"
    c = cutoff_commit(repo)
    added = added_dates(repo, c, "text/")
    for name in git(repo, "ls-tree", "-r", "--name-only", c, "text/").split():
        if not name.endswith(".md"):
            continue
        yield name, added.get(name), git(repo, "show", f"{c}:{name}"), \
            ".md", c


def riscv_files(repo, c):
    """The .tex files the two manuals \\input, transitively, in order."""
    have = set(git(repo, "ls-tree", "--name-only", c, "src/").split())
    seen, order = set(), []

    def walk(name, depth=0):
        p = f"src/{name}" if name.endswith(".tex") else f"src/{name}.tex"
        if p in seen or p not in have or depth > 5:
            return
        seen.add(p)
        if depth:
            order.append(p)
        body = git(repo, "show", f"{c}:{p}")
        body = re.sub(r"(?<!\\)%.*", "", body)
        for m in re.finditer(r"\\(?:input|include)\{([^}]+)\}", body):
            walk(m.group(1), depth + 1)

    for main in ("riscv-spec.tex", "riscv-privileged.tex"):
        walk(main)
    return [p for p in order if not p.endswith("/preamble.tex")]


def docs_riscv():
    repo = SPECS / "riscv"
    c = cutoff_commit(repo)
    for name in riscv_files(repo, c):
        last = git(repo, "log", "-1", "--format=%cs", c, "--", name).strip()
        yield name, last, git(repo, "show", f"{c}:{name}"), ".tex", c


def docs_opentitan():
    repo = SPECS / "opentitan"
    c = cutoff_commit(repo)
    names = [n for n in git(repo, "ls-tree", "-r", "--name-only", c,
                            "hw/").split()
             if n.endswith(".md") and "/doc/" in n
             and not n.startswith("hw/vendor/")
             and not n.endswith("/checklist.md")]
    for name in names:
        d = git(repo, "log", "--follow", "--diff-filter=A", "--format=%cs",
                c, "--", name).split()
        yield name, (d[-1] if d else None), git(repo, "show", f"{c}:{name}"), \
            ".md", c


GATHER = {"peps": docs_peps, "ietf": docs_ietf, "rust": docs_rust,
          "riscv": docs_riscv, "opentitan": docs_opentitan}


def in_window(date):
    return bool(date) and YEARS[0] <= int(date[:4]) <= YEARS[1]


def cmd_fetch(args):
    t0 = time.monotonic()
    fetch_sources()
    TEXT.mkdir(exist_ok=True)
    recs = []
    for src in SOURCES:
        (TEXT / src).mkdir(exist_ok=True)
        for path, date, text, ext, commit in GATHER[src]():
            did = doc_id(src, path)
            out = TEXT / src / f"{did}{ext}"
            out.write_text(text, encoding="utf-8")
            recs.append({"id": did, "source": src, "path": path,
                         "commit": commit, "date": date,
                         "in_window": in_window(date),
                         "file": str(out.relative_to(SPECS)),
                         "raw_words": words_of(text)})
    DOCS.write_text("".join(json.dumps(r) + "\n" for r in recs),
                    encoding="utf-8")
    sample = draw_sample(recs)
    SAMPLE.write_text(json.dumps(sample, indent=1) + "\n", encoding="utf-8")
    survey(recs, sample)
    print(f"\nfetch and extract: {time.monotonic() - t0:.0f} s; "
          f"private/specs/ uses {du(SPECS)}", file=sys.stderr)


def du(p):
    r = subprocess.run(["du", "-sh", str(p)], capture_output=True, text=True)
    return r.stdout.split()[0] if r.stdout else "?"


def draw_sample(recs):
    """Per source: every document in the window, or, above SOURCE_CAP raw
    words, a seeded shuffle drawn until the source reaches the cap (the
    document that crosses it is kept)."""
    out = {"seed": SAMPLE_SEED, "cap": SOURCE_CAP, "years": list(YEARS),
           "sources": {}}
    for src in SOURCES:
        docs = sorted((r for r in recs if r["source"] == src
                       and r["in_window"]), key=lambda r: r["id"])
        total = sum(r["raw_words"] for r in docs)
        capped = total > SOURCE_CAP
        if capped:
            random.Random(f"{SAMPLE_SEED}-{src}").shuffle(docs)
            keep, w = [], 0
            for r in docs:
                if w >= SOURCE_CAP:
                    break
                keep.append(r)
                w += r["raw_words"]
            docs = keep
        out["sources"][src] = {"capped": capped, "window_words": total,
                               "ids": [r["id"] for r in docs]}
    return out


def survey(recs, sample):
    print("| source | origin | license | dated by | documents at cutoff | "
          "in window | raw words in window | sampled documents | sampled "
          "raw words |")
    print("|---|---|---|---|---|---|---|---|---|")
    for src in SOURCES:
        rs = [r for r in recs if r["source"] == src]
        win = [r for r in rs if r["in_window"]]
        ids = set(sample["sources"][src]["ids"])
        smp = [r for r in win if r["id"] in ids]
        print(f"| {src} | {ORIGIN[src]} | {LICENSES[src]} | {DATING[src]} | "
              f"{len(rs):,} | {len(win):,} | "
              f"{sum(r['raw_words'] for r in win):,} | {len(smp):,} | "
              f"{sum(r['raw_words'] for r in smp):,} |")
    print("\nDocuments per year (all dated documents at the cutoff):")
    for src in SOURCES:
        c = Counter((r["date"] or "none")[:4] for r in recs
                    if r["source"] == src)
        print(f"  {src}: " + ", ".join(f"{y} {n}" for y, n in sorted(c.items())))


# ---------------------------------------------------------- exclusions
#
# Each masker takes a document's raw text and returns (kept, cats): kept has
# the same length, with excluded characters replaced by spaces; cats counts
# blanked non-space characters by rule. Newlines stay put except where an
# RFC page break splits a paragraph, where the break is blanked to spaces so
# the paragraph reads on (still in place, offsets unchanged).

class Blanker:
    def __init__(self, text):
        self.src = text
        self.buf = list(text)
        self.cats = Counter()

    def blank(self, lo, hi, cat, newlines=False):
        n = 0
        for i in range(max(lo, 0), min(hi, len(self.buf))):
            c = self.buf[i]
            if c == "\n" and not newlines:
                continue
            if not c.isspace():
                n += 1
            if c != " ":
                self.buf[i] = " "
        if n:
            self.cats[cat] += n

    def text(self):
        return "".join(self.buf)


def line_spans(text):
    """[(start, end)] per line, end excluding the newline."""
    out, pos = [], 0
    for ln in text.split("\n"):
        out.append((pos, pos + len(ln)))
        pos += len(ln) + 1
    return out


# --- IETF RFCs

RFC_FOOTER = re.compile(r"^\S.*\[Page \d+\]\s*$")
RFC_HEADER = re.compile(r"^\f?RFC \d+\s.*\S\s*$")
RFC_DROP = re.compile(
    r"^(?:status of this memo|copyright notice|table of contents|"
    r"(?:normative |informative )?references|acknowledge?ments?|"
    r"contributors|authors?'? address(?:es)?|author's address|index)\b",
    re.I)
RFC_NUM = re.compile(r"^((?:\d+|Appendix [A-Z]|[A-Z])(?:\.\d+)*)\.?\s+(.*)$")
ART_LINE = re.compile(
    r"\+[-=+~]{2,}\+?|[-=~_]{5,}|\|.*\|.*\||^\s*\d(?:\s+\d){3,}\s*$|"
    r"-+>|<-+|<->|^\s*[|+]\s*$|\.{5,}")
ART_CHARS = set("+-|=/\\<>*_.:^~#[]{}")
CAPTION = re.compile(r"^\s*(?:Figure|Table)\s+\d+(?::.*)?\s*$")


def art_ratio(lines):
    s = "".join("".join(ln.split()) for ln in lines)
    return sum(c in ART_CHARS for c in s) / len(s) if s else 0.0


def is_art_block(lines):
    """A blank-line-delimited RFC block that is a figure, packet diagram,
    table or other layout rather than prose."""
    r = art_ratio(lines)
    if r > 0.25:
        return True
    return r > 0.08 and any(ART_LINE.search(ln) for ln in lines)


def mask_rfc(text):
    b = Blanker(text)
    spans = line_spans(text)
    lines = [text[a:z] for a, z in spans]
    n = len(lines)
    # page breaks: footer, form feed, header
    i = 0
    while i < n:
        if RFC_FOOTER.match(lines[i]):
            j = i + 1
            while j < n and (not lines[j].strip() or lines[j].strip() == "\f"
                             or RFC_HEADER.match(lines[j])):
                if RFC_HEADER.match(lines[j]):
                    j += 1
                    break
                j += 1
            p = i - 1
            while p >= 0 and not lines[p].strip():
                p -= 1
            q = j
            while q < n and not lines[q].strip():
                q += 1
            prev = lines[p].rstrip() if p >= 0 else ""
            nxt = lines[q].strip() if q < n else ""
            joins = (prev and not re.search(r"[.:;!?)\]]$", prev)
                     and nxt and lines[q].startswith("   ")
                     and not lines[q].startswith("      ")
                     and lines[p].startswith("   "))
            if joins:
                b.blank(spans[p][1], spans[q][0] + 3, "page break",
                        newlines=True)
            else:
                b.blank(spans[i][0], spans[j - 1][1], "page break")
            i = j
            continue
        if lines[i].strip() == "\f" or lines[i].startswith("\f"):
            b.blank(*spans[i], "page break")
        i += 1
    # headings: column-0 lines that are not page furniture
    heads = [k for k in range(n) if lines[k][:1].strip() and lines[k][0] != "\f"
             and not RFC_FOOTER.match(lines[k]) and not RFC_HEADER.match(lines[k])]
    abstract = next((k for k in heads if lines[k].strip() == "Abstract"), None)
    first = abstract if abstract is not None else (heads[0] if heads else n)
    if first:
        b.blank(0, spans[first - 1][1] if first else 0, "front matter")
    drop_until = None       # (number prefix or None) of an open exclusion
    for idx, k in enumerate(heads):
        if k < first:
            continue
        title = lines[k].strip()
        m = RFC_NUM.match(title)
        num, name = (m.group(1), m.group(2)) if m else (None, title)
        end = spans[heads[idx + 1]][0] if idx + 1 < len(heads) else len(text)
        b.blank(*spans[k], "headings")
        inside = drop_until is not None and (
            drop_until == "" or (num and num.startswith(drop_until + ".")))
        if RFC_DROP.match(name):
            b.blank(spans[k][1], end, "boilerplate and references")
            if not inside:
                drop_until = num or ""
            continue
        if inside and drop_until:
            b.blank(spans[k][1], end, "boilerplate and references")
            continue
        drop_until = None
    # BCP 14 key words boilerplate paragraph
    for m in re.finditer(r"The key words \"MUST\".*?(?:\n[ \t]*\n|\Z)", text,
                         re.S):
        b.blank(m.start(), m.end(), "boilerplate and references")
    # <CODE BEGINS> ... <CODE ENDS>
    for m in re.finditer(r"<CODE BEGINS>.*?(?:<CODE ENDS>|\Z)", text, re.S):
        b.blank(m.start(), m.end(), "figures and code")
    # figures: blank-line-delimited blocks
    cur = b.text()
    k = 0
    while k < n:
        if not cur[spans[k][0]:spans[k][1]].strip():
            k += 1
            continue
        e = k
        while e < n and cur[spans[e][0]:spans[e][1]].strip():
            e += 1
        blk = [cur[spans[t][0]:spans[t][1]] for t in range(k, e)]
        if is_art_block(blk):
            b.blank(spans[k][0], spans[e - 1][1], "figures and code")
        elif len(blk) > 1 and all(re.match(r"^\s*\|", ln) for ln in blk):
            b.blank(spans[k][0], spans[e - 1][1], "quoted text")
        elif len(blk) == 1 and CAPTION.match(blk[0]):
            b.blank(spans[k][0], spans[k][1], "figures and code")
        k = e
    return b.text(), b.cats


# --- PEPs (reStructuredText)

RST_UNDER = re.compile(r"^([=\-~^\"'`#*+:.])\1{2,}\s*$")
PEP_DROP = re.compile(r"^(?:references|footnotes|copyright|"
                      r"acknowledge?ments?)\b", re.I)
ADMONITIONS = {"note", "warning", "tip", "important", "caution", "hint",
               "attention", "danger", "error", "admonition", "seealso",
               "versionadded", "versionchanged", "deprecated", "topic",
               "sidebar", "rubric"}
RST_TABLE_BORDER = re.compile(r"^\s*=+(?:\s+=+)+\s*$")
RST_GRID = re.compile(r"^\s*\+(?:[-=]+\+)+\s*$")


def indent_of(ln):
    return len(ln) - len(ln.lstrip(" "))


def block_end(lines, k, base):
    """Index after the indented block that follows line k: lines indented
    more than base, with blank lines inside."""
    e = k + 1
    last = k
    while e < len(lines):
        if lines[e].strip():
            if indent_of(lines[e]) <= base:
                break
            last = e
        e += 1
    return last + 1


def mask_pep(text):
    b = Blanker(text)
    spans = line_spans(text)
    lines = [text[a:z] for a, z in spans]
    n = len(lines)
    # RFC 2822 header block
    k = 0
    while k < n and lines[k].strip():
        k += 1
    if k:
        b.blank(0, spans[k - 1][1], "header")
    start = k
    # headings: title + underline (optionally overline)
    heads = []
    levels = []
    for i in range(start, n - 1):
        t, u = lines[i], lines[i + 1]
        if (t.strip() and not RST_UNDER.match(t) and RST_UNDER.match(u)
                and len(u.strip()) >= len(t.strip()) - 1
                and not t.startswith(" ")):
            over = i > 0 and RST_UNDER.match(lines[i - 1]) is not None
            key = (u.strip()[0], over)
            if key not in levels:
                levels.append(key)
            heads.append((i, levels.index(key), t.strip(), over))
    for idx, (i, lvl, title, over) in enumerate(heads):
        b.blank(spans[i - 1 if over else i][0], spans[i + 1][1], "headings")
        if PEP_DROP.match(title):
            end = len(text)
            for j, l2, _, o2 in heads[idx + 1:]:
                if l2 <= lvl:
                    end = spans[j - 1 if o2 else j][0]
                    break
            b.blank(spans[i + 1][1], end, "references and copyright")
    # directives, comments, footnotes, targets, substitutions
    for i in range(start, n):
        ln = lines[i]
        m = re.match(r"^(\s*)\.\.(?:\s|$)", ln)
        if not m:
            continue
        base = len(m.group(1))
        d = re.match(r"^\s*\.\.\s+([\w:-]+)::", ln)
        if d and d.group(1).lower() in ADMONITIONS:
            b.blank(*spans[i], "directives")
            continue
        e = block_end(lines, i, base)
        b.blank(spans[i][0], spans[e - 1][1], "directives")
    # literal blocks: a paragraph ending in "::"
    for i in range(start, n):
        ln = lines[i].rstrip()
        if not ln.endswith("::") or re.match(r"^\s*\.\.", ln):
            continue
        p = i
        while p > start and lines[p - 1].strip():
            p -= 1
        base = indent_of(lines[p])
        j = i + 1
        while j < n and not lines[j].strip():
            j += 1
        if j >= n or indent_of(lines[j]) <= base:
            continue
        e = block_end(lines, j - 1, base)
        b.blank(spans[i][1] + 1, spans[e - 1][1], "literal blocks")
        cut = spans[i][0] + len(ln)
        if ln.strip() == "::" or ln.endswith(" ::"):
            b.blank(cut - 2, cut, "literal blocks")
        else:
            b.blank(cut - 1, cut, "literal blocks")
    # tables: grid borders and simple tables
    i = start
    while i < n:
        if RST_GRID.match(lines[i]):
            e = i
            while e < n and lines[e].strip() and (
                    RST_GRID.match(lines[e]) or lines[e].lstrip()[:1] in "|+"):
                e += 1
            b.blank(spans[i][0], spans[e - 1][1], "tables")
            i = e
            continue
        if RST_TABLE_BORDER.match(lines[i]):
            e = i + 1
            while e < n:
                if RST_TABLE_BORDER.match(lines[e]) and (
                        e + 1 >= n or not lines[e + 1].strip()):
                    break
                e += 1
            e = min(e, n - 1)
            b.blank(spans[i][0], spans[e][1], "tables")
            i = e + 1
            continue
        i += 1
    # inline markup on what is left: keep the text, blank the markup
    lit = r"(?:[^`\n]|\n(?![ \t]*\n))"     # one line break allowed
    for m in re.finditer(r"``(" + lit + r"+?)``", b.text()):
        b.blank(m.start(), m.start() + 2, "roles and inline markup")
        b.blank(m.end() - 2, m.end(), "roles and inline markup")
    for m in re.finditer(r"(:[\w:+-]+:)?`(" + lit + r"+?)(?:\s*<[^`<>]*>)?`"
                         r"(__?)?", b.text()):
        inner_lo, inner_hi = m.span(2)
        b.blank(m.start(), inner_lo, "roles and inline markup")
        b.blank(inner_hi, m.end(), "roles and inline markup")
    for m in re.finditer(r"\s?\[(?:#\w*|\d+|\*)\]_", b.text()):
        b.blank(m.start(), m.end(), "roles and inline markup")
    targets = {t.lower() for t in re.findall(r"^\s*\.\. _([^:`\n]+):", text,
                                             re.M)}
    for m in re.finditer(r"\b([\w][\w.-]*?)(__?)(?=[\s.,;:)]|$)", b.text()):
        if m.group(1).lower() in targets:
            b.blank(m.start(2), m.end(2), "roles and inline markup")
    return b.text(), b.cats


# --- markdown sources: Rust RFCs and OpenTitan

MD_REFDEF = re.compile(r"^ {0,3}\[[^\]\n]+\]:\s*\S.*$", re.M)
RUST_META = re.compile(r"^- (?:Feature Name|Start Date|RFC PR|Rust Issue)"
                       r"\b", re.I)


MD_DELIM = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)+\|?\s*$")
MD_SETEXT = re.compile(r"^ {0,3}(?:=+|-+)\s*$")


def mask_md_common(b, text):
    labels = {m.group(1).lower() for m in
              re.finditer(r"^ {0,3}\[([^\]\n]+)\]:", text, re.M)}
    for m in MD_REFDEF.finditer(text):
        b.blank(m.start(), m.end(), "link definitions")
    for m in re.finditer(r"<!--.*?(?:-->|\Z)", text, re.S):
        b.blank(m.start(), m.end(), "comments")
    spans = line_spans(text)
    lines = [text[a:z] for a, z in spans]
    n = len(lines)
    for i, ln in enumerate(lines):
        if re.match(r"^ {0,3}#{1,6}(?:\s|$)", ln):
            b.blank(*spans[i], "headings")
        elif (i + 1 < n and ln.strip() and MD_SETEXT.match(lines[i + 1])
              and not MD_SETEXT.match(ln) and "|" not in ln
              and not re.match(r"^\s*(?:[-*+]|\d+\.)\s", ln)):
            b.blank(spans[i][0], spans[i + 1][1], "headings")
    # pipe tables, with or without outer pipes
    for i, ln in enumerate(lines):
        if not MD_DELIM.match(ln):
            continue
        lo = i
        while lo > 0 and lines[lo - 1].strip() and "|" in lines[lo - 1]:
            lo -= 1
        hi = i
        while hi + 1 < n and lines[hi + 1].strip() and "|" in lines[hi + 1]:
            hi += 1
        b.blank(spans[lo][0], spans[hi][1], "tables")
    # links: keep the text; ticfinder blanks an inline link's "](target)"
    for m in re.finditer(r"(?<!!)\[(?=[^\[\]\n]+\]\()", text):
        b.blank(m.start(), m.end(), "links")
    for m in re.finditer(r"\[([^\[\]\n]+)\]\[([^\[\]\n]*)\]", text):
        b.blank(m.start(), m.start(1), "links")
        b.blank(m.end(1), m.end(), "links")
    for m in re.finditer(r"(?<![\]\w!])\[([^\[\]\n]+)\](?![\[(:])", text):
        if m.group(1).lower() in labels:
            b.blank(m.start(), m.start() + 1, "links")
            b.blank(m.end() - 1, m.end(), "links")


def mask_rust(text):
    b = Blanker(text)
    spans = line_spans(text)
    lines = [text[a:z] for a, z in spans]
    k = 0
    while k < len(lines) and not lines[k].strip():
        k += 1
    if k < len(lines) and RUST_META.match(lines[k]):
        e = k
        while e < len(lines) and lines[e].strip():
            e += 1
        b.blank(spans[k][0], spans[e - 1][1], "header")
    mask_md_common(b, text)
    return b.text(), b.cats


OT_KEEP_ARG = {"regref", "otbninsnref"}


def mask_opentitan(text):
    b = Blanker(text)
    m = re.match(r"\A---\n.*?\n---[ \t]*\n", text, re.S)
    if m:
        b.blank(0, m.end(), "header")
    mask_md_common(b, text)
    for m in re.finditer(r"<!--\s*BEGIN CMDGEN.*?(?:<!--\s*END CMDGEN[^>]*-->"
                         r"|\Z)", text, re.S):
        b.blank(m.start(), m.end(), "generated")
    for m in re.finditer(r"\{\{<\s*(\w+)[^>]*>\}\}.*?\{\{<\s*/\s*\1\s*>\}\}",
                         text, re.S):
        b.blank(m.start(), m.end(), "generated")
    for m in re.finditer(r"\{\{[<%]\s*(/?\w*)(.*?)[>%]\}\}", text, re.S):
        a = re.match(r'\s*"([^"\n]+)"\s*$', m.group(2))
        if m.group(1).lower() in OT_KEEP_ARG and a:
            lo, hi = m.start(2) + a.start(1), m.start(2) + a.end(1)
            b.blank(m.start(), lo, "shortcodes")
            b.blank(hi, m.end(), "shortcodes")
        else:
            b.blank(m.start(), m.end(), "shortcodes")
    return b.text(), b.cats


# --- RISC-V (LaTeX)

TEX_TABLE_ENVS = ("tabular", "tabular*", "table", "table*", "figure",
                  "figure*", "verbatim", "lstlisting", "longtable", "verbbox")
TABLE_FILE_SHARE = 0.8


def tex_env_spans(text, names):
    out = []
    for name in names:
        rb = re.compile(r"\\begin\{" + re.escape(name) + r"\}")
        re_ = re.compile(r"\\end\{" + re.escape(name) + r"\}")
        pos = 0
        while True:
            m = rb.search(text, pos)
            if not m:
                break
            e = re_.search(text, m.end())
            hi = e.end() if e else len(text)
            out.append((m.start(), hi))
            pos = hi
    return out


def mask_riscv(text):
    b = Blanker(text)
    body = AB.strip_comments(text)
    nonws = len("".join(body.split())) or 1
    inside = sum(len("".join(body[lo:hi].split()))
                 for lo, hi in merge_spans(tex_env_spans(body,
                                                         TEX_TABLE_ENVS)))
    if inside / nonws > TABLE_FILE_SHARE:
        b.blank(0, len(text), "table file")
        return b.text(), b.cats
    for lo, hi in tex_env_spans(text, ("verbbox",)):
        b.blank(lo, hi, "floats and code")
    pre = b.text()
    masked, info = AB.mask_tex(pre)
    for k, v in info.get("by_category", {}).items():
        b.cats[k] += v
    out = Blanker(masked)
    for m in re.finditer(r"``|''", masked):
        out.blank(m.start(), m.end(), "tex quotes")
    b.cats.update(out.cats)
    return out.text(), b.cats


def merge_spans(sp):
    out = []
    for lo, hi in sorted(sp):
        if out and lo <= out[-1][1]:
            out[-1] = (out[-1][0], max(out[-1][1], hi))
        else:
            out.append((lo, hi))
    return out


MASKERS = {"peps": mask_pep, "ietf": mask_rfc, "rust": mask_rust,
           "riscv": mask_riscv, "opentitan": mask_opentitan}
SUFFIX = {"peps": ".txt", "ietf": ".txt", "rust": ".md", "riscv": ".txt",
          "opentitan": ".md"}


# ------------------------------------------------------------ selftest
#
# (source, name, input, expected kept text with whitespace collapsed).
# Every rule has a positive row (it blanks) and a negative row (ordinary
# prose that looks close is kept). Synthetic text only.

FOOT = "Doe                          Standards Track                    [Page 3]"
HEAD = "\fRFC 9999                       Widgets                     May 2020"
RFC_FRONT = ("Internet Engineering Task Force (IETF)              J. Doe\n"
             "Request for Comments: 9999                       May 2020\n\n"
             "                     The Widget Protocol\n\n")
SELF_ROWS = [
    # IETF RFCs
    ("ietf", "front matter blanked, abstract kept",
     RFC_FRONT + "Abstract\n\n   This document defines widgets.\n",
     "This document defines widgets."),
    ("ietf", "status, copyright and contents blanked",
     "Abstract\n\n   Widgets.\n\nStatus of This Memo\n\n   This is an "
     "Internet Standards Track document.\n\nCopyright Notice\n\n   Copyright "
     "(c) 2020 IETF Trust.\n\nTable of Contents\n\n   1. Intro ......... 2\n"
     "\n1.  Introduction\n\n   Widgets move data.\n",
     "Widgets. Widgets move data."),
    ("ietf", "references with subsections blanked, appendix kept",
     "1.  Intro\n\n   Text one.\n\n8.  References\n\n8.1.  Normative "
     "References\n\n   [RFC2119]  Bradner, S., \"Key words\".\n\n8.2.  "
     "Informative References\n\n   [X]  Y.\n\nAppendix A.  Notes\n\n"
     "   Text two.\n", "Text one. Text two."),
    ("ietf", "authors' addresses blanked",
     "1.  Intro\n\n   Text one.\n\nAuthors' Addresses\n\n   Jane Doe\n"
     "   Example Corp\n   Email: jd@example.com\n", "Text one."),
    ("ietf", "a section about references is kept",
     "1.  Intro\n\n   Text one.\n\n2.  Referencing Widgets\n\n   A widget "
     "may refer to another.\n", "Text one. A widget may refer to another."),
    ("ietf", "page break inside a paragraph joins it",
     "1.  Intro\n\n   The widget sends a frame to the\n\n\n\n" + FOOT + "\n"
     + HEAD + "\n\n\n   peer after a delay.\n",
     "The widget sends a frame to the peer after a delay."),
    ("ietf", "page break after a sentence keeps the newlines",
     "1.  Intro\n\n   First paragraph ends.\n\n" + FOOT + "\n" + HEAD
     + "\n\n   Second paragraph.\n",
     "First paragraph ends. Second paragraph."),
    ("ietf", "packet diagram blanked",
     "1.  Intro\n\n   The header is:\n\n    0                   1\n"
     "    0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5\n   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
     "   |    Type     |    Length     |\n   +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+\n"
     "\n                 Figure 1: Header\n\n   Type is one octet.\n",
     "The header is: Type is one octet."),
    ("ietf", "flow diagram with arrows blanked",
     "1.  Intro\n\n   Client                Server\n     | ---- Hello ----> |\n"
     "     | <--- Reply ----- |\n\n   The client starts.\n",
     "The client starts."),
    ("ietf", "prose with a dash and a bar is kept",
     "1.  Intro\n\n   A value of 0 or 1 -- the flag -- is set when the\n"
     "   sender uses the | separator.\n",
     "A value of 0 or 1 -- the flag -- is set when the sender uses the "
     "| separator."),
    ("ietf", "bar-quoted text blanked",
     "1.  Intro\n\n   NEW TEXT:\n\n   | If the answer does not contain the\n"
     "   | attribute, the offerer MUST NOT mux.\n\n   Done.\n",
     "NEW TEXT: Done."),
    ("ietf", "one line starting with a bar is kept",
     "1.  Intro\n\n   | is the separator used here.\n",
     "| is the separator used here."),
    ("ietf", "code begins and ends blanked",
     "1.  Intro\n\n   The module:\n\n   <CODE BEGINS>\n   module x {\n"
     "     leaf y;\n   }\n   <CODE ENDS>\n\n   Done.\n", "The module: Done."),
    ("ietf", "BCP 14 key words paragraph blanked",
     "1.  Intro\n\n   The key words \"MUST\", \"MUST NOT\" and \"MAY\" in this "
     "document are to be\n   interpreted as described in BCP 14.\n\n   Text.\n",
     "Text."),
    ("ietf", "a sentence that uses MUST is kept",
     "1.  Intro\n\n   The sender MUST retry the key words exchange.\n",
     "The sender MUST retry the key words exchange."),
    # PEPs
    ("peps", "header block blanked",
     "PEP: 9999\nTitle: A thing\nAuthor: J. Doe\nCreated: 01-Jan-2020\n\n"
     "Abstract\n========\n\nThis PEP adds a thing.\n", "This PEP adds a thing."),
    ("peps", "references, footnotes and copyright blanked",
     "PEP: 1\n\nAbstract\n========\n\nText.\n\nReferences\n==========\n\n"
     ".. [1] https://x\n\nFootnotes\n=========\n\nSome note.\n\nCopyright\n"
     "=========\n\nThis document is placed in the public domain.\n",
     "Text."),
    ("peps", "subsection under references blanked, next section kept",
     "PEP: 1\n\nReferences\n==========\n\nIntro refs.\n\nMore\n----\n\nX.\n"
     "\nRationale\n=========\n\nBecause.\n", "Because."),
    ("peps", "a section on reference counting is kept",
     "PEP: 1\n\nReference Counting\n==================\n\nObjects hold "
     "counts.\n", "Objects hold counts."),
    ("peps", "literal block blanked, colon kept",
     "PEP: 1\n\nUse it like this::\n\n    x = f(1)\n    y = g(x)\n\n"
     "Then return.\n", "Use it like this: Then return."),
    ("peps", "expanded literal marker blanked",
     "PEP: 1\n\nFor example ::\n\n    x = 1\n\nDone.\n", "For example Done."),
    ("peps", "a sentence ending in a colon is not a literal block",
     "PEP: 1\n\nThere are two cases:\n\n* one case.\n* two cases.\n",
     "There are two cases: * one case. * two cases."),
    ("peps", "code-block directive blanked",
     "PEP: 1\n\nText.\n\n.. code-block:: python\n\n   import os\n   "
     "os.exit()\n\nMore.\n", "Text. More."),
    ("peps", "note directive keeps its body",
     "PEP: 1\n\n.. note::\n\n   This changes later.\n", "This changes later."),
    ("peps", "comment and target blanked",
     "PEP: 1\n\nText.\n\n..\n   Local Variables:\n   mode: indented-text\n\n"
     ".. _PEP 8: https://x\n", "Text."),
    ("peps", "roles keep their text",
     "PEP: 1\n\nSee :pep:`484` and :func:`len` and :class:`Foo <a.Foo>`.\n",
     "See 484 and len and Foo ."),
    ("peps", "inline literal and link keep their text",
     "PEP: 1\n\nCall ``f()`` via `the docs <https://x>`_ now [1]_.\n",
     "Call f() via the docs now ."),
    ("peps", "inline literal across a line break keeps its text",
     "PEP: 1\n\nIt reads ``[x,\ny]`` as a subscript.\n",
     "It reads [x, y] as a subscript."),
    ("peps", "named link reference keeps its word",
     "PEP: 1\n\nA known problem in pycoverage_.\n\n.. _pycoverage: "
     "https://x\n", "A known problem in pycoverage ."),
    ("peps", "a trailing underscore with no target is kept",
     "PEP: 1\n\nPass class_ as the name.\n", "Pass class_ as the name."),
    ("peps", "simple table blanked",
     "PEP: 1\n\nText.\n\n=====  =====\nA      B\n=====  =====\n1      2\n"
     "=====  =====\n\nAfter.\n", "Text. After."),
    ("peps", "grid table blanked",
     "PEP: 1\n\nText.\n\n+-----+-----+\n| a   | b   |\n+-----+-----+\n\n"
     "After.\n", "Text. After."),
    ("peps", "emphasis and plain prose kept",
     "PEP: 1\n\nThis is *very* important = not optional.\n",
     "This is *very* important = not optional."),
    # Rust RFCs
    ("rust", "metadata header blanked",
     "- Feature Name: `foo`\n- Start Date: 2020-01-01\n- RFC PR: [x](y)\n\n"
     "# Summary\n\nAdd foo.\n", "Add foo."),
    ("rust", "a list at the top that is not metadata is kept",
     "- First point.\n- Second point.\n", "- First point. - Second point."),
    ("rust", "link definitions blanked",
     "# Summary\n[summary]: #summary\n\nText.\n\n[1]: https://x\n",
     "Text."),
    ("rust", "bracketed text in prose kept",
     "Use [this]: it is fine.\n", "Use [this]: it is fine."),
    ("rust", "atx and setext headings blanked",
     "# Motivation\n\nText.\n\nGuide\n-----\n\nMore.\n\n## Why {#why}\n",
     "Text. More."),
    ("rust", "a hash inside a sentence is kept",
     "Issue #12 says so.\n", "Issue #12 says so."),
    ("rust", "reference link keeps its text",
     "As in the [prior art][prior-art] and [RFC 2045].\n\n[prior-art]: #p\n"
     "[RFC 2045]: https://x\n", "As in the prior art and RFC 2045 ."),
    ("rust", "inline link opening bracket blanked",
     "See [the guide](https://x) now.\n", "See the guide](https://x) now."),
    ("rust", "array index in prose kept",
     "Read a[0] and [1, 2] here.\n", "Read a[0] and [1, 2] here."),
    ("opentitan", "pipe table without outer pipes blanked",
     "Params:\n\nName | Default | Notes\n---- | ------- | -----\nN | 2 | "
     "rounds\n\nDone.\n", "Params: Done."),
    ("opentitan", "a sentence with one pipe is kept",
     "Use a | b to join.\n", "Use a | b to join."),
    ("rust", "html comment blanked",
     "Text.\n<!-- a\nmultiline note -->\nMore.\n", "Text. More."),
    # OpenTitan
    ("opentitan", "front matter blanked",
     "---\ntitle: \"Widget Technical Specification\"\n---\n\n# Overview\n\n"
     "The widget counts.\n", "The widget counts."),
    ("opentitan", "register reference keeps its name",
     "Write {{< regref \"CTRL.EN\" >}} to start.\n", "Write CTRL.EN to start."),
    ("opentitan", "generated register table blanked",
     "Registers:\n\n{{< incGenFromIpDesc \"../data/x.hjson\" \"registers\" >}}"
     "\n\nDone.\n", "Registers: Done."),
    ("opentitan", "wavejson block blanked",
     "Timing:\n\n{{< wavejson >}}\n{signal: [{name: 'clk'}]}\n"
     "{{< /wavejson >}}\n\nDone.\n", "Timing: Done."),
    ("opentitan", "cmdgen region blanked",
     "Help:\n<!-- BEGIN CMDGEN util/x.py -->\nusage: x\n<!-- END CMDGEN -->\n"
     "Done.\n", "Help: Done."),
    ("opentitan", "braces in prose kept",
     "The set {a, b} holds two items.\n", "The set {a, b} holds two items."),
    # RISC-V
    ("riscv", "chapter prose kept, encoding table blanked",
     "\\chapter{Base}\nThe base ISA is small.\n\\begin{center}\\begin{tabular}"
     "{cc}\n\\instbitrange{31}{25} & opcode \\\\\n\\end{tabular}\\end{center}"
     "\nIt has 40 instructions.\n",
     "The base ISA is small. It has 40 instructions."),
    ("riscv", "commentary box kept",
     "\\begin{commentary}\nWe chose this for simplicity.\n\\end{commentary}\n",
     "We chose this for simplicity."),
    ("riscv", "tex quotes blanked",
     "the ``Arbitrary store'' at the end\n", "the Arbitrary store at the end"),
    ("riscv", "an apostrophe is kept",
     "the hart's own store\n", "the hart's own store"),
    ("riscv", "verbbox code blanked",
     "Text.\n\\begin{verbbox}\n  li a0, 1\n\\end{verbbox}\nMore.\n",
     "Text. More."),
    ("riscv", "table file blanked whole",
     "\\begin{table}\n\\begin{tabular}{ll}\nADD & 0110011 \\\\\nSUB & 0110011 "
     "\\\\\nXOR & 0110011 \\\\\n\\end{tabular}\n\\caption{Opcodes.}\n"
     "\\end{table}\n", ""),
    ("riscv", "chapter with one table is not a table file",
     "The opcode map follows and is described in prose at some length here "
     "so that the prose dominates the file.\n\\begin{table}\\begin{tabular}"
     "{l}\nA \\\\\n\\end{tabular}\\end{table}\nMore prose follows the table "
     "and explains each column.\n",
     "The opcode map follows and is described in prose at some length here "
     "so that the prose dominates the file. More prose follows the table "
     "and explains each column."),
]


def cmd_selftest(args):
    fails = 0
    for src, name, text, want in SELF_ROWS:
        got, _ = MASKERS[src](text)
        joined = " ".join(got.split())
        ok = len(got) == len(text) and joined == want
        # offsets: every kept non-space character is the source's own
        ok = ok and all(g == t for g, t in zip(got, text) if not g.isspace())
        if not ok or args.verbose:
            print(f"{'ok ' if ok else 'FAIL'} {src}: {name}")
        if not ok:
            print(f"     want {want!r}\n     got  {joined!r}"
                  f" (len {len(got)} vs {len(text)})")
            fails += 1
    print(f"selftest: {len(SELF_ROWS) - fails}/{len(SELF_ROWS)} rows pass")
    return 1 if fails else 0


# --------------------------------------------------------- mask-report

RESIDUE = {
    "backslash or braces": re.compile(r"\\[A-Za-z]|\{\{|\}\}"),
    "rst markup": re.compile(r"::|:\w+:`|`_|\.\. "),
    "table or diagram characters": re.compile(r"\+-{2,}|\|.*\||-{3,}>|={4,}"),
    "page furniture": re.compile(r"\[Page \d+\]|\bRFC \d{4} .* (?:19|20)\d\d"),
    "code-like": re.compile(r"[;{}]\s*$|\b\w+\(\)\s*;|==|!=|&&|\|\|"),
}
SPOT_SEED = SAMPLE_SEED + 1


def nonws(s):
    return len(s) - sum(c.isspace() for c in s)


def load_docs():
    if not SAMPLE.exists():
        sys.exit("no sample; run fetch")
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    recs = {}
    for line in DOCS.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        recs[r["id"]] = r
    return sample, {src: [recs[i] for i in sorted(v["ids"])]
                    for src, v in sample["sources"].items()}


def kept_text(rec, tf=None):
    """(exclusion-masked text, its rule counts, ticfinder-masked text, tf
    stats). The ticfinder layer is what analyse() itself applies to a file
    with this source's suffix."""
    raw = (SPECS / rec["file"]).read_text(encoding="utf-8")
    kept, cats = MASKERS[rec["source"]](raw)
    final, st = None, {}
    if tf is not None:
        final = tf.mask_markdown(kept, st, tf.CODE_MASK,
                                 markdown=SUFFIX[rec["source"]] == ".md")
    return raw, kept, cats, final, st


def median(v):
    v = sorted(v)
    if not v:
        return math.nan
    h = len(v) // 2
    return v[h] if len(v) % 2 else (v[h - 1] + v[h]) / 2


def mask_summary(tf):
    """Per source and per document: raw and kept non-space characters,
    words kept, shares by layer and by rule."""
    _, docs = load_docs()
    out = {}
    for src in SOURCES:
        rows = []
        for r in docs[src]:
            raw, kept, cats, final, st = kept_text(r, tf)
            n0 = nonws(raw) or 1
            rows.append({"id": r["id"], "raw_words": r["raw_words"],
                         "words": len(re.findall(r"[A-Za-z]+", final)),
                         "excl_pct": 100 * (n0 - nonws(kept)) / n0,
                         "pct": 100 * (n0 - nonws(final)) / n0,
                         "cats": cats, "tf_md": st["md_masked_chars"],
                         "tf_code": st["code_masked_chars"], "n0": n0,
                         "final": final})
        out[src] = rows
    return out


def cmd_mask_report(args):
    tf = AR.load_tf()
    summ = mask_summary(tf)
    for src in SOURCES:
        rows = summ[src]
        pct = [x["pct"] for x in rows]
        tot0 = sum(x["n0"] for x in rows) or 1
        cats = Counter()
        for x in rows:
            cats.update(x["cats"])
        cats["ticfinder markdown rules"] = sum(x["tf_md"] for x in rows)
        cats["ticfinder code masker"] = sum(x["tf_code"] for x in rows)
        print(f"=== {src}: {len(rows)} documents, raw words "
              f"{sum(x['raw_words'] for x in rows):,}, kept words "
              f"{sum(x['words'] for x in rows):,}")
        print(f"  masked share (all layers): median {median(pct):.1f}%, "
              f"min {min(pct):.1f}%, max {max(pct):.1f}%; over 40%: "
              f"{sum(p > 40 for p in pct)}; exclusions alone median "
              f"{median([x['excl_pct'] for x in rows]):.1f}%")
        print("  blanked non-space chars by rule (share of raw): " + ", ".join(
            f"{k} {100 * v / tot0:.1f}%" for k, v in cats.most_common() if v))
        print(f"  documents with under 100 kept words: "
              f"{sum(x['words'] < 100 for x in rows)}")
        hits, pool = Counter(), []
        for x in rows:
            for s in AB.sentences(x["final"], 0, len(x["final"])):
                pool.append(s)
                for k, rx in RESIDUE.items():
                    if rx.search(s):
                        hits[k] += 1
        print(f"  residue scan over {len(pool):,} sentences: " + (", ".join(
            f"{k} {v} ({100 * v / max(len(pool), 1):.2f}%)"
            for k, v in hits.items()) or "no hits"))
        if not args.quiet:
            rng = random.Random(f"{SPOT_SEED}-spot-{src}")
            pick = rng.sample(pool, min(args.n, len(pool)))
            print(f"\n  --- {len(pick)} random masked sentences ({src}); "
                  "console only")
            for i, s in enumerate(pick, 1):
                print(f"  [{src} {i}] {s}")
        print()


# ------------------------------------------------------------- analyse

BOOT_SEED = 9009            # bootstrap seed, new for TF-009
MIN_N = AB.MIN_N
LEVELS = AB.LEVELS
AUTHOR_TABLE = SPECS / "author.jsonl"   # per-file counts, no text
TMP = SPECS / "tmp"
ARXIV_PIN = "0aa23656bb24"  # the TF-015 full tables (ticfinder 22cf4fa);
#   TF-010 to TF-014 used f0fc55a44f37, now in private/arxiv/bodies-tf015/;
#   TF-008/TF-009 used 81ade1e30516, now in private/arxiv/bodies-tf008/
ARXIV_DIR = None            # None: private/arxiv/bodies/
AUTHOR_LEVELS = ("construction", "pattern")
NAMES = {"peps": "PEPs", "ietf": "IETF RFCs", "rust": "Rust RFCs",
         "riscv": "RISC-V", "opentitan": "OpenTitan"}
POOL = "equal"              # the pooled rate requirements 13 to 15 use


def sha16(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]


def use_tables(table_dir=None, arxiv_dir=None, arxiv_sha=None):
    """Read the spec and author tables from a snapshot directory, and the
    arXiv tables from another directory or ticfinder version, so an older
    report can be rebuilt after a rerun replaced the tables (TF-010)."""
    global TABLE, FINDINGS, AUTHOR_TABLE, ARXIV_PIN, ARXIV_DIR
    if table_dir:
        d = Path(table_dir)
        TABLE, FINDINGS = d / "per_doc.jsonl", d / "findings.jsonl"
        AUTHOR_TABLE = d / "author.jsonl"
    if arxiv_dir:
        ARXIV_DIR = arxiv_dir
    if arxiv_sha:
        ARXIV_PIN = arxiv_sha


def phrase_setup(tf):
    extra = []
    for f in tf.discover_phrase_files(None):
        extra.extend(tf.load_phrase_file(f))
    return extra, {e["id"] for e in extra} | set(tf.PHRASE_PATTERNS)


def finding_rec(f, **kw):
    return {**kw, "construction": f.construction,
            "pattern": f.pattern or "-", "label": f.label, "text": f.text,
            "context": f.context}


def run_spec_analysis(tf, nlp, extra, phrase_ids, ver):
    """ticfinder over the kept text of every sampled document. A document
    whose kept text and ticfinder are unchanged keeps its stored row."""
    _, docs = load_docs()
    done, old_f = {}, defaultdict(list)
    if TABLE.exists():
        for line in TABLE.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            done[r["id"]] = r
    if FINDINGS.exists():
        for line in FINDINGS.read_text(encoding="utf-8").splitlines():
            f = json.loads(line)
            old_f[f["id"]].append(f)
    todo = [r for src in SOURCES for r in docs[src]]
    TMP.mkdir(parents=True, exist_ok=True)
    rows, allf = [], []
    t0, n_new, w_new = time.monotonic(), 0, 0
    for i, rec in enumerate(todo, 1):
        _, kept, _, _, _ = kept_text(rec)
        key = (ver["sha256"], sha16(kept))
        r = done.get(rec["id"])
        if r and (r["tf_sha256"], r["mask_sha"]) == key:
            rows.append(r)
            allf.extend(old_f[rec["id"]])
            continue
        tmp = TMP / (rec["id"] + SUFFIX[rec["source"]])
        tmp.write_text(kept, encoding="utf-8")
        try:
            fs, st = tf.analyse(str(tmp), nlp, None, extra, set())
        finally:
            tmp.unlink()
        rows.append({"id": rec["id"], "source": rec["source"],
                     "tf_sha256": ver["sha256"], "mask_sha": key[1],
                     "words": st["words"], "tf_masked_pct": st["masked_pct"],
                     "counts": AB.counts_of(fs, phrase_ids)})
        allf.extend(finding_rec(f, id=rec["id"], source=rec["source"])
                    for f in fs)
        n_new += 1
        w_new += st["words"]
        if n_new % 25 == 0:
            el = time.monotonic() - t0
            print(f"  {i}/{len(todo)} documents, {w_new:,} words, {el:.0f}s "
                  f"({w_new / max(el, 1):.0f} words/s)", file=sys.stderr,
                  flush=True)
    TABLE.write_text("".join(json.dumps(r) + "\n" for r in rows),
                     encoding="utf-8")
    FINDINGS.write_text("".join(json.dumps(f) + "\n" for f in allf),
                        encoding="utf-8")
    try:
        TMP.rmdir()
    except OSError:
        pass
    print(f"analysed {n_new} documents ({len(rows) - n_new} up to date), "
          f"{time.monotonic() - t0:.0f}s", file=sys.stderr)


def author_files():
    import os
    ws = os.environ.get("WRITING_SAMPLES")
    if not ws or not Path(ws).is_dir():
        sys.exit("WRITING_SAMPLES is not set; source tools/setup.sh")
    return Path(ws), sorted(p for p in Path(ws).rglob("*") if p.is_file()
                            and p.suffix.lower() != ".docx")


def run_author(tf, nlp, extra, phrase_ids, ver):
    """ticfinder on the author's spec files, read in place as TF-003 did.
    Stores per-file word counts and construction and pattern counts only,
    keyed by a hash of the path: no text, names or findings."""
    root, files = author_files()
    rows = []
    for p in files:
        fs, st = tf.analyse(str(p), nlp, None, extra, set())
        m = {}
        masked = tf.mask_markdown(p.read_text(encoding="utf-8"), m,
                                  tf.CODE_MASK,
                                  markdown=tf.is_markdown_path(p))
        c = AB.counts_of(fs, phrase_ids)
        rows.append({"id": sha16(str(p.relative_to(root))),
                     "tf_sha256": ver["sha256"], "words": st["words"],
                     "words_ascii": len(re.findall(r"[A-Za-z]+", masked)),
                     "counts": {lvl: c[lvl] for lvl in AUTHOR_LEVELS}})
    AUTHOR_TABLE.write_text("".join(json.dumps(r) + "\n" for r in rows),
                            encoding="utf-8")
    print(f"author: {len(rows)} files", file=sys.stderr)


def run_analysis():
    ver = AR.tf_version()
    tf = AR.load_tf()
    nlp = tf.load_model("en_core_web_md")
    nlp.max_length = 5_000_000
    extra, phrase_ids = phrase_setup(tf)
    run_spec_analysis(tf, nlp, extra, phrase_ids, ver)
    run_author(tf, nlp, extra, phrase_ids, ver)


def load_tables(pin=None):
    """Spec rows per source, author rows and arXiv pre-window rows (all
    sections, the TF-008 full tables, read only)."""
    ver = AR.tf_version(pin)
    sample, docs = load_docs()
    want = {r["id"] for src in SOURCES for r in docs[src]}
    by = defaultdict(list)
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["id"] in want and r["tf_sha256"] == ver["sha256"]:
            by[r["source"]].append(r)
    for src in SOURCES:
        if len(by[src]) != len(docs[src]):
            sys.exit(f"{src}: table has {len(by[src])} of {len(docs[src])} "
                     "documents for this ticfinder version; run analyse")
        by[src].sort(key=lambda r: r["id"])
    author = [r for r in (json.loads(x) for x in AUTHOR_TABLE.read_text(
        encoding="utf-8").splitlines()) if r["tf_sha256"] == ver["sha256"]]
    if not author:
        sys.exit("no author rows for this ticfinder version; run analyse")
    author.sort(key=lambda r: r["id"])
    AB.use_paths(ARXIV_DIR, "full")
    _, arows, _ = AB.load_body_table(ARXIV_PIN)
    arxiv = [{"id": r["id"], "words": r["words"]["all"],
              "counts": r["counts"]["all"]} for r in arows["pre"]]
    return ver, sample, docs, by, author, arxiv


class MBoot:
    """Bootstrap over documents: one index matrix per group (each source,
    the arXiv pre bodies, the author's files), drawn in that order from one
    seed. A pooled draw combines the source draws of the same row of the
    matrices."""

    def __init__(self, groups, draws, seed):
        import numpy as np
        self.np = np
        self.rows = groups
        rng = np.random.default_rng(seed)
        self.idx = {g: rng.integers(0, len(v), size=(draws, len(v)))
                    for g, v in groups.items()}
        self.W = {g: np.array([r["words"] for r in v], dtype=float)
                  for g, v in groups.items()}
        self.Wd = {g: self.W[g][self.idx[g]].sum(axis=1) for g in groups}
        self.cache = {}

    def group(self, g, lvl, key):
        np = self.np
        keys = key if isinstance(key, tuple) else (key,)  # TF-015: sums
        c = np.array([sum(r["counts"].get(lvl, {}).get(k, 0) for k in keys)
                      for r in self.rows[g]], dtype=float)
        cd = c[self.idx[g]].sum(axis=1)
        with np.errstate(divide="ignore", invalid="ignore"):
            d = cd / self.Wd[g] * 1000
        return {"n": int(c.sum()), "docs": int((c > 0).sum()),
                "rate": c.sum() / self.W[g].sum() * 1000, "ci": AB.pct(d),
                "draws": d, "cd": cd}

    def stat(self, lvl, key):
        ck = (lvl, key)
        if ck in self.cache:
            return self.cache[ck]
        np = self.np
        s = {g: self.group(g, lvl, key) for g in self.rows}
        src = [s[g] for g in SOURCES]
        ww_d = sum(x["cd"] for x in src) / sum(self.Wd[g] for g in SOURCES) \
            * 1000
        ew_d = np.mean([x["draws"] for x in src], axis=0)
        pool = {
            "n": sum(x["n"] for x in src), "docs": sum(x["docs"] for x in src),
            "words": {"rate": sum(x["n"] for x in src)
                      / sum(self.W[g].sum() for g in SOURCES) * 1000,
                      "ci": AB.pct(ww_d), "draws": ww_d},
            "equal": {"rate": float(np.mean([x["rate"] for x in src])),
                      "ci": AB.pct(ew_d), "draws": ew_d}}
        res = {"g": s, "pool": pool}
        self.cache[ck] = res
        return res


def ratio(a, b, ad, bd):
    import numpy as np
    with np.errstate(divide="ignore", invalid="ignore"):
        r = a / b if b else (math.inf if a else math.nan)
        rd = ad / bd
    return r, AB.pct(rd, nearest=True)


def side(lo, hi):
    if lo > 1:
        return "above 1"
    if hi < 1:
        return "below 1"
    return "spans 1"


def ci_txt(x, ci):
    return AB.ci_txt(x, ci)


def jrate(rate, ci, **kw):
    return {**kw, "rate": AR.jnum(rate), "rate_lo": AR.jnum(ci[0]),
            "rate_hi": AR.jnum(ci[1])}


def cmd_analyse(args):
    if args.sample:
        return show_sample(args.sample, args.n)
    if not args.report_only:
        run_analysis()
    write_report(args)


def show_sample(key, n):
    """Console only: n random findings per source for a construction, a
    CID|pattern or a CID|phrase key. Writes nothing."""
    pool = defaultdict(list)
    for line in FINDINGS.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        k = (f["construction"], f"{f['construction']}|{f['pattern']}",
             f"{f['construction']}|{' '.join(f['text'].lower().split())}")
        if key in k:
            pool[f["source"]].append(f)
    for src in SOURCES:
        rng = random.Random(f"{SAMPLE_SEED}-check-{key}-{src}")
        pick = rng.sample(pool[src], min(n, len(pool[src])))
        print(f"\n=== {key} {src}: {len(pick)} of {len(pool[src])}")
        for i, f in enumerate(pick, 1):
            print(f"\n[{src} {i}] {f['label']}\n  MATCH: {f['text']}\n  "
                  f"SENT:  {' '.join(f['context'].split())[:400]}")


def write_report(args):
    import numpy as np
    ver, sample, docs, by, author, arxiv = load_tables(args.table_sha)
    groups = {**{s: by[s] for s in SOURCES}, "arxiv": arxiv,
              "author": author}
    draws, seed = args.draws, args.seed
    B = MBoot(groups, draws, seed)
    keys = {lvl: sorted({k for s in SOURCES for r in by[s]
                         for k in r["counts"].get(lvl, {})})
            for lvl in LEVELS}
    akeys = {lvl: sorted({k for r in arxiv for k in r["counts"].get(lvl, {})})
             for lvl in LEVELS}
    ukeys = {lvl: sorted({k for r in author for k in r["counts"].get(lvl, {})})
             for lvl in AUTHOR_LEVELS}
    pat_of = defaultdict(set)
    for g in groups.values():
        for r in g:
            for k in r["counts"].get("pattern", {}):
                pat_of[k.split("|")[0]].add(k)

    def single(lvl, k):
        return lvl == "pattern" and pat_of[k.split("|")[0]] == {k}

    today = __import__("datetime").date.today().isoformat()
    out_path = Path(args.report or AR.HERE / f"spec-baseline-{today}.md")
    L, J = [], []
    p = L.append
    tf = AR.load_tf()
    summ = mask_summary(tf)
    W = {s: int(B.W[s].sum()) for s in groups}
    Wsrc = sum(W[s] for s in SOURCES)

    p("# ticfinder construction rates in public pre-2022 design and "
      "specification documents")
    p("")
    p(f"Generated {today} by `eval/spec_baseline.py` (TF-009). Aggregates "
      "only: no document text, titles, file names or document numbers, and "
      "for the author's specifications no per-file figures. Ratios here "
      "compare two corpora (or one source with the pool). They are not "
      "likelihood ratios; those are step 8.")
    p("")
    p("## Setup")
    p("")
    p("| item | value |")
    p("|---|---|")
    p("| sources | Python PEPs, IETF RFCs, Rust RFCs, the RISC-V ISA manuals "
      "and the OpenTitan hardware docs, each as of its last commit (or "
      "index entry) before 2022-01-01, with documents dated 2018 to 2021 "
      "(the TF-004 pre window) |")
    p(f"| sample | every dated document, except a source over "
      f"{SOURCE_CAP:,} raw words, which is shuffled with seed "
      f"`{SAMPLE_SEED}-<source>` and walked until the cap |")
    p("| exclusions | per source, in place (`selftest` holds the rows): "
      "boilerplate, front matter, references, acknowledgements, headings, "
      "page furniture, figures, tables, code, markup and generated "
      "regions; then ticfinder's own masking |")
    p(f"| ticfinder | `tools/ticfinder.py` at {ver['commit']} (sha256 "
      f"{ver['sha256']}); defaults: `en_core_web_md`, code masker on, "
      "`ticfinder-phrases.json`; Rust and OpenTitan kept text analysed as "
      "`.md`, the others as `.txt` |")
    p(f"| arXiv side | TF-008 full-run per-paper tables, pre window, all "
      f"sections, {len(arxiv)} papers, written at sha256 {ARXIV_PIN} |")
    p(f"| author side | the author's specification files in "
      f"`$WRITING_SAMPLES`, read in place as in TF-003 (the `.docx` "
      f"skipped), {len(author)} files; construction and pattern counts only |")
    p(f"| bootstrap | {draws} draws over documents, seed {seed}; one index "
      "matrix per source, for the arXiv papers and for the author's files; "
      "percentile 95% intervals, nearest rank for ratios |")
    p("| rates | findings per 1,000 words. Words are ticfinder's count "
      "(alphabetic spaCy tokens of the masked text). Pooled by words: total "
      "findings over total words of the five sources. Equal-weight: the "
      "mean of the five source rates |")
    p(f"| rows | at least {MIN_N} findings in the pool; comparisons need at "
      f"least {MIN_N} findings on both sides |")
    p("")

    p("## Sample and masking")
    p("")
    p("| source | documents | raw words | kept words (ticfinder) | median "
      "masked share | documents over 40% masked |")
    p("|---|---|---|---|---|---|")
    smp = {}
    for s in SOURCES:
        rows = summ[s]
        pc = [x["pct"] for x in rows]
        raw = sum(x["raw_words"] for x in rows)
        smp[s] = {"documents": len(rows), "raw_words": raw, "words": W[s],
                  "masked_share_median": median(pc),
                  "masked_share_over_40": sum(x > 40 for x in pc)}
        p(f"| {NAMES[s]} | {len(rows)} | {raw:,} | {W[s]:,} | "
          f"{median(pc):.1f}% | {sum(x > 40 for x in pc)} |")
    p(f"| pool | {sum(len(summ[s]) for s in SOURCES)} | "
      f"{sum(smp[s]['raw_words'] for s in SOURCES):,} | {Wsrc:,} | | |")
    p("")
    aw_ascii = sum(r["words_ascii"] for r in author)
    p(f"Comparison corpora: arXiv pre-window bodies {W['arxiv']:,} words in "
      f"{len(arxiv)} papers; the author's specifications {W['author']:,} "
      f"words by ticfinder's count in {len(author)} files ({aw_ascii:,} by "
      "the TF-003 measure, runs of ASCII letters after code masking).")
    p("")

    p("## Which pooled rate")
    p("")
    p(f"IETF RFCs hold {100 * W['ietf'] / Wsrc:.0f}% of the pool's words, so "
      "the rate pooled by words mostly measures one source's house style. "
      "Requirements 13 to 15 use the equal-weight pool, which counts each "
      "source as one sample of the register. Both are in the rate tables. "
      "The intervals resample documents within each source, so they cover "
      "the choice of documents and not the choice of sources.")
    p("")

    def pool_of(s):
        return s["pool"][POOL]

    # rate tables
    p("## Rates")
    p("")
    p(f"Rows with at least {MIN_N} findings in the pool, sorted by the "
      "equal-weight rate. Source cells are findings, then rate (95% CI). "
      "Phrase rows are phrase-list constructions keyed by the matched text, "
      "lowercased.")
    p("")
    for lvl in LEVELS:
        p(f"### {lvl}")
        p("")
        p(f"| {lvl} | n | documents | pooled by words (95% CI) | equal-weight "
          "(95% CI) | " + " | ".join(NAMES[s] for s in SOURCES) + " |")
        p("|---|---|---|---|---|" + "---|" * len(SOURCES))
        rs = [(k, B.stat(lvl, k)) for k in keys[lvl]]
        rs = [(k, s) for k, s in rs if s["pool"]["n"] >= MIN_N]
        rs.sort(key=lambda x: (-x[1]["pool"]["equal"]["rate"], x[0]))
        for k, s in rs:
            P = s["pool"]
            cells = [f"{s['g'][g]['n']}, "
                     f"{ci_txt(s['g'][g]['rate'], s['g'][g]['ci'])}"
                     for g in SOURCES]
            p(f"| `{k.replace('|', ' / ')}` | {P['n']} | {P['docs']} | "
              f"{ci_txt(P['words']['rate'], P['words']['ci'])} | "
              f"{ci_txt(P['equal']['rate'], P['equal']['ci'])} | "
              + " | ".join(cells) + " |")
            J.append({"table": f"Rates: {lvl}", "level": lvl, "key": k,
                      **AR.split_key(lvl, k), "n": P["n"],
                      "documents": P["docs"],
                      "pool_words": jrate(P["words"]["rate"],
                                          P["words"]["ci"]),
                      "pool_equal": jrate(P["equal"]["rate"],
                                          P["equal"]["ci"]),
                      "sources": {g: jrate(s["g"][g]["rate"], s["g"][g]["ci"],
                                           n=s["g"][g]["n"],
                                           documents=s["g"][g]["docs"])
                                  for g in SOURCES}})
        p("")

    # two-corpus comparisons
    def compare(title, other, other_name, first_is_pool, kset, note):
        p(f"## {title}")
        p("")
        p(note)
        p("")
        a_name, b_name = (("pool", other_name) if first_is_pool
                          else (other_name, "pool"))
        p(f"| row | {a_name} n | {a_name} rate (95% CI) | {b_name} n | "
          f"{b_name} rate (95% CI) | {a_name} over {b_name} (95% CI) | "
          "interval |")
        p("|---|---|---|---|---|---|---|")
        out = []
        for lvl in ("construction", "pattern"):
            ks = sorted(set(keys[lvl]) & set(kset[lvl]))
            rs = []
            for k in ks:
                if single(lvl, k):
                    continue
                s = B.stat(lvl, k)
                P, O = pool_of(s), s["g"][other]
                if s["pool"]["n"] < MIN_N or O["n"] < MIN_N:
                    continue
                A = (s["pool"]["n"], P["rate"], P["ci"], P["draws"])
                Bo = (O["n"], O["rate"], O["ci"], O["draws"])
                a, b = (A, Bo) if first_is_pool else (Bo, A)
                r, rci = ratio(a[1], b[1], a[3], b[3])
                rs.append((lvl, k, a, b, r, rci))
            rs.sort(key=lambda x: (-x[4], x[1]))
            for lvl_, k, a, b, r, rci in rs:
                v = side(*rci)
                p(f"| `{k.replace('|', ' / ')}` | {a[0]} | {ci_txt(a[1], a[2])}"
                  f" | {b[0]} | {ci_txt(b[1], b[2])} | {ci_txt(r, rci)} | "
                  f"{v} |")
                J.append({"table": title, "level": lvl_, "key": k,
                          **AR.split_key(lvl_, k),
                          "first": jrate(a[1], a[2], name=a_name, n=a[0]),
                          "second": jrate(b[1], b[2], name=b_name, n=b[0]),
                          "ratio": {"value": AR.jnum(r), "lo": AR.jnum(rci[0]),
                                    "hi": AR.jnum(rci[1])},
                          "interval": v})
                out.append((lvl_, k, r, rci, v))
        p("")
        return out

    h2 = compare("Pool against arXiv pre-window bodies (H2)", "arxiv",
                 "arXiv", True, akeys,
                 f"Construction and pattern rows with at least {MIN_N} "
                 "findings in the pool and in the arXiv pre-window bodies "
                 "(all sections). A pattern that is its construction's only "
                 "pattern is left out (same counts as the construction row). "
                 "The ratio is the equal-weight pool rate over the arXiv rate.")
    h2x = [x for x in h2 if x[4] != "spans 1"]
    p(f"{len(h2x)} of {len(h2)} rows have a pool over arXiv interval that "
      f"excludes 1 ({sum(x[4] == 'above 1' for x in h2x)} above, "
      f"{sum(x[4] == 'below 1' for x in h2x)} below). H2 needs at least a "
      f"quarter: {'holds' if h2 and len(h2x) >= len(h2) / 4 else 'fails'}.")
    p("")
    h3 = compare("Author against pool (H3)", "author", "author", False, ukeys,
                 f"Construction and pattern rows with at least {MIN_N} "
                 "findings in the author's specifications and in the pool. "
                 "The ratio is the author's rate over the equal-weight pool "
                 "rate; the author side resamples the author's files.")
    a20 = sum(B.stat(lvl, k)["g"]["author"]["n"] >= MIN_N
              for lvl in AUTHOR_LEVELS for k in ukeys[lvl]
              if not single(lvl, k))
    h3in = sum(x[4] == "spans 1" for x in h3)
    p(f"{a20} construction and pattern rows reach {MIN_N} findings in the "
      f"author's specifications; {len(h3)} of them also reach {MIN_N} in the "
      f"pool. {h3in} of {len(h3)} author over pool intervals contain 1. H3 "
      "needs at least three quarters: "
      f"{'holds' if h3 and h3in >= 0.75 * len(h3) else 'fails'}.")
    p("")

    # H4
    title = "Sources against the pool (H4)"
    p(f"## {title}")
    p("")
    p(f"Constructions with at least {MIN_N} findings in every source. Each "
      "source cell is rate (95% CI); the last column names the sources whose "
      "interval excludes the equal-weight pooled rate.")
    p("")
    p("| construction | equal-weight pool (95% CI) | "
      + " | ".join(NAMES[s] for s in SOURCES) + " | outside |")
    p("|---|---|" + "---|" * len(SOURCES) + "---|")
    h4 = []
    for k in keys["construction"]:
        s = B.stat("construction", k)
        if min(s["g"][g]["n"] for g in SOURCES) < MIN_N:
            continue
        P = s["pool"]["equal"]
        outs = [g for g in SOURCES if not (s["g"][g]["ci"][0] <= P["rate"]
                                           <= s["g"][g]["ci"][1])]
        h4.append((k, outs))
        p(f"| `{k}` | {ci_txt(P['rate'], P['ci'])} | "
          + " | ".join(ci_txt(s["g"][g]["rate"], s["g"][g]["ci"])
                       for g in SOURCES)
          + f" | {', '.join(NAMES[g] for g in outs) or 'none'} |")
        J.append({"table": title, "level": "construction", "key": k,
                  "construction": k, "pool_equal": jrate(P["rate"], P["ci"]),
                  "sources": {g: jrate(s["g"][g]["rate"], s["g"][g]["ci"],
                                       n=s["g"][g]["n"]) for g in SOURCES},
                  "outside": outs})
    p("")
    h4x = sum(1 for _, o in h4 if o)
    p(f"{h4x} of {len(h4)} constructions have at least one source outside "
      "the pooled rate. H4 needs at least half: "
      f"{'holds' if h4 and h4x >= len(h4) / 2 else 'fails'}.")
    p("")
    orc_section(B, p, J)
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)
    if args.json:
        AR.write_json(args.json, "spec-baseline", ver, AB.sig4({
            "report": out_path.name, "min_n": MIN_N, "pool_used": POOL,
            "bootstrap": {"draws": draws, "seed": seed,
                          "interval": "percentile 95%, nearest rank for "
                                      "ratios; one index matrix per source, "
                                      "for arXiv and for the author"},
            "sample": smp,
            "arxiv": {"papers": len(arxiv), "words": W["arxiv"],
                      "table_sha256": ARXIV_PIN},
            "author": {"files": len(author), "words": W["author"],
                       "words_ascii": aw_ascii, "rows_reaching_min_n": a20},
            "note": "ratios compare two corpora; they are not likelihood "
                    "ratios"}), AB.sig4(J))

    # console summary
    print(f"\nwords: " + ", ".join(f"{g} {W[g]:,}" for g in groups))
    print(f"H2: {len(h2x)} of {len(h2)} exclude 1: "
          + ", ".join(f"{k} {r:.2f} {v}" for _, k, r, _, v in h2x))
    print(f"H3: {h3in} of {len(h3)} contain 1; author rows >= {MIN_N}: {a20}; "
          "outside: " + ", ".join(f"{k} {r:.2f}" for _, k, r, _, v in h3
                                  if v != "spans 1"))
    print(f"H4: {h4x} of {len(h4)}: "
          + "; ".join(f"{k} {o}" for k, o in h4))
    top = sorted(((B.stat("construction", k)["pool"]["equal"]["rate"], k)
                  for k in keys["construction"]), reverse=True)[:3]
    print("top pooled constructions: " + ", ".join(f"{k} {r:.2f}"
                                                   for r, k in top))
    if h2:
        big = max(h2, key=lambda x: x[2])
        print(f"largest pool over arXiv: {big[1]} {big[2]:.2f}")


def orc_section(B, p, J):
    """TF-015: rates for object relatives and light verbs, every row
    whatever its count, and the zero to `that` ratio per corpus."""
    title = "Rates: object relatives and light verbs"
    p("## Object relatives and light verbs")
    p("")
    p("TF-015 rows: `OBJECT_RELATIVE`, its four patterns, the zero form by "
      "load group (the sum of its subtype counts) and "
      "`TRAILING_LIGHT_VERB`, listed whatever their counts. Source cells "
      "are findings, then rate (95% CI).")
    p("")
    p("| row | n | documents | pooled by words (95% CI) | equal-weight "
      "(95% CI) | " + " | ".join(NAMES[s] for s in SOURCES) + " |")
    p("|---|---|---|---|---|" + "---|" * len(SOURCES))
    for name, lvl, k in AB.ORC_ROWS:
        s = B.stat(lvl, k)
        P = s["pool"]
        cells = [f"{s['g'][g]['n']}, "
                 f"{ci_txt(s['g'][g]['rate'], s['g'][g]['ci'])}"
                 for g in SOURCES]
        p(f"| `{name.replace('|', ' / ')}` | {P['n']} | {P['docs']} | "
          f"{ci_txt(P['words']['rate'], P['words']['ci'])} | "
          f"{ci_txt(P['equal']['rate'], P['equal']['ci'])} | "
          + " | ".join(cells) + " |")
        J.append({"table": title, "level": lvl, "key": name,
                  **AR.split_key(lvl, name), "n": P["n"],
                  "documents": P["docs"],
                  "pool_words": jrate(P["words"]["rate"], P["words"]["ci"]),
                  "pool_equal": jrate(P["equal"]["rate"], P["equal"]["ci"]),
                  "sources": {g: jrate(s["g"][g]["rate"], s["g"][g]["ci"],
                                       n=s["g"][g]["n"],
                                       documents=s["g"][g]["docs"])
                              for g in SOURCES}})
    p("")
    p("## Zero to that ratio")
    p("")
    p(AB.ZT_NOTE + " The pool is the equal-weight pool: the mean of the "
      "source rates, for each form.")
    p("")
    for line in AB.ZT_HEAD:
        p(line)
    z, t = B.stat("pattern", AB.ORC_ZERO), B.stat("pattern", AB.ORC_THAT)
    sides = [("pool, equal-weight", z["pool"]["n"], z["pool"]["equal"],
              t["pool"]["n"], t["pool"]["equal"])]
    sides += [(NAMES[g], z["g"][g]["n"], z["g"][g], t["g"][g]["n"],
               t["g"][g]) for g in SOURCES]
    sides.append(("author", z["g"]["author"]["n"], z["g"]["author"],
                  t["g"]["author"]["n"], t["g"]["author"]))
    for name, zn, zs, tn, ts in sides:
        r, _, ci = AB.ratio_draws(zs["rate"], ts["rate"], zs["draws"],
                                  ts["draws"])
        J.append(AB.zt_row(name, zn, tn, r, ci))
        p(AB.zt_line(J[-1]))
    p("")


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="fetch, extract, date and sample")
    s = sub.add_parser("selftest", help="exclusion-rule rows")
    s.add_argument("-v", "--verbose", action="store_true")
    m = sub.add_parser("mask-report", help="masked shares and a console "
                       "spot-check of masked sentences")
    m.add_argument("-n", type=int, default=40,
                   help="sentences per source (default 40)")
    m.add_argument("-q", "--quiet", action="store_true",
                   help="figures only, no sentences")
    a = sub.add_parser("analyse", help="run ticfinder on the kept text and "
                       "the author's specs, and write the report")
    a.add_argument("--draws", type=int, default=2000)
    a.add_argument("--seed", type=int, default=BOOT_SEED,
                   help=f"bootstrap seed (default {BOOT_SEED})")
    a.add_argument("--report", help="output path (default "
                   "eval/spec-baseline-<today>.md)")
    a.add_argument("--report-only", action="store_true",
                   help="recompute the report from the stored tables")
    a.add_argument("--table-sha", metavar="SHA",
                   help="with --report-only: the ticfinder sha256 prefix the "
                        "stored tables were written with (pinned rebuild)")
    a.add_argument("--table-dir", metavar="DIR",
                   help="with --report-only: read the spec and author "
                        "tables from DIR (a snapshot)")
    a.add_argument("--arxiv-table-dir", metavar="DIR",
                   help="with --report-only: read the arXiv full tables "
                        "from DIR (a snapshot)")
    a.add_argument("--arxiv-sha", metavar="SHA",
                   help=f"with --report-only: the ticfinder sha256 prefix of "
                        f"the arXiv tables (default {ARXIV_PIN})")
    a.add_argument("--json", metavar="PATH",
                   help="also write every report row as JSON")
    a.add_argument("--sample", metavar="KEY",
                   help="print random findings per source for a "
                        "construction, CID|pattern or CID|phrase; console "
                        "only, writes nothing")
    a.add_argument("-n", type=int, default=20)
    args = ap.parse_args()
    if args.cmd == "analyse":
        if args.draws < 1000:
            sys.exit("--draws must be at least 1000")
        if (args.table_sha or args.table_dir or args.arxiv_table_dir
                or args.arxiv_sha) and not args.report_only:
            sys.exit("--table-sha, --table-dir, --arxiv-table-dir and "
                     "--arxiv-sha need --report-only")
        use_tables(args.table_dir, args.arxiv_table_dir, args.arxiv_sha)
    if args.cmd != "selftest" and \
            not (AR.ROOT / ".gitignore").read_text().count("private/"):
        sys.exit("private/ is not in .gitignore; refusing to cache there")
    rc = {"fetch": cmd_fetch, "selftest": cmd_selftest,
          "mask-report": cmd_mask_report, "analyse": cmd_analyse}[args.cmd](
        args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
