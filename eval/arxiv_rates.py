#!/usr/bin/env python3
"""ticfinder construction rates in arXiv cs.AR abstracts, before and after LLMs.

  fetch    pull primary-category cs.AR abstracts for the two windows from
           the arXiv API into private/arxiv/ (git-ignored). One JSON record
           per paper, one manifest per month. A rerun fetches only months
           that are missing or were fetched before they ended.
  analyse  mask LaTeX in each abstract, run ticfinder's analyse() on it,
           write the per-paper count table to private/arxiv/, bootstrap
           rates and ratios, and write the aggregate report.
  check    harvest the OAI-PMH set cs:cs:AR into private/arxiv/oai/ and
           check that the fetch missed no primary cs.AR paper in either
           window. Exits 1 if it did.

Windows are by first-version submission date (the API's submittedDate,
which is the v1 date):
  pre   2018-01-01 to 2021-12-31
  post  2025-01-01 to the latest date the API returns in 2026

Only papers whose primary category is cs.AR are kept. Cross-listed papers
are counted per month and reported, never cached or analysed.

Usage:
  eval/arxiv_rates.py fetch
  eval/arxiv_rates.py analyse [--draws 2000] [--report eval/arxiv-rates-DATE.md]
  eval/arxiv_rates.py analyse --report-only      # recompute from the table
  eval/arxiv_rates.py analyse --sample CID       # 20 findings per window to
                                                 # the console, for checking
  eval/arxiv_rates.py check [--refresh]          # completeness vs OAI-PMH

Bootstrap: numpy is used for the resampling. It is not a new dependency:
spaCy requires it, and ticfinder requires spaCy.

Nothing this script writes outside private/ holds abstract text, titles
or paper ids.
"""

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import math
import random
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TF_PATH = ROOT / "tools" / "ticfinder.py"
CACHE = ROOT / "private" / "arxiv"
PAPERS = CACHE / "papers"
MONTHS = CACHE / "months"
TMP = CACHE / "tmp"
TABLE = CACHE / "per_paper.jsonl"
FINDINGS = CACHE / "findings.jsonl"

API = "https://export.arxiv.org/api/query"
USER_AGENT = "ticfinder-research/0.1"
DELAY = 3.5           # seconds between requests; arXiv asks for at least 3
PAGE = 500
CATEGORY = "cs.AR"

WINDOWS = {
    "pre": (dt.date(2018, 1, 1), dt.date(2021, 12, 31)),
    "post": (dt.date(2025, 1, 1), dt.date(2026, 12, 31)),
}
SAMPLE_MAX = 3000
SAMPLE_SEED = 20261118
BOOT_SEED = 4004
NS = {"a": "http://www.w3.org/2005/Atom",
      "arxiv": "http://arxiv.org/schemas/atom",
      "os": "http://a9.com/-/spec/opensearch/1.1/"}


# ---------------------------------------------------------------- fetch

class FetchError(SystemExit):
    pass


_last_request = [0.0]


def api_get(params):
    wait = DELAY - (time.monotonic() - _last_request[0])
    if wait > 0:
        time.sleep(wait)
    url = API + "?" + urllib.parse.urlencode(params, safe=":[]+")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"arXiv API returned HTTP {e.code} for {url}; "
                         "stopping (rate limit or outage). Rerun later; "
                         "completed months are cached.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"arXiv API unreachable ({e}); stopping. Rerun "
                         "later; completed months are cached.")
    finally:
        _last_request[0] = time.monotonic()
    return ET.fromstring(body)


def months_of(window, today):
    lo, hi = WINDOWS[window]
    hi = min(hi, today)
    y, m = lo.year, lo.month
    while (y, m) <= (hi.year, hi.month):
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def month_end(y, m):
    nxt = dt.date(y + 1, 1, 1) if m == 12 else dt.date(y, m + 1, 1)
    return nxt - dt.timedelta(days=1)


def paper_file(pid):
    return PAPERS / (pid.replace("/", "_") + ".json")


def parse_entry(e):
    raw_id = e.findtext("a:id", namespaces=NS).strip()
    pid = re.sub(r"v\d+$", "", raw_id.rsplit("/abs/", 1)[-1])
    prim = e.find("arxiv:primary_category", NS)
    return {
        "id": pid,
        "first_version": e.findtext("a:published", namespaces=NS)[:10],
        "title": " ".join(e.findtext("a:title", "", NS).split()),
        "abstract": " ".join(e.findtext("a:summary", "", NS).split()),
        "primary_category": prim.get("term") if prim is not None else "",
    }


