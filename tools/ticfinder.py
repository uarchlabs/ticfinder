#!/usr/bin/env python3
"""
ticfinder - find recurring LLM prose constructions in markdown/plain text.

Not a grammar checker. Every construction it finds is legitimate English.
The point is that they cluster in generated prose and break reader flow.
You decide what to cut.

Usage:
    python ticfinder.py article.md
    python ticfinder.py *.md --json out.json
    python ticfinder.py article.md --only NEG_ANTITHESIS,PARTICIPIAL_TAIL
    python ticfinder.py article.md --stats
"""

import argparse
import hashlib
import shutil
import textwrap
import html
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict, field
from pathlib import Path

import spacy
from spacy.matcher import Matcher, DependencyMatcher

MODEL = "en_core_web_md"


# ---------------------------------------------------------------- markdown

def mask_markdown(text: str, stats: dict = None) -> str:
    """Blank out regions that aren't the author's prose, preserving offsets.

    Every masked region is replaced with spaces of identical length, so
    character offsets into the masked string stay valid in the original.

    Flags are PER PATTERN. DOTALL must apply only to the fenced-code
    patterns: with DOTALL on a line-oriented pattern, `.*$` runs greedily to
    the last line of the file and blanks the entire remainder of the
    document.
    """
    def blank(m):
        return re.sub(r"[^\n]", " ", m.group(0))

    code_spans = []

    def unquote(m):
        """Keep inline-code content, blank only its delimiters.

        Inline code sits mid-sentence and usually *is* a noun there:
        'aging ran with `tage_enable_aging` and `ittage_enable_aging` held
        at zero'. Blanking the identifiers leaves a hole the parser reads
        across, inventing a verb coordination that is not in the source.
        Substituting filler distorts the parse a different way. Keeping the
        text and dropping the backticks is the only option that leaves the
        sentence as the author wrote it.
        """
        t = m.group(0)
        if "\n" in t:
            return blank(m)
        if len(t) < 2:
            return blank(m)
        # Offsets are stable because the backticks become spaces in place.
        code_spans.append((m.start() + 1, m.end() - 1))
        return " " + t[1:-1] + " "

    M = re.MULTILINE
    D = re.DOTALL

    # Pragma regions FIRST: the generic HTML-tag rule below would otherwise
    # consume the marker comments before we can pair them up.
    OFF = r"<!--\s*ticfinder[ _-]?off\s*-->"
    ON = r"<!--\s*ticfinder[ _-]?on\s*-->"
    n_regions = 0
    skipped_chars = 0

    def count_blank(m):
        nonlocal n_regions, skipped_chars
        n_regions += 1
        skipped_chars += len(m.group(0).strip())
        return blank(m)

    text = re.sub(OFF + r".*?" + ON, count_blank, text, flags=D | re.I)
    text = re.sub(OFF + r".*\Z", count_blank, text, flags=D | re.I)  # unclosed
    # Single-block skip: applies to the next blank-line-delimited block.
    text = re.sub(
        r"<!--\s*ticfinder[ _-]?skip\s*-->[^\n]*\n.*?(?=\n\s*\n|\Z)",
        count_blank, text, flags=D | re.I)

    if stats is not None:
        stats["pragma_regions"] = n_regions
        stats["pragma_chars"] = skipped_chars

    patterns = [
        (r"^```.*?^```", M | D),          # fenced code
        (r"^~~~.*?^~~~", M | D),          # alt fenced code
        (r"`[^`\n]+`", 0, unquote),      # inline code: keep, drop ticks
        (r"^ {4,}\S[^\n]*$", M),         # indented code
        (r"!\[[^\]]*\]\([^)]*\)", 0),    # images
        (r"\]\([^)]*\)", 0),            # link targets (keep link text)
        (r"^\s*\|[^\n]*\|\s*$", M),     # table rows
        (r"^\s*>[^\n]*$", M),            # blockquotes
        (r"^\s*[-*_]{3,}\s*$", M),       # horizontal rules
        (r"<[^>\n]+>", 0),               # html tags
    ]
    for entry in patterns:
        pat, flags = entry[0], entry[1]
        fn = entry[2] if len(entry) > 2 else blank
        text = re.sub(pat, fn, text, flags=flags)
    if stats is not None:
        stats["code_spans"] = code_spans
    return text


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


# ---------------------------------------------------------------- findings

@dataclass
class Finding:
    construction: str
    label: str
    text: str
    context: str
    line: int
    start: int
    end: int
    note: str = ""
    confidence: str = "med"
    pattern: str = ""
    fp: str = ""


# ------------------------------------------------------------------ waivers

WAIVER_SUFFIX = ".waivers.json"


def fingerprint(f):
    """Stable id for a finding.

    Deliberately excludes line number and character offsets: editing a
    paragraph higher up the file must not invalidate a waiver further down.
    Keyed on what was matched and the sentence it sat in, both
    whitespace-normalised, so reflowing a paragraph is safe too.
    """
    def norm(x):
        return " ".join(x.split()).lower()
    raw = "\u0000".join([f.construction, f.pattern or "",
                          norm(f.text), norm(f.context)])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:6]


def waiver_path(src, waiver_dir=None, explicit=None):
    """Where the waivers for one source file live.

    Derived from the source stem so there is nothing to type and nothing to
    typo -- a mistyped --waiver-file silently creates an empty baseline and
    looks exactly like lost work.
    """
    if explicit:
        return Path(explicit)
    stem = Path(src).stem + WAIVER_SUFFIX
    return (Path(waiver_dir) / stem) if waiver_dir else \
        Path(src).parent / stem


def load_waivers(path, src):
    """Read a waiver file, warning if it was written for a different source.

    Basename collisions are possible when two directories hold the same
    filename, so the source path is recorded and checked rather than
    mangled into the waiver filename.
    """
    p = Path(path)
    if not p.exists():
        return {}, None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {}, f"could not read {p}: {e}"
    recorded = data.get("source")
    warn = None
    if recorded and Path(recorded).as_posix() != Path(src).as_posix():
        warn = (f"{p} was written for {recorded}, not {src} -- "
                f"waivers may not apply")
    return data.get("waivers", {}), warn


def save_waivers(path, src, waivers):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    # An empty waiver file is written, not deleted. It records that the
    # document was reviewed and currently holds no waivers, which is not the
    # same as never having been looked at -- and the tool should not remove
    # files the user created.
    p.write_text(json.dumps(
        {"source": Path(src).as_posix(),
         "generated_by": "ticfinder",
         "waivers": waivers}, indent=2, sort_keys=True), encoding="utf-8")


# ---------------------------------------------------------------- registry

CONSTRUCTIONS = {}


def construction(cid, label, note="", confidence="med"):
    """Declare a construction: a rhetorical move with a stable identity.

    A construction is what a reviewer mutes and what counts are reported
    against. It owns one or more *patterns* -- the executable queries that
    find its surface realisations. Patterns are disposable; when phrasing
    drifts you add patterns and keep the id.
    """
    def deco(fn):
        CONSTRUCTIONS[cid] = {
            "label": label, "note": note, "confidence": confidence,
            "patterns": [(fn.__name__, fn, None)],
        }
        return fn
    return deco


def pattern(cid, confidence=None):
    """Attach an additional pattern to an existing construction.

    A pattern may override the construction's confidence. Patterns within one
    construction can have very different base rates -- 'not X but Y' is rare
    and diagnostic, a bare 'rather than' is ordinary English -- and reporting
    them at the same confidence makes the strong ones look unreliable.
    """
    def deco(fn):
        if cid not in CONSTRUCTIONS:
            raise KeyError(f"pattern for unknown construction {cid!r}")
        CONSTRUCTIONS[cid]["patterns"].append((fn.__name__, fn, confidence))
        return fn
    return deco


def run_construction(cid, doc, nlp, disabled=()):
    """Run every pattern for a construction, dropping duplicate spans.

    Patterns overlap by design -- the same sentence can satisfy two of them.
    The construction reports once, tagged with the pattern that found it.
    """
    base = CONSTRUCTIONS[cid]["confidence"]
    seen, out = [], []
    for pname, fn, pconf in CONSTRUCTIONS[cid]["patterns"]:
        if disabled and pname in disabled:
            continue
        try:
            hits = fn(doc, nlp)
        except Exception:
            continue
        for hit in hits:
            # A pattern may return (span, subtype) or, when confidence
            # varies per finding, (span, subtype, confidence).
            if len(hit) == 3:
                span, sub, hconf = hit
            else:
                (span, sub), hconf = hit, None
            if span.end <= span.start or not span.text.strip():
                continue        # a zero-width span highlights nothing
            key = (span.start, span.end)
            if any(a <= key[0] and key[1] <= b for a, b in seen):
                continue
            seen = [(a, b) for a, b in seen
                    if not (key[0] <= a and b <= key[1])]
            seen.append(key)
            out.append((span, sub, hconf or pconf or base, pname))
    return out



