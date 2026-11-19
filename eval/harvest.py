#!/usr/bin/env python3
"""Harvest labelled findings from a repo's edit history.

For each document that has a waiver file, compare the first committed
version (the LLM draft) against the current version:

  accepted   present now and waived        -> the editor judged it fine
  removed    present in the draft, gone now -> the editor edited it out
             (split into 'rewritten' when a similar sentence survives and
             'deleted' when the sentence disappeared entirely)
  open       present now, not waived        -> unlabelled

Usage:
  eval/harvest.py REPO --docs blogs/A.md blogs/B.md --waiver-dir waivers \
      --out eval/labels.jsonl [--by-subtype]
  eval/harvest.py --summary-only eval/labels.jsonl [--by-subtype]
  eval/harvest.py ... --json PATH

--summary-only regroups an existing labels file without running ticfinder
or reading REPO. --by-subtype splits each pattern row by subtype (see
subtype()). --json PATH also writes the summary rows as JSON, at both
pattern and subtype level whatever --by-subtype says (schema:
eval/TICFINDER_ROADMAP.md s.15). The text output does not change.
"""

import argparse
import datetime
import difflib
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
tf = None


def load_tf():
    """Import ticfinder (and spaCy) only when findings are produced."""
    global tf
    spec = importlib.util.spec_from_file_location(
        "tf", HERE.parent / "tools" / "ticfinder.py")
    tf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tf)


_BRACKET = re.compile(r"\[([^\[\]]*)\]\s*$")
# A leading member-count field, as TRICOLON writes it: "3-part NOUN, " or
# "3 clauses, ".
_COUNT_FIELD = re.compile(r"^\d+(?:-part \S+| clauses),\s*")


def subtype(label_text):
    """Subtype of a finding, from the bracketed tail of its label_text.

    Rule: take the last [...] group at the end of the label. If it starts
    with a member-count field ("3-part NOUN, " or "3 clauses, "), drop that
    field and keep the rest, so "[3-part NOUN, list-like]" groups as
    "list-like" and member count and part of speech do not split rows.
    Otherwise the whole bracket is the subtype: "[rather than]",
    "[paired aside]", and also "[X, not Y]" and "[cleft, across
    sentences]", whose commas are part of the name. Splitting on every
    comma would merge "X, not Y" with "not Y". A label with no bracketed
    tail gives "-".
    """
    m = _BRACKET.search(label_text or "")
    if not m:
        return "-"
    return _COUNT_FIELD.sub("", m.group(1).strip()) or "-"


def aggregate(rows, by_subtype=False):
    """{(construction, pattern[, subtype]): Counter of labels}."""
    agg = defaultdict(Counter)
    for r in rows:
        key = (r["construction"], r["pattern"] or "-")
        if by_subtype:
            key += (subtype(r["label_text"]),)
        lab = r["label"] if r["label"] != "removed" else \
            "removed_" + r["removal"]
        agg[key][lab] += 1
    return agg


JSON_SCHEMA = 1