def fetch_month(y, m):
    lo = f"{y:04d}{m:02d}010000"
    hi = month_end(y, m).strftime("%Y%m%d") + "2359"
    q = f"cat:{CATEGORY} AND submittedDate:[{lo} TO {hi}]"
    entries, start, total, empty = {}, 0, None, 0
    while total is None or start < total:
        root = api_get({"search_query": q, "start": start,
                        "max_results": PAGE, "sortBy": "submittedDate",
                        "sortOrder": "ascending"})
        t = int(root.findtext("os:totalResults", "0", NS))
        total = t if total is None else total
        page = root.findall("a:entry", NS)
        if not page and start < total:
            # The API occasionally returns an empty page mid-listing.
            empty += 1
            if empty > 3:
                raise FetchError(f"{y}-{m:02d}: API returned empty pages "
                                 f"at offset {start} of {total}; stopping.")
            continue
        for e in page:
            r = parse_entry(e)
            entries[r["id"]] = r
        start += len(page)
    return total, entries


def cmd_fetch(args):
    today = dt.date.today()
    PAPERS.mkdir(parents=True, exist_ok=True)
    MONTHS.mkdir(parents=True, exist_ok=True)
    for window in WINDOWS:
        for y, m in months_of(window, today):
            mf = MONTHS / f"{y:04d}-{m:02d}.json"
            if mf.exists() and json.loads(mf.read_text())["complete"]:
                continue
            total, entries = fetch_month(y, m)
            prim, cross, outside = [], 0, 0
            lo, hi = dt.date(y, m, 1), month_end(y, m)
            for pid, r in sorted(entries.items()):
                d = dt.date.fromisoformat(r["first_version"])
                if not lo <= d <= hi:
                    outside += 1
                    continue
                if r["primary_category"] != CATEGORY:
                    cross += 1
                    continue
                prim.append(pid)
                pf = paper_file(pid)
                if not pf.exists():
                    pf.write_text(json.dumps(r), encoding="utf-8")
            man = {"month": f"{y:04d}-{m:02d}", "window": window,
                   "total_results": total, "returned": len(entries),
                   "primary": prim, "cross_listed": cross,
                   "outside_month": outside,
                   "complete": hi < today,
                   "fetched": today.isoformat()}
            mf.write_text(json.dumps(man), encoding="utf-8")
            print(f"{man['month']}: {len(prim)} primary, {cross} cross-listed"
                  + (f", {outside} outside month" if outside else "")
                  + ("" if man["complete"] else " (month not over)"),
                  file=sys.stderr)
    for window in WINDOWS:
        p, c = window_counts(window)
        print(f"{window}: {p} primary {CATEGORY}, {c} cross-listed "
              "(excluded)")


def manifests(window):
    out = []
    for mf in sorted(MONTHS.glob("*.json")):
        man = json.loads(mf.read_text())
        if man["window"] == window:
            out.append(man)
    return out


def window_counts(window):
    ms = manifests(window)
    return sum(len(m["primary"]) for m in ms), sum(m["cross_listed"]
                                                    for m in ms)


# ------------------------------------------------------------- masking

# Math and reference commands are blanked whole. Text commands keep their
# argument and lose only "\cmd{" and the matching "}". Everything is
# replaced by spaces of the same length, so offsets are preserved.
_MATH = re.compile(r"\$\$.+?\$\$|\$.+?\$|\\\(.+?\\\)|\\\[.+?\\\]", re.S)
_DROP = re.compile(r"\\(?:cite[a-z]*|ref|eqref|cref|Cref|autoref|label|url|"
                   r"href|footnote)\*?(?:\[[^\]]*\])*\{[^{}]*\}")
_KEEP = re.compile(r"\\(?:emph|textbf|textit|texttt|textsc|textrm|textsf|"
                   r"textsl|textup|textnormal|underline|mbox|text|mathrm)"
                   r"\s*\{")
_ESCAPE = re.compile(r"\\[%&_#${}]")
_CMD = re.compile(r"\\[A-Za-z]+\*?|\\.")


def _blank(chars, lo, hi):
    for i in range(lo, hi):
        if not chars[i].isspace():
            chars[i] = " "


