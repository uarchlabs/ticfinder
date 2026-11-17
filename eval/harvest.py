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
      --out eval/labels.jsonl
"""

import argparse
import difflib
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location(
    "tf", HERE.parent / "tools" / "ticfinder.py")
tf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tf)


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
    ap.add_argument("repo")
    ap.add_argument("--docs", nargs="+", required=True)
    ap.add_argument("--waiver-dir", default=None)
    ap.add_argument("--out", default=str(HERE / "labels.jsonl"))
    ap.add_argument("--model", default="en_core_web_md")
    args = ap.parse_args()

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

    # per construction / pattern summary
    agg = defaultdict(Counter)
    for r in rows:
        key = (r["construction"], r["pattern"] or "-")
        lab = r["label"] if r["label"] != "removed" else \
            "removed_" + r["removal"]
        agg[key][lab] += 1
    print(f"\n{'construction':<22} {'pattern':<24} {'rewr':>5} {'del':>5} "
          f"{'acc':>5} {'open':>5} {'prec*':>6}")
    for (c, p), n in sorted(agg.items(), key=lambda kv: -sum(kv[1].values())):
        tp, fp = n["removed_rewritten"], n["accepted"]
        prec = f"{tp / (tp + fp):.2f}" if tp + fp else "  -"
        print(f"{c:<22} {p:<24} {tp:>5} {n['removed_deleted']:>5} "
              f"{fp:>5} {n['open']:>5} {prec:>6}")
    print("\nprec* = rewritten / (rewritten + accepted); deleted sentences "
          "excluded as ambiguous evidence.")


if __name__ == "__main__":
    main()