def write_json(path, rows, labels_path):
    """Summary rows as numbers, at pattern and at subtype level."""
    tf_path = HERE.parent / "tools" / "ticfinder.py"
    commit = subprocess.run(
        ["git", "-C", str(HERE.parent), "log", "-1", "--format=%h", "--",
         "tools/ticfinder.py"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(HERE.parent), "status", "--porcelain", "--",
         "tools/ticfinder.py"], capture_output=True, text=True).stdout.strip()

    def level(by_subtype):
        out = []
        for key, n in sorted(aggregate(rows, by_subtype).items()):
            tp, fp = n["removed_rewritten"], n["accepted"]
            d = {"construction": key[0], "pattern": key[1]}
            if by_subtype:
                d["subtype"] = key[2]
            d.update({"rewritten": tp, "deleted": n["removed_deleted"],
                      "accepted": fp, "open": n["open"],
                      "prec": tp / (tp + fp) if tp + fp else None})
            out.append(d)
        return out
    tot = Counter()
    for n in aggregate(rows).values():
        tot.update(n)
    out = {"schema": JSON_SCHEMA, "kind": "harvest-summary",
           "tf_commit": commit + (" with uncommitted changes" if dirty
                                  else ""),
           "tf_sha256": hashlib.sha256(tf_path.read_bytes()).hexdigest()[:12],
           "generated": datetime.date.today().isoformat(),
           "labels": Path(labels_path).name,
           "labels_sha256": hashlib.sha256(
               Path(labels_path).read_bytes()).hexdigest()[:12],
           "prec_definition": "rewritten / (rewritten + accepted); deleted "
                              "excluded; null when both are 0",
           "totals": {"rewritten": tot["removed_rewritten"],
                      "deleted": tot["removed_deleted"],
                      "accepted": tot["accepted"], "open": tot["open"]},
           "patterns": level(False), "subtypes": level(True)}
    Path(path).write_text(json.dumps(out, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {path}", file=sys.stderr)


def summarise(rows, by_subtype=False):
    """Print the per construction / pattern (/ subtype) summary."""
    agg = aggregate(rows, by_subtype)
    sub_hdr = f" {'subtype':<24}" if by_subtype else ""
    print(f"\n{'construction':<22} {'pattern':<24}{sub_hdr} {'rewr':>5} "
          f"{'del':>5} {'acc':>5} {'open':>5} {'prec*':>6}")
    if by_subtype:
        # rows of one pattern stay together: pattern total, then subtype size
        ptot = Counter()
        for k, n in agg.items():
            ptot[k[:2]] += sum(n.values())
        order = sorted(agg.items(), key=lambda kv: (
            -ptot[kv[0][:2]], kv[0][:2], -sum(kv[1].values()), kv[0][2]))
    else:
        order = sorted(agg.items(), key=lambda kv: -sum(kv[1].values()))
    for key, n in order:
        c, p = key[:2]
        sub = f" {key[2]:<24}" if by_subtype else ""
        tp, fp = n["removed_rewritten"], n["accepted"]
        prec = f"{tp / (tp + fp):.2f}" if tp + fp else "  -"
        print(f"{c:<22} {p:<24}{sub} {tp:>5} {n['removed_deleted']:>5} "
              f"{fp:>5} {n['open']:>5} {prec:>6}")
    print("\nprec* = rewritten / (rewritten + accepted); deleted sentences "
          "excluded as ambiguous evidence.")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          capture_output=True, text=True).stdout


def first_version(repo, path):
    revs = git(repo, "log", "--follow", "--format=%h", "--", path).split()
    return revs[-1], git(repo, "show", f"{revs[-1]}:{path}")


def run(nlp, text, extra):
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(text)
        p = fh.name
    findings, _ = tf.analyse(p, nlp, None, extra, set())
    for f in findings:
        f.fp = tf.fingerprint(f)
    Path(p).unlink()
    return findings


def best_match(ctx, sentences):
    best = 0.0
    for s in sentences:
        r = difflib.SequenceMatcher(None, ctx, s).quick_ratio()
        if r > best:
            best = difflib.SequenceMatcher(None, ctx, s).ratio() \
                if r > 0.5 else best
    return best


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", nargs="?")
    ap.add_argument("--docs", nargs="+")
    ap.add_argument("--waiver-dir", default=None)
    ap.add_argument("--out", default=str(HERE / "labels.jsonl"))
    ap.add_argument("--model", default="en_core_web_md")
    ap.add_argument("--by-subtype", action="store_true",
                    help="group the summary by construction, pattern and "
                         "subtype")
    ap.add_argument("--summary-only", metavar="LABELS",
                    help="print the summary for an existing labels.jsonl; "
                         "runs no ticfinder and writes nothing")
    ap.add_argument("--json", metavar="PATH",
                    help="also write the summary rows as JSON")
    args = ap.parse_args()

    if args.summary_only:
        rows = [json.loads(line) for line in
                Path(args.summary_only).read_text(encoding="utf-8")
                .splitlines() if line.strip()]
        summarise(rows, args.by_subtype)
        if args.json:
            write_json(args.json, rows, args.summary_only)
        return
    if not args.repo or not args.docs:
        ap.error("REPO and --docs are required unless --summary-only "
                 "is given")
    load_tf()

    nlp = tf.load_model(args.model)
    extra = []
    for f in tf.discover_phrase_files(None):
        extra.extend(tf.load_phrase_file(f))

    rows = []
    for doc in args.docs:
        rev, draft = first_version(args.repo, doc)
        final = (Path(args.repo) / doc).read_text(encoding="utf-8")
        wpath = tf.waiver_path(Path(args.repo) / doc,
                               Path(args.repo) / args.waiver_dir
                               if args.waiver_dir else None)
        waivers, _ = tf.load_waivers(wpath, doc)
        held = {k for k, v in waivers.items() if tf.is_enabled(v)}

        f_draft = run(nlp, draft, extra)
        f_final = run(nlp, final, extra)
        final_ids = {f.fp for f in f_final}
        final_sents = [" ".join(s.text.split()).lower()
                       for s in nlp(tf.mask_markdown(final)).sents]

        def row(f, label, version):
            return {"doc": doc, "version": version, "fp": f.fp,
                    "construction": f.construction, "pattern": f.pattern,
                    "label_text": f.label, "confidence": f.confidence,
                    "text": f.text, "context": f.context, "line": f.line,
                    "label": label}

        for f in f_final:
            rows.append(row(f, "accepted" if f.fp in held else "open",
                            "final"))
        for f in f_draft:
            if f.fp in final_ids:
                continue
            sim = best_match(" ".join(f.context.split()).lower(), final_sents)
            r = row(f, "removed", rev)
            r["survivor_similarity"] = round(sim, 2)
            r["removal"] = "rewritten" if sim >= 0.6 else "deleted"
            rows.append(r)
        print(f"{doc}: draft {rev} {len(f_draft)} findings, "
              f"final {len(f_final)} ({len(held & final_ids)} waived)",
              file=sys.stderr)

    Path(args.out).write_text(
        "".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")

    summarise(rows, args.by_subtype)
    if args.json:
        write_json(args.json, rows, args.out)


if __name__ == "__main__":
    main()
