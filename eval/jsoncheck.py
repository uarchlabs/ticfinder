#!/usr/bin/env python3
"""Check a JSON summary against its text report.

Usage: python3 eval/jsoncheck.py SUMMARY.json REPORT.md

Renders every JSON row in the report's cell format (2 decimals, intervals
as "v (lo to hi)") and compares the multiset of rendered rows with the
report's table rows. The setup, sample, words and sanity tables are
skipped. Also checks that no numeric field holds a string other than
"inf". Prints MATCH and exits 0 when the two agree, or prints up to 5
rows from each side and exits 1.

Handles the "arxiv-rates" (TF-004), "arxiv-bodies" (TF-005 pilot and
TF-008 full run), "spec-baseline" (TF-009) and "llm-lr" (TF-012) kinds. The harvest summary has a different row shape and
is not covered.
"""
import json
import sys
from collections import Counter


def f(x):
    if x is None:
        return "-"
    if x == "inf":
        return "inf"
    return f"{x:.2f}"


def ci(v, lo, hi):
    return f"{f(v)} ({f(lo)} to {f(hi)})"


def c(d):
    return ci(d["value"], d["lo"], d["hi"])


def key(r):
    return r["key"].replace("|", " / ")


SPEC_SOURCES = (("peps", "PEPs"), ("ietf", "IETF RFCs"),
                ("rust", "Rust RFCs"), ("riscv", "RISC-V"),
                ("opentitan", "OpenTitan"))


def rr(d):
    return ci(d["rate"], d["rate_lo"], d["rate_hi"])


def render_spec(r):
    """Rows of the "spec-baseline" kind (TF-009)."""
    t = r["table"]
    if t.startswith("Rates: "):
        cells = " | ".join(f"{r['sources'][s]['n']}, {rr(r['sources'][s])}"
                           for s, _ in SPEC_SOURCES)
        return (f"| `{key(r)}` | {r['n']} | {r['documents']} | "
                f"{rr(r['pool_words'])} | {rr(r['pool_equal'])} | {cells} |")
    if "first" in r:
        a, b = r["first"], r["second"]
        return (f"| `{key(r)}` | {a['n']} | {rr(a)} | {b['n']} | {rr(b)} | "
                f"{c(r['ratio'])} | {r['interval']} |")
    names = dict(SPEC_SOURCES)
    outs = ", ".join(names[s] for s in r["outside"]) or "none"
    return (f"| `{key(r)}` | {rr(r['pool_equal'])} | "
            + " | ".join(rr(r["sources"][s]) for s, _ in SPEC_SOURCES)
            + f" | {outs} |")


def ci3(d, k):
    if d.get(k) is None:
        return "-"
    return ci(d[k], d[k + "_lo"], d[k + "_hi"])


def render_llm(r, bands):
    """Rows of the "llm-lr" kind (TF-012)."""
    t, k = r["table"], key(r)
    if t == "Sanity reading":
        return f"| `{k}` | {f(r['lr'])} | {r['real']} / {r['read']} |"
    if t == "Proposed bands":
        cur = r["current"] + (f" ({r['current_note']})"
                              if r["current_note"] else "")
        return (f"| `{k}` | {cur} | {ci3(r, 'lr')} | "
                + " | ".join(r["bands"][b["set"]] for b in bands)
                + f" | {r['flag'] or '-'} |")
    a = r["arxiv"]
    ax = "-" if a["ratio"] is None else ci(a["ratio"], a["lo"], a["hi"])
    head = (f"| `{k}` | {r['llm']['n']} | {rr(r['llm'])} | "
            f"{r['pool']['n']} | {rr(r['pool'])} | ")
    if t == "Rows without an LR":
        return head + f"{ax} |"
    return (head + f"{ci3(r, 'lr')} | {r['interval']} | {ax} | "
            f"{f(r['lr_shrunk'])} | {f(r['w'])} | {r['author']['n']} | "
            f"{ci3(r, 'lr_author')} | {r['flag'] or '-'} |")