# ------------------------------------------------------------ phrase files

DEFAULT_PHRASE_FILES = ("ticfinder-phrases.json", ".ticfinder-phrases.json")


def load_phrase_file(path):
    """Read user-defined phrase lists.

    Full form:

        {"constructions": [
           {"id": "OVERUSED_PHRASE", "label": "Overused phrase",
            "note": "...", "confidence": "low",
            "phrases": ["ground truth", "deep dive"]}
        ]}

    Shorthand -- a bare list, or a mapping of id to phrase list:

        ["ground truth", "deep dive"]
        {"JARGON": ["ground truth"], "FILLER": ["at the end of the day"]}
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    if isinstance(data, list):
        data = {"constructions": [{"id": "OVERUSED_PHRASE",
                                   "phrases": data}]}
    elif "constructions" not in data:
        data = {"constructions": [{"id": k, "phrases": v}
                                  for k, v in data.items()]}

    out = []
    for i, c in enumerate(data["constructions"]):
        if "id" not in c:
            raise ValueError(f"{path}: construction {i} has no 'id'")
        phrases = c.get("phrases") or []
        if not phrases:
            continue
        conf = c.get("confidence", "low")
        if conf not in ("high", "med", "low"):
            raise ValueError(f"{path}: bad confidence {conf!r} in {c['id']} "
                             f"(use high, med or low)")
        out.append({
            "id": c["id"],
            "label": c.get("label", "Overused phrase"),
            "note": c.get("note", "Flagged from a user phrase list."),
            "confidence": conf,
            "lemma": bool(c.get("match_lemma", False)),
            "phrases": phrases,
        })
    return out


def phrase_patterns(entry, nlp):
    """Turn phrase strings into Matcher patterns.

    Tokenised with spaCy so contractions and punctuation line up with the
    document -- "don't" is two tokens, not one.
    """
    key = "LEMMA" if entry["lemma"] else "LOWER"
    pats = []
    for ph in entry["phrases"]:
        # nlp.tokenizer() does NOT run the lemmatizer, so lemma_ would be
        # empty and every LEMMA pattern would silently fail to match.
        doc = nlp(ph) if entry["lemma"] else nlp.tokenizer(ph)
        toks = [t for t in doc if not t.is_space]
        if not toks:
            continue
        pats.append([{key: (t.lemma_.lower() if entry["lemma"]
                            else t.lower_)} for t in toks])
    return pats


def discover_phrase_files(explicit):
    """Explicit paths win; otherwise look in cwd and beside the script."""
    if explicit:
        return [Path(x) for x in explicit]
    found = []
    for d in (Path.cwd(), Path(__file__).resolve().parent):
        for name in DEFAULT_PHRASE_FILES:
            f = d / name
            if f.exists() and f not in found:
                found.append(f)
    return found



# ---------------------------------------------------------------- pragmas

PRAGMA_RE = re.compile(
    r"<!--\s*ticfinder[ _-]"
    r"(?P<verb>off|on|disable|enable|ignore)"
    r"(?P<args>[^>]*?)-->",
    re.IGNORECASE)


def suppressed(finding, regions):
    """True if a finding falls inside a region that gates its construction.

    A finding counts as inside if it *starts* inside -- a construction that
    straddles the boundary belongs to where it began.
    """
    for start, end, ids in regions:
        if start <= finding.start < end:
            if ids is None or finding.construction in ids:
                return True
    return False


def gated_words(raw, regions):
    """Words inside blanket (non-selective) regions, for the rate
    denominator. Selective regions still count -- their prose is analysed,
    just not for one construction."""
    n = 0
    for start, end, ids in regions:
        if ids is None:
            n += len([w for w in raw[start:end].split()
                      if any(c.isalpha() for c in w)])
    return n


# ---------------------------------------------------------------- helpers

def sent_context(span, doc):
    return span.sent.text.strip().replace("\n", " ")


def conj_chain(tok, follow_appos=False):
    """All conjuncts of a coordination, in text order.

    spaCy produces several shapes for the same coordination and which one you
    get is not predictable: a chain (A -conj-> B -conj-> C), flat (A with
    conj children B and C), or, for comma-separated noun series, a mix where
    the middle item lands as `appos`. 'a counter, a usefulness field, and a
    target' parses as counter -appos-> field -conj-> target.

    follow_appos picks up that third shape. Callers that use it should
    require a coordinator in the span, so ordinary apposition ('Sam, my
    editor, called') is not read as a series.
    """
    def bracketed(t):
        """A parenthetical gloss -- 'a counter (CTR)' -- is also `appos`,
        and following it would inflate the series with its own labels."""
        prev = t.doc[t.i - 1] if t.i else None
        return prev is not None and prev.text in ("(", "[", "{")

    def crosses_break(a, b):
        """A colon, semicolon or dash ends the series.

        The parser will happily hang a conjunct across one -- in 'checks
        failed ... and passed after, with the values showing the exact
        corruption: expected c000, actual e000, and expected c000' it makes
        both `expected`s conjuncts of `failed`. They are a separate list
        introduced by the colon.
        """
        lo, hi = (a.i, b.i) if a.i < b.i else (b.i, a.i)
        return any(t.text in (":", ";", "\u2014", "\u2013")
                   for t in a.doc[lo:hi])

    links = {"conj", "appos"} if follow_appos else {"conj"}
    out, stack = [tok], [tok]
    while stack:
        cur = stack.pop()
        for c in cur.children:
            if c.dep_ not in links:
                continue
            if c.dep_ == "appos" and bracketed(c):
                continue
            if crosses_break(cur, c):
                continue
            out.append(c)
            stack.append(c)
    return sorted(set(out), key=lambda t: t.i)


# ---------------------------------------------------------------- detectors

@construction(
    "CORRECTIVE_CONTRAST", "Corrective contrast (rejects X, asserts Y)",
    "One rhetorical move with many surface forms: 'not X but Y', 'it's not X, "
    "it's Y', 'X, not Y', 'a feature, not a bug'. Legitimate when X was "
    "actually "
    "claimed by someone. Check the document for where X was raised -- if "
    "nowhere, the contrast is manufactured and the sentence is doing rhythm, "
    "not argument.",
    "high")
def cc_coordinated(doc, nlp):
    """not X but Y -- explicit coordinator.

    Anchor on the negation, not the verb: in 'optimised not for throughput
    but for predictability' the `not` attaches to the preposition.
    """
    out, seen = [], set()
    for neg in doc:
        if neg.dep_ != "neg" and neg.lower_ not in ("not", "n't"):
            continue
        node, hops = neg.head, 0
        while node is not None and hops < 4:
            for pred in list(node.children) + [node]:
                conjs = [c for c in pred.children if c.dep_ == "conj"]
                if not conjs:
                    continue
                ccs = [c for c in pred.children if c.dep_ == "cc"] + \
                      [c for j in conjs for c in j.children if c.dep_ == "cc"]
                if not any(c.lemma_ in ("but", "rather") for c in ccs):
                    continue
                if _independent(conjs):
                    continue
                lo = min(neg.i, pred.left_edge.i)
                hi = max(j.right_edge.i for j in conjs)
                if (lo, hi) in seen:
                    continue
                seen.add((lo, hi))
                out.append((doc[lo:hi + 1], "not X but Y"))
            if node.head is node:
                break
            node, hops = node.head, hops + 1
    return out


def _independent(conjs):
    """True if a conjunct is a full clause with its own subject.

    'I did not go but I read the notes' is ordinary clause coordination.
    A conjunct with a `mark` (that/because) is a complement clause filling
    one slot, so it stays.
    """
    for j in conjs:
        kids = {ch.dep_ for ch in j.children}
        if kids & {"nsubj", "nsubjpass"} and "mark" not in kids:
            return True
    return False


@pattern("CORRECTIVE_CONTRAST")
def cc_cleft(doc, nlp):
    """it's not X, it's Y -- two copulas, including across a period.

    "...was not that it is slow. It is that it validates..." is the same
    construction; the period is a stylistic choice, so the window is
    token-based rather than sentence-scoped.
    """
    out = []
    cops = [t for t in doc if t.lemma_ == "be" and t.pos_ in ("AUX", "VERB")]
    used = set()
    for i, c1 in enumerate(cops):
        if not any(ch.dep_ == "neg" for ch in c1.children) or c1.i in used:
            continue
        for c2 in cops[i + 1:]:
            if c2.i - c1.i > 22:
                break
            if any(ch.dep_ == "neg" for ch in c2.children):
                continue
            gap = doc[c1.i:c2.i].text
            if not re.search(r"[,;:.\u2014\u2013-]", gap):
                continue
            subj = [ch for ch in c2.children
                    if ch.dep_ in ("nsubj", "nsubjpass")]
            if not subj:
                continue
            if subj[0].lower_ not in ("it", "that", "this", "the", "what") \
                    and subj[0].pos_ not in ("PRON", "DET"):
                continue
            lo = min(c1.left_edge.i, c1.sent.start if c1.sent else c1.i)
            out.append((doc[lo:c2.right_edge.i + 1],
                        "cleft, across sentences" if "." in gap
                        else "cleft"))
            used.update({c1.i, c2.i})
            break
    return out


@pattern("CORRECTIVE_CONTRAST")
def cc_parallel_sibling(doc, nlp):
    """X, not Y -- asyndetic, no coordinator, polarity reversed.

    'derived from the row, not from the design under test'

    spaCy gives no `conj` here: both phrases are sibling children of one
    head with the same dependency label, and the negation sits on the
    second. This is the reversed-polarity form, positive first.
    """
    out = []
    for head in doc:
        kids = [c for c in head.children
                if c.dep_ in ("prep", "attr", "dobj", "pobj", "advmod",
                              "acomp", "npadvmod", "oprd", "nmod", "obl")]
        for a, b in zip(kids, kids[1:]):
            if a.dep_ != b.dep_ or b.i - a.i > 18:
                continue
            neg_b = [c for c in b.children if c.dep_ == "neg"]
            neg_a = [c for c in a.children if c.dep_ == "neg"]
            if bool(neg_a) == bool(neg_b):
                continue                   # need exactly one negated
            between = doc[a.right_edge.i:b.left_edge.i].text
            if not re.search(r"[,;\u2014\u2013]", between):
                continue                   # needs the pause
            lo = a.left_edge.i
            out.append((doc[lo:b.right_edge.i + 1],
                        "X, not Y" if neg_b else "not X, Y"))
    return out


@pattern("CORRECTIVE_CONTRAST")
def cc_negated_apposition(doc, nlp):
    """X, not Y where spaCy calls Y an apposition of X.

    'It is a feature, not a bug.'  'We chose speed, not correctness.'

    The parser attaches `not` to the FIRST element, not the second, so the
    signature is: head with an `appos` child, and a `neg` child of the head
    sitting linearly between the two.
    """
    out = []
    for head in doc:
        apps = [c for c in head.children if c.dep_ == "appos"]
        if not apps:
            continue
        negs = [c for c in head.children if c.dep_ == "neg"]
        for app in apps:
            if app.i - head.i > 18:
                continue
            mid = [n for n in negs if head.i < n.i < app.i] or \
                  [n for n in app.children if n.dep_ == "neg"]
            if not mid:
                continue
            out.append((doc[head.left_edge.i:app.right_edge.i + 1],
                        "X, not Y"))
    return out


@construction(
    "ALTERNATIVE_FRAMING", "Alternative framing (rather than / instead of)",
    "Separate from CORRECTIVE_CONTRAST because the base rate is completely "
    "different: 'rather than' is ordinary English and describes real choices "
    "between real options. Only a tic when the rejected alternative was never "
    "on the table. Expect false positives in technical writing; mute this id "
    "with --off if it is not earning its place.",
    "low")
def af_rather_instead(doc, nlp):
    """rather than X, Y / instead of X, Y.

    Purely lexical -- no negation, no structural check. Kept at low
    confidence and behind its own id so it can be muted without losing the
    diagnostic patterns.
    """
    out = []
    for tok in doc:
        if tok.lower_ not in ("rather", "instead"):
            continue
        nxt = doc[tok.i + 1] if tok.i + 1 < len(doc) else None
        if nxt is None or nxt.lower_ not in ("than", "of"):
            continue
        anchor = tok.head
        lo = min(tok.i, anchor.left_edge.i)
        hi = max(tok.right_edge.i, anchor.right_edge.i)
        out.append((doc[lo:hi + 1], f"{tok.lower_} {nxt.lower_}"))
    return out


@pattern("ALTERNATIVE_FRAMING")
def af_less_than(doc, nlp):
    """less about X than about Y."""
    out = []
    for tok in doc:
        if tok.lower_ not in ("less", "more"):
            continue
        for t in doc[tok.i + 1:min(tok.i + 14, len(doc))]:
            if t.lower_ == "than":
                out.append((doc[tok.head.left_edge.i:
                                min(t.right_edge.i + 6, len(doc))],
                            f"{tok.lower_}...than"))
                break
    return out


@construction(
    "NEG_ESCALATION", "Negation escalation (didn't X, and couldn't have)",
    "Second conjunct is gapped and upgrades the modality -- from 'did not' to "
    "'could not have'. Adds emphasis, not information. Check whether the "
    "counterfactual is doing any work.",
    "high")
def neg_escalation(doc, nlp):
    """Negation, coordination, then a gapped conjunct that raises modality.

    'Manual testing did not catch this, and could not have.'

    Distinguished from ordinary and-coordination by the absence of a subject
    in the second conjunct: it is elliptical, sharing the first clause's
    subject and verb.
    """
    modals = {"could", "would", "should", "might", "can", "will", "must",
              "may", "shall"}
    out = []
    for tok in doc:
        if tok.dep_ != "conj":
            continue
        kids = {c.dep_ for c in tok.children}
        if "nsubj" in kids or "nsubjpass" in kids:
            continue
        head = tok.head
        if not any(c.dep_ == "neg" for c in head.children):
            continue
        negs = [c for c in tok.children if c.dep_ == "neg"]
        auxs = [c for c in tok.children if c.dep_ in ("aux", "auxpass")]
        if not negs:
            continue
        never = any(n.lower_ == "never" for n in negs)
        modal = any(x.lower_ in modals for x in auxs)
        if not (modal or never):
            continue
        lo = min(head.left_edge.i, tok.left_edge.i)
        out.append((doc[lo:tok.right_edge.i + 1],
                    "modal" if modal else "never"))
    return out


@construction(
    "ABSTRACT_ADVERB", "Abstract adverb + adjective",
    "'structurally unable', 'fundamentally different'. The adverb adds a "
    "claim of rigour without narrowing the adjective. Usually deletable.",
    "high")
def abstract_adverb(doc, nlp):
    """-ally adverb premodifying an adjective: 'structurally unable'.

    Restricted to adjective heads. An -ally adverb on a VERB is usually an
    ordinary manner adverb -- 'writes these fields individually' -- which is
    plain English, not a tic. Also requires the adverb to precede its head:
    the construction is premodification, and a postposed adverb is a
    different thing.
    """
    skip = {"really", "actually", "usually", "generally", "finally",
            "originally", "normally", "typically", "eventually", "equally",
            "literally", "specially", "especially", "occasionally",
            "totally", "personally", "annually", "initially", "individually",
            "respectively", "manually", "automatically", "electrically",
            "mechanically", "physically", "locally", "globally", "internally",
            "externally", "serially", "sequentially", "conditionally",
            "optionally", "statically", "dynamically"}
    out = []
    for tok in doc:
        if tok.pos_ != "ADV" or tok.lower_ in skip:
            continue
        if not tok.lower_.endswith("ally"):
            continue
        if tok.dep_ != "advmod":
            continue
        head = tok.head
        if head.pos_ != "ADJ" and head.tag_ != "VBN":
            continue
        if tok.i >= head.i:
            continue
        out.append((doc[tok.i:head.i + 1], tok.lower_))
    return out


@construction(
    "EMPHATIC_REFLEXIVE", "Emphatic reflexive",
    "'the rule document itself'. Marks a distinction the sentence may not "
    "have earned. Check that the contrast is real.",
    "med")
def emphatic_reflexive(doc, nlp):
    out = []
    for tok in doc:
        if tok.lower_.endswith(("itself", "themselves", "himself",
                                "herself")) and tok.dep_ != "dobj":
            out.append((doc[max(tok.i - 3, 0):tok.i + 1], tok.lower_))
    return out


@construction(
    "PARTICIPIAL_TAIL", "Sentence-final participial adjunct",
    "', making/allowing/ensuring...' tacked onto a finished clause. Usually "
    "restates the consequence the reader already inferred. Try deleting it.",
    "high")
def participial_tail(doc, nlp):
    out = []
    for tok in doc:
        if tok.dep_ != "advcl" or tok.tag_ != "VBG":
            continue
        if tok.i == 0 or doc[tok.i - 1].text != ",":
            continue
        if tok.i < tok.head.i:            # fronted, not a tail
            continue
        out.append((doc[tok.i - 1:tok.right_edge.i + 1], tok.lemma_))
    return out


@construction(
    "TRICOLON", "Coordination of three or more",
    "Every coordination is reported, labelled by how list-like it looks: "
    "figure, list-like, or enumeration. Ordinary lists share the parse of a "
    "rhetorical tricolon and no test separates them reliably, so the label is "
    "a hint and the judgement is yours. Filter with --off tricolon or waive "
    "the enumerations.",
    "low")
def tricolon(doc, nlp):
    """Coordination of three or more items, classified but not suppressed.

    Ordinary enumerations have the same parse as a rhetorical tricolon, and
    no test separates them reliably. Rather than guess and hide the ones it
    guesses wrong, this reports every coordination and labels how
    list-like it looks, so the reviewer decides. The subtype is in the
    finding label and drives confidence:

        figure       few enumeration signals -- probably rhetorical
        list-like    some signals
        enumeration  several signals -- probably an ordinary list

    Genuine parse errors are still dropped: a coordination with no commas is
    a compound, not a series.
    """
    ENUM_CUES = {
        "example", "examples", "condition", "conditions", "type", "types",
        "kind", "kinds", "category", "categories", "field", "fields",
        "format", "formats", "option", "options", "value", "values",
        "state", "states", "component", "components", "element", "elements",
        "item", "items", "column", "columns", "parameter", "parameters",
        "flag", "flags", "mode", "modes", "stage", "stages", "step", "steps",
        "case", "cases", "rule", "rules", "table", "tables", "entry",
        "entries", "list", "signal", "signals", "port", "ports",
    }
    ENUM_VERBS = {"include", "comprise", "consist", "contain", "hold",
                  "specify", "list", "define", "cover", "support", "accept"}
    out = []
    seen = set()
    for tok in doc:
        if tok.dep_ == "conj":
            continue
        if tok.dep_ == "appos" and any(c.dep_ == "conj"
                                       for c in tok.head.children):
            continue        # the head owns the series; it will be the root
        if not any(c.dep_ in ("conj", "appos") for c in tok.children):
            continue
        chain = conj_chain(tok, follow_appos=True)
        if len(chain) < 3 or chain[0].i in seen:
            continue

        span = doc[chain[0].left_edge.i:chain[-1].right_edge.i + 1]

        # A series needs a coordinator. Without one this is apposition --
        # 'Postgres, the primary store, went down'.
        if not any(t.dep_ == "cc" for t in span):
            continue

        # Not a judgement call: a series is punctuated. Without commas this
        # is a compound, and often a parse error -- spaCy makes 'table' a
        # conjunct of 'TAGE' in 'a TAGE or ITTAGE table entry'.
        if sum(1 for t in span if t.text == ",") < len(chain) - 2:
            continue

        widths = []
        for i, c in enumerate(chain):
            lo, hi = c.left_edge.i, c.right_edge.i
            if i + 1 < len(chain):
                hi = min(hi, chain[i + 1].left_edge.i - 1)
            widths.append(max(1, hi - lo + 1))

        score = 0
        if len(chain) > 3:
            score += 1                      # a catalogue, not a triad
        if sum(1 for c in chain
               if any(k.dep_ in ("det", "poss") for k in c.children)) >= 2:
            score += 1                      # items are referents
        if sum(1 for c in chain
               if any(k.dep_ in ("amod", "compound", "nmod")
                      for k in c.children)) >= len(chain) - 1:
            score += 1                      # a taxonomy being listed
        lead = doc[tok.sent.start:chain[0].i]
        low = lead.text.lower()
        if any(t.lemma_.lower() in ENUM_CUES or t.lemma_.lower() in ENUM_VERBS
               for t in lead) or any(
                   k in low for k in ("such as", "e.g.", "i.e.", "namely",
                                      "including", "for example",
                                      "for instance")):
            score += 2                      # strongest single signal
        if max(widths) > 5 or max(widths) - min(widths) > 3:
            score += 1                      # uneven members: narration

        if score >= 3:
            kind, conf = "enumeration", "low"
        elif score >= 1:
            kind, conf = "list-like", "low"
        else:
            kind, conf = "figure", "med"

        seen.add(chain[0].i)
        out.append((span, f"{len(chain)}-part {tok.pos_}, {kind}", conf))
    return out


@pattern("TRICOLON", confidence="med")
def tricolon_parataxis(doc, nlp):
    """Asyndetic clause tricolon: 'He came, he saw, he conquered.'

    No coordinator, so spaCy uses parataxis/ccomp rather than conj. Requires
    three short clauses of similar length -- long paratactic runs are
    ordinary comma-spliced narration, not a figure.
    """
    out = []
    for root in doc:
        kids = [c for c in root.children
                if c.dep_ in ("parataxis", "ccomp") and c.pos_ == "VERB"]
        if len(kids) < 1:
            continue
        clauses = sorted(kids + [root], key=lambda t: t.i)
        if len(clauses) < 3:
            continue
        def own_width(t):
            kid_spans = {i for k in t.children
                         if k.dep_ in ("parataxis", "ccomp")
                         for i in range(k.left_edge.i, k.right_edge.i + 1)}
            return len([x for x in t.subtree if x.i not in kid_spans
                        and not x.is_punct])
        widths = [own_width(c) for c in clauses]
        if max(widths) > 4:
            continue                # long clauses: narration, not a figure
        if any(any(k.dep_ == "cc" for k in c.children) for c in clauses):
            continue                # has a coordinator; the conj pattern owns it
        lo = min(c.left_edge.i for c in clauses)
        hi = max(c.right_edge.i for c in clauses)
        out.append((doc[lo:hi + 1], "3 clauses, asyndetic"))
    return out


@construction(
    "DISGUISE_METAPHOR", "Concealment metaphor (X wrapped in a Y)",
    "Abstract noun given physical clothing. Reads as clever once, as a "
    "verbal tic by the third instance.",
    "high")
def disguise_metaphor(doc, nlp):
    """A thing described as disguised as another thing.

    'A bug wrapped in an excuse trenchcoat.'

    Verbs split into two groups. `masquerade`, `disguise`, `pose` and
    `dress up as` are metaphorical on their own. `wrap`, `wear`, `cloak` and
    `veil` are used literally all the time -- 'wrapped in brown paper' -- so
    those additionally require a garment or covering noun as the object.
    """
    ALWAYS = {"masquerade", "disguise", "pose", "parade", "pass"}
    NEEDS_GARMENT = {"wrap", "wear", "cloak", "clothe", "veil", "drape",
                     "dress", "mask", "package"}
    GARMENT = {"trenchcoat", "coat", "costume", "clothing", "clothes",
               "disguise", "mask", "veil", "cloak", "guise", "garb", "suit",
               "dress", "uniform", "wrapper", "cover", "camouflage",
               "outfit", "robe", "shroud", "skin", "packaging", "wrapping"}
    out = []
    for tok in doc:
        if tok.tag_ not in ("VBN", "VBG"):
            continue
        lemma = tok.lemma_
        if lemma not in ALWAYS and lemma not in NEEDS_GARMENT:
            continue
        objs, as_frame = [], False
        for c in tok.children:
            if c.dep_ == "prep" and c.lemma_ in ("in", "as", "up"):
                if c.lemma_ == "as":
                    as_frame = True
                objs += [g for g in c.children if g.dep_ == "pobj"]
                for g in c.children:
                    if g.dep_ == "prep":
                        if g.lemma_ == "as":
                            as_frame = True
                        objs += [h for h in g.children if h.dep_ == "pobj"]
            elif c.dep_ == "dobj":
                objs.append(c)
        if not objs:
            continue
        # 'X as Y' asserts a false identity and is always the construction.
        # 'X in Y' is literal half the time -- 'wrapped in brown paper' --
        # so it needs a garment or covering to qualify.
        if not as_frame and lemma in NEEDS_GARMENT and not any(
                o.lemma_.lower() in GARMENT for o in objs):
            continue
        if tok.dep_ not in ("acl", "advcl", "relcl", "ROOT", "conj",
                            "xcomp", "ccomp"):
            continue
        out.append((doc[tok.head.left_edge.i:tok.right_edge.i + 1], lemma))
    return out


# ------------------------------------------------- lexical / phrasal layer

PHRASE_PATTERNS = {
    "FRAME_MARKER": (
        "Throat-clearing / advance organizer",
        "Announces what the sentence will do instead of doing it. Almost "
        "always deletable with no loss.",
        "high",
        [
            [{"LOWER": "it"}, {"LEMMA": "be"}, {"LOWER": "worth"},
             {"LOWER": {"IN": ["noting", "mentioning", "remembering",
                               "considering", "pointing"]}}],
            [{"LOWER": {"IN": ["it", "its", "it's"]}}, {"LEMMA": "be",
                                                        "OP": "?"},
             {"LOWER": "important"}, {"LOWER": "to"}],
            [{"LOWER": "let"}, {"LOWER": {"IN": ["me", "us", "'s"]}},
             {"LOWER": "be"}, {"LOWER": {"IN": ["clear", "honest",
                                                "precise"]}}],
            [{"LOWER": "before"}, {"LOWER": "we"},
             {"LOWER": {"IN": ["dive", "begin", "start", "get"]}}],
            [{"LOWER": "i"}, {"LOWER": {"IN": ["'ll", "will"]}},
             {"LOWER": "say"}, {"LOWER": "this"}],
            [{"LOWER": "here"}, {"LOWER": {"IN": ["'s", "is"]}},
             {"LOWER": "the"}, {"LOWER": {"IN": ["thing", "key", "catch",
                                                 "problem", "kicker"]}}],
            [{"LOWER": "to"}, {"LOWER": "be"}, {"LOWER": {"IN":
                ["clear", "fair", "honest", "blunt"]}}],
            [{"LOWER": "at"}, {"LOWER": {"IN": ["its", "their"]}},
             {"LOWER": "core"}],
            [{"LOWER": "in"}, {"LOWER": "today"}, {"LOWER": "'s"}],
        ]),

    "HOLLOW_BOOSTER": (
        "Unearned assertion of importance",
        "Claims the next clause matters more than its neighbours. Check that "
        "it actually does; if every paragraph has one, none of them do.",
        "med",
        [
            [{"LOWER": {"IN": ["crucially", "importantly", "critically",
                               "notably", "tellingly", "significantly"]}},
             {"LOWER": ","}],
            [{"LOWER": "and"}, {"LOWER": {"IN": ["this", "that"]}},
             {"LEMMA": "be"}, {"LOWER": "the"},
             {"LOWER": {"IN": ["real", "true", "actual", "core"]}}],
            [{"LOWER": "the"}, {"LOWER": {"IN": ["real", "true", "actual"]}},
             {"LOWER": {"IN": ["problem", "issue", "question", "point",
                               "answer", "reason"]}}],
            [{"LOWER": "this"}, {"LEMMA": "be"}, {"LOWER": "the"},
             {"LOWER": {"IN": ["crux", "heart", "core", "essence"]}}],
            [{"LOWER": "cannot"}, {"LOWER": "be"},
             {"LOWER": {"IN": ["overstated", "understated", "overstressed"]}}],
        ]),

    "CLOSER": (
        "Summative closer",
        "Signals a conclusion. Fine once per piece; a tic when every section "
        "ends this way.",
        "med",
        [
            [{"LOWER": {"IN": ["ultimately", "fundamentally", "essentially"]}},
             {"LOWER": ","}],
            [{"LOWER": "at"}, {"LOWER": "the"}, {"LOWER": "end"},
             {"LOWER": "of"}, {"LOWER": "the"}, {"LOWER": "day"}],
            [{"LOWER": "in"}, {"LOWER": {"IN": ["conclusion", "short",
                                                "essence", "summary"]}}],
            [{"LOWER": "the"}, {"LOWER": "bottom"}, {"LOWER": "line"}],
            [{"LOWER": "when"}, {"LOWER": "all"}, {"LOWER": "is"},
             {"LOWER": "said"}],
        ]),

    "HEDGE_STACK": (
        "Stacked hedge",
        "Two or more hedges on one claim. Usually means the claim should be "
        "stated plainly or dropped.",
        "med",
        [
            [{"LOWER": {"IN": ["perhaps", "arguably", "possibly", "maybe"]}},
             {"LOWER": {"IN": ["somewhat", "slightly", "fairly", "rather"]}}],
            [{"LOWER": "may"}, {"LOWER": "or"}, {"LOWER": "may"},
             {"LOWER": "not"}],
            [{"LOWER": "tend"}, {"LOWER": "to"},
             {"LOWER": {"IN": ["somewhat", "generally", "often"]}}],
            [{"LEMMA": "be"}, {"LOWER": "not"}, {"LOWER": "necessarily"}],
        ]),
}


# ---------------------------------------------------------------- em dash

def em_dash_findings(doc, raw, offset_base=0):
    """Em dashes, split by function. The pivot use is the high-signal one."""
    out = []
    for tok in doc:
        if tok.text not in ("—", "–"):
            continue
        after = doc[tok.i + 1:min(tok.i + 6, len(doc))].text.lower()
        before = doc[max(0, tok.i - 5):tok.i].text.lower()
        if re.search(r"\b(it|that|this)\s*('s|s| is| was)\b", after):
            sub = "pivot (— it's Y)"
            conf = "high"
        elif "not" in before or "n't" in before:
            sub = "pivot (not X — Y)"
            conf = "high"
        elif sum(1 for t in doc[tok.sent.start:tok.sent.end]
                 if t.text in ("—", "–")) >= 2:
            sub = "paired aside"
            conf = "med"
        else:
            sub = "single break"
            conf = "low"
        out.append((doc[max(tok.sent.start, tok.i - 8):
                        min(tok.sent.end, tok.i + 9)], sub, conf))
    return out


# ------------------------------------------------------------ html report

CONF_COLOR = {"high": "#c1440e", "med": "#b8860b", "low": "#6b7280"}

CSS = """
:root{--bg:#fbfaf8;--fg:#1c1a17;--mut:#6b6560;--line:#e3ded6;--card:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#16150f;--fg:#e8e4dc;
--mut:#9a938a;--line:#2f2c26;--card:#1e1c16}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
font:15px/1.65 ui-sans-serif,-apple-system,"Segoe UI",sans-serif}
header{padding:18px 24px;border-bottom:1px solid var(--line);
display:flex;gap:24px;align-items:baseline;flex-wrap:wrap;
position:sticky;top:0;background:var(--bg);z-index:10}
h1{font-size:17px;margin:0;font-weight:600}
.meta{color:var(--mut);font-size:13px}
.wrap{display:grid;grid-template-columns:1fr 380px;gap:0;
align-items:start}
@media(max-width:900px){.wrap{grid-template-columns:1fr}}
.src{padding:24px 28px;white-space:pre-wrap;
font:14px/1.75 ui-monospace,"SF Mono",Menlo,monospace;
border-right:1px solid var(--line);min-height:100vh}
.side{padding:18px;position:sticky;top:64px;max-height:calc(100vh - 64px);
overflow:auto}
mark{padding:1px 2px;border-radius:3px;cursor:pointer;
border-bottom:2px solid currentColor;background:transparent;color:inherit}
mark.high{background:rgba(193,68,14,.16);border-color:#c1440e}
mark.med{background:rgba(184,134,11,.16);border-color:#b8860b}
mark.low{background:rgba(107,114,128,.13);border-color:#9ca3af}
mark.on{outline:2px solid var(--fg);outline-offset:1px}
mark.off{background:transparent!important;border-color:transparent!important}
.f{padding:8px 10px;border:1px solid var(--line);border-radius:6px;
margin-bottom:6px;background:var(--card);cursor:pointer;font-size:13px}
.f:hover{border-color:var(--mut)}
.f .cid{font-weight:600;font-size:11px;letter-spacing:.04em}
.f .ln{color:var(--mut);font-size:11px;float:right;
font-family:ui-monospace,monospace;user-select:all}
.f .tx{color:var(--mut);margin-top:3px;
font-family:ui-monospace,monospace;font-size:12px}
.leg{margin-bottom:14px}
.leg label{display:flex;align-items:center;gap:7px;padding:3px 0;
font-size:12.5px;cursor:pointer;user-select:none}
.leg .n{margin-left:auto;color:var(--mut);font-variant-numeric:tabular-nums}
.sw{width:9px;height:9px;border-radius:2px;flex:none}
.note{color:var(--mut);font-size:12px;margin:6px 0 12px;line-height:1.5}
"""

JS = """
const marks=[...document.querySelectorAll('mark')];
const cards=[...document.querySelectorAll('.f')];
function sync(){
 const off=new Set([...document.querySelectorAll('.leg input')]
   .filter(i=>!i.checked).map(i=>i.dataset.cid));
 marks.forEach(m=>m.classList.toggle('off',off.has(m.dataset.cid)));
 cards.forEach(c=>c.style.display=off.has(c.dataset.cid)?'none':'');
}
document.querySelectorAll('.leg input').forEach(i=>i.onchange=sync);
function focus(id){
 marks.forEach(m=>m.classList.remove('on'));
 const m=document.querySelector(`mark[data-id="${id}"]`);
 if(m){m.classList.add('on');
  m.scrollIntoView({block:'center',behavior:'smooth'});}
}
cards.forEach(c=>c.onclick=()=>focus(c.dataset.id));
marks.forEach(m=>m.onclick=()=>{
 const c=document.querySelector(`.f[data-id="${m.dataset.id}"]`);
 if(c){cards.forEach(x=>x.style.background='');
  c.style.background='rgba(120,120,120,.14)';
  c.scrollIntoView({block:'center',behavior:'smooth'});}
});
"""


def build_html(path, raw, findings, stats):
    # Resolve overlaps: keep the highest-confidence span at each point,
    # then longest. Nested marks would break the HTML.
    rank = {"high": 0, "med": 1, "low": 2}
    ordered = sorted(enumerate(findings),
                     key=lambda t: (t[1].start, rank[t[1].confidence],
                                    -(t[1].end - t[1].start)))
    kept, last = [], -1
    for i, f in ordered:
        if f.start < last:
            continue
        kept.append((i, f))
        last = f.end

    out, pos = [], 0
    for i, f in kept:
        out.append(html.escape(raw[pos:f.start]))
        out.append(
            f'<mark class="{f.confidence}" data-cid="{f.construction}" '
            f'data-id="{i}" title="{html.escape(f.construction)}: '
            f'{html.escape(f.note[:200])}">'
            f'{html.escape(raw[f.start:f.end])}</mark>')
        pos = f.end
    out.append(html.escape(raw[pos:]))

    counts, notes, confs = {}, {}, {}
    for f in findings:
        counts[f.construction] = counts.get(f.construction, 0) + 1
        notes.setdefault(f.construction, f.note)
        confs.setdefault(f.construction, f.confidence)

    leg = "".join(
        f'<label><input type="checkbox" checked data-cid="{c}">'
        f'<span class="sw" style="background:{CONF_COLOR[confs[c]]}"></span>'
        f'{c}<span class="n">{n}</span></label>'
        for c, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))

    cards = "".join(
        f'<div class="f" data-cid="{f.construction}" data-id="{i}">'
        f'<span class="ln">{html.escape(f.fp)} &middot; L{f.line}</span>'
        f'<span class="cid" style="color:{CONF_COLOR[f.confidence]}">'
        f'{f.construction}</span>'
        f'<div class="tx">{html.escape(f.text[:110])}</div></div>'
        for i, f in enumerate(findings))

    hidden = len(findings) - len(kept)
    hid = (f' &middot; {hidden} overlapping hidden' if hidden else '')

    return f"""<!doctype html><meta charset="utf-8">
<title>ticfinder &mdash; {html.escape(Path(path).name)}</title>
<style>{CSS}</style>
<header><h1>{html.escape(Path(path).name)}</h1>
<span class="meta">{stats['words']} words &middot; {stats['sentences']}
sentences &middot; {stats['findings']} findings &middot;
{stats['per_1000_words']} per 1k{hid}</span></header>
<div class="wrap"><div class="src">{''.join(out)}</div>
<div class="side"><div class="leg">{leg}</div>
<div class="note">Click a finding to jump to it. Uncheck a construction to
hide it. Everything here is legitimate English &mdash; the flag means look,
not delete.</div>{cards}</div></div>
<script>{JS}</script>"""


# ---------------------------------------------------------------- analysis

@spacy.Language.component("block_boundaries")
def block_boundaries(doc):
    """Markdown headings, list items and paragraph breaks carry no terminal
    punctuation, so the parser merges them into the next sentence. Force a
    sentence start after any blank line. Must run BEFORE the parser."""
    for tok in doc:
        if tok.i == 0:
            continue
        prev = doc[tok.i - 1]
        if "\n\n" in prev.text or "\n\n" in prev.whitespace_:
            tok.is_sent_start = True
        elif ("\n" in prev.text or "\n" in prev.whitespace_) and \
                re.match(r"^[#*+\-]|^\d+\.", tok.text):
            tok.is_sent_start = True
    return doc


SHORTHAND = {"sm": "en_core_web_sm", "md": "en_core_web_md",
             "lg": "en_core_web_lg", "trf": "en_core_web_trf",
             "small": "en_core_web_sm", "medium": "en_core_web_md",
             "large": "en_core_web_lg"}


def resolve_model(name):
    """Accept 'md' as well as 'en_core_web_md'."""
    return SHORTHAND.get(name.lower(), name)


def load_model(name):
    nlp = spacy.load(resolve_model(name))
    if "block_boundaries" not in nlp.pipe_names:
        nlp.add_pipe("block_boundaries", before="parser")
    return nlp


def analyse(path, nlp, only=None, extra=(), disabled=()):
    raw = Path(path).read_text(encoding="utf-8")
    pragma = {}
    masked = mask_markdown(raw, pragma)
    code_spans = pragma.get("code_spans", [])

    def in_code(start, end):
        """True when a finding lies entirely inside inline code.

        Inline code keeps its text so the sentence still parses, but a
        construction written between backticks is being *named*, not used --
        `not X but Y` in a document about the tool is an example, not a tic.
        A finding that straddles the boundary still reports, because there
        the parse genuinely runs through the identifier.
        """
        return any(a <= start and end <= b for a, b in code_spans)

    def trimmed(span):
        """Character range of a span ignoring leading/trailing whitespace.

        Backticks are replaced by spaces, so a finding that covers exactly
        the code content still reports end_char two past it.
        """
        lo, hi = span.start_char, span.end_char
        while lo < hi and masked[lo].isspace():
            lo += 1
        while hi > lo and masked[hi - 1].isspace():
            hi -= 1
        return lo, hi
    doc = nlp(masked)

    findings = []

    def add(cid, label, span, note, conf, sub="", pname=""):
        if in_code(*trimmed(span)):
            return          # a construction named between backticks is an
                            # example, not a tic
        findings.append(Finding(
            construction=cid,
            label=label + (f" [{sub}]" if sub else ""),
            text=span.text.strip().replace("\n", " "),
            context=span.sent.text.strip().replace("\n", " ")[:240],
            line=line_of(raw, span.start_char),
            start=span.start_char, end=span.end_char,
            note=note, confidence=conf, pattern=pname))

    # structural
    for cid, meta in CONSTRUCTIONS.items():
        if only and cid not in only:
            continue
        if cid in disabled:
            continue
        for span, sub, conf, pname in run_construction(cid, doc, nlp,
                                                       disabled):
            add(cid, meta["label"], span, meta["note"], conf, sub,
                pname)

    # phrasal
    matcher = Matcher(nlp.vocab)
    meta = {}
    for cid, (label, note, conf, pats) in PHRASE_PATTERNS.items():
        if only and cid not in only:
            continue
        if cid in disabled:
            continue
        matcher.add(cid, pats)
        meta[cid] = (label, note, conf)
    for entry in extra:
        cid = entry["id"]
        if only and cid not in only:
            continue
        if cid in disabled:
            continue
        pats = phrase_patterns(entry, nlp)
        if not pats:
            continue
        matcher.add(cid, pats)
        meta[cid] = (entry["label"], entry["note"], entry["confidence"])
    for mid, ms, me in (matcher(doc) if len(matcher) else []):
        cid = nlp.vocab.strings[mid]
        label, note, conf = meta[cid]
        add(cid, label, doc[ms:me], note, conf)

    # em dash
    if not only or "EM_DASH" in only:
        for span, sub, conf in em_dash_findings(doc, raw):
            add("EM_DASH", "Em dash", span,
                "Not wrong. But count them, and look hard at the pivot uses.",
                conf, sub)

    findings.sort(key=lambda f: f.start)

    kept = len(masked.strip())
    orig = len(raw.strip())
    # Deliberate <!-- ticfinder_off --> regions are not accidental loss, so
    # they must not trigger the "did the masker eat my file" warning.
    orig_auto = max(orig - pragma.get("pragma_chars", 0), 1)
    masked_pct = 100 * (1 - kept / orig_auto) if orig else 0
    masked_pct = max(0.0, min(100.0, masked_pct))

    words = sum(1 for t in doc if t.is_alpha)
    sents = list(doc.sents)
    lens = [len([t for t in s if t.is_alpha]) for s in sents] or [0]
    mean = sum(lens) / len(lens)
    var = (sum((x - mean) ** 2 for x in lens) / len(lens)) ** 0.5
    stats = {
        "words": words, "sentences": len(sents),
        "mean_sentence_len": round(mean, 1),
        "sentence_len_stdev": round(var, 1),
        "findings": len(findings),
        "per_1000_words": round(len(findings) / max(words, 1) * 1000, 1),
        "masked_pct": round(masked_pct, 1),
        "pragma_regions": pragma.get("pragma_regions", 0),
    }
    return findings, stats


# ---------------------------------------------------------------- output

C = {"high": "\033[91m", "med": "\033[93m", "low": "\033[90m",
     "b": "\033[1m", "d": "\033[2m", "0": "\033[0m"}

# Characters that show up in prose being quoted back. Mapped, not stripped,
# so a flagged em dash is still visible as an em dash in ASCII mode.
TRANSLIT = {
    "\u2014": "--", "\u2013": "-", "\u2026": "...", "\u00b7": "*",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u2192": "->", "\u00ab": '"', "\u00bb": '"',
    "\u2032": "'", "\u2033": '"', "\u2212": "-", "\u200b": "",
}

ASCII_MODE = False


def a(text):
    """Force output to ASCII when asked, or when stdout cannot encode it."""
    if not ASCII_MODE:
        return text
    for k, v in TRANSLIT.items():
        text = text.replace(k, v)
    return text.encode("ascii", "backslashreplace").decode("ascii")


def summary_table(findings, c, width=28):
    """Aligned counts, sorted by frequency. Bars are ASCII-safe."""
    by = Counter(f.construction for f in findings)
    if not by:
        return []
    conf = {}
    for f in findings:
        conf.setdefault(f.construction, f.confidence)
    top = max(by.values())
    name_w = max(len(k) for k in by)
    rows = []
    for cid, n in sorted(by.items(), key=lambda kv: (-kv[1], kv[0])):
        bar = "#" * max(1, round(n / top * 12))
        col = c[conf.get(cid, "med")]
        rows.append(f"  {col}{cid:<{name_w}}{c['0']}  "
                    f"{n:>3}  {c['d']}{bar}{c['0']}")
    return rows


def term_width(default=100):
    try:
        w = shutil.get_terminal_size((default, 24)).columns
    except Exception:
        w = default
    return max(60, min(w, 120))


def wrap(text, width, indent=""):
    return textwrap.fill(text, width=width, initial_indent=indent,
                         subsequent_indent=indent,
                         break_long_words=False, break_on_hyphens=False)


def window(context, match, width):
    """Show the match inside its sentence, trimmed on word boundaries.

    Truncating from the start of the sentence often cuts the flagged text off
    entirely, which is the one thing that has to stay visible.
    """
    ctx = " ".join(context.split())
    m = " ".join(match.split())
    if len(ctx) <= width:
        return ctx
    i = ctx.find(m[:40])
    if i < 0:
        i = 0
    half = max(0, (width - len(m)) // 2)
    lo = max(0, i - half)
    hi = min(len(ctx), lo + width)
    lo = max(0, hi - width)
    out = ctx[lo:hi]
    if lo > 0:
        out = out[out.find(" ") + 1:]
        out = ("..." if ASCII_MODE else "\u2026") + " " + out
    if hi < len(ctx):
        out = out[:out.rfind(" ")] + " " + ("..." if ASCII_MODE
                                            else "\u2026")
    return out


def report(path, findings, stats, plain=False, show_stats=False,
           summary_only=False, by_position=False, compact=False,
           show_context=False, explain=False):
    c = {k: "" for k in C} if plain else C
    sep = "*" if ASCII_MODE else "\u00b7"
    W = term_width()

    print(a(f"\n{c['b']}{path}{c['0']}"))
    print(a(f"  {c['d']}{stats['words']} words {sep} "
            f"{stats['sentences']} sentences {sep} "
            f"{stats['findings']} findings "
            f"({stats['per_1000_words']} per 1k words){c['0']}"))
    if stats.get("waived") or stats.get("stale"):
        bits = []
        if stats.get("waived"):
            bits.append(f"{stats['waived']} waived")
        if stats.get("stale"):
            bits.append(f"{stats['stale']} stale (no longer in the text)")
        line = ", ".join(bits)
        if stats.get("waiver_file"):
            line += f" [{stats['waiver_file']}]"
        print(a(f"  {c['d']}{line}{c['0']}"))
        for e in stats.get("stale_entries", []):
            txt = " ".join(str(e["text"]).split())
            room = max(20, W - 34)
            print(a(f"    {c['d']}{e['fp']}  was L{e['line']}  "
                    f"{e['construction']}: {txt[:room]}{c['0']}"))
    if stats.get("pragma_regions"):
        n = stats["pragma_regions"]
        print(a(f"  {c['d']}{n} region{'s' if n != 1 else ''} skipped via "
                f"ticfinder_off{c['0']}"))
    if stats.get("masked_pct", 0) >= 40:
        print(a(wrap(f"warning: {stats['masked_pct']}% of this file was "
                     f"masked as non-prose (code, tables, quotes). If that "
                     f"looks wrong, check the fences.", W, "  ")))
    if show_stats:
        print(a(f"  {c['d']}mean sentence {stats['mean_sentence_len']} words, "
                f"stdev {stats['sentence_len_stdev']}{c['0']}"))

    if not findings:
        print(a(f"  {c['d']}clean{c['0']}\n"))
        return

    print()
    for row in summary_table(findings, c):
        print(a(row))
    print()

    if summary_only:
        return

    if compact:
        cw = max(len(f.construction) for f in findings)
        for f in sorted(findings, key=lambda x: x.start):
            col = c[f.confidence]
            txt = " ".join(f.text.split())
            room = W - (18 + cw)
            print(a(f"  {c['d']}{f.fp}{c['0']} {col}L{f.line:<5}{c['0']} "
                    f"{f.construction:<{cw}}  {txt[:room]}"))
        print()
        return

    # Grouped by construction so each header and note is printed once.
    if by_position:
        order = sorted(findings, key=lambda x: x.start)
    else:
        counts = Counter(f.construction for f in findings)
        order = sorted(findings,
                       key=lambda x: (-counts[x.construction],
                                      x.construction, x.start))

    dash = "--" if ASCII_MODE else "\u2014"
    current = None
    for f in order:
        if f.construction != current:
            current = f.construction
            n = sum(1 for x in order if x.construction == current)
            lab = f.label.split(" [")[0]
            room = W - len(f.construction) - len(dash) - len(str(n)) - 5
            if len(lab) > room:
                lab = lab[:max(0, room - 3)].rstrip() + "..."
            print(a(f"{c['b']}{f.construction}{c['0']} {dash} "
                    f"{lab} {c['d']}({n}){c['0']}"))
            if f.note:
                note = f.note if explain else f.note.split(". ")[0] + "."
                print(a(f"{c['d']}{wrap(note, W - 2, '  ')}{c['0']}"))
        col = c[f.confidence]
        sub = f.label.split(" [")[1].rstrip("]") if " [" in f.label else ""
        tag = f"{c['d']}[{sub}]{c['0']} " if sub else ""
        txt = " ".join(f.text.split())
        head = f"  {c['d']}{f.fp}{c['0']} {col}L{f.line:<5}{c['0']} {tag}"
        room = W - (2 + 7 + 7 + (len(sub) + 3 if sub else 0))
        print(a(head + txt[:room]))
        if show_context and f.context:
            ctx = window(f.context, f.text, W - 15)
            print(a(f"{c['d']}         {ctx}{c['0']}"))
    print()


def pattern_report(allout, c):
    """Hits per pattern. A pattern with a big share and a low confidence is
    the first thing to look at when the tool feels noisy."""
    agg = Counter()
    for v in allout.values():
        for f in v["findings"]:
            key = (f["construction"], f["pattern"] or "-")
            agg[key] += 1
    if not agg:
        return
    print(a(f"{c['b']}PATTERNS{c['0']}"))
    w1 = max(len(k[0]) for k in agg)
    w2 = max(len(k[1]) for k in agg)
    for (cid, pn), n in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0])):
        print(a(f"  {cid:<{w1}}  {c['d']}{pn:<{w2}}{c['0']}  {n:>4}"))
    print()


def totals(allout, c):
    """Aggregate across files -- the view that matters for a whole blog."""
    agg = Counter()
    words = 0
    for v in allout.values():
        words += v["stats"]["words"]
        for f in v["findings"]:
            agg[f["construction"]] += 1
    if not agg:
        return
    sep = "*" if ASCII_MODE else "\u00b7"
    total = sum(agg.values())
    print(a(f"{c['b']}ALL FILES{c['0']}"))
    print(a(f"  {c['d']}{len(allout)} files {sep} {words} words {sep} "
            f"{total} findings "
            f"({round(total / max(words, 1) * 1000, 1)} per 1k words){c['0']}"))
    print()
    name_w = max(len(k) for k in agg)
    top = max(agg.values())
    for cid, n in sorted(agg.items(), key=lambda kv: (-kv[1], kv[0])):
        bar = "#" * max(1, round(n / top * 12))
        pct = n / total * 100
        print(a(f"  {cid:<{name_w}}  {n:>4}  {pct:>5.1f}%  "
                f"{c['d']}{bar}{c['0']}"))
    print()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", help="write findings to JSON")
    ap.add_argument("--html", metavar="DIR",
                    help="write a side-by-side HTML report per file")
    ap.add_argument("--only", help="comma-separated construction ids")
    ap.add_argument("--off", metavar="IDS",
                    help="comma-separated construction ids or pattern names "
                         "to suppress, e.g. ALTERNATIVE_FRAMING or "
                         "af_less_than")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--phrases", action="append", metavar="FILE",
                    help="JSON phrase list; repeatable. Without this, "
                         "ticfinder-phrases.json is picked up from the "
                         "current directory or next to the script.")
    ap.add_argument("--no-phrases", action="store_true",
                    help="ignore phrase files entirely")
    ap.add_argument("--waive", metavar="IDS",
                    help="waive findings by short id (comma list), or 'all' "
                         "for everything currently shown")
    ap.add_argument("--unwaive", metavar="IDS",
                    help="remove waivers by short id, or 'all'")
    ap.add_argument("--show-waived", action="store_true",
                    help="include already-waived findings in the output")
    ap.add_argument("--waiver-dir", metavar="DIR",
                    help="keep waiver files in DIR instead of beside the "
                         "source (default: alongside the source file)")
    ap.add_argument("--waiver-file", metavar="FILE",
                    help="explicit waiver path; only valid for a single "
                         "input file")
    ap.add_argument("--no-waivers", action="store_true",
                    help="ignore waiver files entirely")
    ap.add_argument("--prune-stale", action="store_true",
                    help="remove waivers whose text is no longer in the "
                         "document")
    ap.add_argument("--compact", action="store_true",
                    help="one line per finding")
    ap.add_argument("--by-position", action="store_true",
                    help="order findings by position in the document "
                         "(default groups them by construction)")
    ap.add_argument("--context", action="store_true",
                    help="show the surrounding sentence for each finding")
    ap.add_argument("--explain", action="store_true",
                    help="print the full note for each construction, not "
                         "just its first line")
    ap.add_argument("--patterns", action="store_true",
                    help="report hits per pattern, not per construction -- "
                         "use this to find which patterns are noisy")
    ap.add_argument("--summary", action="store_true",
                    help="counts only, no individual findings")
    ap.add_argument("--plain", action="store_true",
                    help="no ANSI colour (automatic when piped)")
    ap.add_argument("--colour", "--color", action="store_true",
                    dest="colour",
                    help="force colour even when piped")
    ap.add_argument("--model", default=MODEL,
                    metavar="NAME",
                    help="spaCy model: en_core_web_md (default), or the "
                         "shorthand sm/md/lg/trf")
    ap.add_argument("--ascii", action="store_true",
                    help="ASCII-only output (auto-enabled if stdout can't "
                         "encode UTF-8)")
    args = ap.parse_args()

    global ASCII_MODE
    enc = (sys.stdout.encoding or "ascii").lower()
    ASCII_MODE = args.ascii or enc not in ("utf-8", "utf8")

    # Colour is ANSI escapes, which are ASCII -- so --ascii does NOT remove
    # them. Suppress them whenever output isn't a terminal, which covers
    # pipes, redirects and CI logs. --colour forces them back on.
    import os
    plain = (args.plain
             or os.environ.get("NO_COLOR") is not None
             or os.environ.get("TERM") == "dumb"
             or not sys.stdout.isatty())
    if args.colour:
        plain = False

    want = resolve_model(args.model)
    try:
        nlp = load_model(want)
    except OSError:
        installed = [m for m in spacy.util.get_installed_models()
                     if m.startswith("en_core_web")]
        msg = [f"spaCy model '{want}' is not installed.",
               "",
               f"  python -m spacy download {want}"]
        if installed:
            msg += ["", "Installed English models: " + ", ".join(installed)]
        else:
            msg += ["", "No English models are installed. 'en_core_web_md' "
                        "is the recommended one."]
        msg += ["", "Note: --model takes a full package name "
                    "(en_core_web_md); 'sm', 'md', 'lg' and 'trf' also work "
                    "as shorthand."]
        sys.exit("\n".join(msg))

    only = set(args.only.split(",")) if args.only else None
    disabled = set(x.strip() for x in args.off.split(",")) if args.off \
        else set()
    if only:
        only = only - disabled

    extra = []
    if not args.no_phrases:
        for f in discover_phrase_files(args.phrases):
            try:
                extra.extend(load_phrase_file(f))
            except (ValueError, json.JSONDecodeError) as e:
                sys.exit(f"{e}")
            except OSError as e:
                sys.exit(f"cannot read {f}: {e}")
        if extra and args.phrases:
            n = sum(len(x["phrases"]) for x in extra)
            print(f"  {n} phrases from "
                  f"{', '.join(str(f) for f in discover_phrase_files(args.phrases))}")

    if args.waiver_file and len(args.files) > 1:
        sys.exit("--waiver-file takes a single input file; use --waiver-dir "
                 "for multiple files")

    waive_ids = {x.strip() for x in args.waive.split(",")} if args.waive \
        else set()
    unwaive_ids = {x.strip() for x in args.unwaive.split(",")} \
        if args.unwaive else set()

    allout = {}
    for p in args.files:
        f, st = analyse(p, nlp, only, extra, disabled)
        for x in f:
            x.fp = fingerprint(x)

        wpath = waiver_path(p, args.waiver_dir, args.waiver_file)
        waivers, warn = ({}, None) if args.no_waivers \
            else load_waivers(wpath, p)
        if warn:
            print(f"  warning: {warn}")
        held = set(waivers)
        dirty = False

        if unwaive_ids and not args.no_waivers:
            # set(held), not held: `held -= drop` mutates in place, and an
            # alias would be emptied before the count is read.
            drop = set(held) if "all" in unwaive_ids else \
                (held & unwaive_ids)
            if drop:
                for fp in drop:
                    waivers.pop(fp, None)
                held -= drop
                dirty = True
                print(f"  removed {len(drop)} waiver"
                      f"{'s' if len(drop) != 1 else ''} from {wpath}")

        if waive_ids and not args.no_waivers:
            live = {x.fp: x for x in f if x.fp not in held}
            take = set(live) if "all" in waive_ids else \
                (set(live) & waive_ids)
            unknown = (waive_ids - {"all"}) - set(live) - held
            if unknown:
                print(f"  warning: no such finding: "
                      f"{', '.join(sorted(unknown))}")
            if take:
                for fp in sorted(take):
                    waivers[fp] = {
                        "construction": live[fp].construction,
                        "pattern": live[fp].pattern,
                        "line_when_waived": live[fp].line,
                        "text": live[fp].text[:100],
                    }
                held |= take
                dirty = True
                print(f"  waived {len(take)} finding"
                      f"{'s' if len(take) != 1 else ''} -> {wpath}")

        seen_fps = {x.fp for x in f}
        stale = held - seen_fps
        st["stale_entries"] = [
            {"fp": fp,
             "construction": waivers.get(fp, {}).get("construction", "?"),
             "text": waivers.get(fp, {}).get("text", ""),
             "line": waivers.get(fp, {}).get("line_when_waived", "?")}
            for fp in sorted(stale)]
        st["waived"] = len(held & seen_fps)
        st["stale"] = len(stale)
        st["waiver_file"] = str(wpath) if held else ""

        if args.prune_stale and stale and not args.no_waivers:
            for fp in stale:
                waivers.pop(fp, None)
            held -= stale
            st["stale"] = 0
            st["stale_entries"] = []
            dirty = True
            print(f"  pruned {len(stale)} stale waiver"
                  f"{'s' if len(stale) != 1 else ''} from {wpath}")

        if dirty:
            save_waivers(wpath, p, waivers)

        if not args.show_waived and held:
            f = [x for x in f if x.fp not in held]
            st["findings"] = len(f)
            st["per_1000_words"] = round(
                len(f) / max(st["words"], 1) * 1000, 1)

        report(p, f, st, plain, args.stats, args.summary,
               args.by_position, args.compact, args.context, args.explain)
        allout[p] = {"stats": st, "findings": [asdict(x) for x in f]}

        if args.html:
            d = Path(args.html)
            d.mkdir(parents=True, exist_ok=True)
            raw = Path(p).read_text(encoding="utf-8")
            dest = d / (Path(p).stem + ".html")
            dest.write_text(build_html(p, raw, f, st), encoding="utf-8")
            print(f"  -> {dest}")

    if args.patterns:
        pattern_report(allout, {k: "" for k in C} if plain else C)
    if len(args.files) > 1:
        totals(allout, {k: "" for k in C} if plain else C)

    if args.json:
        # JSON is always UTF-8 on disk; ensure_ascii keeps the file 7-bit safe.
        Path(args.json).write_text(
            json.dumps(allout, indent=2, ensure_ascii=ASCII_MODE),
            encoding="utf-8")
        print(f"wrote {args.json}")


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # Downstream closed early (`| head`, quitting `less`). Redirect
        # stdout to devnull so the interpreter's own flush at exit doesn't
        # raise a second BrokenPipeError on the way out.
        import os
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)

