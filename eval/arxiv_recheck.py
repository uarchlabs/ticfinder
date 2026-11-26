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
console, for reading. --subtype S keeps only stored findings whose
subtype (the harvest.py rule, as in the reports) is S, such as the
lemma `use` for PARTICIPIAL_TAIL. Nothing is written to disk unless
--save names a file under private/.

TF-010 added --pattern P, which keeps stored findings of one pattern and
counts a finding kept only when the new code reports it under P (a span
the new code reports under another pattern of the construction counts as
moved, such as cc_additive split from cc_coordinated). It also added two
sources: `spec`, the TF-009 spec findings (groups are the five sources),
and `full`, the TF-008 full bodies, all sections. Both read the private
snapshots that TF-010 took before its reruns. TF-011 added `spec10` and
`full10`, the TF-010 spec findings and full bodies, from the snapshots
TF-011 took before its reruns. A stored sentence is the
one the span starts in, so a cleft across sentences cannot reproduce
from it; --cross parses the stored span text instead when the span runs
past its sentence.

  python3 eval/arxiv_recheck.py DISGUISE_METAPHOR --old OLD.py --show 20
  python3 eval/arxiv_recheck.py CORRECTIVE_CONTRAST --pattern cc_cleft \
      --old OLD.py --sources spec,full --save private/recheck/cleft.json
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
    ("full", "TF-008 full bodies, all sections", PRIVATE / "bodies-tf008" /
     "findings.jsonl", PRIVATE / "bodies-tf008" / "per_paper.jsonl"),
    ("spec", "TF-009 spec baseline", ROOT / "private" / "specs-tf009" /
     "findings.jsonl", ROOT / "private" / "specs-tf009" / "per_doc.jsonl"),
    ("full10", "TF-010 full bodies, all sections", PRIVATE /
     "bodies-tf010" / "findings.jsonl", PRIVATE / "bodies-tf010" /
     "per_paper.jsonl"),
    ("spec10", "TF-010 spec baseline", ROOT / "private" / "specs-tf010" /
     "findings.jsonl", ROOT / "private" / "specs-tf010" / "per_doc.jsonl"),
]
SPEC_KEYS = ("spec", "spec10")
FULL_KEYS = ("body", "full", "full10")
WINDOWS = ["pre", "post"]
SPEC_SOURCES = ["peps", "ietf", "rust", "riscv", "opentitan"]


def groups(key):
    return SPEC_SOURCES if key in SPEC_KEYS else WINDOWS


def group_of(key, r):
    return r["source"] if key in SPEC_KEYS else r["window"]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm(s):
    return " ".join(s.split())


def subtype(label):
    """Same rule as eval/harvest.py and eval/arxiv_rates.py subtype()."""
    m = re.search(r"\[([^\[\]]*)\]\s*$", label or "")
    if not m:
        return "-"
    return re.sub(r"^\d+(?:-part \S+| clauses),\s*", "",
                  m.group(1).strip()) or "-"


def detect(mod, cid, doc, nlp):
    """(text, start_char, end_char, pattern) of each span the detector
    produces."""
    if cid in mod.CONSTRUCTIONS:
        spans = [(h[0], h[3]) for h in mod.run_construction(cid, doc, nlp)]
    elif cid in mod.PHRASE_PATTERNS:
        from spacy.matcher import Matcher
        m = Matcher(nlp.vocab)
        m.add(cid, mod.PHRASE_PATTERNS[cid][3])
        spans = [(doc[s:e], "-") for _, s, e in m(doc)]
    else:
        raise SystemExit(f"{cid}: not a structural or built-in phrase "
                         "construction")
    return [(norm(sp.text.strip().replace("\n", " ")), sp.start_char,
             sp.end_char, pn) for sp, pn in spans]