def render(kind, r, j=None):
    t = r["table"]
    if kind == "llm-lr":
        return render_llm(r, j["bands"])
    if kind == "spec-baseline":
        return render_spec(r)
    if kind == "arxiv-rates":
        a, b = r["pre"], r["post"]
        return (f"| `{key(r)}` | {a['n']} | {a['papers']} | "
                f"{ci(a['rate'], a['rate_lo'], a['rate_hi'])} | {b['n']} | "
                f"{b['papers']} | {ci(b['rate'], b['rate_lo'], b['rate_hi'])}"
                f" | {ci(r['ratio'], r['ratio_lo'], r['ratio_hi'])} | "
                f"{r['verdict']} |")
    if t == "EM_DASH per text type":
        a, b = r["pre"], r["post"]
        return (f"| {r['text_type']} | {a['n']} | "
                f"{ci(a['rate'], a['rate_lo'], a['rate_hi'])} | {b['n']} | "
                f"{ci(b['rate'], b['rate_lo'], b['rate_hi'])} | "
                f"{ci(r['ratio'], r['ratio_lo'], r['ratio_hi'])} | "
                f"{r['verdict']} |")
    if t == "Check against TF-004":
        x = r["tf004"]
        return (f"| `{key(r)}` | {ci(x['value'], x['lo'], x['hi'])} | "
                f"{r['n_pre']} / {r['n_post']} | {c(r['sample_ratio'])} | "
                f"{'yes' if r['sample_inside_tf004'] else 'no'} | "
                f"{'yes' if r['tf004_inside_sample'] else 'no'} |")
    if t == "ALTERNATIVE_FRAMING by pattern":
        return (f"| {r['text_type']} | `{r['pattern']}` | {r['pre']['n']} | "
                f"{r['post']['n']} | "
                f"{ci(r['ratio'], r['ratio_lo'], r['ratio_hi'])} | "
                f"{r['verdict']} |")
    if "text_type_b" in r:
        return (f"| `{key(r)}` | {r['n_a']['pre']} / {r['n_a']['post']} | "
                f"{c(r['ratio_a'])} | {r['n_b']['pre']} / {r['n_b']['post']}"
                f" | {c(r['ratio_b'])} | {c(r['ratio_of_ratios'])} | "
                f"{'yes' if r['inside'] else 'no'} |")
    a, b = r["pre"], r["post"]
    return (f"| `{key(r)}` | {a['n']} | "
            f"{ci(a['rate'], a['rate_lo'], a['rate_hi'])}"
            f" | {ci(a['mean'], a['mean_lo'], a['mean_hi'])} | {b['n']} | "
            f"{ci(b['rate'], b['rate_lo'], b['rate_hi'])} | "
            f"{ci(b['mean'], b['mean_lo'], b['mean_hi'])} | "
            f"{ci(r['ratio'], r['ratio_lo'], r['ratio_hi'])} | "
            f"{r['verdict']} |")


SKIP = ("## Setup", "## Sample and masking", "## Words per text type",
        "## Sanity measures")


def report_rows(path):
    lines = open(path, encoding="utf-8").read().splitlines()
    out, skip = [], False
    for i, line in enumerate(lines):
        if line.startswith("## "):
            skip = line.startswith(SKIP)
        if skip or not line.startswith("|") or line.startswith("|---"):
            continue
        if i + 1 < len(lines) and lines[i + 1].startswith("|---"):
            continue            # header row
        out.append(line)
    return out


def walk(x):
    """Exit if a numeric field holds a string other than "inf"."""
    if isinstance(x, dict):
        for k, v in x.items():
            if (k in ("n", "papers", "rate", "ratio", "mean", "lr",
                      "lr_shrunk", "lr_author")
                    and isinstance(v, str) and v != "inf"):
                sys.exit(f"string number {k}={v}")
            walk(v)
    elif isinstance(x, list):
        for v in x:
            walk(v)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__.split("\n\n")[1])
    j = json.load(open(sys.argv[1], encoding="utf-8"))
    R = Counter(render(j["kind"], r, j) for r in j["rows"])
    T = Counter(report_rows(sys.argv[2]))
    print(f"{sys.argv[1]}: {sum(R.values())} JSON rows, "
          f"{sum(T.values())} report rows")
    miss, extra = T - R, R - T
    for line in list(miss)[:5]:
        print("  in report only:", line)
    for line in list(extra)[:5]:
        print("  in JSON only:  ", line)
    walk(j)
    print("  MATCH" if not miss and not extra else "  DIFFER")
    sys.exit(0 if not miss and not extra else 1)


if __name__ == "__main__":
    main()
