#!/usr/bin/env python3
"""Recheck stored arXiv findings for one construction against a detector fix.

Reads the stored findings for CONSTRUCTION from the TF-004 abstracts
(private/arxiv/findings.jsonl) and the TF-005 bodies
(private/arxiv/bodies/findings.jsonl). TF-005 sources: all sections
(body), the `body` section type alone (bsec), and the sample abstracts
(babs). Each stored sentence is parsed on
its own and run through the old detector (--old, a copy of the committed
tools/ticfinder.py) and the new one (the working tree). Reports, per
source and window:

  stored      findings in the stored table
  old repro   stored findings the old code reproduces on the isolated
              sentence (same matched text)
  new kept    of those, findings the new code still produces (a new
              span that covers the old one counts)

The reproduction rate shows how far an isolated parse differs from the
in-document parse. The adjusted rate is kept findings over the words in
the private per-paper tables; the scaled rate multiplies the stored count
by kept / reproduced. Both are point estimates.

--show N prints up to N dropped and N kept findings per window to the
console, for reading. Nothing is written to disk.

  python3 eval/arxiv_recheck.py DISGUISE_METAPHOR --old OLD.py --show 20
"""
import argparse
import importlib.util
import json
import random
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRIVATE = ROOT / "private" / "arxiv"
SECTION_TYPES = ["introduction", "body", "related", "conclusion"]

# source key, label, findings file, per-paper file
SOURCES = [
    ("abs", "TF-004 abstracts", PRIVATE / "findings.jsonl",
     PRIVATE / "per_paper.jsonl"),
    ("body", "TF-005 bodies, all sections", PRIVATE / "bodies" /
     "findings.jsonl", PRIVATE / "bodies" / "per_paper.jsonl"),
    ("bsec", "TF-005 bodies, body sections", PRIVATE / "bodies" /
     "findings.jsonl", PRIVATE / "bodies" / "per_paper.jsonl"),
    ("babs", "TF-005 sample abstracts", PRIVATE / "bodies" /
     "findings.jsonl", PRIVATE / "bodies" / "per_paper.jsonl"),
]
WINDOWS = ["pre", "post"]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(s):
    return " ".join(s.split())


def detect(mod, cid, doc, nlp):
    """(text, start_char, end_char) of each span the detector produces."""
    if cid in mod.CONSTRUCTIONS:
        spans = [h[0] for h in mod.run_construction(cid, doc, nlp)]
    elif cid in mod.PHRASE_PATTERNS:
        from spacy.matcher import Matcher
        m = Matcher(nlp.vocab)
        m.add(cid, mod.PHRASE_PATTERNS[cid][3])
        spans = [doc[s:e] for _, s, e in m(doc)]
    else:
        raise SystemExit(f"{cid}: not a structural or built-in phrase "
                         "construction")
    return [(norm(sp.text.strip().replace("\n", " ")), sp.start_char,
             sp.end_char) for sp in spans]


def stored(cid, key, path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["construction"] != cid:
            continue
        t = r.get("type")
        if key == "body" and t not in SECTION_TYPES:
            continue
        if key == "babs" and t != "abstract":
            continue
        if key == "bsec" and t != "body":
            continue
        rows.append(r)
    return rows


def words(key, path):
    w = defaultdict(int)
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        x = r["words"]
        if isinstance(x, dict):
            x = (sum(x[t] for t in SECTION_TYPES) if key == "body"
                 else x["body"] if key == "bsec" else x["abstract"])
        w[r["window"]] += x
    return w


def ratio(a, b):
    if not b:
        return "inf" if a else "-"
    return f"{a / b:.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("construction")
    ap.add_argument("--old", required=True,
                    help="copy of the committed tools/ticfinder.py")
    ap.add_argument("--show", type=int, default=0)
    ap.add_argument("--seed", default="tf006")
    ap.add_argument("--sources", default="abs,body",
                    help="comma list of abs, body, bsec, babs")
    args = ap.parse_args()
    cid = args.construction

    new = load_module("tf_new", ROOT / "tools" / "ticfinder.py")
    old = load_module("tf_old", args.old)
    nlp = new.load_model("en_core_web_md")

    keys = args.sources.split(",")
    table, reading = [], defaultdict(lambda: {"dropped": [], "kept": []})
    cache = {}
    for key, label, fpath, ppath in SOURCES:
        if key not in keys:
            continue
        w = words(key, ppath)
        rates = {}
        for win in WINDOWS:
            rows = [r for r in stored(cid, key, fpath) if r["window"] == win]
            n_old = n_new = n_new_only = 0
            for r in rows:
                sent = r["context"]
                if sent not in cache:
                    doc = nlp(sent)
                    cache[sent] = (detect(old, cid, doc, nlp),
                                   detect(new, cid, doc, nlp))
                o, n = cache[sent]
                t = norm(r["text"])
                at = [(a, b) for x, a, b in o if x == t]
                if not at:
                    if any(x == t for x, _, _ in n):
                        n_new_only += 1
                    continue
                n_old += 1
                # Kept when a new span covers the old one: a fix may widen
                # a span to the left ('More significantly,').
                cover = [x for x, a, b in n
                         if any(a <= oa and ob <= b for oa, ob in at)]
                if cover:
                    n_new += 1
                    reading[win]["kept"].append((label, dict(
                        r, text=cover[0])))
                else:
                    reading[win]["dropped"].append((label, r))
            kw = w[win] / 1000
            scaled = len(rows) * n_new / n_old if n_old else 0.0
            rates[win] = (len(rows) / kw, n_new / kw, scaled / kw)
            table.append((label, win, len(rows), n_old, n_new, n_new_only,
                          w[win], *rates[win]))
        table.append((label, "post/pre", None, None, None, None, None,
                      *(ratio(rates["post"][i], rates["pre"][i])
                        for i in range(3))))

    print(f"\n{cid}: stored findings rechecked on isolated sentences\n")
    hdr = ("source", "window", "stored", "old repro", "new kept",
           "new only", "words", "stored /1k", "kept /1k", "scaled /1k")
    print("| " + " | ".join(hdr) + " |")
    print("|" + "---|" * len(hdr))
    for row in table:
        cells = []
        for v in row:
            if v is None:
                cells.append("")
            elif isinstance(v, float):
                cells.append(f"{v:.3f}")
            elif isinstance(v, int):
                cells.append(f"{v:,}")
            else:
                cells.append(str(v))
        print("| " + " | ".join(cells) + " |")

    if args.show:
        rng = random.Random(f"{args.seed}-{cid}")
        for win in WINDOWS:
            for kind in ("dropped", "kept"):
                items = reading[win][kind]
                pick = rng.sample(items, min(args.show, len(items)))
                print(f"\n== {win} {kind}: {len(pick)} of {len(items)}")
                for i, (label, r) in enumerate(pick, 1):
                    print(f"{i:2}. [{label}] <{norm(r['text'])}>")
                    print(f"    {norm(r['context'])[:300]}")


if __name__ == "__main__":
    main()
