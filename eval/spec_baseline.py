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
               an earlier ticfinder (pinned rebuild). --json PATH also
               writes every report row as JSON (schema: roadmap s.15).

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


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="fetch, extract, date and sample")
    args = ap.parse_args()
    if not (AR.ROOT / ".gitignore").read_text().count("private/"):
        sys.exit("private/ is not in .gitignore; refusing to cache there")
    rc = {"fetch": cmd_fetch}[args.cmd](args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