def mask_latex(text):
    """Blank LaTeX math and commands in place. Returns (masked, n_blanked).

    n_blanked counts non-whitespace characters blanked.
    """
    chars = list(text)
    # escaped symbols: blank the backslash, keep the symbol, and hide it
    # from the math rule so "\$5" does not open math
    work = list(text)
    for m in _ESCAPE.finditer(text):
        chars[m.start()] = " "
        work[m.start()] = work[m.start() + 1] = "\0"
    w = "".join(work)
    for m in _MATH.finditer(w):
        _blank(chars, m.start(), m.end())
    for m in _DROP.finditer(w):
        _blank(chars, m.start(), m.end())
    for m in _KEEP.finditer(w):
        _blank(chars, m.start(), m.end())
        depth, i = 1, m.end()
        while i < len(w) and depth:
            depth += {"{": 1, "}": -1}.get(w[i], 0)
            i += 1
        if depth == 0:
            chars[i - 1] = " "
    cur = "".join(chars)
    for m in _CMD.finditer(cur):
        _blank(chars, m.start(), m.end())
    for i, ch in enumerate(chars):
        if ch in "{}~":
            chars[i] = " "
    masked = "".join(chars)
    n = sum(1 for a, b in zip(text, masked) if a != b and not a.isspace())
    return masked, n


# ------------------------------------------------------------ analyse

def tf_version():
    def git(*a):
        return subprocess.run(["git", "-C", str(ROOT), *a],
                              capture_output=True, text=True).stdout.strip()
    commit = git("log", "-1", "--format=%h", "--", "tools/ticfinder.py")
    dirty = git("status", "--porcelain", "--", "tools/ticfinder.py")
    digest = hashlib.sha256(TF_PATH.read_bytes()).hexdigest()[:12]
    label = commit + (" with uncommitted changes" if dirty else "")
    return {"commit": label, "sha256": digest}


def load_tf():
    spec = importlib.util.spec_from_file_location("tf", TF_PATH)
    tf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tf)
    return tf


def subtype(label):
    """Same rule as eval/harvest.py subtype()."""
    m = re.search(r"\[([^\[\]]*)\]\s*$", label or "")
    if not m:
        return "-"
    return re.sub(r"^\d+(?:-part \S+| clauses),\s*", "",
                  m.group(1).strip()) or "-"


def selection():
    """Paper ids per window, sampled to SAMPLE_MAX with a fixed seed."""
    sel, info = {}, {}
    for window in WINDOWS:
        ids = sorted({pid for m in manifests(window) for pid in m["primary"]})
        n = len(ids)
        if n > SAMPLE_MAX:
            ids = sorted(random.Random(f"{SAMPLE_SEED}-{window}")
                         .sample(ids, SAMPLE_MAX))
        sel[window] = ids
        info[window] = {"papers": n, "analysed": len(ids),
                        "sampled": n > SAMPLE_MAX}
    return sel, info


def cmd_analyse(args):
    if args.sample:
        return show_sample(args.sample, args.n)
    if not args.report_only:
        run_analysis()
    write_report(args)