def stored(cid, key, path, sub=None, pat=None):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        r = json.loads(line)
        if r["construction"] != cid:
            continue
        if sub is not None and subtype(r.get("label")) != sub:
            continue
        if pat is not None and r.get("pattern") != pat:
            continue
        t = r.get("type")
        if key in FULL_KEYS and t not in SECTION_TYPES:
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
            x = (sum(x[t] for t in SECTION_TYPES) if key in FULL_KEYS
                 else x["body"] if key == "bsec" else x["abstract"])
        w[group_of(key, r)] += x
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
                    help="comma list of abs, body, bsec, babs, full, spec, "
                         "full10, spec10")
    ap.add_argument("--subtype", default=None,
                    help="only stored findings with this subtype")
    ap.add_argument("--pattern", default=None,
                    help="only stored findings of this pattern; kept means "
                         "the new code reports it under the same pattern")
    ap.add_argument("--cross", action="store_true",
                    help="parse the stored span text, not the sentence, "
                         "when the span runs past its sentence (cc_cleft "
                         "across sentences)")
    ap.add_argument("--save", metavar="PATH",
                    help="write the per-finding outcomes as JSON (holds "
                         "sentences, so PATH must be under private/)")
    args = ap.parse_args()
    cid = args.construction
    if args.save and (ROOT / "private") not in \
            Path(args.save).resolve().parents:
        raise SystemExit("--save must name a file under private/")

    new = load_module("tf_new", ROOT / "tools" / "ticfinder.py")
    old = load_module("tf_old", args.old)
    nlp = new.load_model("en_core_web_md")

    keys = args.sources.split(",")
    table = []
    reading = defaultdict(lambda: {"dropped": [], "kept": [], "moved": []})
    cache, saved = {}, []
    for key, label, fpath, ppath in SOURCES:
        if key not in keys:
            continue
        w = words(key, ppath)
        rates = {}
        allrows = stored(cid, key, fpath, args.subtype, args.pattern)
        for win in groups(key):
            rows = [r for r in allrows if group_of(key, r) == win]
            n_old = n_new = n_new_only = n_moved = 0
            for r in rows:
                sent = r["context"]
                if args.cross and norm(r["text"]) not in norm(sent):
                    sent = r["text"]
                if sent not in cache:
                    doc = nlp(sent)
                    cache[sent] = (detect(old, cid, doc, nlp),
                                   detect(new, cid, doc, nlp))
                o, n = cache[sent]
                t = norm(r["text"])
                at = [(a, b) for x, a, b, pn in o if x == t
                      and (args.pattern is None or pn == args.pattern)]
                if not at:
                    if any(x == t for x, _, _, _ in n):
                        n_new_only += 1
                    continue
                n_old += 1
                # Kept when a new span covers the old one: a fix may widen
                # a span to the left ('More significantly,').
                cover = [(x, pn) for x, a, b, pn in n
                         if any(a <= oa and ob <= b for oa, ob in at)]
                same = [x for x, pn in cover
                        if args.pattern is None or pn == args.pattern]
                if same:
                    n_new += 1
                    outcome = "kept"
                    reading[win]["kept"].append((label, dict(
                        r, text=same[0])))
                elif cover:
                    n_moved += 1
                    outcome = "moved:" + cover[0][1]
                    reading[win]["moved"].append((label, r))
                else:
                    outcome = "dropped"
                    reading[win]["dropped"].append((label, r))
                saved.append(dict(r, recheck=outcome, group=win,
                                  corpus=key,
                                  same_span=bool(same) and same[0] == t))
            kw = w[win] / 1000
            scaled = len(rows) * n_new / n_old if n_old else 0.0
            rates[win] = (len(rows) / kw, n_new / kw, scaled / kw)
            table.append((label, win, len(rows), n_old, n_new, n_moved,
                          n_new_only, w[win], *rates[win]))
        if key not in SPEC_KEYS:
            table.append((label, "post/pre", None, None, None, None, None,
                          None, *(ratio(rates["post"][i], rates["pre"][i])
                                  for i in range(3))))

    what = f"{cid} [{args.subtype}]" if args.subtype else cid
    if args.pattern:
        what += f" {args.pattern}"
    print(f"\n{what}: stored findings rechecked on isolated sentences\n")
    hdr = ("source", "group", "stored", "old repro", "new kept", "moved",
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

    if args.save:
        Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        Path(args.save).write_text("".join(json.dumps(r) + "\n"
                                           for r in saved), encoding="utf-8")
    if args.show:
        rng = random.Random(f"{args.seed}-{cid}")
        for win in sorted({w for w in reading}):
            for kind in ("dropped", "kept"):
                items = reading[win][kind]
                pick = rng.sample(items, min(args.show, len(items)))
                print(f"\n== {win} {kind}: {len(pick)} of {len(items)}")
                for i, (label, r) in enumerate(pick, 1):
                    print(f"{i:2}. [{label}] <{norm(r['text'])}>")
                    print(f"    {norm(r['context'])[:300]}")


if __name__ == "__main__":
    main()