def run_analysis():
    ver = tf_version()
    sel, _ = selection()
    done = {}
    if TABLE.exists():
        for line in TABLE.read_text(encoding="utf-8").splitlines():
            r = json.loads(line)
            if r["tf_sha256"] == ver["sha256"]:
                done[r["id"]] = r
    todo = [(w, pid) for w in sel for pid in sel[w] if pid not in done]
    if not todo:
        print(f"analysis up to date ({len(done)} papers)", file=sys.stderr)
        return
    # keep only rows of this version, then append
    keep_ids = {pid for w in sel for pid in sel[w]}
    rows = [r for r in done.values() if r["id"] in keep_ids]
    old_f = []
    if FINDINGS.exists():
        old_f = [json.loads(x) for x in
                 FINDINGS.read_text(encoding="utf-8").splitlines()]
        old_f = [f for f in old_f if f["id"] in done
                 and f["id"] in keep_ids]
    TABLE.write_text("".join(json.dumps(r) + "\n" for r in rows),
                     encoding="utf-8")
    FINDINGS.write_text("".join(json.dumps(f) + "\n" for f in old_f),
                        encoding="utf-8")

    tf = load_tf()
    nlp = tf.load_model("en_core_web_md")
    extra = []
    for f in tf.discover_phrase_files(None):
        extra.extend(tf.load_phrase_file(f))
    phrase_ids = {e["id"] for e in extra} | set(tf.PHRASE_PATTERNS)
    TMP.mkdir(parents=True, exist_ok=True)
    t0 = time.monotonic()
    with TABLE.open("a", encoding="utf-8") as tab, \
            FINDINGS.open("a", encoding="utf-8") as fnd:
        for i, (window, pid) in enumerate(todo, 1):
            rec = json.loads(paper_file(pid).read_text(encoding="utf-8"))
            masked, nblank = mask_latex(rec["abstract"])
            # Plain-text suffix: an abstract is not markdown. ticfinder's
            # defaults otherwise apply (code masker, phrase lists, md model).
            tmp = TMP / (pid.replace("/", "_") + ".txt")
            tmp.write_text(masked, encoding="utf-8")
            try:
                findings, stats = tf.analyse(str(tmp), nlp, None, extra,
                                             set())
            finally:
                tmp.unlink()
            by_c, by_p, by_s, by_phrase = Counter(), Counter(), Counter(), \
                Counter()
            for f in findings:
                pat = f.pattern or "-"
                by_c[f.construction] += 1
                by_p[f"{f.construction}|{pat}"] += 1
                by_s[f"{f.construction}|{pat}|{subtype(f.label)}"] += 1
                if f.construction in phrase_ids:
                    by_phrase[f"{f.construction}|"
                              f"{' '.join(f.text.lower().split())}"] += 1
                fnd.write(json.dumps({
                    "id": pid, "window": window,
                    "construction": f.construction, "pattern": pat,
                    "label": f.label, "text": f.text,
                    "context": f.context}) + "\n")
            nonws = sum(1 for ch in rec["abstract"] if not ch.isspace())
            tab.write(json.dumps({
                "id": pid, "window": window, "tf_sha256": ver["sha256"],
                "words": stats["words"], "nonws_chars": nonws,
                "latex_masked_chars": nblank,
                "tf_masked_pct": stats["masked_pct"],
                "construction": by_c, "pattern": by_p, "subtype": by_s,
                "phrase": by_phrase}) + "\n")
            if i % 200 == 0 or i == len(todo):
                el = time.monotonic() - t0
                print(f"  {i}/{len(todo)} papers, {el:.0f}s", file=sys.stderr)
    try:
        TMP.rmdir()
    except OSError:
        pass


# ------------------------------------------------------------ report

def load_table():
    sel, info = selection()
    want = {pid: w for w in sel for pid in sel[w]}
    ver = tf_version()
    rows = defaultdict(list)
    for line in TABLE.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["id"] in want and r["tf_sha256"] == ver["sha256"]:
            rows[r["window"]].append(r)
    for w in sel:
        if len(rows[w]) != len(sel[w]):
            sys.exit(f"{w}: table has {len(rows[w])} of {len(sel[w])} "
                     "papers for this ticfinder version; run analyse")
        rows[w].sort(key=lambda r: r["id"])
    return rows, info, ver


def fmt(x, nd=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    if math.isinf(x):
        return "inf"
    return f"{x:.{nd}f}"


def write_report(args):
    import numpy as np
    rows, info, ver = load_table()
    draws = args.draws
    rng = np.random.default_rng(BOOT_SEED)
    pre, post = rows["pre"], rows["post"]
    W = {w: np.array([r["words"] for r in rows[w]], dtype=float)
         for w in rows}
    # one index matrix per window, shared by every row so rows are
    # comparable
    idx = {w: rng.integers(0, len(rows[w]), size=(draws, len(rows[w])))
           for w in ("pre", "post")}
    wsum = {w: W[w][idx[w]].sum(axis=1) for w in idx}

    def stat(level, key):
        out = {}
        for w in ("pre", "post"):
            c = np.array([r[level].get(key, 0) for r in rows[w]],
                         dtype=float)
            rate = c.sum() / W[w].sum() * 1000
            br = c[idx[w]].sum(axis=1) / wsum[w] * 1000
            out[w] = (int(c.sum()), rate, *np.percentile(br, [2.5, 97.5]),
                      br, int((c > 0).sum()))
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = out["post"][1] / out["pre"][1] if out["pre"][1] \
                else (math.inf if out["post"][1] else math.nan)
            br = out["post"][4] / out["pre"][4]   # 0/0 draws are nan
            lo, hi = (np.nanpercentile(br, [2.5, 97.5], method="nearest")
                      if not np.isnan(br).all() else (math.nan, math.nan))
        return out, ratio, lo, hi

    def verdict(n_tot, lo, hi):
        if n_tot < 20:
            return "too few"
        if lo > 1:
            return "rose"
        if hi < 1:
            return "fell"
        return "flat"

    keys = {lvl: sorted({k for w in rows for r in rows[w] for k in r[lvl]})
            for lvl in ("construction", "pattern", "subtype", "phrase")}
    tables = {}
    for lvl, ks in keys.items():
        out = []
        for k in ks:
            o, ratio, lo, hi = stat(lvl, k)
            n_tot = o["pre"][0] + o["post"][0]
            out.append({"key": k, "o": o, "ratio": ratio, "lo": lo,
                        "hi": hi, "n": n_tot,
                        "verdict": verdict(n_tot, lo, hi)})
        out.sort(key=lambda d: (-(d["ratio"] if not math.isnan(d["ratio"])
                                  else -1), -d["n"]))
        tables[lvl] = out

    # sanity: lengths and masking
    def mean_ci(vals):
        a = np.array(vals, dtype=float)
        b = a[rng.integers(0, len(a), size=(draws, len(a)))].mean(axis=1)
        return a.mean(), *np.percentile(b, [2.5, 97.5])
    lens = {w: mean_ci(W[w]) for w in W}
    masked = {w: 100 * sum(r["latex_masked_chars"] for r in rows[w])
              / max(sum(r["nonws_chars"] for r in rows[w]), 1) for w in rows}
    any_masked = {w: 100 * sum(1 for r in rows[w] if r["latex_masked_chars"])
                  / len(rows[w]) for w in rows}
    tfm = {w: sum(r["tf_masked_pct"] for r in rows[w]) / len(rows[w])
           for w in rows}
    # Em dash proxy. arXiv abstracts as served are ASCII, so EM_DASH (which
    # looks for U+2014 and U+2013) cannot fire. Count TeX "---" and a
    # spaced " -- " instead; "--" between digits is a range and is left out.
    for w in rows:
        for r in rows[w]:
            a = json.loads(paper_file(r["id"]).read_text())["abstract"]
            r["dash_proxy"] = {"x": a.count("---") + len(
                re.findall(r"(?<=\s)--(?=\s)", a))}
    dash = stat("dash_proxy", "x")
    cross = {w: window_counts(w)[1] for w in rows}
    span = {}
    for w in rows:
        ds = [json.loads(paper_file(r["id"]).read_text())["first_version"]
              for r in rows[w]]
        span[w] = (min(ds), max(ds))

    today = dt.date.today().isoformat()
    out_path = Path(args.report or HERE / f"arxiv-rates-{today}.md")
    L = []
    p = L.append
    p("# ticfinder construction rates in arXiv cs.AR abstracts, "
      "before and after LLMs")
    p("")
    p(f"Generated {today} by `eval/arxiv_rates.py` (TF-004). Aggregates "
      "only: no abstract text, titles or paper ids.")
    p("")
    p("## Setup")
    p("")
    p("| item | value |")
    p("|---|---|")
    p(f"| source | arXiv API, `cat:{CATEGORY}`, primary category "
      f"{CATEGORY} only; metadata is CC0 |")
    p("| pre window | first version 2018-01-01 to 2021-12-31 "
      f"(analysed papers span {span['pre'][0]} to {span['pre'][1]}) |")
    p("| post window | first version 2025-01-01 to the latest date "
      f"available, {span['post'][1]} (analysed papers from "
      f"{span['post'][0]}) |")
    for w in ("pre", "post"):
        i = info[w]
        smp = (f"random sample of {i['analysed']}, seed "
               f"`{SAMPLE_SEED}-{w}`" if i["sampled"]
               else "all analysed, no sampling")
        p(f"| {w} papers | {i['papers']} primary {CATEGORY}; {smp}; "
          f"{cross[w]} cross-listed papers excluded |")
    p(f"| ticfinder | `tools/ticfinder.py` at {ver['commit']} "
      f"(sha256 {ver['sha256']}); defaults: `en_core_web_md`, code "
      "masker on, `ticfinder-phrases.json`; abstracts analysed as plain "
      "text (`.txt`) |")
    p(f"| bootstrap | {draws} draws over papers, seed {BOOT_SEED}; "
      "percentile 95% intervals (nearest rank for ratios, so draws "
      "with a zero pre rate give inf, not nan); the ratio interval "
      "resamples both windows independently |")
    p("| rate | findings per 1,000 words, pooled over papers (total "
      "findings / total words); words are alphabetic tokens after "
      "masking |")
    p("")
    p("## Sanity measures")
    p("")
    p("| measure | pre | post |")
    p("|---|---|---|")
    p(f"| papers analysed | {len(pre)} | {len(post)} |")
    p(f"| words analysed | {int(W['pre'].sum()):,} | "
      f"{int(W['post'].sum()):,} |")
    p("| mean abstract length, words (95% interval) | "
      f"{lens['pre'][0]:.1f} ({lens['pre'][1]:.1f} to {lens['pre'][2]:.1f})"
      f" | {lens['post'][0]:.1f} ({lens['post'][1]:.1f} to "
      f"{lens['post'][2]:.1f}) |")
    p(f"| LaTeX-masked share of non-space characters | {masked['pre']:.2f}%"
      f" | {masked['post']:.2f}% |")
    p(f"| abstracts with any LaTeX masked | {any_masked['pre']:.1f}% | "
      f"{any_masked['post']:.1f}% |")
    p(f"| ticfinder masked_pct, mean per abstract | {tfm['pre']:.2f}% | "
      f"{tfm['post']:.2f}% |")
    p("| Unicode em and en dashes in the abstracts | 0 | 0 |")
    dpre, dpost = dash[0]["pre"], dash[0]["post"]
    p(f"| em dash proxy (TeX `---` and spaced ` -- `), n | {dpre[0]} | "
      f"{dpost[0]} |")
    p(f"| em dash proxy per 1k words (95% CI) | {fmt(dpre[1])} "
      f"({fmt(dpre[2])} to {fmt(dpre[3])}) | {fmt(dpost[1])} "
      f"({fmt(dpost[2])} to {fmt(dpost[3])}) |")
    p(f"| em dash proxy ratio, post over pre (95% CI) | "
      f"{fmt(dash[1])} ({fmt(dash[2])} to {fmt(dash[3])}) | |")
    p("")

    def table(title, lvl, label):
        p(f"## {title}")
        p("")
        p(f"Sorted by ratio. `n` is findings in both windows; `papers` is "
          "abstracts with at least one finding. Verdict: `rose` when the "
          "ratio interval is above 1, `fell` when below, `flat` when it "
          "spans 1, `too few` under 20 findings in total.")
        p("")
        p(f"| {label} | pre n | pre papers | pre rate (95% CI) | post n | "
          "post papers | post rate (95% CI) | ratio (95% CI) | verdict |")
        p("|---|---|---|---|---|---|---|---|---|")
        for d in tables[lvl]:
            a, b = d["o"]["pre"], d["o"]["post"]
            key = d["key"].replace("|", " / ")
            p(f"| `{key}` | {a[0]} | {a[5]} | {fmt(a[1])} ({fmt(a[2])} to "
              f"{fmt(a[3])}) | {b[0]} | {b[5]} | {fmt(b[1])} ({fmt(b[2])} "
              f"to {fmt(b[3])}) | {fmt(d['ratio'])} ({fmt(d['lo'])} to "
              f"{fmt(d['hi'])}) | {d['verdict']} |")
        p("")

    table("Rates per construction", "construction", "construction")
    table("Rates per pattern", "pattern", "construction / pattern")
    # subtype and phrase rows only where there is something to see
    tables["subtype"] = [d for d in tables["subtype"] if d["n"] >= 20]
    table("Rates per subtype, at least 20 findings", "subtype",
          "construction / pattern / subtype")
    tables["phrase"] = [d for d in tables["phrase"] if d["n"] >= 20]
    table("Phrase-list matches, at least 20 findings", "phrase",
          "construction / matched phrase")
    p(f"With {len(tables['pattern'])} pattern rows at 95%, one or two "
      "`rose` or `fell` verdicts near the interval edge are expected by "
      "chance.")
    p("")
    out_path.write_text("\n".join(L), encoding="utf-8")
    print(f"wrote {out_path}", file=sys.stderr)

    # console summary
    print(f"\npapers: pre {info['pre']['papers']} "
          f"(analysed {len(pre)}), post {info['post']['papers']} "
          f"(analysed {len(post)})")
    print(f"mean words: pre {lens['pre'][0]:.1f}, post {lens['post'][0]:.1f}")
    print(f"\n{'construction':<24} {'pre':>6} {'post':>6} {'ratio':>6} "
          f"{'95% CI':>15} verdict")
    for d in tables["construction"]:
        print(f"{d['key']:<24} {fmt(d['o']['pre'][1]):>6} "
              f"{fmt(d['o']['post'][1]):>6} {fmt(d['ratio']):>6} "
              f"{fmt(d['lo']):>6} to {fmt(d['hi']):>5} {d['verdict']}")


def show_sample(cid, n):
    """Print n random findings per window for one construction (console
    only, for the sanity check; nothing is written)."""
    sel, _ = selection()
    want = {pid for w in sel for pid in sel[w]}
    pool = defaultdict(list)
    for line in FINDINGS.read_text(encoding="utf-8").splitlines():
        f = json.loads(line)
        if f["id"] in want and (f["construction"] == cid
                                or f"{f['construction']}|{f['pattern']}"
                                == cid):
            pool[f["window"]].append(f)
    rng = random.Random(f"{SAMPLE_SEED}-check-{cid}")
    for w in ("pre", "post"):
        pick = rng.sample(pool[w], min(n, len(pool[w])))
        print(f"\n=== {cid} {w}: {len(pick)} of {len(pool[w])}")
        for i, f in enumerate(pick, 1):
            print(f"\n[{w} {i}] {f['label']}\n  MATCH: {f['text']}\n"
                  f"  SENT:  {f['context']}")


# ------------------------------------------------------------- check

OAI = "https://oaipmh.arxiv.org/oai"
OAI_SET = "cs:cs:AR"
OAI_FROM = "2018-01-01"
OAI_DIR = CACHE / "oai"
ONS = {"o": "http://www.openarchives.org/OAI/2.0/",
       "x": "http://arxiv.org/OAI/arXiv/"}


def oai_get(params):
    wait = DELAY - (time.monotonic() - _last_request[0])
    if wait > 0:
        time.sleep(wait)
    url = OAI + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            body = r.read()
    except urllib.error.HTTPError as e:
        raise FetchError(f"OAI-PMH returned HTTP {e.code} (Retry-After: "
                         f"{e.headers.get('Retry-After')}); stopping. Pages "
                         "so far are cached; rerun to resume.")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise FetchError(f"OAI-PMH unreachable ({e}); stopping. Pages so "
                         "far are cached; rerun to resume.")
    finally:
        _last_request[0] = time.monotonic()
    root = ET.fromstring(body)
    err = root.find("o:error", ONS)
    if err is not None:
        raise FetchError(f"OAI-PMH error {err.get('code')}: {err.text}")
    return body, root


def _token(root):
    tok = root.find(".//o:resumptionToken", ONS)
    return (tok.text or "").strip() if tok is not None else ""


def oai_harvest():
    """Harvest OAI_SET into OAI_DIR/page-NNN.xml, resuming if interrupted.

    OAI-PMH selects by last-modified datestamp. A record is modified on or
    after it is created, so from=2018-01-01 covers every paper submitted
    since then.
    """
    OAI_DIR.mkdir(parents=True, exist_ok=True)
    pages = sorted(OAI_DIR.glob("page-*.xml"))
    if pages:
        tok = _token(ET.fromstring(pages[-1].read_bytes()))
        if not tok:
            print(f"OAI harvest cached ({len(pages)} pages)", file=sys.stderr)
            return
        params = {"verb": "ListRecords", "resumptionToken": tok}
    else:
        params = {"verb": "ListRecords", "metadataPrefix": "arXiv",
                  "set": OAI_SET, "from": OAI_FROM}
    n = len(pages)
    while True:
        body, root = oai_get(params)
        n += 1
        (OAI_DIR / f"page-{n:03d}.xml").write_bytes(body)
        print(f"  page {n}: {len(root.findall('.//o:record', ONS))} records",
              file=sys.stderr)
        tok = _token(root)
        if not tok:
            return
        params = {"verb": "ListRecords", "resumptionToken": tok}


def id_year(pid):
    """First-version year from a new-style id (YYMM.NNNNN), else None.

    The id is assigned at announcement, so a paper submitted at the end
    of a month can carry the next month's prefix.
    """
    m = re.match(r"^(\d{2})(\d{2})\.\d+$", pid)
    return 2000 + int(m.group(1)) if m else None


def window_of(year):
    for w, (lo, hi) in WINDOWS.items():
        if year is not None and lo.year <= year <= hi.year:
            return w
    return None


def cmd_check(args):
    """Check the API fetch for completeness against OAI-PMH.

    OAI's <created> field is not the v1 date (some 2018 papers show
    2022), so papers are matched by the YYMM prefix of their arXiv id.
    Papers that OAI lists and the API did not return are looked up by id
    through the API, and their v1 date decides whether they were missed.
    Exits 1 when a paper inside a window is missing. Ids are not printed.
    """
    if args.refresh and OAI_DIR.exists():
        for p in OAI_DIR.glob("page-*.xml"):
            p.unlink()
    oai_harvest()
    oai_prim, oai_cross = {}, 0
    for p in sorted(OAI_DIR.glob("page-*.xml")):
        for rec in ET.fromstring(p.read_bytes()).findall(".//o:record", ONS):
            md = rec.find(".//x:arXiv", ONS)
            if md is None:
                continue                      # deleted record
            cats = md.findtext("x:categories", "", ONS).split()
            pid = md.findtext("x:id", "", ONS)
            if cats and cats[0] == CATEGORY:
                oai_prim[pid] = id_year(pid)
            elif CATEGORY in cats:
                oai_cross += 1
    api_date, api_cross = {}, Counter()
    for w in WINDOWS:
        for man in manifests(w):
            api_cross[man["month"][:4]] += man["cross_listed"]
            for pid in man["primary"]:
                rec = json.loads(paper_file(pid).read_text(encoding="utf-8"))
                api_date[pid] = rec["first_version"]
    if not api_date:
        sys.exit("no API manifests under private/arxiv/months; run fetch")

    years = sorted({int(d[:4]) for d in api_date.values()})
    print(f"\n{'year':<6} {'API v1':>7} {'OAI id':>7} {'API id':>7} "
          f"{'OAI only':>9} {'API cross':>10}")
    for y in years:
        a_v1 = sum(1 for d in api_date.values() if int(d[:4]) == y)
        o_id = {p for p, yy in oai_prim.items() if yy == y}
        a_id = {p for p in api_date if id_year(p) == y}
        print(f"{y:<6} {a_v1:>7} {len(o_id):>7} {len(a_id):>7} "
              f"{len(o_id - a_id):>9} {api_cross[str(y)]:>10}")
    print("API v1: primary papers by the API's v1 date (the windows use "
          "this).\nOAI id, API id: primary papers by arXiv id year.")

    not_prim = [p for p in api_date if p not in oai_prim]
    print(f"\nAPI papers not primary {CATEGORY} in OAI: {len(not_prim)}")
    only = sorted(p for p, y in oai_prim.items()
                  if window_of(y) and p not in api_date)
    missed = 0
    if only:
        v1 = {}
        for i in range(0, len(only), 100):
            root = api_get({"id_list": ",".join(only[i:i + 100]),
                            "max_results": 100})
            for e in root.findall("a:entry", NS):
                r = parse_entry(e)
                v1[r["id"]] = r["first_version"]
        for p in only:
            d = v1.get(p)
            if d is None or window_of_date(d):
                missed += 1
        outside = len(only) - missed
        print(f"OAI-only papers in a window by id year: {len(only)}; "
              f"{outside} have a v1 date outside both windows, "
              f"{missed} were missed by the fetch")
    else:
        print("OAI-only papers in a window by id year: 0")
    print("fetch complete" if not missed else "fetch INCOMPLETE")
    return 1 if missed else 0


def window_of_date(iso):
    d = dt.date.fromisoformat(iso[:10])
    return next((w for w, (lo, hi) in WINDOWS.items() if lo <= d <= hi),
                None)


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="fetch abstracts into private/arxiv/")
    c = sub.add_parser("check", help="check the fetch for completeness "
                       "against OAI-PMH")
    c.add_argument("--refresh", action="store_true",
                   help="discard cached OAI pages and harvest again")
    a = sub.add_parser("analyse", help="run ticfinder and write the report")
    a.add_argument("--draws", type=int, default=2000)
    a.add_argument("--report", help="output path (default "
                   "eval/arxiv-rates-<today>.md)")
    a.add_argument("--report-only", action="store_true",
                   help="recompute the report from the per-paper table")
    a.add_argument("--sample", metavar="CID",
                   help="print random findings for a construction (or "
                        "CID|pattern) per window; writes nothing")
    a.add_argument("-n", type=int, default=20)
    args = ap.parse_args()
    if not (ROOT / ".gitignore").read_text().count("private/"):
        sys.exit("private/ is not in .gitignore; refusing to cache there")
    if args.draws < 1000 if args.cmd == "analyse" else False:
        sys.exit("--draws must be at least 1000")
    rc = {"fetch": cmd_fetch, "analyse": cmd_analyse,
          "check": cmd_check}[args.cmd](args)
    sys.exit(rc or 0)


if __name__ == "__main__":
    main()
